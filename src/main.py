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

max_angular_speed = 0.8
max_extendon_speed = 0.3
max_acceleration = 0.5

async def main():
    global runMotor, frontButton, angleButton, startTime, overBrick, max_acceleration, max_extendon_speed, max_angular_speed
    print("Starting main")
    await crane.init(motors.MotorPort.D, motors.MotorPort.B, motors.MotorPort.C, sensors.SensorPort.S1)
    while True:
        await crane.moveLinear(0.3, -0.3, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)  # @crane:3baa353e31d2f0cf7c92ca39
        await crane.moveLinear(0.6, -0.3, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)  # @crane:158161fda0ebe4be81e03fa0
        await crane.moveLinear(0.6, 0.3, 90, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)  # @crane:a63dea85782a4c1bb77d82f5
        await crane.moveLinear(0.3, 0.3, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)  # @crane:a9a66ac488ce17846023d570

asyncio.run(main())