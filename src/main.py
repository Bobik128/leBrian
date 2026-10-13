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
        await crane.moveLinear(0.4, 0.4, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)
        await crane.moveLinear(0.4, -0.4, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)
        await crane.moveLinear(0.7, -0.4, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)
        await crane.moveLinear(0.7, 0.4, 0, max_angular_speed=max_angular_speed, max_extension_speed=max_extendon_speed, max_acceleration=max_acceleration)


asyncio.run(main())