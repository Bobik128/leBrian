from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid
import time
import sys

startTime: float
white: int
black: int
middleCol: int

runMotor: motors.Motor
leftButton: sensors.EV3.TouchSensorEV3
rightButton: sensors.EV3.TouchSensorEV3

speed: int = 650
fastSpeed: int = 700
turnSpeed: int = 450

speedWithBricks: int = 500
turnSpeedWithBricks: int = 340

def clamp(val: int, minVal: int, maxVal: int):
    return max(minVal, min(val, maxVal))

async def intiLeftButton(port: sensors.SensorPort):
    global leftButton
    leftButton = sensors.EV3.TouchSensorEV3(port)
    while not leftButton.is_ready():
        asyncio.sleep(0.1)

async def intiRightButton(port: sensors.SensorPort):
    global rightButton
    rightButton = sensors.EV3.TouchSensorEV3(port)
    while not rightButton.is_ready():
        asyncio.sleep(0.1)

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def waitForPressWithGyroCheck():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(brick.gyro.angle()) > 5:
            print("GYRO DRIFT")
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break
    
async def initArm():
    global runMotor
    audio.play_tone(800, 300)
    runMotor = motors.Motor(motors.MotorPort.C)
    runMotor.run_at_speed(260)
    while not runMotor.is_stalled():
        await asyncio.sleep(0.1)

    runMotor.brake()
    runMotor.reset_angle()

    audio.play_tone(800, 300)

async def moveArm(pos: int):
    runMotor.rotate_to_angle(-clamp(pos, 10, 600), 800)

async def initColor():
    global white, black, middleCol
    await brick.initColor(sensors.SensorPort.S4)

    print("init white")
    await waitForPress()

    white = brick.color.reflected_value()
    print(white)

    await asyncio.sleep(0.5)

    print("init black")
    await waitForPress()

    black = brick.color.reflected_value()
    print(black)

    middleCol = (white + black)/2

async def moveRightBackTilButton():
    global rightButton
    buggy.rMotor.run_at_speed(-200)

    while not rightButton.is_pressed():
        await asyncio.sleep(0.1)

    await asyncio.sleep(0.5)
    buggy.rMotor.brake()

async def moveLeftBackTilButton():
    global leftButton
    buggy.lMotor.run_at_speed(-200)

    while not leftButton.is_pressed():
        await asyncio.sleep(0.1)

    await asyncio.sleep(0.5)
    buggy.lMotor.brake()

async def alignByWall():
    left = asyncio.create_task(moveLeftBackTilButton())
    right = asyncio.create_task(moveRightBackTilButton())

    await asyncio.gather(left, right)

async def initRun():
    global runMotor, leftButton, rightButton, startTime
    buggy.init(motors.MotorPort.D, motors.MotorPort.A)
    pid.init(7, 0.0001, 0.3,     #FORWARD
             0.04, 0.01, 0.04) #TURNING
    
    await initArm()
    await intiLeftButton(sensors.SensorPort.S2)
    await intiRightButton(sensors.SensorPort.S3)

    await initColor()

    await alignByWall()

    print("Reset gyro")
    await waitForPress() 
    await asyncio.sleep(1)
    await brick.initGyro(sensors.SensorPort.S1)

    brick.resetGyro()

    await pid.goForDegrees(0, 320, 260)
    print("")
    print("Start")

    await waitForPressWithGyroCheck()
    startTime = time.time()
    await asyncio.sleep(0.1)
    print("Started!")

async def grabBlue():
    await pid.turnTo(45, 3, turnSpeedWithBricks, 0)
    await pid.goForDegrees(45, 100, speedWithBricks)
    await pid.turnTo(0, 3, turnSpeedWithBricks, 0)
    await pid.goForDegrees(0, 300, speedWithBricks)

    await moveArm(230)

    await pid.turnTo(180, 3, turnSpeed)

async def timeWatcher():
    while time.time() - startTime < 90:
        await asyncio.sleep(0.01)
    
    return "t2"
    
