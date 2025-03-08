from brian import *
import buggy
import brick
import asyncio

Kp: float
Ki: float
Kd: float

def init(kp: float, ki: float, kd: float):
    global Kp, Ki, Kd
    Kp = kp
    Ki = ki
    Kd = kd

async def goForDegrees(targetAngle: float, dist: float, speed: float):
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

        print(brick.gyro.angle())

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100


        await asyncio.sleep(0.01)
    
    buggy.lMotor.hold()
    buggy.rMotor.hold()

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
