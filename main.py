from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid

async def main():
    buggy.init(motors.MotorPort.B, motors.MotorPort.A)
    await brick.initGyro(sensors.SensorPort.S1)
    await brick.initColor(sensors.SensorPort.S2)
    pid.init(8, 0.0001, 0.3)

    await pid.lineFollower(55, 250)


asyncio.run(main())