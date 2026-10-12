from brian import *
import asyncio
import time
import math
import brick
import pid

yawMotor: motors.Motor
extendonMotor: motors.Motor
endMotor: motors.Motor

extendonResetButton: sensors.EV3.TouchSensorEV3

YAW_KP: float = 0.5
YAW_KI: float = 0.0
YAW_KD: float = 0.0

EXTENDON_CONVERSION: float = 700.0 # how many degrees of extendonMotor correspond to 1 unit of grid
EXTENDON_MAX: float = 1.0 # max extendon length in units of grid
EXTENDON_MIN: float = 0.1 # min extendon length in units of grid
YAW_RATIO: float = 0.21 * math.pi / 180.0  # how many degrees of yawMotor correspond to 1 radian of rotation

async def init(yaw_motor: motors.MotorPort, extendon_motor: motors.MotorPort, end_motor: motors.MotorPort, extendon_reset_button: sensors.SensorPort):
    global yawMotor, extendonMotor, endMotor, extendonResetButton
    yawMotor = motors.Motor(yaw_motor)
    extendonMotor = motors.Motor(extendon_motor)
    endMotor = motors.Motor(end_motor)

    extendonResetButton = sensors.EV3.TouchSensor(extendon_reset_button)

    while not yawMotor.is_ready() or not extendonMotor.is_ready() or not endMotor.is_ready():
        await asyncio.sleep(0.1)

    await resetExtendon()
    resetEndMotor()
    # program expects the yaw motor to be at 0 degrees when the crane is facing forward, so we don't reset it here

def resetEndMotor():
    global endMotor
    endMotor.reset_angle()

async def resetExtendon():
    global extendonMotor, extendonResetButton
    extendonMotor.hold()
    extendonMotor.run_at_speed(-100)
    while True:
        if extendonResetButton.is_pressed():
            break
        await asyncio.sleep(0.01)
    extendonMotor.hold()
    await asyncio.sleep(0.5)
    extendonMotor.reset_angle()

def getExtendonDistance() -> float:
    global extendonMotor
    return (extendonMotor.current_angle() / EXTENDON_CONVERSION) + EXTENDON_MIN

def getExtendonSpeed() -> float:
    global extendonMotor
    return (extendonMotor.current_speed() / EXTENDON_CONVERSION)

