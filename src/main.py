from brian import *
from brian.sensors.EV3 import ColorSensorEV3
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
default_extension_speed: float = 0.26
default_end_motor_speed: float = 130
default_yaw_acceleration: float = 500.0
default_extension_acceleration: float = 600.0
default_end_acceleration: float = 1000.0

brick_orientations: dict[int, ColorSensorEV3.Color] = {
    1: ColorSensorEV3.Color.BLUE,
    2: ColorSensorEV3.Color.GREEN,
    3: ColorSensorEV3.Color.BLUE,
    4: ColorSensorEV3.Color.RED,
    5: ColorSensorEV3.Color.GREEN,
    6: ColorSensorEV3.Color.YELLOW,
    7: ColorSensorEV3.Color.YELLOW,
    8: ColorSensorEV3.Color.GREEN,
    9: ColorSensorEV3.Color.RED,
    10: ColorSensorEV3.Color.YELLOW,
    11: ColorSensorEV3.Color.BLUE,
    12: ColorSensorEV3.Color.YELLOW,
    13: ColorSensorEV3.Color.RED,
    14: ColorSensorEV3.Color.RED,
    15: ColorSensorEV3.Color.RED,
    16: ColorSensorEV3.Color.BLUE,
}

async def checkColor(index: int):
    await crane.moveExtendonTo(0.288, speed=0.2, acceleration=default_extension_acceleration)
    base_angle = (crane.endMotor.current_angle()*crane.END_RATIO) % 360
    base_yaw = brick.gyroAngle()*crane.GYRO_SIGN
    await crane.moveEndToRaw(crane.endMotor.current_angle()*crane.END_RATIO + 185 - (base_angle), speed=80, acceleration=default_end_acceleration)
    await asyncio.sleep(0.5)
    color = await brick.getColor()
    print(f"Color detected: {color}, expected: {brick_orientations[index]}")
    if color != brick_orientations[index]:
        print(f"Color mismatch for brick {index}: detected {color}, expected {brick_orientations[index]}")
        crane.endMotor.rotate_to(int((crane.endMotor.current_angle() + 180/ crane.END_RATIO)), speed=160, timeout_ms=0)
        while not crane.endMotor.is_done():
            await asyncio.sleep(0.01)
        crane.endMotor.hold()
        await crane.moveYawTo(base_yaw -30, speed=35, acceleration=default_yaw_acceleration)
        await crane.moveExtendonTo(0.6, speed=0.3, acceleration=default_extension_acceleration)
        await crane.moveYawTo(base_yaw, speed=30, acceleration=default_yaw_acceleration)
        crane.endMotor.rotate_to(int((crane.endMotor.current_angle() + 180/ crane.END_RATIO)), speed=160, timeout_ms=0)
        while not crane.endMotor.is_done():
            await asyncio.sleep(0.01)
        crane.endMotor.hold()
        return


async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick, default_yaw_acceleration, default_extension_acceleration, default_end_acceleration
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

    print("Press to start")
    await brick.waitForPressWithGyroCheck()
    print("Program started")
    await crane.moveTo(0.057619, -0.304297, 0, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:8bd5ef2e031e6013e1299a46
    await crane.moveTo(0.080095, -0.583499, -64.747805, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:abefd9ab22b26730240932d1
    await crane.moveYawTo(-64.818497, speed=30, acceleration=default_yaw_acceleration)  # @crane:9766f74de4d2b5f2d309c879
    await crane.moveEndTo(60.990629, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:9b7802af4765fa05f35f448c
    await checkColor(1)
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