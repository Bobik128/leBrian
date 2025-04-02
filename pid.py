from brian import *
import buggy
import brick
import asyncio
import math

Kp: float
Ki: float
Kd: float

rKp: float
rKi: float
rKd: float

def init(kp: float, ki: float, kd: float, rkp: float, rki: float, rkd: float):
    global Kp, Ki, Kd, rKp, rKi, rKd
    Kp = kp
    Ki = ki
    Kd = kd

    rKp = rkp
    rKi = rki
    rKd = rkd

async def goForDegrees(targetAngle: float, dist: float, speed: float, stopAtEnd: bool = True):
    dir: bool = buggy.getDir(speed, dist)
    speed = abs(speed)

    #startDist: float = buggy.getAbsoluteAngle()
    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist: float = abs(dist)

    integral: float = 0
    lastError: float = 0

    while buggy.getRelativeAbsAngle(startLAngle, startRAngle) < absDist:
        error: float = targetAngle + brick.gyro.angle()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(dir, output, speed)

        integral += error
        lastError = error

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100

        await asyncio.sleep(0.01)
    if stopAtEnd: buggy.stop()


async def goTilLine(targetAngle: float, speed: float, stopAtEnd: bool = True):
    dir: bool = buggy.getDir(speed, 1)
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    integral: float = 0
    lastError: float = 0

    while brick.color.reflected_value() > 60:
        error: float = targetAngle + brick.gyro.angle()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(dir, output, speed)

        integral += error
        lastError = error

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100

        await asyncio.sleep(0.01)
    if stopAtEnd: buggy.stop()


async def goTilButton(targetAngle: float, speed: float, button: sensors.EV3.TouchSensorEV3, stopDelay: int = 0):
    dir: bool = buggy.getDir(speed, 0)
    speed = abs(speed)

    integral: float = 0
    lastError: float = 0

    while not button.is_pressed():
        error: float = targetAngle + brick.gyro.angle()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(dir, output, speed)

        integral += error
        lastError = error

        print(brick.gyro.angle())

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100

        await asyncio.sleep(0.01)

    await asyncio.sleep(stopDelay)
    buggy.stop()

async def lineFollower(target: float, speed: float):
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    await asyncio.sleep(0.5)

    integral: float = 0
    lastError: float = 0

    while True:
        error: float = target - brick.color.reflected_value()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(True, output, speed)

        integral += error
        lastError = error

        print(brick.color.reflected_value())

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100


        await asyncio.sleep(0.01)

    
async def turnTo(targetAngle: int, tolerance: int, speed: int, powerup: int = 0, stopAtEnd: bool = True):
    dir: bool = False

    nowDir: int = brick.gyro.angle()
    print(nowDir)

    if nowDir == targetAngle:
        return

    integral: float = 0
    lastError: float = 0

    print("started")

    while abs(targetAngle + nowDir) > tolerance:
        nowDir = brick.gyro.angle()

        ILimit: float = 15
        if integral > ILimit:
            integral = ILimit
        elif integral < -ILimit:
            integral = -ILimit

        error: float = targetAngle + nowDir
        output: float = rKp * error + rKi * integral + rKd * (error - lastError)

        # minSpeed: float = 0.3
        # if output > 0:
        #     if output < minSpeed: output = minSpeed
        # else:
        #     if output > -minSpeed: output = -minSpeed

        print(output)

        lSpeed: float = (speed + powerup) * -output
        rSpeed: float = (speed - powerup) * output

        speedLimit: float = 600
        if lSpeed > speedLimit:
            lSpeed = speedLimit
        elif lSpeed < -speedLimit:
            lSpeed = -speedLimit

        if rSpeed > speedLimit:
            rSpeed = speedLimit
        elif rSpeed < -speedLimit:
            rSpeed = -speedLimit

        buggy.lMotor.run_at_speed(math.floor(lSpeed))
        buggy.rMotor.run_at_speed(math.floor(rSpeed))

        integral += error
        lastError = error

        await asyncio.sleep(0.01)
    
    if stopAtEnd: buggy.stop()