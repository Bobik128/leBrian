"""Brian crane control in the XZ plane, using the yaw motor encoder.

Distances use your grid units. The crane position is:
    x = r * cos(theta), z = r * sin(theta)

Targets are relative to the stationary crane base. Yaw encoder zero must
correspond to the arm pointing along +X. init() does not change that zero.
The existing 'Extendon' names are retained for compatibility with your code.
"""

from brian import motors, sensors
import asyncio
import math
import time


# Some MicroPython builds do not provide the CPython TimeoutError class.
try:
    TimeoutError
except NameError:
    class TimeoutError(Exception):
        pass


yawMotor = None
extendonMotor = None
endMotor = None
extendonResetButton = None

EXTENDON_CONVERSION = 1500.0  # Extension motor degrees per grid unit.
EXTENDON_MAX = 1.0          # Physical maximum radius in grid units.
EXTENDON_MIN = 0.2          # Radius at the retracted homing switch.
YAW_RATIO = 0.21 * math.pi / 180.0  # Crane radians per yaw motor degree.

_motion_busy = False
_extension_homed = False


def _hypot(x, z):
    return math.sqrt(x * x + z * z)


def _finite(value):
    return -float("inf") < value < float("inf")


def _positive(name, value):
    if not _finite(value) or value <= 0:
        raise ValueError(name + " must be finite and positive")


def _check_timeout(start_ms, timeout, message):
    if time.ticks_diff(time.ticks_ms(), start_ms) >= timeout * 1000.0:
        raise TimeoutError(message)


async def _wait_ready(devices, timeout):
    start_ms = time.ticks_ms()
    while not all(device.is_ready() for device in devices):
        _check_timeout(start_ms, timeout, "Motor or sensor readiness timed out")
        await asyncio.sleep(0.01)


def _hold_motion_motors():
    # Attempt both holds even if the first motor reports an error.
    try:
        if yawMotor is not None:
            yawMotor.hold()
    finally:
        if extendonMotor is not None:
            extendonMotor.hold()


def _check_calibration():
    _positive("EXTENDON_CONVERSION", EXTENDON_CONVERSION)
    if not _finite(YAW_RATIO) or YAW_RATIO == 0:
        raise ValueError("YAW_RATIO must be finite and nonzero")


async def init(
    yaw_motor: motors.MotorPort,
    extendon_motor: motors.MotorPort,
    end_motor: motors.MotorPort,
    extendon_reset_button: sensors.SensorPort,
    *,
    readiness_timeout: float = 10.0,
    homing_timeout: float = 15.0,
    extension_limit_margin: float = 0.01,
):
    global yawMotor, extendonMotor, endMotor, extendonResetButton

    _check_calibration()
    _positive("readiness_timeout", readiness_timeout)
    _positive("homing_timeout", homing_timeout)
    if _motion_busy or yawMotor is not None:
        raise RuntimeError("Crane is busy or init() has already been called")

    try:
        yawMotor = motors.Motor(yaw_motor)
        extendonMotor = motors.Motor(extendon_motor)
        endMotor = motors.Motor(end_motor)
        extendonResetButton = sensors.EV3.TouchSensorEV3(extendon_reset_button)

        await _wait_ready(
            (yawMotor, extendonMotor, endMotor, extendonResetButton),
            readiness_timeout,
        )
        await resetExtendon(
            timeout=homing_timeout,
            extension_limit_margin=extension_limit_margin,
        )
        resetEndMotor()
        # Preserve the existing yaw reference, as in your original init().
    finally:
        try:
            _hold_motion_motors()
        finally:
            if endMotor is not None:
                endMotor.hold()


def resetEndMotor():
    if endMotor is None:
        raise RuntimeError("Call init() first")
    endMotor.reset_angle()


def resetYawMotor():
    """Call only when the arm is stationary and physically points along +X."""
    if yawMotor is None:
        raise RuntimeError("Call init() first")
    if _motion_busy:
        raise RuntimeError("Cannot reset yaw during a movement")
    yawMotor.hold()
    yawMotor.reset_angle()


