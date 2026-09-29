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

pidDir: int = 1
integralClamp: float = 100

async def init(kp: float, ki: float, kd: float, rkp: float, rki: float, rkd: float):
    global Kp, Ki, Kd, rKp, rKi, rKd, integralClamp
    Kp = kp
    Ki = ki
    Kd = kd

    rKp = rkp
    rKi = rki
    rKd = rkd

async def pidLoop(target: float, integral: float, last_error: float, derivative: float, last_angle: float, last_time: int, low_pass: float, integralClamp: float):
    global Kp, Ki, Kd, pidDir, integralClamp
    now_angle: float = brick.gyroAngle()

    # Proportional
    error: float = target - now_angle * pidDir

    # Integral
    integral = integral + error

    if ((error > 0) != (last_error > 0)):
        integral = 0
    
    integral = clamp(integral, -integralClamp, integralClamp)

    # Derivative
    now_time: int = time.ticks_ms()
    time_diff: int = now_time - last_time
    raw_derivative: float = (now_angle - last_angle) / time_diff if now_time - last_time != 0 else Exception("You time traveller!")

    alpha: float =  time_diff / (time_diff + low_pass)
    derivative = derivative + alpha * (raw_derivative - derivative)

    # Post process
    last_time = now_time
    last_angle = now_angle

    output: float = Kp * error + Ki * integral + Kd * derivative

async def goForDegrees(target_angle: float, speed: float, dist: float, start_speed: float, end_speed: float, decel_dist: float, accel_dist: float):
    start_angle: float = brick.gyroAngle()
    start_time: int = time.ticks_ms()
    integral: float = 0
    last_error: float = 0
    derivative: float = 0
    last_angle: float = start_angle
    last_time: int = start_time

    start_l_angle: float = buggy.lMotor.current_angle()
    start_r_angle: float = buggy.rMotor.current_angle()

    forward: bool = (dist > 0) == (speed > 0)
    dist = abs(dist)
    speed = abs(speed)

    while buggy.getRelativeAbsAngle(start_l_angle, start_r_angle) < dist:
        now_angle: float = brick.gyroAngle()
        now_dist: float = buggy.getRelativeAbsAngle(start_l_angle, start_r_angle)

        await pidLoop(target_angle, integral, last_error, derivative, last_angle, last_time, 0.001, integralClamp)

        speed = buggy.speedHelper(speed, end_speed, start_speed, dist, decel_dist, accel_dist, now_dist)
        buggy.buggySpeedSetterUtil(forward, output, speed)

    buggy.stop()


    

