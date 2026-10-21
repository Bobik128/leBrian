from brian import *
import asyncio
import time
import math
import brick
import pid

yawMotor = None
extendonMotor = None
endMotor = None
extendonResetButton = None

GYRO_SIGN = -1.0
EXTENDON_CONVERSION = 1900.0
EXTENDON_MAX = 1.0
EXTENDON_MIN = 0.2
END_RATIO = -0.5988
YAW_RATIO = 1/7

KP: float = 3.6
KI: float = 0.001
KD: float = 0.0001

def _check_timeout(start_ms, timeout, message):
    if time.ticks_diff(time.ticks_ms(), start_ms) >= timeout * 1000.0:
        raise TimeoutError(message)

def _clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

async def moveYawTo(target_angle_deg: float, speed: float = 100.0, acceleration: float = 1000.0, tolerance: float = 1.1, timeout: float = 8.0):
    global yawMotor, KP, KI, KD
    # yawMotor.set_acceleration_limit(int(acceleration))
    pid_state = pid.PIDState()

    start_ms = time.ticks_ms()
    while abs(brick.gyroAngle() - target_angle_deg * GYRO_SIGN) > tolerance and time.ticks_diff(time.ticks_ms(), start_ms) < timeout * 1000.0:
        current_angle = brick.gyroAngle() * GYRO_SIGN
        output = pid.pidLoop(
            target_angle_deg,
            current_angle,
            pid_state,
            0.001,
            Kp=KP,
            Ki=KI,
            Kd=KD,
        )

        speed_out = _clamp(output, -speed, speed)
        print(current_angle)
        print(target_angle_deg)
        yawMotor.run_at_speed(int(speed_out / YAW_RATIO))
        await asyncio.sleep(0.01)

    yawMotor.hold()

async def moveEndTo(target_deg: float, speed: float = 100.0, acceleration: float = 600.0):
    global yawMotor, GYRO_SIGN
    await moveEndToRaw(int(target_deg - brick.gyroAngle() * GYRO_SIGN))

async def moveEndToRaw(target_deg: float, speed: float = 100.0, acceleration: float = 600.0):
    global endMotor
    target_angle = int(target_deg / END_RATIO)
    # endMotor.set_acceleration_limit(int(acceleration))
    endMotor.rotate_to(target_angle, int(speed / END_RATIO), timeout_ms=0)

    while not endMotor.is_done():
        await asyncio.sleep(0.01)
    endMotor.hold()

async def moveExtendonTo(target: float, speed: float = 0.3, acceleration: float = 600.0):
    global extendonMotor
    if not (EXTENDON_MIN <= target <= EXTENDON_MAX):
        raise ValueError(f"Target {target} is out of range [{EXTENDON_MIN}, {EXTENDON_MAX}]")

    target = _clamp(target, EXTENDON_MIN, EXTENDON_MAX)
    target_angle = -int((EXTENDON_MAX - target) * EXTENDON_CONVERSION)
    # extendonMotor.set_acceleration_limit(int(acceleration))
    print("started noneblocking")
    extendonMotor.rotate_to(target_angle, int(speed * EXTENDON_CONVERSION), timeout_ms=0)

    while not extendonMotor.is_done():
        await asyncio.sleep(0.01)
    extendonMotor.hold()
    print("exendon done")

async def moveExtendonAndEnd(
        extendon_target: float, 
        end_target: float, 
        extendon_speed: float, 
        end_speed: float, 
        extendon_acceleration: float = 600.0, 
        end_acceleration: float = 1000.0
    ):
    await asyncio.gather(
        moveExtendonTo(extendon_target, speed=extendon_speed, acceleration=extendon_acceleration),
        moveEndTo(end_target, speed=end_speed, acceleration=end_acceleration)
    )

async def moveYawAndEnd(
        yaw_target: float,
        end_target: float,
        yaw_speed: float,
        end_speed: float,
        yaw_acceleration: float = 600.0,
        end_acceleration: float = 1000.0
    ):
    await asyncio.gather(
        moveYawTo(yaw_target, speed=yaw_speed, acceleration=yaw_acceleration),
        moveEndToRaw(int(end_target - yaw_target), speed=end_speed, acceleration=end_acceleration)
    )

async def moveEndBy(angle: float, speed: float):
    global END_RATIO
    endMotor.rotate_to(int((endMotor.current_angle() + angle / END_RATIO)), speed=(speed / END_RATIO), timeout_ms=0)
    
    while not endMotor.is_done():
        await asyncio.sleep(0.01)
    endMotor.hold()

async def moveEndToRelative(angle: float, speed: float, shortest_path: bool = True):
    global END_RATIO
    relative_now_angle = (endMotor.current_angle()*END_RATIO) % 360
    if shortest_path:
        await moveEndToRaw(endMotor.current_angle()*END_RATIO + angle - relative_now_angle, speed=speed, acceleration=1000)
    else:
        await moveEndToRaw(angle, speed=speed, acceleration=1000)