async def moveLinear(
    target_x: float,
    target_z: float,
    *,
    max_angular_speed: float,       # rad/s
    max_extension_speed: float,     # grid units/s
    max_acceleration: float,        # grid units/s^2
    min_extension: float = EXTENDON_MIN,    # grid units
    max_extension: float = EXTENDON_MAX,     # grid units
    extension_limit_margin: float = 0.01,  # grid units
    control_hz: float = 100.0,
    position_tolerance: float = 0.005,     # grid units
    position_gain: float = 3.0,
    timeout: float = 30.0,
):
    """
    Move the end effector along a straight line in the XZ plane.

    All distances, speeds and accelerations use consistent custom
    grid units. Angles and angular velocities use radians.

    Crane model:
        x = r * cos(theta)
        z = r * sin(theta)

    Returns True on success.
    Raises ValueError for unreachable paths and TimeoutError on timeout.
    """

    global yawMotor, extendonMotor

    if control_hz <= 0:
        raise ValueError("control_hz must be positive")
    if max_angular_speed <= 0 or max_extension_speed <= 0:
        raise ValueError("Motor speed limits must be positive")
    if max_acceleration <= 0:
        raise ValueError("max_acceleration must be positive")
    if min_extension < 0 or max_extension <= min_extension:
        raise ValueError("Invalid extension limits")
    if extension_limit_margin < 0:
        raise ValueError("Extension margin cannot be negative")
    if 2 * extension_limit_margin >= max_extension - min_extension:
        raise ValueError("Extension margin leaves no usable range")

    dt_nominal = 1.0 / control_hz

    safe_min = min_extension + extension_limit_margin
    safe_max = max_extension - extension_limit_margin

    # -------------------------------------------------------
    # HARDWARE INTERFACE
    # -------------------------------------------------------

    def get_rotation_angle():
        return brick.gyro.angle() * math.pi / 180.0

    def get_extension_position():
        return getExtendonDistance()

    def get_rotation_speed():
        return brick.gyro.speed() * math.pi / 180.0

    def get_extension_speed():
        return getExtendonSpeed()

    def set_rotation_speed(speed):
        yawMotor.run_at_speed(speed * (1/YAW_RATIO))

    def set_extension_speed(speed):
        extendonMotor.run_at_speed(speed * EXTENDON_CONVERSION)

    def stop_motors():
        set_rotation_speed(0.0)
        set_extension_speed(0.0)
        yawMotor.hold()
        extendonMotor.hold()

    # -------------------------------------------------------
    # INITIAL STATE AND PATH VALIDATION
    # -------------------------------------------------------

    theta_start = get_rotation_angle()
    r_start = get_extension_position()

    if not safe_min <= r_start <= safe_max:
        raise ValueError(
            f"Current extension {r_start} is outside the safe range "
            f"[{safe_min}, {safe_max}]"
        )

    x_start = r_start * math.cos(theta_start)
    z_start = r_start * math.sin(theta_start)

    dx = target_x - x_start
    dz = target_z - z_start
    length = math.hypot(dx, dz)

    target_r = math.hypot(target_x, target_z)

    if not safe_min <= target_r <= safe_max:
        raise ValueError(
            f"Target extension {target_r} is outside the safe range "
            f"[{safe_min}, {safe_max}]"
        )

    if length < position_tolerance:
        stop_motors()
        return True

    ux = dx / length
    uz = dz / length

    # The closest point on the requested segment to the rotation axis
    # determines the minimum required extension.
    projection = -(x_start * ux + z_start * uz)
    closest_s = max(0.0, min(length, projection))

    closest_x = x_start + ux * closest_s
    closest_z = z_start + uz * closest_s
    minimum_path_radius = math.hypot(closest_x, closest_z)

    # Distance from the origin is convex along a straight segment,
    # so the maximum occurs at one of its endpoints.
    maximum_path_radius = max(r_start, target_r)

    if minimum_path_radius < safe_min or maximum_path_radius > safe_max:
        raise ValueError(
            "Straight-line path crosses the safe extension limits. "
            f"Path radius range: [{minimum_path_radius}, "
            f"{maximum_path_radius}], safe range: "
            f"[{safe_min}, {safe_max}]."
        )

    # -------------------------------------------------------
    # TRAJECTORY STATE
    # -------------------------------------------------------

    progress = 0.0
    path_speed = 0.0

    start_time = time.monotonic()
    last_time = start_time

    try:
        while True:
            now = time.monotonic()
            dt = min(now - last_time, 0.05)
            last_time = now

            if now - start_time > timeout:
                raise TimeoutError("Crane movement timed out")

            if dt <= 0:
                continue

            # 1. Read actual state.
            theta = get_rotation_angle()
            r = get_extension_position()

            theta_dot_actual = get_rotation_speed()
            r_dot_actual = get_extension_speed()

            # 2. Runtime safety check.
            if not safe_min <= r <= safe_max:
                raise RuntimeError(
                    f"Extension limit violated: r={r}"
                )

            # 3. Actual Cartesian position.
            x = r * math.cos(theta)
            z = r * math.sin(theta)

            error_x = target_x - x
            error_z = target_z - z
            remaining = math.hypot(error_x, error_z)

            if (
                remaining < position_tolerance
                and abs(theta_dot_actual) < 0.03
                and abs(r_dot_actual) < 0.01
            ):
                stop_motors()
                return True

            # 4. Desired point on the line.
            desired_progress = min(progress, length)

            desired_x = x_start + ux * desired_progress
            desired_z = z_start + uz * desired_progress

            track_error_x = desired_x - x
            track_error_z = desired_z - z

            # 5. Joint velocity required per unit Cartesian path speed.
            a_r = ux * math.cos(theta) + uz * math.sin(theta)

            a_theta = (
                -ux * math.sin(theta) + uz * math.cos(theta)
            ) / max(r, safe_min)

            speed_limit = float("inf")

            if abs(a_theta) > 1e-9:
                speed_limit = min(
                    speed_limit,
                    max_angular_speed / abs(a_theta),
                )

            if abs(a_r) > 1e-9:
                speed_limit = min(
                    speed_limit,
                    max_extension_speed / abs(a_r),
                )

            # 6. Braking constraint for the endpoint.
            braking_speed = math.sqrt(
                max(0.0, 2.0 * max_acceleration * remaining)
            )

            desired_speed = min(speed_limit, braking_speed)

            # 7. Acceleration-limited path speed.
            max_speed_change = max_acceleration * dt

            path_speed += max(
                -max_speed_change,
                min(
                    max_speed_change,
                    desired_speed - path_speed,
                ),
            )

            path_speed = max(0.0, path_speed)

            # 8. Cartesian feedforward + position feedback.
            vx = ux * path_speed + position_gain * track_error_x
            vz = uz * path_speed + position_gain * track_error_z

            # 9. Inverse Jacobian.
            extension_command = (
                vx * math.cos(theta) + vz * math.sin(theta)
            )

            rotation_command = (
                -vx * math.sin(theta) + vz * math.cos(theta)
            ) / max(r, safe_min)

            # 10. Scale both velocities together to respect speed limits.
            ratio = max(
                1.0,
                abs(rotation_command) / max_angular_speed,
                abs(extension_command) / max_extension_speed,
            )

            rotation_command /= ratio
            extension_command /= ratio

            # 11. Enforce extension boundaries.
            # Never command movement farther outside the safe range.
            if r <= safe_min and extension_command < 0:
                extension_command = 0.0

            if r >= safe_max and extension_command > 0:
                extension_command = 0.0

            # 12. Send velocity commands.
            set_rotation_speed(rotation_command)
            set_extension_speed(extension_command)

            # 13. Advance the virtual trajectory.
            progress = min(
                length,
                progress + path_speed * dt,
            )

            elapsed = time.monotonic() - now
            await asyncio.sleep(max(0.0, dt_nominal - elapsed))

    except Exception:
        stop_motors()
        raise