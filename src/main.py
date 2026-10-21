from brian import *
from brian.sensors.EV3 import ColorSensorEV3
import brick
import time
import math
import asyncio
import pid
import time
import sys
import crane
import config
import program_actions

runMotor: motors.Motor
extendon: sensors.EV3.TouchSensorEV3
ressetingRoller: bool = False
rollerStuck: bool = False
overBrick: bool = False

startTime: float

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick
    print("Starting main")
    pid.init(0,0,0,0,0,0)
    await brick.initColor(sensors.SensorPort.S4)
    await asyncio.sleep(1)
    print("Init gyro")
    await brick.waitForPress()
    await brick.initGyro(sensors.SensorPort.S3)
    print(brick.gyroAngle())

    print("Init crane")
    await brick.waitForPressWithGyroCheck()
    await asyncio.sleep(0.5)
    await crane.init(motors.MotorPort.D, motors.MotorPort.B, motors.MotorPort.C, sensors.SensorPort.S1)

    await program_actions.program()
try:
    asyncio.run(main())
except Exception as error:
    sys.print_exception(error)
    raise