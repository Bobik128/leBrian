"""Simple Brian crane controller: gyro yaw, straight XZ moves, absolute tip angle.

Yaw zero points along +X. Positive extension motor speed extends; the switch
is at maximum extension. Initialize the gyro in brick.py before crane.init().

moveLinear uses degrees for the end heading, radians/s for angular speeds,
and grid units/s for extension. Independent yaw/end moves use degrees.
The controller uses proportional feedback and acceleration limits only.
"""

from brian import motors, sensors
import asyncio
import math
import time
import brick

try:
    TimeoutError
except NameError:
    class TimeoutError(Exception):
        pass

DEG = math.pi / 180.0
EXTENDON_CONVERSION = 1750.0
EXTENDON_MAX = 1.0
EXTENDON_MIN = 0.2
YAW_RATIO = 0.21 * DEG
END_RATIO = -0.5988 * DEG

yawMotor = None
extendonMotor = None
endMotor = None
extendonResetButton = None
_motion_busy = False
_extension_homed = False
_gyro_sign = -1.0
_gyro_zero_degrees = 0.0
_end_zero_radians = 0.0


def _hypot(x, z):
    return math.sqrt(x * x + z * z)


def _finite(value):
    return -float("inf") < value < float("inf")


def _positive(name, value):
    if not _finite(value) or value <= 0:
        raise ValueError(name + " must be finite and positive")


def _nonnegative(name, value):
    if not _finite(value) or value < 0:
        raise ValueError(name + " must be finite and nonnegative")


def _clip(value, low, high):
    return max(low, min(high, value))


