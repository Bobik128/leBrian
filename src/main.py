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

max_angular_speed: float = 0.6
max_extendon_speed: float = 0.25
max_acceleration: float = 1.0
max_end_motor_speed: float = 4.0

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick, max_acceleration, max_extendon_speed, max_angular_speed
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

    await crane.moveLinear(0.356433, 0.002862, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_end_angular_speed=max_end_motor_speed, max_acceleration=max_acceleration)  # @crane:0d4078471721155934dfe7e3
    await crane.moveLinear(0.309794, -0.385148, -80, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_end_angular_speed=max_end_motor_speed, max_acceleration=max_acceleration)  # @crane:386efeca860f91789af030f1
    await crane.moveLinear(0.353302, -0.647924, -79.265985, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_end_angular_speed=max_end_motor_speed, max_acceleration=max_acceleration)  # @crane:fd4b03b249af2a8375b5411e
    await crane.moveEnd(-3.398186, max_speed=200, max_acceleration=240)  # @crane:2b54300696cfee20bfa7c4cb
    await crane.moveLinear(0.483737, -0.300785, 60, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_end_angular_speed=max_end_motor_speed, max_acceleration=max_acceleration)  # @crane:dfddffe656ff5910a951f5e7
    
try:
    asyncio.run(main())
except Exception as error:
    sys.print_exception(error)
    raise