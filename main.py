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
backButton: sensors.EV3.TouchSensorEV3
angleButton: sensors.EV3.TouchSensorEV3

async def intiAngleButton(port: sensors.SensorPort):
    global angleButton
    angleButton = sensors.EV3.TouchSensorEV3(port)
    while not angleButton.is_ready():
        asyncio.sleep(0.1)

async def intiBackButton(port: sensors.SensorPort):
    global backButton
    backButton = sensors.EV3.TouchSensorEV3(port)
    while not backButton.is_ready():
        asyncio.sleep(0.1)

async def resetRollerPos(speed: int = 1100):
    global runMotor, angleButton
    runMotor.run_at_speed(-abs(speed))

    while not angleButton.is_pressed():
        await asyncio.sleep(0.01)

    while angleButton.is_pressed():
        await asyncio.sleep(0.01)
    
    runMotor.hold()

    runMotor.rotate_by_angle(-300, abs(speed))
    runMotor.hold()

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

async def manuver1(turnSpeed, speed, angle):
    await pid.goForDegrees(angle, -250, speed*1.2, True)
    await pid.turnTo(angle + 90, 3, turnSpeed * 0.8, -360, False)  
    

async def main():
    global runMotor, backButton, angleButton
    runMotor = motors.Motor(motors.MotorPort.C)
    buggy.init(motors.MotorPort.B, motors.MotorPort.A)
    await intiBackButton(sensors.SensorPort.S4)
    await intiAngleButton(sensors.SensorPort.S1)
    await brick.initColor(sensors.SensorPort.S2)
    pid.init(8, 0.0001, 0.3, 0.03, 0.001, 0.016)

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
    timerRun()

    runMotor.run_at_speed(-1100)

    speed: int = 300
    turnSpeed: int = 300

    await pid.turnTo(50, 3, turnSpeed, -200, False)
    await pid.goTilLine(60, speed, False)
    await pid.turnTo(70, 3, turnSpeed, -200, False)
    await pid.goForDegrees(75, 290, speed, False)
    await pid.turnTo(90, 3, turnSpeed, -200)
    await asyncio.sleep(1)

    await pid.goTilLine(90, -speed, True)
    await pid.turnTo(120, 3, turnSpeed)
    await pid.goForDegrees(120, 230, speed, False)
    await pid.turnTo(180, 3, turnSpeed, -450, False)
    buggy.rMotor.reset_angle()
    buggy.lMotor.reset_angle()
    await pid.goForDegrees(180, 860, speed)
    await asyncio.sleep(1)

    await manuver1(turnSpeed, speed, 180)
    await pid.goTilLine(270, speed, False)
    await asyncio.sleep(0.2)
    await pid.goTilLine(270, speed, False)
    await asyncio.sleep(0.2)
    await pid.goTilLine(270, speed, False)
    await pid.goForDegrees(270, 200, speed, True)
    await asyncio.sleep(1)

    await manuver1(turnSpeed, speed, 270)

    # await resetRollerPos()

    # await pid.goTilButton(0, -300, backButton, 0.5)
    # await pid.goForDegrees(0, 500, -400)

    # while True:
    #     await pid.goForDegrees(angle, 1000, 400)
    #     angle += 90
    #     await pid.turnTo(angle, 1, 200, -100)

    await asyncio.sleep(2)


asyncio.run(main())