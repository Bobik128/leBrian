from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid
import time
import sys

runMotor: motors.Motor
frontButton: sensors.EV3.TouchSensorEV3
angleButton: sensors.EV3.TouchSensorEV3
ressetingRoller: bool = False
rollerStuck: bool = False

runMotorSpeed: int = 1100


async def intiAngleButton(port: sensors.SensorPort):
    global angleButton
    angleButton = sensors.EV3.TouchSensorEV3(port)
    while not angleButton.is_ready():
        asyncio.sleep(0.1)

async def intiBackButton(port: sensors.SensorPort):
    global frontButton
    frontButton = sensors.EV3.TouchSensorEV3(port)
    while not frontButton.is_ready():
        asyncio.sleep(0.1)

async def resetRollerPos(speed: int = runMotorSpeed):
    global runMotor, angleButton, ressetingRoller, rollerStuck
    ressetingRoller = True
    runMotor.run_at_speed(-abs(speed))

    while not angleButton.is_pressed() or rollerStuck:
        await asyncio.sleep(0.01)

    while angleButton.is_pressed() or rollerStuck:
        await asyncio.sleep(0.01)
    
    runMotor.hold()

    runMotor.rotate_by_angle(-300, abs(speed))
    runMotor.hold()
    ressetingRoller = False

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def timerRun():
    start: float = time.time()
    while time.time() < 90 + start:
        await asyncio.sleep(0.01)

    sys.exit()

async def sMotorStuckDetector():
    global runMotor, angleButton, rollerStuck, ressetingRoller
    stuckDelay: float = 3
    lastChangeTime = time.time() 
    isPressed: bool = angleButton.is_pressed()
    while True:
        if isPressed != angleButton.is_pressed():
            lastChangeTime = time.time() 
            isPressed = angleButton.is_pressed()

        if runMotor.current_speed() > 5 and time.time() - lastChangeTime > stuckDelay:
            rollerStuck = True
            print("small motor stuck")
            runMotor.brake()
            runMotor.run_at_speed(600)
            await asyncio.sleep(0.5)
            runMotor.hold()
            runMotor.run_at_speed(-runMotorSpeed)
            rollerStuck = False
            lastChangeTime = time.time()
        else:
            lastChangeTime = time.time() 
            rollerStuck = False

        await asyncio.sleep(0.02)



async def manuver1(turnSpeed, speed, angle):
    await pid.goForDegrees(angle, -250, speed*1.2, True)
    await pid.turnTo(angle + 90, 3, turnSpeed * 0.8, -315, False)  

async def wiggleBackward():
    await buggy.moveTank(-600, -600, 80)
    await buggy.moveTank(600, 600, 80)
    await buggy.moveTank(-600, -600, 80)
    await buggy.moveTank(600, 600, 80)

async def manuver2(turnSpeed, speed, angle):
    buggy.resetAngle()
    await pid.goForDegrees(angle, -280, speed*1.2, True)
    m_angle: float = buggy.rMotor.current_angle()
    buggy.rMotor.run_at_speed(turnSpeed)
    buggy.lMotor.run_at_speed(math.floor(turnSpeed/3.6))
    while buggy.rMotor.current_angle() - m_angle < 450:
        await asyncio.sleep(0.01)

    await pid.goForDegrees(angle+70, 100, speed*1.2)

async def initRun():
    global runMotor, frontButton, angleButton
    runMotor = motors.Motor(motors.MotorPort.C)
    buggy.init(motors.MotorPort.B, motors.MotorPort.A)
    await intiBackButton(sensors.SensorPort.S2)
    await intiAngleButton(sensors.SensorPort.S1)
    # await brick.initColor(sensors.SensorPort.S2)
    pid.init(7, 0.0001, 0.3, 0.03, 0.001, 0.016)

    # print("Init color")
    # await pid.initLineFollower( 2, 0.00001, 0.5)

    print("Reset gyro")
    await waitForPress() 
    await asyncio.sleep(1)
    await brick.initGyro(sensors.SensorPort.S3)

    brick.resetGyro()
    print("gyro resetted")
    print("Press to start")
    await waitForPress()
    await asyncio.sleep(0.1)
    print("Started!")

async def robotRun():
    global runMotor, frontButton, angleButton
    await initRun()

    runMotor.run_at_speed(-runMotorSpeed)

    speed: int = 360
    turnSpeed: int = 250

    # await pid.lineFollowerWithGyroTilButton(0, speed, backButton, 0.1)

    await pid.turnTo(60, 3, turnSpeed, -200, False)
    await pid.goForDegrees(65, 200, speed, False)
    await pid.goForDegrees(30, 320, speed, False)
    await pid.goForDegrees(70, 100, speed)
    await pid.goTilButton(90, speed, frontButton, 0.1)
    await wiggleBackward()
    await asyncio.sleep(0.5)

    await manuver2(turnSpeed, speed, 90)

    await pid.goTilButton(177, speed, frontButton, 0.1)

    await wiggleBackward()
    await asyncio.sleep(0.5)

    await pid.goForDegrees(175, -800, speed*1.5, True)
    await pid.turnTo(210, 3, turnSpeed * 0.8, -320, False)  
    await pid.goForDegrees(210, 620, speed, False)
    await pid.goForDegrees(230, 80, speed, False)
    await pid.goForDegrees(260, 200, speed, False)
    await pid.goTilButton(268, speed, frontButton, 0.1)

    await wiggleBackward()
    await asyncio.sleep(0.5)

    await pid.goForDegrees(265, -1000, speed*1.5, True)
    await pid.turnTo(290, 3, turnSpeed * 0.8, -320, False)  
    await pid.goTilButton(290, speed, frontButton, 0.1)
    await asyncio.sleep(1)
    await pid.goForDegrees(270, -800, speed*1.5) 
    await pid.turnTo(300, 3, turnSpeed * 0.8, -320, False) 
    await pid.goForDegrees(300, 500, speed, False)
    await pid.goForDegrees(360, 200, speed, False)
    await wiggleBackward()
    await asyncio.sleep(0.5)
    
    await manuver2(turnSpeed, speed, 360)

async def main():
    global runMotor, frontButton, angleButton
    timerTask = asyncio.create_task(timerRun())
    robotRunTask = asyncio.create_task(robotRun())
    sMotorStuckDetectorTask = asyncio.create_task(sMotorStuckDetector())

    await asyncio.gather(timerTask, robotRunTask, sMotorStuckDetectorTask)


asyncio.run(main())