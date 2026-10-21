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
    await crane.moveExtendonTo(0.34, speed=0.25, acceleration=50)
    
    base_yaw = brick.gyroAngle()*crane.GYRO_SIGN
    
    await crane.moveEndToRelative(185, 100)
    await asyncio.sleep(0.5)
    color = await brick.getColor()
    print(f"Color detected: {color}, expected: {config.brick_orientations[index]}")
    if color != config.brick_orientations[index]:
        print(f"Clr mismatch for {index}: det. {color}, exp. {config.brick_orientations[index]}")
        
        await crane.moveEndBy(180, 100)
        
        await crane.moveExtendonTo(0.37, speed=0.3, acceleration=config.default_extension_acceleration)
        await crane.moveYawTo(base_yaw -30, speed=35, acceleration=config.default_yaw_acceleration)
        await crane.moveExtendonTo(0.6, speed=0.3, acceleration=config.default_extension_acceleration)
        
        await asyncio.gather(
            crane.moveYawTo(base_yaw - 10, speed=30, acceleration=config.default_yaw_acceleration),
            crane.moveEndBy(160, 160)
        )

        crane.endMotor.reset_angle(crane.endMotor.current_angle()-360/crane.END_RATIO)
        
        await crane.moveExtendonTo(0.34, speed=0.3, acceleration=config.default_extension_acceleration)
        return
