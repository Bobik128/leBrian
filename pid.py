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

lKp: float
lKi: float
lKd: float

lightTarget: int = 60

def isStuck(lastCheckTime, lastError, error):
    currentTime = time.time()

    if currentTime - lastCheckTime < 1:
        return False, lastCheckTime, lastError
    
    if abs(error) >= 20:
        if lastError > 0 and lastError - error < 5:
            return True, currentTime, error
        elif lastError < 0 and lastError - error > -5:
            return True, currentTime, error
    return False, currentTime, error

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def initLineFollower(p, i, d):
    global lightTarget, lKp, lKi, lKd
    lKp = p
    lKi = i
    lKd = d
    brick.color
    brick.color.reflected_value()
    print("Init color")
    await waitForPress()
    lightTarget = brick.color.reflected_value()

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

    lastCheckTime = time.time()
    lastStuckError = 0
    stuck_timer_start = None
    stuck_timeout = 3.0

    while buggy.getRelativeAbsAngle(startLAngle, startRAngle) < absDist:
        error: float = targetAngle + brick.gyro.angle()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(dir, output, speed)

        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)

        if stuck:
            print("STUCK detected, aborting.")
            buggy.brake()
            s: int
            if dir: s = -speed 
            else: s = speed
            await buggy.moveTank(s, s, 160)
            stuck_timer_start = None
        else:
            stuck_timer_start = None

        integral += error
        lastError = error

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100

        await asyncio.sleep(0.01)
    if stopAtEnd: buggy.stop()


async def goTilLine(targetAngle: float, speed: float, stopAtEnd: bool = True, timeout: float = 5):
    dir: bool = buggy.getDir(speed, 1)
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    integral: float = 0
    lastError: float = 0

    startTime = time.time()

    while brick.color.reflected_value() > 60 and time.time() - startTime < timeout:
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


async def goTilButton(targetAngle: float, spd: float, button: sensors.EV3.TouchSensorEV3, stopDelay: int = 0, timeout: float = 8):
    dir: bool = buggy.getDir(spd, 1)
    speed: float = abs(spd)

    integral: float = 0
    lastError: float = 0
    startTime = time.time()

    lastCheckTime = time.time()
    lastStuckError = 0
    stuck_timer_start = None
    stuck_timeout = 3.0

    while not button.is_pressed() and time.time() - startTime < timeout:
        error: float = targetAngle + brick.gyro.angle()
        output: float = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(True, output, speed)

        integral += error
        lastError = error

        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)

        if stuck:
            print("STUCK detected, aborting.")
            buggy.brake()
            s: int
            if dir: s = -speed 
            else: s = speed
            await buggy.moveTank(s, s, 160)
            stuck_timer_start = None
        else:
            stuck_timer_start = None

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100

        await asyncio.sleep(0.01)

    await asyncio.sleep(stopDelay)
    buggy.stop()

async def lineFollowerWithGyro(angle: int, speed: float, dist: int):
    global lightTarget
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist: float = abs(dist)

    await asyncio.sleep(0.5)

    integral: float = 0
    lastError: float = 0

    while buggy.getRelativeAbsAngle(startLAngle, startRAngle) < absDist:
        error: float = lightTarget - brick.color.reflected_value()
        output: float = lKp * error + lKi * integral + lKd * (error - lastError)

        if brick.gyro.angle() + angle > 5 and output > 0:
            output = 0
            error = 0
        elif brick.gyro.angle() + angle < -5 and output < 0:
            output = 0
            error = 0

        buggy.buggySpeedSetterUtil(True, -output, speed)

        integral += error
        lastError = error

        print(brick.color.reflected_value())

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100


        await asyncio.sleep(0.01)

async def lineFollowerWithGyroTilButton(angle: int, speed: float, button: sensors.EV3.TouchSensorEV3, delay: float):
    global lightTarget
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    await asyncio.sleep(0.5)

    integral: float = 0
    lastError: float = 0

    while not button.is_pressed():
        error: float = lightTarget - brick.color.reflected_value()
        output: float = lKp * error + lKi * integral + lKd * (error - lastError)

        if brick.gyro.angle() + angle > 5 and output > 0:
            output = 0
        elif brick.gyro.angle() + angle < -5 and output < 0:
            output = 0

        buggy.buggySpeedSetterUtil(True, -output, speed)

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

    lastCheckTime = time.time()
    lastStuckError = 0
    stuck_timer_start = None
    stuck_timeout = 3.0

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
        

        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)

        if stuck:
            print("STUCK detected, aborting.")
            buggy.brake()
            s: int = -speed 
            await buggy.moveTank(s, s, 160)
            stuck_timer_start = None
        else:
            stuck_timer_start = None

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