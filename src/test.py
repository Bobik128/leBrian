from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid
import time
import sys
import song

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
superFastSpeed: int = 800

bluePartK = 0.92

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
    runMotor.rotate_to_angle(-clamp(pos, 10, 450), 800)

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

    await pid.goForDegrees(0, 310, 260)
    print("")
    print("Start")

    await waitForPressWithGyroCheck()
    startTime = time.time()
    await asyncio.sleep(0.1)
    print("Started!")

async def grabBlue():
    await pid.turnTo(45, 3, turnSpeedWithBricks, 0)
    await pid.goForDegrees(50, 90 * bluePartK, speedWithBricks)
    await pid.turnTo(0, 3, turnSpeedWithBricks, 0)
    await pid.goForDegrees(0, 350 * bluePartK, speedWithBricks)

    await moveArm(230)
    # await asyncio.sleep(0.01)

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

    await pid.goForDegrees(190, 310 * bluePartK, speed)
    asyncio.create_task(moveArm(0))
    await pid.goForDegrees(185, -195 * bluePartK, speed)
    await pid.turnTo(-20, 3, turnSpeed, 0)
    await pid.goForDegrees(-20, 180 * bluePartK, speed)

    # align second blue bricks in arm
    await grabBlue()

    await pid.goForDegrees(184, 1220, fastSpeed)
    asyncio.create_task(moveArm(0))

    await asyncio.sleep(0.2)
    await pid.goForDegrees(187, -320, speed)

    # Grab first 2 green blocks
    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, 280, speed)

    await moveArm(230)

    await pid.goForDegrees(270, -280, speed)

    await pid.turnTo(305, 3, turnSpeed, 0)

    asyncio.create_task(moveArm(0))

    await pid.goForDegrees(305, 385, speedWithBricks)
    await moveArm(230)

    # put green to its place
    await pid.goForDegrees(315, -190, speed)

    # await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, -130, speed)
    await pid.turnTo(180, 3, turnSpeed, 0)
    await pid.goForDegrees(180, 160, speed)

    asyncio.create_task(moveArm(0))
    await asyncio.sleep(0.2)

    # Grab second 2 green blocks
    await pid.goForDegrees(180, -740, speed)
    await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, 300, speedWithBricks)

    await moveArm(220)

    await pid.goForDegrees(270, -320, speed)

    await pid.turnTo(300, 3, turnSpeed, 0)

    asyncio.create_task(moveArm(0))

    await pid.goForDegrees(300, 390, speedWithBricks)
    await moveArm(230)

    # put green (2nd) to its place
    await pid.goForDegrees(310, -160, speed)

    # await pid.turnTo(270, 3, turnSpeed, 0)
    await pid.goForDegrees(270, -120, speed)
    await pid.turnTo(180, 3, turnSpeed, 0)
    await pid.goForDegrees(180, 950, fastSpeed)

    asyncio.create_task(moveArm(0))

    # reset gyro
    await pid.goForDegrees(180, -170, speed - 50)
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

    await pid.goForDegrees(0, 380, speed, False, decelDist=0)
    await pid.goTilLine(0, speedWithBricks - 100, middle=middleCol, accelDist=0, postDecelDist=30, decelDist=50)

    await pid.turnTo(-60, 3, turnSpeed, 0)

    await pid.goForDegrees(-60, 140, speed, decelDist=0, endDecelFactor=1)
    await pid.goTilLine(-60, speedWithBricks, middle=middleCol, postDecelDist=0, accelDist=0)

    await pid.turnTo(10, 3, turnSpeed, 0)
    await pid.goTilLine(10, speedWithBricks - 100, middle=middleCol, accelDist=0, postDecelDist=50, decelDist=50)
    await pid.turnTo(90, 3, turnSpeedWithBricks, right_powerup=-40, left_powerup=40)

    await pid.goForDegrees(93, 220, speedWithBricks)

    asyncio.create_task(moveArm(600))
    await asyncio.sleep(0.2)
    await pid.goForDegrees(93, 120, speedWithBricks)
    asyncio.create_task(moveArm(0))
    await pid.goForDegrees(93, -290, speed)

    await pid.turnTo(0, 3, turnSpeedWithBricks, 0)
    await pid.goTilLine(1, speedWithBricks, middle=middleCol, accelDist=0, postDecelDist=100, decelDist=50)

    await pid.turnTo(90, 3, turnSpeedWithBricks - 40, left_powerup=130, right_powerup=-130)

    await pid.goForDegrees(85, 440, speedWithBricks)
    await pid.goForDegrees(85, -60, speedWithBricks)

    await pid.turnTo(146, 3, turnSpeedWithBricks - 130, left_powerup=30, right_powerup=-30)

    await pid.goForDegrees(146, -100, speedWithBricks)
    await pid.turnTo(116, 3, turnSpeed, left_powerup=20)
    await pid.goForDegrees(116, 430, speedWithBricks)
    await moveArm(230)

    await pid.turnTo(170, 3, turnSpeedWithBricks, left_powerup=60, right_powerup=-20)
    await pid.goForDegrees(170, 100, fastSpeed)

    await pid.goForDegrees(200, 1000, fastSpeed)
    await pid.goForDegrees(180, 430, fastSpeed)
    await moveArm(0)
    await pid.goForDegrees(180, 800, -fastSpeed, False, decelDist=0, endDecelFactor=0)
    await pid.goTilLine(180, -speed, middle=middleCol, accelDist=0, postDecelDist=50, decelDist=50)

    await pid.turnTo(115, 3, turnSpeedWithBricks, right_powerup=120, left_powerup=-120)
    await pid.goForDegrees(115, 280, fastSpeed, False)
    # await pid.turnTo(100, 3, turnSpeedWithBricks, False)
    await pid.goForDegrees(95, 150, fastSpeed)

    # second row
    asyncio.create_task(moveArm(600))
    await asyncio.sleep(0.07)
    await pid.goForDegrees(95, 170, speedWithBricks)
    asyncio.create_task(moveArm(0))
    # await asyncio.sleep(0.05)
    await pid.goForDegrees(92, -395, speed)

    await pid.turnTo(0, 3, turnSpeedWithBricks, 0)
    asyncio.create_task(moveArm(300))
    await pid.goTilLine(0, speedWithBricks, middle=middleCol, accelDist=0, postDecelDist=40, decelDist=50)

    await pid.turnTo(90, 3, turnSpeedWithBricks, left_powerup=30)

    # start pseudo move
    asyncio.create_task(moveArm(0))
    await pid.goForDegrees(85, 700, speedWithBricks)
    await pid.goForDegrees(85, -90, speedWithBricks)

    await pid.turnTo(146, 3, turnSpeedWithBricks - 70, left_powerup=30, right_powerup=-30)

    await pid.goForDegrees(146, -100, speedWithBricks)
    await pid.turnTo(120, 3, turnSpeed, left_powerup=20)
    await pid.goForDegrees(120, 380, speedWithBricks)
    await moveArm(230)
    await asyncio.sleep(0.2)

    await pid.turnTo(170, 3, turnSpeed - 100, left_powerup=130, right_powerup=-200)
    await pid.goForDegrees(175, 160, speedWithBricks, False, decelDist=0, endDecelFactor=1)
    asyncio.create_task(moveArm(0))
    await pid.goForDegrees(160, 90, speedWithBricks, False, decelDist=0, accelDist=0, endDecelFactor=1, startAccelFactor=1)
    await pid.goForDegrees(180, 90, speedWithBricks, accelDist=0, startAccelFactor=1)

    asyncio.create_task(moveArm(230))

    await pid.goForDegrees(205, 1000, fastSpeed)
    await pid.goForDegrees(180, 330, speedWithBricks)

    await moveArm(0)
    await pid.goForDegrees(180, -100, fastSpeed)
    await pid.turnTo(205, 3, turnSpeedWithBricks)
    await pid.turnTo(180, 3, turnSpeedWithBricks)
    await pid.goForDegrees(180, 25, fastSpeed)
    await pid.goForDegrees(180, -50, fastSpeed)
    await pid.turnTo(125, 3, turnSpeedWithBricks)

    asyncio.create_task(moveArm(600))
    await pid.goForDegrees(120, 400, fastSpeed)
    await pid.turnTo(50, 3, turnSpeedWithBricks)
    await pid.goForDegrees(45, -300, speedWithBricks, False, decelDist=0, endDecelFactor=1)

    await pid.goForDegrees(90, -820, speedWithBricks, False, accelDist=0, startAccelFactor=1)

    await pid.goForDegrees(90, 180, speed)

    await pid.turnTo(0, 3, turnSpeed)

    # after push in
    await pid.goTilButton(0, -speedWithBricks, leftButton, postDecelDist=30)
    await pid.goForDegrees(0, 400, fastSpeed, decelDist=0, endDecelFactor=1, stopAtEnd=False)
    await pid.goForDegrees(-60, 800, fastSpeed, startAccelFactor=1, accelDist=0)

    await pid.turnTo(0, 3, speed)
    await pid.goForDegrees(0, -450, speedWithBricks)

    await pid.goForDegrees(0, 50, fastSpeed, decelDist=0, endDecelFactor=1, stopAtEnd=False)
    await pid.goForDegrees(-50, 260, fastSpeed, startAccelFactor=1, accelDist=0)

    await pid.turnTo(0, 3, speed, left_powerup=-turnSpeed)
    await pid.goForDegrees(0, -480, fastSpeed)

    await pid.goForDegrees(0, 50, fastSpeed, decelDist=0, endDecelFactor=1, stopAtEnd=False)

    asyncio.create_task(moveArm(0))

    await pid.goForDegrees(23, 1220, fastSpeed, startAccelFactor=1, accelDist=0, decelDist=0, endDecelFactor=1, stopAtEnd=False)
    await pid.goTilLine(0, speedWithBricks, middle=middleCol, accelDist=0, postDecelDist=40, decelDist=50)

    asyncio.create_task(moveArm(480))

    await pid.turnTo(-167, 3, turnSpeed)

    asyncio.create_task(moveArm(400))
    await pid.goForDegrees(-167, 1500, fastSpeed + 200, startAccelFactor=0.5, accelDist=60, decelDist=0, endDecelFactor=1)

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

    await song.main()

asyncio.run(main())