async def rotateRoundOffPivot(
        target_end_angle: float, 
        radius: float = 0.15, 
        angular_speed_deg: float = 100
    ):
    start_yaw: float = brick.gyroAngle() * GYRO_SIGN
    start_end_rel: float = endMotor.current_angle() * END_RATIO
    start_end_abs: float = start_end_rel + start_yaw
    start_length = extendonMotor.current_angle() / EXTENDON_CONVERSION

    if start_end_abs - target_end_angle < 0:
        angular_speed_deg = -angular_speed_deg

    angular_speed_rad = math.radians(angular_speed_deg)

    # get knee pivot
    yaw_rad = math.radians(start_yaw)
    end_abs_rad = math.radians(start_end_abs)
    x_center: float = math.cos(yaw_rad) * start_length + math.cos(end_abs_rad) * radius
    y_center: float = math.sin(yaw_rad) * start_length + math.sin(end_abs_rad) * radius

    dist_to_center: float = math.sqrt(x_center**2 + y_center**2)

    # main loop
    while (abs(start_end_rel - endMotor.current_angle() * END_RATIO) < abs(start_end_abs - target_end_angle)):
        alpha = math.radians((endMotor.current_angle() * END_RATIO - 90) % 360)
        x = radius * math.cos(alpha)
        y = radius * math.sin(alpha)

        beta = math.atan2(x, y + dist_to_center)
        dist_to_knee: float = math.sqrt((dist_to_center + y)**2 + x**2)

        v_of_extendon: float = math.cos(alpha + beta) * angular_speed_rad * radius
        v_of_yaw: float = math.sin(alpha + beta) * (angular_speed_rad * radius / dist_to_knee)

        yawMotor.run_at_speed(math.degrees(v_of_yaw) / YAW_RATIO)
        extendonMotor.run_at_speed(v_of_extendon * EXTENDON_CONVERSION)
        endMotor.run_at_speed(angular_speed_deg / END_RATIO)

        await asyncio.sleep(0.01)
    
    yawMotor.hold()
    extendonMotor.hold()
    endMotor.hold()

async def moveTo(
        x: float, 
        y: float, 
        end_angle: float,
        yaw_speed: float, 
        extendon_speed: float, 
        end_speed: float, 
        yaw_acceleration: float = 600.0, 
        extendon_acceleration: float = 600.0, 
        end_acceleration: float = 1000.0
    ):

    yaw_target = math.degrees(math.atan2(y, x))
    extendon_target = math.sqrt(x**2 + y**2)
    await asyncio.gather(
        moveYawTo(yaw_target, speed=yaw_speed, acceleration=yaw_acceleration),
        moveExtendonTo(extendon_target, speed=extendon_speed, acceleration=extendon_acceleration),
        moveEndToRaw(int(end_angle - yaw_target), speed=end_speed, acceleration=end_acceleration)
    )

async def moveToSynced( # computes the speeds so all three effectors arrive at the same time
        x: float, 
        y: float, 
        end_angle: float,
        time_s: float, 
        yaw_acceleration: float = 600.0, 
        extendon_acceleration: float = 600.0, 
        end_acceleration: float = 1000.0
    ):

    yaw_target = math.degrees(math.atan2(y, x))
    extendon_target = math.sqrt(x**2 + y**2)

    yaw_now = brick.gyroAngle() * GYRO_SIGN
    extendon_now = extendonMotor.current_angle() / EXTENDON_CONVERSION
    end_now = endMotor.current_angle() * END_RATIO + yaw_now

    extendon_speed = abs(extendon_now - extendon_target) / time_s
    yaw_speed = abs(yaw_now - yaw_target) / time_s
    end_speed = abs(end_now - end_angle) / time_s

    await asyncio.gather(
        moveYawTo(yaw_target, speed=yaw_speed, acceleration=yaw_acceleration),
        moveExtendonTo(extendon_target, speed=extendon_speed, acceleration=extendon_acceleration),
        moveEndToRaw(int(end_angle - yaw_target), speed=end_speed, acceleration=end_acceleration)
    )

async def initEndMotor():
    global endMotor
    await asyncio.sleep(0.1)
    endMotor.reset_angle()
    endMotor.hold()

async def initExtendonMotor(
    speed=0.23
):
    global extendonMotor
    await asyncio.sleep(0.1)
    start_ms = time.ticks_ms()

    if not extendonResetButton.is_pressed():
        extendonMotor.run_at_speed(int(speed * EXTENDON_CONVERSION))

    while not extendonResetButton.is_pressed():
        if not extendonMotor.is_ready() or not extendonResetButton.is_ready():
            raise RuntimeError("Homing motor or switch became unavailable")
        await asyncio.sleep(0.01)

    extendonMotor.hold()
    await asyncio.sleep(0.1)
    extendonMotor.reset_angle()

    target_angle = 0.4
    await moveExtendonTo(target_angle, speed=speed, acceleration=600.0)

async def initYawMotor():
    global yawMotor
    await asyncio.sleep(0.1)
    yawMotor.reset_angle()
    yawMotor.hold()
    
def _check_timeout(start_ms, timeout, message):
    if time.ticks_diff(time.ticks_ms(), start_ms) >= timeout * 1000.0:
        raise TimeoutError(message)

async def _wait_ready(devices, timeout):
    start_ms = time.ticks_ms()
    while not all(device.is_ready() for device in devices):
        _check_timeout(start_ms, timeout, "Motor or sensor readiness timed out")
        await asyncio.sleep(0.01)

async def init(
    yaw_motor: motors.MotorPort,
    extendon_motor: motors.MotorPort,
    end_motor: motors.MotorPort,
    extendon_reset_button: sensors.SensorPort,
):
    global yawMotor, extendonMotor, endMotor, extendonResetButton
    yawMotor = motors.EV3LargeMotor(yaw_motor)
    extendonMotor = motors.EV3LargeMotor(extendon_motor)
    endMotor = motors.EV3MediumMotor(end_motor)
    extendonResetButton = sensors.EV3.TouchSensorEV3(extendon_reset_button)

    print("waiting for motor init")
    await _wait_ready((yawMotor, extendonMotor, endMotor), 10)
    print("motors available")

    await initYawMotor()
    print("yaw ok")
    await initEndMotor()
    print("end ok")
    await initExtendonMotor()