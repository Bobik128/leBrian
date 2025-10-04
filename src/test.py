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

speed: int = 700
turnSpeed: int = 400

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
    
async def initRun():
    global runMotor, frontButton, angleButton, startTime, overBrick
    buggy.init(motors.MotorPort.D, motors.MotorPort.A)
    pid.init(7, 0.0001, 0.3,     #FORWARD
             0.03, 0.01, 0.016) #TURNING

    print("Reset gyro")
    await waitForPress() 
    await asyncio.sleep(1)
    await brick.initGyro(sensors.SensorPort.S1)

    brick.resetGyro()
    print("")
    print("Start")

    await waitForPressWithGyroCheck()
    startTime = time.time()
    await asyncio.sleep(0.1)
    print("Started!")

async def main():
    await initRun()
    ang: int = 0

    while True:
        ang = ang + 90
        await pid.turnTo(ang, 3, turnSpeed, -200)
        await asyncio.sleep(0.5)
        await pid.goForDegrees(ang, 500, speed)
        await asyncio.sleep(0.5)

asyncio.run(main())