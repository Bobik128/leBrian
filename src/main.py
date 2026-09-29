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

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick
    print("Starting main")
    buggy.init(motors.MotorPort.D, motors.MotorPort.A)
    pid.init(7, 0.0001, 0.3, 0.03, 0.001, 0.016)

    # print("Init color")
    # await pid.initLineFollower( 2, 0.00001, 0.5)

    print("Press to reset gyro")
    await brick.waitForPress() 
    await asyncio.sleep(1)
    await brick.initGyro(sensors.SensorPort.S4)

    brick.resetGyro()
    print("gyro OK")

    await brick.waitForPress()
    await asyncio.sleep(1)

    await buggy.moveTank(80, 80, 600)


asyncio.run(main())