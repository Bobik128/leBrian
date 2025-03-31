from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid

async def main():
    buggy.init(motors.MotorPort.B, motors.MotorPort.A)
    await brick.initGyro(sensors.SensorPort.S3)
    await brick.initColor(sensors.SensorPort.S2)
    pid.init(8, 0.0001, 0.3, 0.025, 0.001, 0.016)

    brick.resetGyro()
    await asyncio.sleep(2)

    angle: int = 0

    while True:
        await pid.goForDegrees(angle, 1000, 400)
        angle += 90
        await pid.turnTo(angle, 1, 400, 0)


asyncio.run(main())