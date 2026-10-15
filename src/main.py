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

default_yaw_speed: float = 40
default_extension_speed: float = 0.22
default_end_motor_speed: float = 100
default_yaw_acceleration: float = 400.0
default_extension_acceleration: float = 600.0
default_end_acceleration: float = 1000.0

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick, default_yaw_acceleration, default_extension_acceleration, default_end_acceleration
    print("Starting main")
    pid.init(0,0,0,0,0,0)
    await asyncio.sleep(1)
    print("Init gyro")
    await brick.waitForPress()
    await brick.initGyro(sensors.SensorPort.S3)
    print(brick.gyroAngle())

    print("Init crane")
    await brick.waitForPressWithGyroCheck()
    await asyncio.sleep(0.5)
    await crane.init(motors.MotorPort.D, motors.MotorPort.B, motors.MotorPort.C, sensors.SensorPort.S1)

    print("Press to start")
    await brick.waitForPressWithGyroCheck()
    print("Program started")

    await crane.moveTo(0.2, -0.4, -90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:6a50f87c2f2e6c41178e5ffb
    await asyncio.sleep(0.5)
    await crane.moveTo(0.232922, -0.663299, -89.03189, yaw_speed=30, extendon_speed=0.15, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:7208cfa759ecddd29f2ededb
    await crane.moveEndTo(-3.520852, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:fa421c488adbdfb3b59832a3
    await crane.moveTo(0.396009, -0.531933, 44.41498, yaw_speed=25, extendon_speed=0.1, end_speed=60, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:8f13254fdec68616ad3681da
    await crane.moveTo(0.486348, -0.139924, 177.765645, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:c8c344b0fb543eb65b0ff70b
    await crane.moveTo(0.755844, -0.131343, 1.127487, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:1642b0b7cde7840595e75fc4
    await asyncio.sleep(0.5)
    await crane.moveTo(0.984452, -0.155376, -1.350575, yaw_speed=default_yaw_speed, extendon_speed=0.15, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:c1b853749c38a47bc5781208
    await crane.moveEndTo(75.645013, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:37757c0fccb2cf59ac091e2b
    await crane.moveTo(0.8602, 0.050636, 160.855415, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:59ac7b78c1564a3533eee5fa
        
    # while True:

        # await crane.moveTo(0.6, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:1100f4d856d1a90182930f5c
        # await crane.moveTo(0.8, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:7e6eb707f0a0ef13111165b8
        # await crane.moveTo(0.2, -0.5, -90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:3ba6acdf5d83964c96ffe185
        # await asyncio.sleep(0.5)
        # await crane.moveTo(0.6, -0.5, -90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:a4b229df087af1a0accfdf35
        # await asyncio.sleep(0.5)
        # await crane.moveTo(0.8, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:cda1d91a13d583197160a088
        # await asyncio.sleep(0.5)
        # await crane.moveTo(0.6, 0.5, 90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:0fb9a65aebf78f7542ccbec3
        # await asyncio.sleep(0.5)
        # await crane.moveTo(0.2, 0.5, 90, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:0769c7f15fe1d7dadc71d627
        # await asyncio.sleep(0.5)
        # await crane.moveTo(0.3, 0, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:b6c894b256a7cd2d8a95e235
        # await asyncio.sleep(0.5)
try:
    asyncio.run(main())
except Exception as error:
    sys.print_exception(error)
    raise