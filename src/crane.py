"""Brian crane controller: gyro yaw, straight XZ travel and absolute tip heading.

Coordinates share the gyro's fixed frame: yaw 0 degrees points along +X.
The yaw sensor must report the actual rotating chassis/arm heading. Positive
extension motor speed extends. The maximum-extension switch is encoder zero.

moveLinear(x, z, absolute_end_angle, ...) takes its end heading in DEGREES;
its angular speed/acceleration limits use rad/s and rad/s^2. Independent
moveYaw() and moveEnd() use DEGREES for angles, degrees/s for speed and
degrees/s^2 for acceleration. END_RATIO means one motor degree produces
0.5988 degrees at the geared end joint.
"""

from brian import motors, sensors
import asyncio
import math
import time

try:
    TimeoutError
except NameError:
    class TimeoutError(Exception):
        pass

DEG = math.pi / 180.0
EXTENDON_CONVERSION = 1500.0  # Motor degrees per grid unit.
EXTENDON_MAX = 1.0
EXTENDON_MIN = 0.2
YAW_RATIO = 0.21 * DEG       # Used for commands, NOT gyro measurements.
END_RATIO = 0.5988 * DEG     # Set negative if positive motor speed turns backward.

yawMotor = None
extendonMotor = None
endMotor = None
extendonResetButton = None
_motion_busy = False
_extension_homed = False
_gyro_sign = 1.0
_gyro_offset_degrees = 0.0
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
    # Attempt every hold, including when a previous hold fails.
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


def _check_calibration():
    _positive("EXTENDON_CONVERSION", EXTENDON_CONVERSION)
    if not EXTENDON_MAX > EXTENDON_MIN > 0:
        raise ValueError("Invalid extension calibration")
    for name, value in (("YAW_RATIO", YAW_RATIO), ("END_RATIO", END_RATIO)):
        if not _finite(value) or value == 0:
            raise ValueError(name + " must be finite and nonzero")


def _gyro_reader():
    # This is your local brick.py helper, not brian.brick.
    # Override with init(..., gyro_reader=your_function) if it exposes a
    # different interface. The callback returns (degrees, degrees/second).
    import brick
    return brick.gyro.angle_and_speed()


def getYawState():
    """Read one gyro sample and return (angle radians, speed radians/s)."""
    angle, speed = _gyro_reader()
    if not _finite(angle) or not _finite(speed):
        raise RuntimeError("Gyro returned an invalid angle or speed")
    return (
        (_gyro_sign * angle - _gyro_offset_degrees) * DEG,
        _gyro_sign * speed * DEG,
    )


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
    """Absolute end heading in radians, in the same frame as gyro yaw."""
    return getYawAngle() + getEndRelativeAngle()


