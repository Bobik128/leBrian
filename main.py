from brian import *
import buggy
import time
import math
import asyncio

async def main():
    buggy.init(motors.MotorPort.B, motors.MotorPort.A)
    await buggy.steering(200, 600, 60)


asyncio.run(main())