async def program():
    global middleCol
    await initRun()

    # align first blue bricks in arm
    await grabBlue()

    await pid.goForDegrees(180, 260, speed)
    await moveArm(0)
    await pid.goForDegrees(180, -300, speed)
    await pid.turnTo(-10, 3, turnSpeed, 0)
    await pid.goForDegrees(-10, 200, speed)

    # align second blue bricks in arm
    await grabBlue()

    await pid.goForDegrees(180, 1180, fastSpeed)
    await moveArm(0)
    await pid.goForDegrees(180, -370, speed)

    # Grab first 2 green blocks
    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, 300, speed)

    await moveArm(230)

    await pid.goForDegrees(270, -160, speed)

    await pid.turnTo(315, 3, turnSpeed, 0)

    await moveArm(0)

    await pid.goForDegrees(315, 320, speedWithBricks)
    await moveArm(230)

    # put green to its place
    await pid.goForDegrees(315, -200, speed)

    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, -160, speed)
    await pid.turnTo(180, 3, turnSpeed, 0)
    await pid.goForDegrees(180, 160, speed)

    await moveArm(0)

    # Grab second 2 green blocks
    await pid.goForDegrees(180, -680, speed)
    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, 260, speed)

    await moveArm(230)

    await pid.goForDegrees(270, -180, speed)

    await pid.turnTo(310, 3, turnSpeed, 0)

    await moveArm(0)

    await pid.goForDegrees(310, 350, speedWithBricks)
    await moveArm(230)

    # put green (2nd) to its place
    await pid.goForDegrees(315, -190, speed)

    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, -160, speed)
    await pid.turnTo(180, 3, turnSpeed, 0)
    await pid.goForDegrees(180, 885, speed - 50)

    await moveArm(0)

    # reset gyro
    await pid.goForDegrees(180, -160, speed - 50)
    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goTilButton(270, -speedWithBricks, leftButton, postDecelDist=30)

    await asyncio.sleep(0.1)
    brick.resetGyro()
    await asyncio.sleep(0.1)

    # Bricko Le Blacko
    # await pid.goTilLine(0, speed, False, middle=middleCol, postDecelDist=80, decelDist=0, accelDist=0, startAccelFactor=1, endDecelFactor=1)
    # await pid.goTilLine(0, speed, False, middle=middleCol, postDecelDist=80, decelDist=0, accelDist=0, startAccelFactor=1, endDecelFactor=1)
    # await pid.goForDegrees(0, 130, speedWithBricks)

    # await pid.turnTo(45, 3, turnSpeedWithBricks, 0)
    # await pid.goForDegrees(45, -120, speedWithBricks)
    # await pid.turnTo(52, 3, turnSpeedWithBricks, 0)

    # await pid.goForDegrees(52, 300, speedWithBricks)
    # await moveArm(230)
    # await pid.goForDegrees(52, -100, speedWithBricks)
    # await pid.turnTo(180, 3, turnSpeed, 0)
    # await pid.goForDegrees(180, 1000, fastSpeed)

    # await moveArm(0)

    # await pid.goForDegrees(180, -50, speed)
    # await pid.turnTo(225, 3, turnSpeedWithBricks, 0)

    # await pid.goForDegrees(225, -1000, fastSpeed)

    await pid.goForDegrees(0, 400, speed, False, decelDist=0)
    await pid.goTilLine(0, speedWithBricks, middle=middleCol, accelDist=0, postDecelDist=50, decelDist=50)

    await pid.turnTo(-60, 3, turnSpeed, 0)
    await pid.goForDegrees(-60, 500, speed)
    await pid.turnTo(0, 3, turnSpeed, 0)
    await pid.goTilLine(0, speedWithBricks, middle=middleCol, accelDist=0, postDecelDist=50, decelDist=50)
    await pid.turnTo(90, 3, turnSpeedWithBricks, 0)
    await pid.goForDegrees(90, 260, speedWithBricks)

    await moveArm(90)
    await pid.goForDegrees(90, 260, speedWithBricks)
    await moveArm(0)

    return "t1"

async def main():
    await program()

    t1 = asyncio.create_task(program())
    t2 = asyncio.create_task(timeWatcher())

    tasks = [t1, t2]

    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Get the first result (optional)
        first_task = next(iter(done))
        result = await first_task  # or first_task.result()
        print("First result:", result)
    except Exception as e:
        print("First task raised:", e)
    
    print(f"Elapsed time: {time.time() - startTime:.2f} seconds")

asyncio.run(main())