def resetEndMotor(relative_angle_degrees=0.0):
    """Zero end encoder at a known heading RELATIVE to the arm.

    With the default 0, physically align the end with the arm before calling.
    No automatic end homing is possible without an end reference sensor.
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
    """Set software gyro yaw zero while stationary and pointing along +X.

    Does not reset the sensor itself or other users of the gyro.
    """
    global _gyro_offset_degrees
    if _motion_busy:
        raise RuntimeError("Cannot reset yaw during a movement")
    yawMotor.hold()
    angle, speed = _gyro_reader()
    if not _finite(angle) or not _finite(speed):
        raise RuntimeError("Invalid gyro reading")
    _gyro_offset_degrees = _gyro_sign * angle


async def init(
    yaw_motor: motors.MotorPort,
    extendon_motor: motors.MotorPort,
    end_motor: motors.MotorPort,
    extendon_reset_button: sensors.SensorPort,
    *,
    gyro_sign: float = 1.0,
    yaw_zero_degrees: float = 0.0,
    end_relative_zero_degrees: float = 0.0,
    readiness_timeout: float = 10.0,
    homing_timeout: float = 200.0,
    extension_limit_margin: float = 0.01,
):
    """Initialize and home. Preserve the gyro's existing coordinate zero.

    gyro_reader() must return (angle_deg, speed_deg_s), synchronously.
    Default: brick.gyro.angle_and_speed(). Initialize its sensor/mode in brick.py
    first. Its positive direction must agree with +Z from +X (gyro_sign=-1
    reverses the sensor). END_RATIO/YAW_RATIO signs control motor directions.
    yaw_zero_degrees is the raw gyro reading corresponding to +X.

    End encoder zero is initialized at its CURRENT physical position, which
    must equal end_relative_zero_degrees relative to the arm (default aligned).
    """
    global yawMotor, extendonMotor, endMotor, extendonResetButton
    global _gyro_sign, _gyro_offset_degrees
    _check_calibration()
    _positive("readiness_timeout", readiness_timeout)
    _positive("homing_timeout", homing_timeout)
    if gyro_sign not in (-1, 1) or not _finite(yaw_zero_degrees):
        raise ValueError("Invalid gyro sign or zero")
    if not _finite(end_relative_zero_degrees):
        raise ValueError("Invalid end reference angle")
    if _motion_busy or yawMotor is not None:
        raise RuntimeError("Crane is busy or init() has already been called")
    _gyro_sign = gyro_sign
    _gyro_offset_degrees = gyro_sign * yaw_zero_degrees
    getYawState()  # Verify the configured gyro before moving any motor.
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
    _motion_busy = True
    _extension_homed = False
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


class _JointPI:
    """PI correction with speed-unit integral clamp and conditional windup."""
    def __init__(self, kp, ki, integral_limit):
        self.kp, self.ki = kp, ki
        self.limit = integral_limit
        self.integral = 0.0
        self.previous_error = 0.0
        self.limited = False

    def correction(self, error, dt):
        if error * self.previous_error < 0:
            self.integral = 0.0
        if not self.limited:
            self.integral = _clip(self.integral + self.ki * error * dt, -self.limit, self.limit)
        self.previous_error = error
        return self.kp * error + self.integral

    def limit_feedback(self, error, requested, applied):
        # Integration may unwind a saturated command, but must not push
        # further into saturation. The crawl floor does not count as windup.
        self.limited = error * (requested - applied) > 1e-9

    def clear(self):
        self.integral = 0.0
        self.limited = False


def _crawl(command, error, speed, stopped_time, deadband, minimum, delay):
    if (
        stopped_time >= delay and abs(error) > deadband
        and abs(command) < minimum and abs(speed) < minimum * 0.25
    ):
        return minimum if error > 0 else -minimum
    return command


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
    yaw_position_gain: float = 4.0,
    end_position_gain: float = 4.0,
    extension_integral_gain: float = 1.0,
    yaw_integral_gain: float = 1.2,
    end_integral_gain: float = 1.5,
    yaw_velocity_gain: float = 1.0,
    yaw_response_time: float = 0.12,
    tracking_lead: float = 0.012,
    min_yaw_motor_speed: float = 25.0,
    min_extension_motor_speed: float = 20.0,
    min_end_motor_speed: float = 20.0,
    crawl_delay: float = 0.20,
    settle_time: float = 0.20,
    shortest_end_rotation: bool = True,
    timeout: float = 30.0,
):
    """Follow a line and interpolate absolute end heading with common progress.

    absolute_end_angle and end_angle_tolerance are DEGREES; speed limits are
    rad/s (yaw, end joint) or grid units/s (extension). The end joint's relative
    speed includes counter-rotation against measured gyro yaw. A None heading
    keeps the starting ABSOLUTE heading. Zero means point along fixed +X.
    shortest_end_rotation=True interpolates the nearest equivalent heading;
    False permits explicit accumulated rotations such as 360 degrees.

    Gyro yaw supplies all measured geometry; YAW_RATIO is command conversion
    only. Joint PI, yaw velocity/acceleration feedforward and a small measured
    reference lead compensate friction, yaw lag and backlash. A crawl floor is
    applied only after a joint stops outside its error deadband. Joint/boundary
    caps and integer commands follow Cartesian acceleration limiting; hard
    caps and the final position hold can stop faster than max_acceleration.
    Return True only after position AND end heading settle. Always hold all
    three motors on success, error, timeout or cancellation.
    """
    global _motion_busy
    if any(m is None for m in (yawMotor, extendonMotor, endMotor)) or not _extension_homed:
        raise RuntimeError("Call init() and successfully home the extension first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")
    _motion_busy = True
    try:
        _check_calibration()
        for name, value in (
            ("max_angular_speed", max_angular_speed), ("max_extension_speed", max_extension_speed),
            ("max_acceleration", max_acceleration), ("max_end_angular_speed", max_end_angular_speed),
            ("max_end_acceleration", max_end_acceleration), ("control_hz", control_hz),
            ("position_tolerance", position_tolerance), ("end_angle_tolerance", end_angle_tolerance),
            ("position_gain", position_gain), ("yaw_position_gain", yaw_position_gain),
            ("end_position_gain", end_position_gain), ("tracking_lead", tracking_lead), ("timeout", timeout),
        ):
            _positive(name, value)
        for name, value in (
            ("extension_integral_gain", extension_integral_gain), ("yaw_integral_gain", yaw_integral_gain),
            ("end_integral_gain", end_integral_gain), ("yaw_velocity_gain", yaw_velocity_gain),
            ("yaw_response_time", yaw_response_time), ("min_yaw_motor_speed", min_yaw_motor_speed),
            ("min_extension_motor_speed", min_extension_motor_speed), ("min_end_motor_speed", min_end_motor_speed),
            ("crawl_delay", crawl_delay), ("settle_time", settle_time),
            ("extension_limit_margin", extension_limit_margin),
        ):
            _nonnegative(name, value)
        if not _finite(target_x) or not _finite(target_z):
            raise ValueError("Invalid target coordinates")
        if absolute_end_angle is not None and not _finite(absolute_end_angle):
            raise ValueError("Invalid end heading")
        if (
            not _finite(min_extension) or not _finite(max_extension)
            or min_extension < EXTENDON_MIN or max_extension > EXTENDON_MAX
            or max_extension <= min_extension
            or 2 * extension_limit_margin >= max_extension - min_extension
        ):
            raise ValueError("Invalid extension limits or margin")
        if not all(m.is_ready() for m in (yawMotor, extendonMotor, endMotor)):
            raise RuntimeError("A motion motor is unavailable")
        if not extendonResetButton.is_ready():
            raise RuntimeError("Extension switch is unavailable")

        theta_start, theta_speed = getYawState()
        r_start = getExtendonDistance()
        radial_speed = getExtendonSpeed()
        target_r = _hypot(target_x, target_z)
        safe_min, safe_max = min_extension + extension_limit_margin, max_extension - extension_limit_margin
        # A start at the physical minimum may move outward through the margin.
        radius_slop = 1.0 / EXTENDON_CONVERSION + 1e-9
        if not min_extension - radius_slop <= r_start <= safe_max:
            raise ValueError("Current extension is outside the permitted starting range")
        if not safe_min <= target_r <= safe_max:
            raise ValueError("Target is outside the usable extension range")
        x_start, z_start = r_start * math.cos(theta_start), r_start * math.sin(theta_start)
        dx, dz = target_x - x_start, target_z - z_start
        line_length = _hypot(dx, dz)
        line_ux, line_uz = (dx / line_length, dz / line_length) if line_length else (0.0, 0.0)
        closest_s = _clip(-(x_start * line_ux + z_start * line_uz), 0.0, line_length)
        minimum_path_radius = _hypot(x_start + line_ux * closest_s, z_start + line_uz * closest_s)
        if minimum_path_radius + radius_slop < min(safe_min, r_start):
            raise ValueError("Straight-line path crosses the minimum extension")
        maximum_path_radius = max(r_start, target_r)

        end_start = theta_start + getEndRelativeAngle()
        target_end = end_start if absolute_end_angle is None else absolute_end_angle * DEG
        end_delta = target_end - end_start
        if shortest_end_rotation:
            end_delta = _wrap(end_delta)
        target_end = end_start + end_delta
        end_tolerance = end_angle_tolerance * DEG
        # A common scalar progress supports both translation and end-only moves.
        # Scale its virtual length so either motion can set a sensible duration.
        motion_length = max(line_length, abs(end_delta) * max_extension_speed / max_end_angular_speed, 1e-9)
        ux, uz = dx / motion_length, dz / motion_length
        end_slope = end_delta / motion_length
        cross = x_start * uz - z_start * ux
        radial_slope = max(
            abs((x_start * ux + z_start * uz) / r_start),
            abs((target_x * ux + target_z * uz) / target_r),
        )
        yaw_slope_max = abs(cross) / minimum_path_radius ** 2
        # End-relative speed = absolute heading speed - arm yaw speed.
        end_slope_max = max(
            abs(end_slope - cross / minimum_path_radius ** 2),
            abs(end_slope - cross / maximum_path_radius ** 2),
        )
        path_limit = max_extension_speed
        if radial_slope > 1e-9:
            path_limit = min(path_limit, max_extension_speed / radial_slope)
        if yaw_slope_max > 1e-9:
            path_limit = min(path_limit, max_angular_speed / yaw_slope_max)
        if end_slope_max > 1e-9:
            path_limit = min(path_limit, max_end_angular_speed / end_slope_max)

        radial_pi = _JointPI(position_gain, extension_integral_gain, min(0.06, max_extension_speed))
        yaw_pi = _JointPI(yaw_position_gain, yaw_integral_gain, min(0.3, max_angular_speed))
        end_pi = _JointPI(end_position_gain, end_integral_gain, min(0.6, max_end_angular_speed))
        radial_floor = min_extension_motor_speed / EXTENDON_CONVERSION
        yaw_floor = min_yaw_motor_speed * abs(YAW_RATIO)
        end_floor = min_end_motor_speed * abs(END_RATIO)
        period = 1.0 / control_hz
        progress, path_speed = 0.0, 0.0
        previous_vx = radial_speed * math.cos(theta_start) - r_start * theta_speed * math.sin(theta_start)
        previous_vz = radial_speed * math.sin(theta_start) + r_start * theta_speed * math.cos(theta_start)
        previous_end_speed = endMotor.current_speed() * END_RATIO
        previous_yaw_ff, filtered_yaw_acceleration = 0.0, 0.0
        stopped_yaw, stopped_radial, stopped_end = 0.0, 0.0, 0.0
        held = [False, False, False]
        devices = (yawMotor, extendonMotor, endMotor)
        stable_since = None
        start_ms = last_ms = time.ticks_ms()

        def send(index, command):
            value = int(command)
            if value == 0:
                if not held[index]:
                    devices[index].hold()
                    held[index] = True
            else:
                devices[index].run_at_speed(value)
                held[index] = False

        while True:
            now_ms = time.ticks_ms()
            _check_timeout(start_ms, timeout, "Crane movement timed out")
            dt = time.ticks_diff(now_ms, last_ms) / 1000.0
            if dt <= 0:
                await asyncio.sleep(period)
                continue
            last_ms = now_ms
            if not all(m.is_ready() for m in devices):
                raise RuntimeError("A motion motor became unavailable")
            if not extendonResetButton.is_ready() or extendonResetButton.is_pressed():
                raise RuntimeError("Maximum-extension switch unavailable or unexpectedly pressed")
            theta, theta_speed = getYawState()
            r, radial_speed = getExtendonDistance(), getExtendonSpeed()
            relative_end = getEndRelativeAngle()
            end_speed = endMotor.current_speed() * END_RATIO
            alpha, alpha_speed = theta + relative_end, theta_speed + end_speed
            if not min_extension - radius_slop <= r <= max_extension + radius_slop:
                raise RuntimeError("Physical extension limit violated: r=" + str(r))
            c, sn = math.cos(theta), math.sin(theta)
            x, z = r * c, r * sn
            target_error = _hypot(target_x - x, target_z - z)
            end_error_final = target_end - alpha
            if shortest_end_rotation:
                end_error_final = _wrap(end_error_final)
            position_ok = target_error <= position_tolerance
            orientation_ok = abs(end_error_final) <= end_tolerance
            slow = abs(theta_speed) < 0.03 and abs(radial_speed) < 0.01 and abs(alpha_speed) < 0.05
            if position_ok and orientation_ok and slow:
                if stable_since is None:
                    stable_since = now_ms
                if time.ticks_diff(now_ms, stable_since) >= settle_time * 1000:
                    return True
            else:
                stable_since = None

            # Advance the reference by TIME, gated by measured tracking error.
            # Unlike projecting the command onto the line, a tiny endpoint
            # speed/quantized zero cannot permanently lock the reference.
            fraction = progress / motion_length
            ref_x, ref_z = x_start + dx * fraction, z_start + dz * fraction
            ref_alpha = end_start + end_delta * fraction
            tracking_error = _hypot(ref_x - x, ref_z - z)
            heading_tracking_error = abs(ref_alpha - alpha)
            if shortest_end_rotation:
                heading_tracking_error = abs(_wrap(ref_alpha - alpha))
            follow = _clip((tracking_lead - tracking_error) / (0.5 * tracking_lead), 0.0, 1.0)
            follow = min(follow, _clip((8 * DEG - heading_tracking_error) / (4 * DEG), 0.0, 1.0))
            remaining = max(0.0, motion_length - progress)
            desired_speed = min(path_limit, math.sqrt(2 * max_acceleration * remaining)) * follow
            path_speed += _clip(desired_speed - path_speed, -max_acceleration * dt, max_acceleration * dt)
            next_progress = min(motion_length, progress + path_speed * dt)
            if line_length > 1e-9:
                measured_s = ((x - x_start) * line_ux + (z - z_start) * line_uz) * motion_length / line_length
                lead_s = tracking_lead * motion_length / line_length
                next_progress = min(next_progress, max(progress, measured_s + lead_s))
            actual_path_speed = (next_progress - progress) / dt
            progress = next_progress
            fraction = progress / motion_length
            ref_x, ref_z = x_start + dx * fraction, z_start + dz * fraction
            ref_alpha = end_start + end_delta * fraction
            ref_r = _hypot(ref_x, ref_z)
            ref_theta = math.atan2(ref_z, ref_x)
            ref_c, ref_sn = ref_x / ref_r, ref_z / ref_r
            radial_ff = (ux * ref_c + uz * ref_sn) * actual_path_speed
            yaw_ff = (-ux * ref_sn + uz * ref_c) * actual_path_speed / ref_r
            alpha_ff = end_slope * actual_path_speed
            radial_error = ref_r - r
            yaw_error = _wrap(ref_theta - theta)
            alpha_error = ref_alpha - alpha
            if shortest_end_rotation:
                alpha_error = _wrap(alpha_error)
            at_end = progress >= motion_length - 1e-9
            if at_end:
                radial_ff = yaw_ff = alpha_ff = 0.0

            # Inertia compensation uses the desired yaw acceleration, filtered
            # to keep reference-governor or sensor steps from causing spikes.
            derivative = (yaw_ff - previous_yaw_ff) / dt
            filtered_yaw_acceleration += dt / (0.08 + dt) * (derivative - filtered_yaw_acceleration)
            previous_yaw_ff = yaw_ff
            yaw_boost = _clip(yaw_response_time * filtered_yaw_acceleration, -0.5 * max_angular_speed, 0.5 * max_angular_speed)
            requested_radial = radial_ff + radial_pi.correction(radial_error, dt)
            requested_yaw = yaw_ff + yaw_pi.correction(yaw_error, dt) + yaw_velocity_gain * (yaw_ff - theta_speed) + yaw_boost
            # Feedback error is ABSOLUTE end heading; subtract ACTUAL gyro
            # velocity so yaw lag/backlash does not falsely rotate the end.
            requested_end = alpha_ff - theta_speed + end_pi.correction(alpha_error, dt)

            stopped_yaw = stopped_yaw + dt if abs(theta_speed) < max(0.01, yaw_floor * 0.25) else 0.0
            stopped_radial = stopped_radial + dt if abs(radial_speed) < max(0.001, radial_floor * 0.25) else 0.0
            stopped_end = stopped_end + dt if abs(end_speed) < max(0.01, end_floor * 0.25) else 0.0
            yaw_deadband = 0.5 * position_tolerance / max(r, min_extension)
            radial_deadband = 0.5 * position_tolerance
            yaw_request = _crawl(requested_yaw, yaw_error, theta_speed, stopped_yaw, yaw_deadband, yaw_floor, crawl_delay)
            radial_request = _crawl(requested_radial, radial_error, radial_speed, stopped_radial, radial_deadband, radial_floor, crawl_delay)
            end_request = _crawl(requested_end, alpha_error, end_speed, stopped_end, end_tolerance * 0.5, end_floor, crawl_delay)

            # Slew the COMPLETE Cartesian command, including PI and crawl.
            vx, vz = radial_request * c - r * yaw_request * sn, radial_request * sn + r * yaw_request * c
            delta_x, delta_z = vx - previous_vx, vz - previous_vz
            change = _hypot(delta_x, delta_z)
            if change > max_acceleration * dt:
                blend = max_acceleration * dt / change
                vx, vz = previous_vx + delta_x * blend, previous_vz + delta_z * blend
            radial = vx * c + vz * sn
            angular = (-vx * sn + vz * c) / r
            scale = min(1.0, max_extension_speed / max(abs(radial), 1e-12), max_angular_speed / max(abs(angular), 1e-12))
            # Boundary limiting affects extension alone: a radial boundary
            # must not prevent the yaw/end joints correcting their headings.
            angular *= scale
            radial *= scale
            inner_boundary = min(safe_min, r_start)
            clearance = max(0.0, safe_max - r if radial > 0 else r - inner_boundary)
            radial_cap = min(clearance / dt, math.sqrt(2 * max_acceleration * clearance))
            radial = _clip(radial, -radial_cap, radial_cap)
            end_command = previous_end_speed + _clip(end_request - previous_end_speed, -max_end_acceleration * dt, max_end_acceleration * dt)
            end_command = _clip(end_command, -max_end_angular_speed, max_end_angular_speed)

            # A hold removes residual crawl/PI once within final tolerance.
            # Re-enter feedback if inertia/noise takes it outside the window.
            if position_ok:
                radial = angular = 0.0
                radial_pi.clear()
                yaw_pi.clear()
            if at_end and orientation_ok:
                end_command = -theta_speed  # Maintain heading during yaw settling.
                if position_ok and slow:
                    end_command = 0.0
                end_pi.clear()
            end_command = _clip(end_command, -max_end_angular_speed, max_end_angular_speed)
            radial_pi.limit_feedback(radial_error, requested_radial, radial)
            yaw_pi.limit_feedback(yaw_error, requested_yaw, angular)
            end_pi.limit_feedback(alpha_error, requested_end, end_command)
            previous_vx = radial * c - r * angular * sn
            previous_vz = radial * sn + r * angular * c
            previous_end_speed = end_command
            send(0, angular / YAW_RATIO)
            send(1, radial * EXTENDON_CONVERSION)
            send(2, end_command / END_RATIO)
            elapsed = time.ticks_diff(time.ticks_ms(), now_ms) / 1000.0
            await asyncio.sleep(max(0.0, period - elapsed))
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


async def _move_single_joint(
    axis,
    target,
    *,
    max_speed,
    max_acceleration,
    tolerance,
    shortest_rotation=False,
    extension_limit_margin=0.01,
    position_gain=None,
    integral_gain=None,
    integral_limit=None,
    min_motor_speed=None,
    velocity_gain=None,
    response_time=None,
    tracking_lead=None,
    settle_speed=None,
    control_hz=100.0,
    crawl_delay=0.20,
    settle_time=0.20,
    timeout=30.0,
):
    """One joint only. Internal velocities use grid units/s or DEGREES/s."""
    global _motion_busy
    if any(m is None for m in (yawMotor, extendonMotor, endMotor)) or not _extension_homed:
        raise RuntimeError("Call init() and successfully home the extension first")
    if _motion_busy:
        raise RuntimeError("Another crane movement is already running")
    _motion_busy = True
    try:
        _check_calibration()
        defaults = {
            "extension": (extendonMotor, EXTENDON_CONVERSION, 3.0, 1.0, 0.06, 20.0, 0.0, 0.0, 0.01),
            "yaw": (yawMotor, DEG / YAW_RATIO, 4.0, 1.2, 0.3 / DEG, 25.0, 1.0, 0.12, 2.0),
            "end": (endMotor, DEG / END_RATIO, 4.0, 1.5, 0.6 / DEG, 20.0, 0.0, 0.0, 3.0),
        }
        motor, conversion, kp, ki, ilim, floor, vg, response, stop_speed = defaults[axis]
        position_gain = kp if position_gain is None else position_gain
        integral_gain = ki if integral_gain is None else integral_gain
        integral_limit = min(ilim, max_speed) if integral_limit is None else integral_limit
        min_motor_speed = floor if min_motor_speed is None else min_motor_speed
        velocity_gain = vg if velocity_gain is None else velocity_gain
        response_time = response if response_time is None else response_time
        settle_speed = stop_speed if settle_speed is None else settle_speed
        tracking_lead = max(2.0 * tolerance, 0.04 * max_speed) if tracking_lead is None else tracking_lead
        if not _finite(target):
            raise ValueError("Target must be finite")
        for name, value in (
            ("max_speed", max_speed), ("max_acceleration", max_acceleration),
            ("tolerance", tolerance), ("position_gain", position_gain),
            ("tracking_lead", tracking_lead), ("settle_speed", settle_speed),
            ("control_hz", control_hz), ("timeout", timeout),
        ):
            _positive(name, value)
        for name, value in (
            ("integral_gain", integral_gain), ("integral_limit", integral_limit),
            ("min_motor_speed", min_motor_speed), ("velocity_gain", velocity_gain),
            ("response_time", response_time), ("crawl_delay", crawl_delay),
            ("settle_time", settle_time), ("extension_limit_margin", extension_limit_margin),
        ):
            _nonnegative(name, value)
        if axis == "extension" and not (
            2 * extension_limit_margin < EXTENDON_MAX - EXTENDON_MIN
            and EXTENDON_MIN + extension_limit_margin <= target <= EXTENDON_MAX - extension_limit_margin
        ):
            raise ValueError("Extension target is outside the usable range")
        if not all(m.is_ready() for m in (yawMotor, extendonMotor, endMotor)):
            raise RuntimeError("A motion motor is unavailable")

        def measure():
            # Extension-only movement does not need a gyro reading.
            if axis == "extension":
                return getExtendonDistance(), getExtendonSpeed(), 0.0
            angle, rate = getYawState()
            if axis == "yaw":
                return angle / DEG, rate / DEG, 0.0
            return (
                (angle + getEndRelativeAngle()) / DEG,
                (rate + endMotor.current_speed() * END_RATIO) / DEG,
                rate / DEG,
            )

        _hold_motion_motors()
        start, speed, yaw_rate = measure()
        if axis == "extension":
            slop = 1.0 / EXTENDON_CONVERSION + 1e-9
            if not EXTENDON_MIN - slop <= start <= EXTENDON_MAX + slop:
                raise RuntimeError("Physical extension limit violated")
            # Permit a retracted/extended start to enter the normal margin.
            lower = min(EXTENDON_MIN + extension_limit_margin, start)
            upper = max(EXTENDON_MAX - extension_limit_margin, start)
        elif shortest_rotation:
            target = start + _wrap((target - start) * DEG) / DEG
        direction = 1.0 if target >= start else -1.0
        distance = abs(target - start)
        progress, path_speed = 0.0, 0.0
        previous_command = speed - yaw_rate
        previous_ff, filtered_acceleration = 0.0, 0.0
        stopped_time = 0.0
        stable_since = None
        held = True
        pi = _JointPI(position_gain, integral_gain, integral_limit)
        native_floor = min_motor_speed / abs(conversion)
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
            if not all(m.is_ready() for m in (yawMotor, extendonMotor, endMotor)):
                raise RuntimeError("A motion motor became unavailable")
            position, speed, yaw_rate = measure()
            switch_pressed = False
            if axis == "extension":
                if not extendonResetButton.is_ready():
                    raise RuntimeError("Extension switch became unavailable")
                switch_pressed = extendonResetButton.is_pressed()
                if not EXTENDON_MIN - slop <= position <= EXTENDON_MAX + slop:
                    raise RuntimeError("Physical extension limit violated")
                # A pressed maximum switch still permits retraction. Only a
                # target at calibrated maximum may stop there successfully.
                if switch_pressed and target > position + tolerance and target < EXTENDON_MAX:
                    raise RuntimeError("Unexpected maximum-extension switch contact")
            final_error = target - position
            arrived = abs(final_error) <= tolerance
            if arrived and abs(speed) <= settle_speed:
                if stable_since is None:
                    stable_since = now_ms
                if time.ticks_diff(now_ms, stable_since) >= settle_time * 1000:
                    return True
            else:
                stable_since = None

            reference = start + direction * progress
            error = reference - position
            follow = _clip((tracking_lead - abs(error)) / (0.5 * tracking_lead), 0.0, 1.0)
            desired_speed = min(max_speed, math.sqrt(2 * max_acceleration * max(0.0, distance - progress))) * follow
            path_speed += _clip(desired_speed - path_speed, -max_acceleration * dt, max_acceleration * dt)
            next_progress = min(distance, progress + path_speed * dt)
            measured_progress = direction * (position - start)
            next_progress = min(next_progress, max(progress, measured_progress + tracking_lead))
            ff = direction * (next_progress - progress) / dt
            progress = next_progress
            reference = start + direction * progress
            error = reference - position
            if progress >= distance:
                ff = 0.0
            derivative = (ff - previous_ff) / dt
            filtered_acceleration += dt / (0.08 + dt) * (derivative - filtered_acceleration)
            previous_ff = ff
            boost = _clip(response_time * filtered_acceleration, -0.5 * max_speed, 0.5 * max_speed)
            requested = ff + pi.correction(error, dt) + velocity_gain * (ff - speed) + boost - yaw_rate
            actual_joint_speed = speed - yaw_rate
            stopped_time = stopped_time + dt if abs(actual_joint_speed) < max(settle_speed * 0.1, native_floor * 0.25) else 0.0
            desired = _crawl(requested, error, actual_joint_speed, stopped_time, 0.5 * tolerance, native_floor, crawl_delay)
            command = previous_command + _clip(desired - previous_command, -max_acceleration * dt, max_acceleration * dt)
            command = _clip(command, -max_speed, max_speed)
            if axis == "extension":
                clearance = max(0.0, upper - position if command > 0 else position - lower)
                cap = min(clearance / dt, math.sqrt(2 * max_acceleration * clearance))
                command = _clip(command, -cap, cap)
                if switch_pressed and command > 0:
                    command = 0.0
            if arrived:
                command = 0.0
                pi.clear()
            pi.limit_feedback(error, requested, command)
            previous_command = command
            motor_command = int(command * conversion)
            if motor_command == 0:
                if not held:
                    motor.hold()
                    held = True
            else:
                motor.run_at_speed(motor_command)
                held = False
            elapsed = time.ticks_diff(time.ticks_ms(), now_ms) / 1000.0
            await asyncio.sleep(max(0.0, period - elapsed))
    finally:
        try:
            _hold_motion_motors()
        finally:
            _motion_busy = False


async def moveExtendon(
    length: float,
    *,
    max_speed: float = 0.3,
    max_acceleration: float = 0.5,
    tolerance: float = 0.01,
    extension_limit_margin: float = 0.01,
    **control_options,
):
    """Move ONLY extension to an absolute radius, in your grid units.

    max_speed: units/s; max_acceleration: units/s^2; tolerance: units.
    Set extension_limit_margin=0 to allow the calibrated physical endpoints.
    Yaw and end motor hold their motor positions throughout the move.
    """
    return await _move_single_joint(
        "extension", length, max_speed=max_speed,
        max_acceleration=max_acceleration, tolerance=tolerance,
        extension_limit_margin=extension_limit_margin, **control_options,
    )


async def moveYaw(
    angle_degrees: float,
    *,
    max_speed: float = 45.0,
    max_acceleration: float = 120.0,
    tolerance: float = 1.0,
    shortest_rotation: bool = True,
    **control_options,
):
    """Move ONLY yaw to an absolute gyro heading in degrees.

    max_speed: degrees/s; max_acceleration: degrees/s^2; tolerance: degrees.
    The extension and end motors hold. The end therefore turns with the arm;
    its relative angle stays fixed, rather than its absolute heading.
    shortest_rotation=False permits explicit accumulated yaw turns.
    """
    return await _move_single_joint(
        "yaw", angle_degrees, max_speed=max_speed,
        max_acceleration=max_acceleration, tolerance=tolerance,
        shortest_rotation=shortest_rotation, **control_options,
    )


async def moveEnd(
    absolute_angle_degrees: float,
    *,
    max_speed: float = 90.0,
    max_acceleration: float = 240.0,
    tolerance: float = 2.0,
    shortest_rotation: bool = True,
    **control_options,
):
    """Move ONLY the end motor to an absolute heading in degrees.

    Angle uses the same gyro frame as moveLinear's absolute_end_angle.
    max_speed: end joint degrees/s; max_acceleration: degrees/s^2;
    tolerance: absolute heading degrees. Extension and yaw motors hold.
    shortest_rotation=False permits an explicit accumulated end rotation.

    All three independent functions accept timeout, settle_time, control_hz,
    position_gain, integral_gain, integral_limit (native speed units),
    min_motor_speed (MOTOR degrees/s), tracking_lead, crawl_delay,
    velocity_gain, response_time and settle_speed as extra control_options.
    Await moves sequentially; they share the moveLinear/homing movement lock.
    """
    return await _move_single_joint(
        "end", absolute_angle_degrees, max_speed=max_speed,
        max_acceleration=max_acceleration, tolerance=tolerance,
        shortest_rotation=shortest_rotation, **control_options,
    )