def _wrap(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def _check_timeout(start_ms, timeout, message):
    if time.ticks_diff(time.ticks_ms(), start_ms) >= timeout * 1000.0:
        raise TimeoutError(message)


async def _wait_ready(devices, timeout):
    start_ms = time.ticks_ms()
    while not all(device.is_ready() for device in devices):
        _check_timeout(start_ms, timeout, "Motor or sensor readiness timed out")
        await asyncio.sleep(0.01)


def _hold_motion_motors():
    # Attempt every hold, even if one motor reports an error.
    try:
        if yawMotor is not None:
            yawMotor.hold()
    finally:
        try:
            if extendonMotor is not None:
                extendonMotor.hold()
        finally:
            if endMotor is not None:
                endMotor.hold()


def _send(motor, speed, held):
    command = int(speed)
    if command:
        motor.run_at_speed(command)
        return False
    if not held:
        motor.hold()
    return True


def _check_calibration():
    _positive("EXTENDON_CONVERSION", EXTENDON_CONVERSION)
    if not EXTENDON_MAX > EXTENDON_MIN > 0:
        raise ValueError("Invalid extension calibration")
    for name, value in (("YAW_RATIO", YAW_RATIO), ("END_RATIO", END_RATIO)):
        if not _finite(value) or value == 0:
            raise ValueError(name + " must be finite and nonzero")


def _require_motion():
    if any(m is None for m in (yawMotor, extendonMotor, endMotor)) or not _extension_homed:
        raise RuntimeError("Call init() and successfully home the extension first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")


def _check_motors():
    if not all(m.is_ready() for m in (yawMotor, extendonMotor, endMotor)):
        raise RuntimeError("A motion motor is unavailable")


def _gyro_reader():
    # Use the sensor already initialized in your local brick.py module.
    return brick.gyroAngleAndSpeed()


def getYawState():
    """Return gyro yaw and angular speed in radians and radians/s."""
    angle, speed = _gyro_reader()
    if not _finite(angle) or not _finite(speed):
        raise RuntimeError("Gyro returned an invalid angle or speed")
    return (_gyro_sign * (angle - _gyro_zero_degrees) * DEG,
            _gyro_sign * speed * DEG)


def getYawAngle():
    return getYawState()[0]


def getYawSpeed():
    return getYawState()[1]


def getExtendonDistance():
    return EXTENDON_MAX + extendonMotor.current_angle() / EXTENDON_CONVERSION


def getExtendonSpeed():
    return extendonMotor.current_speed() / EXTENDON_CONVERSION


def getEndRelativeAngle():
    return _end_zero_radians + endMotor.current_angle() * END_RATIO


def getEndAngle():
    """Return absolute tip heading in radians, in the gyro coordinate frame."""
    return getYawAngle() + getEndRelativeAngle()


def resetEndMotor(relative_angle_degrees=0.0):
    """Zero the end encoder at a known angle relative to the arm.

    With the default zero, physically align the tip with the arm first.
    """
    global _end_zero_radians
    if endMotor is None:
        raise RuntimeError("Call init() first")
    if _motion_busy:
        raise RuntimeError("Cannot reset the end motor during a movement")
    if not _finite(relative_angle_degrees):
        raise ValueError("Invalid end reference angle")
    endMotor.hold()
    endMotor.reset_angle()
    _end_zero_radians = relative_angle_degrees * DEG


def resetYawMotor():
    """Reset brick.py's gyro zero while stationary and pointing along +X."""
    global _gyro_zero_degrees
    if yawMotor is None:
        raise RuntimeError("Call init() first")
    if _motion_busy:
        raise RuntimeError("Cannot reset yaw during a movement")
    yawMotor.hold()
    brick.resetGyro()
    _gyro_zero_degrees = 0.0


async def init(
    yaw_motor: motors.MotorPort,
    extendon_motor: motors.MotorPort,
    end_motor: motors.MotorPort,
    extendon_reset_button: sensors.SensorPort,
    *,
    gyro_sign: float = -1.0,
    yaw_zero_degrees: float = 0.0,
    end_relative_zero_degrees: float = 0.0,
    readiness_timeout: float = 10.0,
    homing_timeout: float = 200.0,
    extension_limit_margin: float = 0.01,
):
    """Initialize motors and home the extension; keep the existing gyro zero.

    brick.gyroAngleAndSpeed() must return (degrees, degrees/s).
    yaw_zero_degrees is the raw gyro reading corresponding to +X.
    The end encoder is zeroed at its current physical position, which must
    match end_relative_zero_degrees relative to the arm (default aligned).
    """
    global yawMotor, extendonMotor, endMotor, extendonResetButton
    global _gyro_sign, _gyro_zero_degrees
    _check_calibration()
    _positive("readiness_timeout", readiness_timeout)
    _positive("homing_timeout", homing_timeout)
    if gyro_sign not in (-1, 1) or not _finite(yaw_zero_degrees):
        raise ValueError("Invalid gyro calibration")
    if not _finite(end_relative_zero_degrees):
        raise ValueError("Invalid end reference angle")
    if _motion_busy or yawMotor is not None:
        raise RuntimeError("Crane is busy or init() has already been called")
    _gyro_sign, _gyro_zero_degrees = gyro_sign, yaw_zero_degrees
    getYawState()
    try:
        yawMotor = motors.Motor(yaw_motor)
        extendonMotor = motors.Motor(extendon_motor)
        endMotor = motors.Motor(end_motor)
        extendonResetButton = sensors.EV3.TouchSensorEV3(extendon_reset_button)
        await _wait_ready((yawMotor, extendonMotor, endMotor, extendonResetButton), readiness_timeout)
        await resetExtendon(timeout=homing_timeout, extension_limit_margin=extension_limit_margin)
        resetEndMotor(end_relative_zero_degrees)
    finally:
        _hold_motion_motors()


async def resetExtendon(
    *,
    timeout: float = 200.0,
    homing_speed: float = 200.0,
    extension_limit_margin: float = 0.01,
    settle_time: float = 0.25,
):
    """Extend to the maximum switch, zero there, retract to usable minimum."""
    global _motion_busy, _extension_homed
    _check_calibration()
    _positive("timeout", timeout)
    _positive("homing_speed", homing_speed)
    _nonnegative("settle_time", settle_time)
    _nonnegative("extension_limit_margin", extension_limit_margin)
    speed = int(homing_speed)
    if speed < 1 or 2 * extension_limit_margin + 0.005 >= EXTENDON_MAX - EXTENDON_MIN:
        raise ValueError("Invalid homing speed or extension margin")
    if extendonMotor is None or extendonResetButton is None:
        raise RuntimeError("Call init() first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")
    _motion_busy, _extension_homed = True, False
    start_ms = time.ticks_ms()
    try:
        await _wait_ready((extendonMotor, extendonResetButton), timeout)
        _hold_motion_motors()
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
        if not extendonResetButton.is_pressed():
            raise RuntimeError("Homing switch released before zeroing")
        extendonMotor.reset_angle()
        clearance = extension_limit_margin + (0.005 if extension_limit_margin else 0.0)
        target_angle = -int((EXTENDON_MAX - EXTENDON_MIN - clearance) * EXTENDON_CONVERSION)
        extendonMotor.run_at_speed(-speed)
        while extendonMotor.current_angle() > target_angle:
            _check_timeout(start_ms, timeout, "Extension retraction timed out")
            if not extendonMotor.is_ready():
                raise RuntimeError("Extension motor became unavailable")
            await asyncio.sleep(0.01)
        extendonMotor.hold()
        await asyncio.sleep(settle_time)
        _check_timeout(start_ms, timeout, "Extension homing timed out")
        if not extendonResetButton.is_ready() or extendonResetButton.is_pressed():
            raise RuntimeError("Extension switch did not release during retraction")
        _extension_homed = True
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


def _advance_profile(progress, speed, length, limit, acceleration, dt):
    remaining = max(0.0, length - progress)
    desired = min(limit, math.sqrt(2.0 * acceleration * remaining))
    next_speed = speed + _clip(desired - speed, -acceleration * dt, acceleration * dt)
    next_progress = min(length, progress + 0.5 * (speed + next_speed) * dt)
    feedforward = (next_progress - progress) / dt if next_progress < length else 0.0
    return next_progress, next_speed, feedforward


async def moveLinear(
    target_x: float,
    target_z: float,
    absolute_end_angle: float = None,
    *,
    max_angular_speed: float,
    max_extension_speed: float,
    max_acceleration: float,
    max_end_angular_speed: float = 2.0,
    max_end_acceleration: float = 6.0,
    min_extension: float = EXTENDON_MIN,
    max_extension: float = EXTENDON_MAX,
    extension_limit_margin: float = 0.01,
    control_hz: float = 100.0,
    position_tolerance: float = 0.01,
    end_angle_tolerance: float = 2.0,
    position_gain: float = 3.0,
    end_position_gain: float = 2.0,
    settle_time: float = 0.20,
    shortest_end_rotation: bool = True,
    timeout: float = 30.0,
):
    """Follow a straight XZ line while interpolating absolute tip heading.

    End angles/tolerance are degrees; angular speed/acceleration limits are
    radians/s and radians/s^2. Translation acceleration is grid units/s^2.
    None keeps the starting absolute tip heading. Set shortest_end_rotation
    to False for explicit accumulated end rotations, such as 360 degrees.

    A shared acceleration/deceleration profile advances the line and heading.
    Proportional position feedback corrects tracking error. The end joint
    counter-rotates against gyro yaw speed to produce an absolute heading.
    Return True after both final tolerances hold for settle_time. Hard limits
    and holding at the target can stop faster than the acceleration settings.
    """
    global _motion_busy
    _require_motion()
    _motion_busy = True
    try:
        _check_calibration()
        for name, value in (
            ("max_angular_speed", max_angular_speed), ("max_extension_speed", max_extension_speed),
            ("max_acceleration", max_acceleration), ("max_end_angular_speed", max_end_angular_speed),
            ("max_end_acceleration", max_end_acceleration), ("control_hz", control_hz),
            ("position_tolerance", position_tolerance), ("end_angle_tolerance", end_angle_tolerance),
            ("position_gain", position_gain), ("end_position_gain", end_position_gain), ("timeout", timeout),
        ):
            _positive(name, value)
        _nonnegative("settle_time", settle_time)
        _nonnegative("extension_limit_margin", extension_limit_margin)
        if not _finite(target_x) or not _finite(target_z):
            raise ValueError("Invalid target coordinates")
        if absolute_end_angle is not None and not _finite(absolute_end_angle):
            raise ValueError("Invalid end heading")
        if (not _finite(min_extension) or not _finite(max_extension)
                or min_extension < EXTENDON_MIN or max_extension > EXTENDON_MAX
                or max_extension <= min_extension
                or 2 * extension_limit_margin >= max_extension - min_extension):
            raise ValueError("Invalid extension limits or margin")
        _check_motors()
        _hold_motion_motors()
        theta_start, theta_speed = getYawState()
        r_start, radial_speed = getExtendonDistance(), getExtendonSpeed()
        target_r = _hypot(target_x, target_z)
        safe_min, safe_max = min_extension + extension_limit_margin, max_extension - extension_limit_margin
        slop = 1.0 / EXTENDON_CONVERSION + 1e-9
        if not min_extension - slop <= r_start <= safe_max:
            raise ValueError("Current extension is outside the permitted starting range")
        if not safe_min <= target_r <= safe_max:
            raise ValueError("Target is outside the usable extension range")
        x_start, z_start = r_start * math.cos(theta_start), r_start * math.sin(theta_start)
        dx, dz = target_x - x_start, target_z - z_start
        line_length = _hypot(dx, dz)
        line_ux, line_uz = (dx / line_length, dz / line_length) if line_length else (0.0, 0.0)
        closest = _clip(-(x_start * line_ux + z_start * line_uz), 0.0, line_length)
        minimum_radius = _hypot(x_start + line_ux * closest, z_start + line_uz * closest)
        if minimum_radius + slop < min(safe_min, r_start):
            raise ValueError("Straight-line path crosses the minimum extension")

        end_start = theta_start + getEndRelativeAngle()
        end_delta = 0.0 if absolute_end_angle is None else absolute_end_angle * DEG - end_start
        if shortest_end_rotation:
            end_delta = _wrap(end_delta)
        target_end = end_start + end_delta
        end_tolerance = end_angle_tolerance * DEG
        # A virtual length also gives heading-only moves a motion profile.
        length = max(line_length, abs(end_delta) * max_extension_speed / max_end_angular_speed, 1e-9)
        ux, uz, end_slope = dx / length, dz / length, end_delta / length
        cross = x_start * uz - z_start * ux
        radial_slope = max(abs((x_start * ux + z_start * uz) / r_start),
                           abs((target_x * ux + target_z * uz) / target_r))
        yaw_slope = abs(cross) / minimum_radius ** 2
        maximum_radius = max(r_start, target_r)
        end_joint_slope = max(abs(end_slope - cross / minimum_radius ** 2),
                              abs(end_slope - cross / maximum_radius ** 2))
        path_limit = max_extension_speed
        for slope, limit in ((radial_slope, max_extension_speed),
                             (yaw_slope, max_angular_speed), (end_joint_slope, max_end_angular_speed)):
            if slope > 1e-9:
                path_limit = min(path_limit, limit / slope)

        def limit_translation(vx, vz, r, c, sn, dt):
            radial, angular = vx * c + vz * sn, (-vx * sn + vz * c) / r
            scale = min(1.0, max_extension_speed / max(abs(radial), 1e-12),
                        max_angular_speed / max(abs(angular), 1e-12))
            radial, angular = radial * scale, angular * scale
            inner = min(safe_min, r_start)
            clearance = max(0.0, safe_max - r if radial > 0 else r - inner)
            cap = min(clearance / dt, math.sqrt(2 * max_acceleration * clearance))
            radial = _clip(radial, -cap, cap)
            return radial * c - r * angular * sn, radial * sn + r * angular * c

        progress, path_speed = 0.0, 0.0
        previous_vx = radial_speed * math.cos(theta_start) - r_start * theta_speed * math.sin(theta_start)
        previous_vz = radial_speed * math.sin(theta_start) + r_start * theta_speed * math.cos(theta_start)
        previous_end = endMotor.current_speed() * END_RATIO
        devices, held = (yawMotor, extendonMotor, endMotor), [True, True, True]
        stable_since = None
        period = 1.0 / control_hz
        start_ms = last_ms = time.ticks_ms()
        while True:
            now_ms = time.ticks_ms()
            _check_timeout(start_ms, timeout, "Crane movement timed out")
            dt = time.ticks_diff(now_ms, last_ms) / 1000.0
            if dt <= 0:
                await asyncio.sleep(period)
                continue
            last_ms = now_ms
            _check_motors()
            if not extendonResetButton.is_ready() or extendonResetButton.is_pressed():
                raise RuntimeError("Maximum-extension switch unavailable or unexpectedly pressed")
            theta, theta_speed = getYawState()
            r = getExtendonDistance()
            if not min_extension - slop <= r <= max_extension + slop:
                raise RuntimeError("Physical extension limit violated: r=" + str(r))
            c, sn = math.cos(theta), math.sin(theta)
            x, z = r * c, r * sn
            alpha = theta + getEndRelativeAngle()
            position_ok = _hypot(target_x - x, target_z - z) <= position_tolerance
            final_end_error = target_end - alpha
            if shortest_end_rotation:
                final_end_error = _wrap(final_end_error)
            arrived = position_ok and abs(final_end_error) <= end_tolerance
            if arrived:
                if stable_since is None:
                    stable_since = now_ms
                if time.ticks_diff(now_ms, stable_since) >= settle_time * 1000:
                    return True
            else:
                stable_since = None

            progress, path_speed, feedforward = _advance_profile(
                progress, path_speed, length, path_limit, max_acceleration, dt)
            fraction = progress / length
            ref_x, ref_z = x_start + dx * fraction, z_start + dz * fraction
            ref_end = end_start + end_delta * fraction
            vx = ux * feedforward + position_gain * (ref_x - x)
            vz = uz * feedforward + position_gain * (ref_z - z)
            vx, vz = limit_translation(vx, vz, r, c, sn, dt)
            change = _hypot(vx - previous_vx, vz - previous_vz)
            if change > max_acceleration * dt:
                blend = max_acceleration * dt / change
                vx = previous_vx + (vx - previous_vx) * blend
                vz = previous_vz + (vz - previous_vz) * blend
            vx, vz = limit_translation(vx, vz, r, c, sn, dt)
            radial, angular = vx * c + vz * sn, (-vx * sn + vz * c) / r
            if position_ok and (progress >= length or arrived):
                radial = angular = 0.0
            previous_vx = radial * c - r * angular * sn
            previous_vz = radial * sn + r * angular * c

            end_error = ref_end - alpha
            if shortest_end_rotation:
                end_error = _wrap(end_error)
            # This subtraction is the geometry of an absolute tip heading.
            requested_end = end_slope * feedforward + end_position_gain * end_error - theta_speed
            end_command = previous_end + _clip(requested_end - previous_end,
                                               -max_end_acceleration * dt, max_end_acceleration * dt)
            end_command = _clip(end_command, -max_end_angular_speed, max_end_angular_speed)
            if arrived:
                end_command = 0.0
            previous_end = end_command
            for index, command in enumerate((angular / YAW_RATIO,
                                             radial * EXTENDON_CONVERSION, end_command / END_RATIO)):
                held[index] = _send(devices[index], command, held[index])
            elapsed = time.ticks_diff(time.ticks_ms(), now_ms) / 1000.0
            await asyncio.sleep(max(0.0, period - elapsed))
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


async def _move_single_joint(
    axis, target, *, max_speed, max_acceleration, tolerance,
    shortest_rotation=False, extension_limit_margin=0.01,
    position_gain=3.0, control_hz=100.0, settle_time=0.20, timeout=30.0,
):
    """Move one motor with proportional feedback and braking/acceleration limits."""
    global _motion_busy
    _require_motion()
    _motion_busy = True
    try:
        _check_calibration()
        if not _finite(target):
            raise ValueError("Target must be finite")
        for name, value in (("max_speed", max_speed), ("max_acceleration", max_acceleration),
                            ("tolerance", tolerance), ("position_gain", position_gain),
                            ("control_hz", control_hz), ("timeout", timeout)):
            _positive(name, value)
        _nonnegative("settle_time", settle_time)
        _nonnegative("extension_limit_margin", extension_limit_margin)
        if axis == "extension" and not (
                2 * extension_limit_margin < EXTENDON_MAX - EXTENDON_MIN
                and EXTENDON_MIN + extension_limit_margin <= target <= EXTENDON_MAX - extension_limit_margin):
            raise ValueError("Extension target is outside the usable range")
        motor, conversion = {
            "extension": (extendonMotor, EXTENDON_CONVERSION),
            "yaw": (yawMotor, DEG / YAW_RATIO),
            "end": (endMotor, DEG / END_RATIO),
        }[axis]

        def measure():
            if axis == "extension":
                return getExtendonDistance(), 0.0
            angle, rate = getYawState()
            if axis == "yaw":
                return angle / DEG, 0.0
            return (angle + getEndRelativeAngle()) / DEG, rate / DEG

        _check_motors()
        _hold_motion_motors()
        start, yaw_rate = measure()
        slop = 1.0 / EXTENDON_CONVERSION + 1e-9
        if axis == "extension":
            if not EXTENDON_MIN - slop <= start <= EXTENDON_MAX + slop:
                raise RuntimeError("Physical extension limit violated")
            lower = min(EXTENDON_MIN + extension_limit_margin, start)
            upper = max(EXTENDON_MAX - extension_limit_margin, start)
        elif shortest_rotation:
            target = start + _wrap((target - start) * DEG) / DEG
        command, held, stable_since = 0.0, True, None
        period = 1.0 / control_hz
        start_ms = last_ms = time.ticks_ms()
        while True:
            now_ms = time.ticks_ms()
            _check_timeout(start_ms, timeout, "Independent " + axis + " movement timed out")
            dt = time.ticks_diff(now_ms, last_ms) / 1000.0
            if dt <= 0:
                await asyncio.sleep(period)
                continue
            last_ms = now_ms
            _check_motors()
            position, yaw_rate = measure()
            if axis == "extension":
                if not extendonResetButton.is_ready():
                    raise RuntimeError("Extension switch became unavailable")
                if not EXTENDON_MIN - slop <= position <= EXTENDON_MAX + slop:
                    raise RuntimeError("Physical extension limit violated")
            error = target - position
            if abs(error) <= tolerance:
                command = 0.0
                if stable_since is None:
                    stable_since = now_ms
                if time.ticks_diff(now_ms, stable_since) >= settle_time * 1000:
                    return True
            else:
                stable_since = None
                braking_limit = min(max_speed, math.sqrt(2.0 * max_acceleration * abs(error)))
                requested = _clip(position_gain * error, -braking_limit, braking_limit) - yaw_rate
                command += _clip(requested - command, -max_acceleration * dt, max_acceleration * dt)
                command = _clip(command, -max_speed, max_speed)
                if axis == "extension":
                    clearance = max(0.0, upper - position if command > 0 else position - lower)
                    cap = min(clearance / dt, math.sqrt(2.0 * max_acceleration * clearance))
                    command = _clip(command, -cap, cap)
                    if extendonResetButton.is_pressed() and command > 0:
                        raise RuntimeError("Unexpected maximum-extension switch contact")
            held = _send(motor, command * conversion, held)
            elapsed = time.ticks_diff(time.ticks_ms(), now_ms) / 1000.0
            await asyncio.sleep(max(0.0, period - elapsed))
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


async def moveExtendon(
    length: float, *, max_speed: float = 0.3, max_acceleration: float = 0.5,
    tolerance: float = 0.01, extension_limit_margin: float = 0.01, **control_options,
):
    """Move only extension to an absolute radius in grid units.

    Speed is units/s; acceleration is units/s^2. Yaw and end motors hold.
    Set extension_limit_margin=0 to allow the physical endpoints.
    """
    return await _move_single_joint(
        "extension", length, max_speed=max_speed, max_acceleration=max_acceleration,
        tolerance=tolerance, extension_limit_margin=extension_limit_margin, **control_options)


async def moveYaw(
    angle_degrees: float, *, max_speed: float = 45.0, max_acceleration: float = 120.0,
    tolerance: float = 1.0, shortest_rotation: bool = True, **control_options,
):
    """Move only yaw to an absolute gyro heading in degrees.

    Speed is degrees/s; acceleration is degrees/s^2. Extension and end motors
    hold, so the end's absolute heading turns with the arm.
    """
    return await _move_single_joint(
        "yaw", angle_degrees, max_speed=max_speed, max_acceleration=max_acceleration,
        tolerance=tolerance, shortest_rotation=shortest_rotation, **control_options)


async def moveEnd(
    absolute_angle_degrees: float, *, max_speed: float = 90.0, max_acceleration: float = 240.0,
    tolerance: float = 2.0, shortest_rotation: bool = True, **control_options,
):
    """Move only the end motor to an absolute gyro-frame heading in degrees.

    Speed is joint degrees/s; acceleration is degrees/s^2. Yaw/extension hold.
    Set shortest_rotation=False for explicit accumulated yaw/end rotations.
    All independent moves accept position_gain, control_hz, settle_time and
    timeout as extra control_options. Await movements sequentially.
    """
    return await _move_single_joint(
        "end", absolute_angle_degrees, max_speed=max_speed, max_acceleration=max_acceleration,
        tolerance=tolerance, shortest_rotation=shortest_rotation, **control_options)