async def resetExtendon(
    *,
    timeout: float = 200.0,
    homing_speed: float = 200.0,
    extension_limit_margin: float = 0.01,
    settle_time: float = 0.25,
):
    """Home at maximum extension, then retract to the usable minimum.

    Positive motor speed extends; encoder zero is at EXTENDON_MAX.
    Set extension_limit_margin=0 to retract to the physical minimum.
    """
    global _motion_busy, _extension_homed

    _check_calibration()
    _positive("timeout", timeout)
    _positive("homing_speed", homing_speed)
    speed = int(homing_speed)
    if speed < 1:
        raise ValueError("homing_speed must be at least 1 motor degree/s")
    if not _finite(settle_time) or settle_time < 0:
        raise ValueError("Invalid settle_time")
    if (
        not _finite(extension_limit_margin) or extension_limit_margin < 0
        or 2 * extension_limit_margin + 0.005 >= EXTENDON_MAX - EXTENDON_MIN
    ):
        raise ValueError("Invalid extension margin")
    if extendonMotor is None or extendonResetButton is None:
        raise RuntimeError("Call init() first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")

    _motion_busy = True
    _extension_homed = False
    start_ms = time.ticks_ms()
    try:
        await _wait_ready((extendonMotor, extendonResetButton), timeout)
        _hold_motion_motors()

        # Extend until the maximum-extension switch is pressed.
        if not extendonResetButton.is_pressed():
            extendonMotor.run_at_speed(speed)
        while not extendonResetButton.is_pressed():
            _check_timeout(start_ms, timeout, "Extension homing timed out")
            if not extendonMotor.is_ready() or not extendonResetButton.is_ready():
                raise RuntimeError("Homing motor or switch became unavailable")
            await asyncio.sleep(0.01)

        extendonMotor.hold()
        await asyncio.sleep(settle_time)
        _check_timeout(start_ms, timeout, "Extension homing timed out")
        extendonMotor.reset_angle()  # Zero now means maximum extension.

        # Retract by the calibrated travel. Leave a little stopping room
        # inside the margin when it is enabled, for moveLinear() compatibility.
        clearance = extension_limit_margin
        if clearance > 0:
            clearance += 0.005
        travel = (EXTENDON_MAX - EXTENDON_MIN - clearance) * EXTENDON_CONVERSION
        target_angle = -int(travel)
        extendonMotor.run_at_speed(-speed)
        while extendonMotor.current_angle() > target_angle:
            _check_timeout(start_ms, timeout, "Extension retraction timed out")
            if not extendonMotor.is_ready():
                raise RuntimeError("Extension motor became unavailable")
            await asyncio.sleep(0.01)

        extendonMotor.hold()
        await asyncio.sleep(settle_time)
        _check_timeout(start_ms, timeout, "Extension homing timed out")
        if extendonResetButton.is_pressed():
            raise RuntimeError("Extension switch did not release during retraction")
        _extension_homed = True
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


def getExtendonDistance() -> float:
    return (extendonMotor.current_angle() + EXTENDON_CONVERSION) / EXTENDON_CONVERSION + EXTENDON_MIN


def getExtendonSpeed() -> float:
    return extendonMotor.current_speed() / EXTENDON_CONVERSION


def getYawAngle() -> float:
    return yawMotor.current_angle() * YAW_RATIO


def getYawSpeed() -> float:
    return yawMotor.current_speed() * YAW_RATIO


