from brian import *
import buggy
import brick
import asyncio
import math
import time

Kp: float
Ki: float
Kd: float

rKp: float
rKi: float
rKd: float

integralClamp: float
pidDir: int

def init(kp: float, ki: float, kd: float, rkp: float, rki: float, rkd: float):
    global Kp, Ki, Kd, rKp, rKi, rKd, integralClamp, pidDir
    integralClamp = 100
    pidDir = 1
    Kp = kp
    Ki = ki
    Kd = kd

    rKp = rkp
    rKi = rki
    rKd = rkd

def pidLoop(target: float, now: float, state: PIDState, low_pass: float, Kp: float, Ki: float, Kd: float, pidDIr: int = 1):
    global integralClamp

    # Proportional
    error = target - now * pidDir

    # Integral
    state.integral += error

    if (error > 0) != (state.last_error > 0):
        state.integral = 0

    state.integral = max(
        min(state.integral, integralClamp),
        -integralClamp
    )

    # Derivative
    now_time = time.ticks_ms()
    time_diff = time.ticks_diff(now_time, state.last_time)

    if time_diff > 0:
        raw_derivative = (
            now - state.last_angle
        ) / time_diff
    else:
        raw_derivative = 0.0

    alpha = time_diff / (time_diff + low_pass)

    state.derivative += alpha * (
        raw_derivative - state.derivative
    )

    # Update state
    state.last_error = error
    state.last_time = now_time
    state.last_angle = now

    return (
        Kp * error
        + Ki * state.integral
        + Kd * state.derivative
    )

async def goUntil(
    target_angle: float,
    speed: float,
    max_dist: float,
    start_speed: float = 0,
    end_speed: float = 0,
    decel_dist: float = 0,
    accel_dist: float = 0,
    stop_at_the_end: bool = True,
    stop_condition_func: callable = None
):
    global Kp, Ki, Kd, pidDir
    pid = PIDState()
    
    start_l_angle = buggy.lMotor.current_angle()
    start_r_angle = buggy.rMotor.current_angle()

    forward = (max_dist > 0) == (speed > 0)

    max_dist = abs(max_dist)
    speed = abs(speed)

    while not stop_condition_func():

        now_dist = buggy.getRelativeAbsAngle(
            start_l_angle,
            start_r_angle
        )

        output = pidLoop(
            target_angle,
            brick.gyroAngle(),
            pid,
            0.001,
            Kp,
            Ki,
            Kd,
            pidDir
        )

        speed_out = buggy.speedHelper(
            speed,
            end_speed,
            start_speed,
            max_dist,
            decel_dist,
            accel_dist,
            now_dist
        )

        buggy.buggySpeedSetterUtil(
            forward,
            output,
            speed_out
        )

        await asyncio.sleep(0.04)

    if stop_at_the_end:
        buggy.stop()

async def goForDegrees(
    target_angle: float,
    speed: float,
    dist: float,
    start_speed: float = 0,
    end_speed: float = 0,
    decel_dist: float = 0,
    accel_dist: float = 0,
    stop_at_the_end: bool = True
):
    start_l_angle = buggy.lMotor.current_angle()
    start_r_angle = buggy.rMotor.current_angle()

    await goUntil(
        target_angle,
        speed,
        dist,
        start_speed,
        end_speed,
        decel_dist,
        accel_dist,
        stop_at_the_end,
        lambda: buggy.getRelativeAbsAngle(
            start_l_angle,
            start_r_angle
        ) >= abs(dist)
    )

async def goTilLine(
    target_angle: float,
    speed: float,
    dist: float,
    start_speed: float = 0,
    end_speed: float = 0,
    decel_dist: float = 0,
    accel_dist: float = 0,
    stop_at_the_end: bool = True
):
    start_l_angle = buggy.lMotor.current_angle()
    start_r_angle = buggy.rMotor.current_angle()

    await goUntil(
        target_angle,
        speed,
        dist,
        start_speed,
        end_speed,
        decel_dist,
        accel_dist,
        stop_at_the_end,
        lambda: buggy.getRelativeAbsAngle(
            start_l_angle,
            start_r_angle
        ) >= abs(dist)
    )

async def turnTo(
    target_angle: float,
    speed: float,
    left_powerup: float = 0,
    right_powerup: float = 0,
    start_speed: float = 0,
    accel_angle: float = 0,
    stop_at_the_end: bool = True,
    tolerance_degrees: float = 2.0,
    speed_limit: float = 600.0
):
    pid = PIDState()

    start_angle = brick.gyroAngle()

    angle_diff = abs(target_angle - start_angle)
    speed = abs(speed)

    while abs(brick.gyroAngle() - target_angle) > tolerance_degrees:

        now_angle = brick.gyroAngle()
        output = pidLoop(
            target_angle,
            now_angle,
            pid,
            0.001,
            Kp=rKp,
            Ki=rKi,
            Kd=rKd,
        )

        now_angle_diff = abs(target_angle - now_angle)

        speed_out = buggy.speedHelper(
            speed,
            speed,
            start_speed,
            angle_diff,
            0,
            accel_angle,
            now_angle_diff
        )

        lSpeed: float = -output * (speed_out + left_powerup)
        rSpeed: float =  output * (speed_out + right_powerup)

        lSpeed = min(max(lSpeed, -speed_limit), speed_limit)
        rSpeed = min(max(rSpeed, -speed_limit), speed_limit)

        buggy.lMotor.run_at_speed(math.floor(lSpeed))
        buggy.rMotor.run_at_speed(math.floor(rSpeed))

        await asyncio.sleep(0.04)

    if stop_at_the_end:
        buggy.stop()

class PIDState:
    def __init__(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.derivative = 0.0
        self.last_angle = brick.gyroAngle()
        self.last_time = time.ticks_ms()


    

