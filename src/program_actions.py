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
import helper

async def program():
    print("Press to prep")
    await brick.waitForPressWithGyroCheck()
    await crane.moveTo(0.647829, -0.208751, 0, yaw_speed=16, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:abefd9ab22b26730240932d1
    await crane.moveTo(0.87263, -0.237109, 24.584846, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:f631dad89605d078b4dfab17
    
    print("Press to start")
    await brick.waitForPressWithGyroCheck()
    print("Program started")

    await crane.moveYawAndEnd(-4.661187, 108.691649, yaw_speed=35, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:bc108c4c490cbc035a0b5ba8
    await helper.checkColor(0.33, 1)  # @crane:128e39bbbb94f3385ceb3ffd
    await crane.moveEndTo(205.634354, speed=50, acceleration=config.default_end_acceleration)  # @crane:7d9b743546744709860e2bef
    await crane.moveTo(0.474674, -0.265576, 198.762396, yaw_speed=config.default_yaw_speed, extendon_speed=0.15, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:3bb399a10716d12f0858e06e
    await crane.moveTo(0.380305, -0.425497, 127.893971, yaw_speed=30, extendon_speed=0.15, end_speed=105, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:0b54d9380436896e2a31b034
    await crane.moveTo(0.248759, -0.378926, 71.759982, yaw_speed=30, extendon_speed=0.15, end_speed=105, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:ce18d8a39dc8ec89c483f311
    await crane.moveTo(0.227201, -0.201876, 71.759982, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:e20d274332a77ab66dd3e107
    await crane.moveEndTo(86.045276, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:d7f7d3d399fa13b37e45c961

    # await crane.moveExtendonTo(0.542534, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:ec26477964aa4734373c7e62
    # await crane.moveEndTo(218.102573, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:dd780da08c825d2debf419ee
    # await crane.moveExtendonTo(0.412215, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:53d9e9cc21128d3929443ae8
    # await crane.moveEndTo(170.722641, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:d7a778394462871366d03f92
    # await crane.moveExtendonTo(0.360845, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:718b77a13feb8754c09f2425
    # await crane.moveEndTo(171.084698, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:a71e802435a44d921188baa4
    # await crane.moveTo(0.349911, 0.1358, 127.791678, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:c41d94ac7b84ecf3cec4d558
    # await crane.moveTo(0.407707, 0.231948, 207.240015, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=70, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:8e2fb1ae3abc9ae64bb1f1b6
    # await crane.moveTo(0.226071, 0.349474, 268.203847, yaw_speed=config.default_yaw_speed, extendon_speed=0.08, end_speed=70, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:0f320e4b0e6239d5e3448fe9
    # await crane.moveExtendonTo(0.318187, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:427d4c7fe9950c37ef876ee7
