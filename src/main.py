from brian import *
import buggy
import brick
import time
import math
import asyncio
import pid
import time
import sys
import crane

runMotor: motors.Motor
extendon: sensors.EV3.TouchSensorEV3
ressetingRoller: bool = False
rollerStuck: bool = False
overBrick: bool = False

startTime: float

default_yaw_speed: float = 100
default_extension_speed: float = 0.25
default_end_motor_speed: float = 100
default_yaw_acceleration: float = 600.0
default_extension_acceleration: float = 600.0
default_end_acceleration: float = 1000.0

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick, default_yaw_acceleration, default_extension_acceleration, default_end_acceleration
    print("Starting main")
    await asyncio.sleep(1)
    print("Init gyro")
    await brick.waitForPress()
    await brick.initGyro(sensors.SensorPort.S3)
    print(brick.gyroAngleAndSpeed())

    print("Init crane")
    await brick.waitForPressWithGyroCheck()
    await asyncio.sleep(0.5)
    await crane.init(motors.MotorPort.D, motors.MotorPort.B, motors.MotorPort.C, sensors.SensorPort.S1)

    print("Press to start")
    await brick.waitForPressWithGyroCheck()
    print("Program started")

    while True:
        await crane.moveTo(0.6, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:1100f4d856d1a90182930f5c
        await crane.moveTo(0.8, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:7e6eb707f0a0ef13111165b8
        # await crane.moveTo(0.2, -0.5, -90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:3ba6acdf5d83964c96ffe185
        # await crane.moveTo(0.6, -0.5, -90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:a4b229df087af1a0accfdf35
        # await crane.moveTo(0.8, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:cda1d91a13d583197160a088
        # await crane.moveTo(0.6, 0.5, 90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:0fb9a65aebf78f7542ccbec3
        # await crane.moveTo(0.2, 0.5, 90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:0769c7f15fe1d7dadc71d627
        # await crane.moveTo(0.3, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:b6c894b256a7cd2d8a95e235
try:
    asyncio.run(main())
except Exception as error:
    sys.print_exception(error)
    raise