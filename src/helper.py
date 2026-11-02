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

async def checkColor(extendon_placeholder_pos: float = 0.33, index: int = 1):
    await crane.moveExtendonTo(0.395, speed=0.25, acceleration=50)
    
    base_yaw = brick.gyroAngle()*crane.GYRO_SIGN

    start_angle = 160
    end_angle = 200
    iterations = 15

    measurements = []

    for i in range(iterations):
        diff = end_angle - start_angle
        angle = start_angle + (diff/iterations)*i
        await crane.moveEndToRelative(angle, 50)
        measurements.append(await brick.getColor())

    clr1 = measurements.count(config.brick_orientations[index][0])
    clr2 = measurements.count(config.brick_orientations[index][1])

    await asyncio.sleep(0.5)
    color = await brick.getColor()
    swapped: bool = clr1 < clr2
    # if (color == config.brick_orientations[index][0]):
    #     swapped = False
    # elif (color != config.brick_orientations[index][1]):
    #     swapped = True
    # print(f"Color detected: {color}, expected: {config.brick_orientations[index]}")

    if swapped:
        # print(f"Clr mismatch for {index}: det. {color}, exp. {config.brick_orientations[index][0]}")
        await crane.moveExtendonTo(0.5, speed=0.20, acceleration=50)
        await asyncio.gather(
            crane.moveEndToRelative(270, 100),
            crane.moveYawTo(base_yaw - 10, 15)
        )
        await asyncio.gather(
            crane.moveEndToRelative(160, 100),
            crane.moveExtendonTo(0.55, speed=0.05, acceleration=50)
        )
        await crane.moveYawTo(base_yaw + 5, 30)
        await crane.moveExtendonTo(0.82, speed=0.25, acceleration=50)
        await asyncio.gather(
            crane.moveYawTo(base_yaw - 25, 23),
            crane.moveEndToRelative(190, 50)
        )
        await crane.moveExtendonTo(0.67, speed=0.25, acceleration=50)
    else:
        # print(f"Clr OK for {index}: det. {color}")
        await crane.moveExtendonTo(0.6, speed=0.25, acceleration=50)
        await asyncio.gather(
            crane.moveEndToRelative(110, 60),
            crane.moveExtendonTo(0.48, speed=0.11, acceleration=50),
            crane.moveYawTo(base_yaw - 42, speed=30)
        )
        await crane.moveExtendonTo(0.7, speed=0.25, acceleration=50)
        await asyncio.gather(
            crane.moveEndToRelative(200, 90),
            crane.moveYawTo(base_yaw - 30, speed=20)
        )
        await crane.moveExtendonTo(0.62, speed=0.25, acceleration=50)
        
# async def checkColor(extendon_placeholder_pos: float = 0.33, index: int = 1):
#     await crane.moveExtendonTo(0.42, speed=0.25, acceleration=50)
    
#     base_yaw = brick.gyroAngle()*crane.GYRO_SIGN
    
#     await crane.moveEndToRelative(160, 100)
#     await asyncio.sleep(0.5)
#     color = await brick.getColor()
#     print(f"Color detected: {color}, expected: {config.brick_orientations[index]}")
#     if color != config.brick_orientations[index]:
#         print(f"Clr mismatch for {index}: det. {color}, exp. {config.brick_orientations[index]}")
        
#         await crane.moveEndBy(180, 180)
        
#         await crane.moveExtendonTo(0.37, speed=0.3, acceleration=config.default_extension_acceleration)
#         await crane.moveYawTo(base_yaw -30, speed=35, acceleration=config.default_yaw_acceleration)
#         await crane.moveExtendonTo(0.6, speed=0.3, acceleration=config.default_extension_acceleration)
        
#         await asyncio.gather(
#             crane.moveYawTo(base_yaw - 10, speed=30, acceleration=config.default_yaw_acceleration),
#             crane.moveEndBy(160, 160)
#         )

#         crane.endMotor.reset_angle(crane.endMotor.current_angle()-360/crane.END_RATIO)
        
#         await crane.moveExtendonTo(0.34, speed=0.3, acceleration=config.default_extension_acceleration)
#         return
