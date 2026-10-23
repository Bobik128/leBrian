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
    await crane.moveEndTo(224.657895, speed=50, acceleration=config.default_end_acceleration)  # @crane:7d9b743546744709860e2bef
    await crane.moveTo(0.425811, -0.250038, 224.657895, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:d6d7179925c3615cdfdbe99e
    await crane.rotateRoundOffPivot(90, angular_speed_deg=config.default_end_motor_speed_off_pivot)  # @crane:ebeb546fff47b728e293a030
    await crane.moveTo(0.273904, -0.165517, 90, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:8b3a9e317e0290ad2dd280d6
    await crane.moveExtendonTo(0.274125, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:c8d8bbb61893e51e4d66f570
    
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