async def moveLinear(
    target_x: float,
    target_z: float,
    absolute_end_angle: float,
    *,
    max_angular_speed: float,
    max_extension_speed: float,
    max_acceleration: float,
    min_extension: float = EXTENDON_MIN,
    max_extension: float = EXTENDON_MAX,
    extension_limit_margin: float = 0.01,
    control_hz: float = 100.0,
    position_tolerance: float = 0.01,
    position_gain: float = 3.0,
    timeout: float = 30.0,
):
    """Follow a straight line in base-relative XZ coordinates; return True.

    Angular speeds are rad/s; other speeds/accelerations are grid units/s
    and grid units/s^2. max_acceleration slews the complete Cartesian command
    including position correction. Joint speed/boundary limits take priority
    if they require a faster reduction; integer motor commands add quantization.

    The margin reserves space inside the physical radius limits. Both path
    endpoints and the whole reference line must stay inside that margin.
    Measured physical-limit violations, timeout, errors, and cancellation
    stop both motion motors. The end motor is not moved by this function.
    """
    global _motion_busy

    if yawMotor is None or extendonMotor is None or not _extension_homed:
        raise RuntimeError("Call init() and successfully home the extension first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")

    _motion_busy = True
    try:
        _check_calibration()
        for name, value in (
            ("max_angular_speed", max_angular_speed),
            ("max_extension_speed", max_extension_speed),
            ("max_acceleration", max_acceleration),
            ("control_hz", control_hz),
            ("position_tolerance", position_tolerance),
            ("position_gain", position_gain),
            ("timeout", timeout),
        ):
            _positive(name, value)
        if not _finite(target_x) or not _finite(target_z):
            raise ValueError("Target coordinates must be finite")
        if (
            not _finite(min_extension) or not _finite(max_extension)
            or min_extension < EXTENDON_MIN or max_extension > EXTENDON_MAX
            or max_extension <= min_extension
        ):
            raise ValueError("Invalid physical extension limits")
        if (
            not _finite(extension_limit_margin) or extension_limit_margin < 0
            or 2.0 * extension_limit_margin >= max_extension - min_extension
        ):
            raise ValueError("Invalid extension margin")

        dt_nominal = 1.0 / control_hz
        safe_min = min_extension + extension_limit_margin
        safe_max = max_extension - extension_limit_margin
        if not yawMotor.is_ready() or not extendonMotor.is_ready():
            raise RuntimeError("A motion motor is unavailable")
        if not extendonResetButton.is_ready():
            raise RuntimeError("Extension limit switch is unavailable")
        theta_start = getYawAngle()
        r_start = getExtendonDistance()
        target_r = _hypot(target_x, target_z)
        if not safe_min <= r_start <= safe_max:
            raise ValueError("Current extension is outside the usable range")
        if not safe_min <= target_r <= safe_max:
            raise ValueError("Target is outside the usable extension range")

        x_start = r_start * math.cos(theta_start)
        z_start = r_start * math.sin(theta_start)
        dx, dz = target_x - x_start, target_z - z_start
        length = _hypot(dx, dz)
        if length > 0:
            ux, uz = dx / length, dz / length
        else:
            ux, uz = 0.0, 0.0

        closest_s = max(0.0, min(length, -(x_start * ux + z_start * uz)))
        minimum_path_radius = _hypot(
            x_start + ux * closest_s, z_start + uz * closest_s
        )
        if minimum_path_radius < safe_min:
            raise ValueError("Straight-line path crosses the minimum extension")

        # Conservative feedforward cap valid over the entire reference line.
        # The cross product is constant along a line: d(theta)/ds = cross/r^2.
        path_speed_limit = float("inf") if length > 0 else 0.0
        if length > 0:
            cross = abs(x_start * uz - z_start * ux)
            if cross > 1e-9:
                path_speed_limit = min(
                    path_speed_limit,
                    max_angular_speed * minimum_path_radius ** 2 / cross,
                )
            max_radial_slope = max(
                abs((x_start * ux + z_start * uz) / r_start),
                abs((target_x * ux + target_z * uz) / target_r),
            )
            if max_radial_slope > 1e-9:
                path_speed_limit = min(
                    path_speed_limit, max_extension_speed / max_radial_slope
                )

        def limit_cartesian(vx, vz, r, cos_theta, sin_theta, dt):
            radial = vx * cos_theta + vz * sin_theta
            angular = (-vx * sin_theta + vz * cos_theta) / r
            scale = 1.0
            if abs(angular) > max_angular_speed:
                scale = min(scale, max_angular_speed / abs(angular))
            if abs(radial) > max_extension_speed:
                scale = min(scale, max_extension_speed / abs(radial))

            # Reduce movement toward a boundary before reaching it. The margin
            # gives the physical motor room for its response/braking delay.
            if radial != 0.0:
                clearance = max(0.0, safe_max - r if radial > 0 else r - safe_min)
                radial_cap = min(
                    clearance / dt,
                    math.sqrt(2.0 * max_acceleration * clearance),
                )
                if abs(radial) > radial_cap:
                    scale = min(scale, radial_cap / abs(radial))
            return vx * scale, vz * scale, scale

        progress, path_speed = 0.0, 0.0
        theta_speed = getYawSpeed()
        radial_speed = getExtendonSpeed()
        previous_vx = radial_speed * math.cos(theta_start) - r_start * theta_speed * math.sin(theta_start)
        previous_vz = radial_speed * math.sin(theta_start) + r_start * theta_speed * math.cos(theta_start)
        # Bound reference lead if motor saturation, lag or a stall prevents
        # the real arm from following the requested speed.
        allowed_lead = max(4.0 * position_tolerance, 0.01)
        start_ms = time.ticks_ms()
        last_ms = start_ms

        while True:
            now_ms = time.ticks_ms()
            _check_timeout(start_ms, timeout, "Crane movement timed out")
            dt = time.ticks_diff(now_ms, last_ms) / 1000.0
            if dt <= 0:
                await asyncio.sleep(dt_nominal)
                continue
            last_ms = now_ms

            if not yawMotor.is_ready() or not extendonMotor.is_ready():
                raise RuntimeError("A motion motor became unavailable")
            theta = getYawAngle()
            r = getExtendonDistance()
            theta_speed = getYawSpeed()
            radial_speed = getExtendonSpeed()
            if not min_extension <= r <= max_extension:
                raise RuntimeError("Physical extension limit violated: r=" + str(r))
            if not extendonResetButton.is_ready():
                raise RuntimeError("Extension limit switch became unavailable")
            if extendonResetButton.is_pressed():
                raise RuntimeError("Unexpected contact with the retracted limit switch")

            cos_theta, sin_theta = math.cos(theta), math.sin(theta)
            x, z = r * cos_theta, r * sin_theta
            if (
                _hypot(target_x - x, target_z - z) <= position_tolerance
                and abs(theta_speed) < 0.03 and abs(radial_speed) < 0.01
            ):
                return True

            path_remaining = max(0.0, length - progress)
            desired_speed = min(
                path_speed_limit, math.sqrt(2.0 * max_acceleration * path_remaining)
            )
            speed_step = max_acceleration * dt
            path_speed += max(-speed_step, min(speed_step, desired_speed - path_speed))

            desired_x = x_start + ux * progress
            desired_z = z_start + uz * progress
            # Once the reference reaches the endpoint, only position
            # correction remains. Overshoot cannot restart feedforward.
            feedforward_speed = path_speed if progress < length else 0.0
            vx = ux * feedforward_speed + position_gain * (desired_x - x)
            vz = uz * feedforward_speed + position_gain * (desired_z - z)
            vx, vz, speed_scale = limit_cartesian(vx, vz, r, cos_theta, sin_theta, dt)

            delta_vx, delta_vz = vx - previous_vx, vz - previous_vz
            delta_speed = _hypot(delta_vx, delta_vz)
            if delta_speed > speed_step:
                blend = speed_step / delta_speed
                vx = previous_vx + delta_vx * blend
                vz = previous_vz + delta_vz * blend

            # The current joint geometry/boundary envelope can change while
            # the motors move. Reapply hard command limits after slewing.
            vx, vz, final_scale = limit_cartesian(vx, vz, r, cos_theta, sin_theta, dt)
            previous_vx, previous_vz = vx, vz
            extension_command = vx * cos_theta + vz * sin_theta
            rotation_command = (-vx * sin_theta + vz * cos_theta) / r
            # Truncate toward zero so quantization cannot exceed speed limits.
            yawMotor.run_at_speed(int(rotation_command / YAW_RATIO))
            extendonMotor.run_at_speed(int(extension_command * EXTENDON_CONVERSION))

            # endMotor.run_at_speed(int(rotation_command) * 1.67 / YAW_RATIO, 300)

            # Advance only as fast as the limited forward command, with an
            # additional cap on how far the reference can lead the real arm.
            commanded_forward = max(0.0, vx * ux + vz * uz)
            advance_speed = min(path_speed * speed_scale * final_scale, commanded_forward)
            measured_progress = (x - x_start) * ux + (z - z_start) * uz
            next_progress = min(length, progress + advance_speed * dt)
            lead_limit = max(progress, measured_progress + allowed_lead)
            progress = min(next_progress, lead_limit)

            elapsed = time.ticks_diff(time.ticks_ms(), now_ms) / 1000.0
            await asyncio.sleep(max(0.0, dt_nominal - elapsed))
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False