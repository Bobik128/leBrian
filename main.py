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
overBrick: bool = False

startTime: float

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

    runMotor.rotate_by_angle(-170, abs(speed))
    runMotor.hold()
    ressetingRoller = False

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def play(freq, duration):
    """
    :param freq: note freq Hz
    :param duration: duration in s
    :return:
    """

    audio.play_tone(round(freq), duration)  # hz, ms
    await asyncio.sleep(duration/1000)

async def waitForAnyPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(brick.gyro.angle()) > 5:
            print("GYRO DRIFT")
        buttons: uicontrol.UiEventsListener.ButtonsEvent = listener.buttons_event_since_last()
        if buttons.top_right.just_pressed:
            return 1
        elif buttons.top_left.just_pressed:
            return 2
        elif buttons.bottom_right.just_pressed:
            return 3
        elif buttons.bottom_left.just_pressed:
            return 4

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
    speed: int = 160
    dist: int = 40
    await asyncio.sleep(0.7)
    await buggy.moveTank(-speed, -speed, dist)
    await buggy.moveTank(speed, speed, dist + 10)
    # await asyncio.sleep(0.3)
    # await buggy.moveTank(-speed, -speed, dist)
    # await buggy.moveTank(speed, speed, dist + 10)

async def manuver2(turnSpeed, speed, angle):
    buggy.resetAngle()
    await pid.goForDegrees(angle-2, -285, speed*1.2, True)
    m_angle: float = buggy.rMotor.current_angle()
    buggy.rMotor.run_at_speed(turnSpeed)
    buggy.lMotor.run_at_speed(math.floor(turnSpeed/3.6))
    while buggy.rMotor.current_angle() - m_angle < 450:
        await asyncio.sleep(0.01)

    await pid.goForDegrees(angle+70, 100, speed*1.2, False)

async def initRun():
    global runMotor, frontButton, angleButton, startTime, overBrick
    runMotor = motors.Motor(motors.MotorPort.D)
    buggy.init(motors.MotorPort.C, motors.MotorPort.A)
    await intiBackButton(sensors.SensorPort.S3)
    await intiAngleButton(sensors.SensorPort.S1)
    await brick.initSonic(sensors.SensorPort.S2)
    pid.init(7, 0.0001, 0.3, 0.03, 0.001, 0.016)

    # print("Init color")
    # await pid.initLineFollower( 2, 0.00001, 0.5)

    print("Reset gyro")
    await waitForPress() 
    await asyncio.sleep(1)
    await brick.initGyro(sensors.SensorPort.S4)

    brick.resetGyro()
    print("gyro resetted")
    print("Press to start")
    print("top right: catching program")
    print("top left: random drive programm")
    print("bottom right: without oponent")
    prog: int = await waitForAnyPress()
    print("")
    print("throw over brick?")
    print("No                    Yes")
    throw: int = await waitForAnyPress()
    overBrick = (throw == 1 or throw == 3)
    print("")
    print("Start")

    await waitForPress()
    startTime = time.time()
    await asyncio.sleep(0.1)
    print("Started!")

    return prog

async def robotRun():
    global runMotor, frontButton, angleButton, overBrick
    prog: int = await initRun()

    runMotor.run_at_speed(-runMotorSpeed)

    speed: int = 400
    fastSpeed: int = 560
    ultraFastSpeed: int = 700
    turnSpeed: int = 280

    # await pid.lineFollowerWithGyroTilButton(0, speed, backButton, 0.1)

    await pid.turnTo(60, 3, turnSpeed, -200, False)
    await pid.goForDegrees(65, 200, speed, False)
    await pid.goForDegrees(30, 320, speed, False)
    await pid.goForDegrees(70, 100, speed)
    await pid.goTilButton(90, speed, frontButton, 0.05)
    await wiggleBackward()
    await asyncio.sleep(0.5)

    await manuver2(turnSpeed, speed, 90)

    await pid.goTilButton(177, fastSpeed, frontButton, 0.05)

    await wiggleBackward()
    await asyncio.sleep(0.8)

    await pid.goForDegrees(175, -850, fastSpeed, True)
    await pid.turnTo(210, 3, turnSpeed * 0.8, -320, False)  
    await pid.goForDegrees(210, 620, speed, False)
    await pid.goForDegrees(230, 80, speed, False)
    await pid.goForDegrees(260, 230, speed, False)
    await pid.goTilButton(268, fastSpeed, frontButton, 0.05)

    await wiggleBackward()
    await asyncio.sleep(0.8)

    await pid.goForDegrees(265, -1000, fastSpeed, True)
    await pid.turnTo(290, 3, turnSpeed * 0.8, -320, False)  
    await pid.goTilButton(290, speed, frontButton, 0.2)
    await wiggleBackward()
    await asyncio.sleep(0.5)
    await pid.goForDegrees(270, -800, fastSpeed) 
    await pid.turnTo(300, 3, turnSpeed * 0.8, -320, False) 
    await pid.goForDegrees(300, 550, speed, False)
    await pid.goForDegrees(330, 300, speed, False)
    await pid.goTilButton(360, speed * 0.8, frontButton, 0)
    await asyncio.sleep(1.2)

    if prog == 3:
        await unload(fastSpeed, turnSpeed, speed)
    elif prog == 1 or prog == 4:
        await pid.goForDegrees(300, -600, fastSpeed)
        await pid.turnTo(410, 3, turnSpeed, 0, False)
        await pid.goForDegrees(410, 100, fastSpeed)
        await pid.turnTo(360, 3, turnSpeed)
        await pid.goForDegrees(360, 200, speed)

        if prog == 4:
            while time.time() - startTime < 72:
                await asyncio.sleep(0.1)
        else:
            while time.time() - startTime < 82:
                await asyncio.sleep(0.1)
        
        await pid.goForDegrees(360, -50, fastSpeed, False)
        
        if not overBrick:
            await pid.goForDegrees(450, 800, fastSpeed)
            
            p1 = asyncio.create_task(pid.turnTo(540, 3, turnSpeed, 0))
            p2 = asyncio.create_task(resetRollerPos())

            await asyncio.gather(p1, p2)
            await pid.goForDegrees(540, -600, speed, False)
        else:
            p1 = asyncio.create_task(buggy.moveTank(-1100, -100, 600))
            p2 = asyncio.create_task(resetRollerPos())

            await asyncio.gather(p1, p2)
            await pid.goForDegrees(180, -600, speed, False)

        if prog == 1:
            if not overBrick:
                await asyncio.sleep(2)
                await pid.goForDegrees(540, 100, speed)
                await pid.goForDegrees(540, -150, speed)
            else:
                await asyncio.sleep(2)
                await pid.goForDegrees(180, 100, speed)
                await pid.goForDegrees(180, -150, speed)
        else:
            await asyncio.sleep(0.5)
            buggy.stop()
            # await pid.goForDegrees(540, 80, ultraFastSpeed, False)
            dist: int = 700

            p3
            p4

            if not overBrick:
                buggy.resetAngle()
                await buggy.moveTank(320, 1100, dist*2/3, False)
                runMotor.run_at_speed(-runMotorSpeed)
                buggy.resetAngle()
                await buggy.moveTank(320, 1100, dist*3/4)
            
                # await pid.goForDegrees(630, 860, ultraFastSpeed, False)
                # await pid.goForDegrees(720, 160, ultraFastSpeed)

                p3 = asyncio.create_task(buggy.moveTank(-200, -1100, dist))
                p4 = asyncio.create_task(resetRollerPos())
            else:
                buggy.resetAngle()
                await buggy.moveTank(1100, 320, dist*2/3, False)
                runMotor.run_at_speed(-runMotorSpeed)
                buggy.resetAngle()
                await buggy.moveTank(1100, 320, dist*3/4)
            
                # await pid.goForDegrees(630, 860, ultraFastSpeed, False)
                # await pid.goForDegrees(720, 160, ultraFastSpeed)

                p3 = asyncio.create_task(buggy.moveTank(-1100, -200, dist))
                p4 = asyncio.create_task(resetRollerPos())

            while time.time() - startTime < 85:
                await asyncio.sleep(0.1)

            buggy.resetAngle()
            await asyncio.gather(p3, p4)
            # await resetRollerPos()
            # await buggy.moveTank(-200, -1100, dist)
            if not overBrick:
                await pid.goForDegrees(540, -100, fastSpeed, False)
                await asyncio.sleep(1.5)
                await pid.goForDegrees(540, 100, speed)
                await pid.goForDegrees(540, -150, speed)
            else:
                await pid.goForDegrees(180, -100, fastSpeed, False)
                await asyncio.sleep(1.5)
                await pid.goForDegrees(180, 100, speed)
                await pid.goForDegrees(180, -150, speed)

    elif prog == 2:
        angle = 360
        await pid.goForDegrees(angle, -60, speed)
        for i in range(4):
            await manuver2(turnSpeed, speed, angle)
            angle = 90 + angle
            if i == 1:
                timeout = 10
            else:
                timeout = 6
            await pid.goTilButton(angle - 3, fastSpeed, frontButton, 0.05, timeout)
            await wiggleBackward()
            await asyncio.sleep(0.8)
        
        await pid.goForDegrees(angle - 8, -600, fastSpeed, False)
        await manuver2(turnSpeed, speed, angle)
        await pid.goTilButton(angle + 90, fastSpeed, frontButton, 0.05)
        await wiggleBackward()
        await asyncio.sleep(0.8)
        await pid.goForDegrees(angle + 90, -500, fastSpeed)
        
        p1 = asyncio.create_task(pid.turnTo(angle + 180, 3, turnSpeed, 0))
        p2 = asyncio.create_task(resetRollerPos())

        await asyncio.gather(p1, p2)

        while time.time() - startTime < 82:
            await asyncio.sleep(0.1)

        await pid.goForDegrees(angle + 180, -600, speed, False)
        await asyncio.sleep(2)
        await pid.goForDegrees(angle + 180, 100, speed)
        await pid.goForDegrees(angle + 180, -150, speed)

    buggy.stop()

async def unload(fastSpeed, turnSpeed, speed, angle = 360):
    await pid.goForDegrees(angle - 10, -600, fastSpeed)
    await pid.turnTo(angle + 90, 3, turnSpeed, -320, False)
    await pid.goForDegrees(angle + 90, 1000, fastSpeed)

    p1 = asyncio.create_task(pid.turnTo(angle + 180, 3, turnSpeed, 0))
    p2 = asyncio.create_task(resetRollerPos())

    await asyncio.gather(p1, p2)

    # while time.time() - startTime < 85:
    #     await asyncio.sleep(0.1)

    await pid.goForDegrees(angle + 180, -600, speed, False)
    await asyncio.sleep(2)
    await pid.goForDegrees(angle + 180, 100, speed)
    await pid.goForDegrees(angle + 180, -150, speed)

async def main():
    global runMotor, frontButton, angleButton
    robotRunTask = asyncio.create_task(robotRun())

    await asyncio.gather(robotRunTask)


asyncio.run(main())