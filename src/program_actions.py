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
    await crane.moveTo(0.653836, -0.474913, 0, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:abefd9ab22b26730240932d1
    await crane.moveTo(0.834304, -0.527698, -17.50974, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:f631dad89605d078b4dfab17
    
    print("Press to start")
    await brick.waitForPressWithGyroCheck()
    print("Program started")

    await crane.moveYawAndEnd(-23.380305, 16.910352, yaw_speed=15, end_speed=70, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:bc108c4c490cbc035a0b5ba8
    await crane.moveExtendonTo(0.758847, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:0cd6dfb4b3377bb69f0dd7ce
    await crane.moveExtendonAndEnd(0.511943, 157.47249, extendon_speed=0.21, end_speed=120)  # @crane:96ef24109c93cd6d20885e88
    await crane.moveYawAndEnd(-95.875004, 12.493666, yaw_speed=config.default_yaw_speed, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:c4664a5116d0ec4084cbcc8d
    await crane.moveExtendonAndEnd(0.297354, 0.180831, extendon_speed=0.3, end_speed=60)  # @crane:2004ffa5211aac9442b1c37b

    await crane.moveExtendonTo(0.574963, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:c7827661e9f963ece18d50ff
    await crane.moveYawAndEnd(-88.917844, 90.13949, yaw_speed=30, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:62409dfba4bcb6fd9220d663
    await crane.moveExtendonTo(0.444219, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:b22d4d1672927d161edde1c3
    await crane.moveTo(0.072021, -0.4284, 88.970634, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:88e692fb71803ef533ec4aea
    await crane.moveTo(0.102968, -0.337466, 100.315445, yaw_speed=28, extendon_speed=0.18, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:1d527684b10c3d9077a9af77
    await crane.moveYawAndEnd(-78.48124, 62.930115, yaw_speed=config.default_yaw_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration, timewait=0)  # @crane:0b74b51cb5cae95beb5ecc11


    await crane.moveYawTo(-86.170912, speed=config.default_yaw_speed, acceleration=config.default_yaw_acceleration, timewait = 0)  # @crane:9a0ec78214eea83fd8e8ddbc
    # await crane.moveTo(0.031531, -0.452331, 67.070239, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:352ebc6a72aa17008a6c2e5e

    # await crane.moveYawAndEnd(24.77681, -5.23506, yaw_speed=50, end_speed=150, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:8cf17ba29944bfaa75c6732f
    # await crane.moveTo(0.838428, 0.323232, -4.248281, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:f4cf61c86eb96bbaa208338a
    # await crane.moveTo(0.928641, 0.32974, 9.061195, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:42fce226cd7f0feb515ba338

    # await crane.moveYawAndEnd(28.305016, 32.850034, yaw_speed=25, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:cdd64cbe7463a02bae6e4588
    # await crane.moveExtendonTo(0.736513, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:bb646ccf83d737015e1d2a84
    # await crane.moveExtendonAndEnd(0.674476, 107.567892, extendon_speed=0.24, end_speed=120)  # @crane:cfab29724e92eb9c06357e7d
    # await crane.moveTo(0.467794, 0.004603, 111.820551, yaw_speed=30, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:fb984b611060e0bb2ce736cd
    # await helper.checkColor(0.268562, 1)  # @crane:5d729131aa9e578493a55a5f
    # await crane.moveTo(0.431234, -0.089646, 110.921019, yaw_speed=20, extendon_speed=config.default_extension_speed, end_speed=30, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:0b55ad50394faaa804d9bd27
    # await crane.moveYawTo(-0.780572, speed=config.default_yaw_speed, acceleration=config.default_yaw_acceleration)  # @crane:d0b73b7639324de3bcb6a65b

    # await crane.moveTo(0.401594, 0.079588, 161.648532, yaw_speed=30, extendon_speed=0.1, end_speed=30, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:58d1d849cd1b465281972f5a


    # await crane.moveTo(0.402192, 0.071654, 200.284039, yaw_speed=20, extendon_speed=0.12, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:74d98fbf03f4d820799bb9c4
    # await crane.moveEndTo(148.523643, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:b5acb38bcb829f79f5bbbf5f


    # await crane.moveTo(0.501979, 0.022527, 130.463166, yaw_speed=40, extendon_speed=0.25, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:7b55254aaf5bbee1a68ab1f3
    # await crane.moveTo(0.679321, -0.008533, -3.862466, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:234c864b02f8f35feb10562d
    # await crane.moveTo(0.907836, 0.023608, 4.358566, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:dbc6f41a0891974a3f06e4a3

    # await crane.moveYawAndEnd(9.346586, 23.754063, yaw_speed=config.default_yaw_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:11e0bbc880c6c6d5f6cbaaef
    # await crane.moveExtendonAndEnd(0.516574, 132.048774, extendon_speed=0.3, end_speed=90)  # @crane:f4d87330cf53bc434a7f2c2b
    # await crane.moveYawTo(-12.985551, speed=config.default_yaw_speed, acceleration=config.default_yaw_acceleration)  # @crane:85175d27b58d0506d2c6ccdd
    # await helper.checkColor(0.268025, 2)  # @crane:955d7522dbfba04333ad7497
    # await crane.moveTo(0.431938, -0.219325, 147.797352, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:c37063d6b9de4eb6963602b4
    # await crane.moveTo(0.465565, -0.119733, 167.448219, yaw_speed=25, extendon_speed=config.default_extension_speed, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration, timewait=0)  # @crane:587755c7452779dfcdb7bca4
    # await crane.moveTo(0.407003, 0.003807, 196.520607, yaw_speed=20, extendon_speed=0.08, end_speed=60, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration, timewait = 0)  # @crane:81bfdbbc9eca1fbf38c9071e
    # await crane.moveEndTo(147.594789, speed=70, acceleration=config.default_end_acceleration)  # @crane:8915deaf1530a6b894c68a7a


    # await helper.checkColor(0.33, 1)  # @crane:128e39bbbb94f3385ceb3ffd
    # await crane.moveExtendonTo(0.49981, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:49bd9ca2c16da701f8ae5f1c
    # await crane.moveEndTo(225.779703, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:d32982caf2290db31caf31fd
    # await crane.moveExtendonTo(0.398474, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:74d061d255dd467bda41c8e1
    # await crane.moveEndTo(180.951365, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:48018236528f23c3fc0607da
    # await crane.moveExtendonTo(0.32987, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:66c98e8151a2bed076fa0c1c
    # await crane.moveEndTo(127.926272, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:33ef2184e8231227ed69be72
    # await crane.moveYawTo(10.135271, speed=config.default_yaw_speed, acceleration=config.default_yaw_acceleration)  # @crane:4aa08ba8e6acf8f8c500947a
    # await crane.moveTo(0.361161, 0.144375, 122.019245, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:7e8b7eb6cee2a0d57dfe6331
    # await crane.rotateRoundOffPivot(271.838332, angular_speed_deg=config.default_end_motor_speed_off_pivot)  # @crane:8d5e550bc592f18acd4fdeae
    # await crane.moveTo(0.338261, 0.256789, 263.708218, yaw_speed=30, extendon_speed=0.12, end_speed=70, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:8fdbcd47978ce5ebceb0ee6a
    # await crane.moveExtendonTo(0.350315, speed=0.1, acceleration=config.default_extension_acceleration)  # @crane:e5679c5113d06e63280f6e70
    # await crane.moveExtendonTo(0.44785, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:3a016d73c8fd519b803796be
    # await crane.moveTo(0.299425, 0.412359, 106.306781, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=200, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:3ea3a9d0bcc3fae3f82a8e25
    # await crane.moveTo(0.262091, 0.56239, 106.306781, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:aee5946e847c707907990a16
    # await crane.moveYawTo(81.011145, speed=config.default_yaw_speed, acceleration=config.default_yaw_acceleration)  # @crane:d963e7cd77693eb77ff82516
    # await crane.moveEndTo(232.114291, speed=70, acceleration=config.default_end_acceleration)  # @crane:d04f71b7edd15654b84cbadd
    # await crane.moveTo(0.480375, -0.161722, 226.779607, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:824affa86f497f1e0e7fa2aa
    # await crane.rotateRoundOffPivot(90.310889, angular_speed_deg=config.default_end_motor_speed_off_pivot, radius=0.35)  # @crane:237f76932d44f4b4c4f40bc4
    # await crane.moveTo(0.383472, -0.270651, 96.172103, yaw_speed=config.default_yaw_speed, extendon_speed=80, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:b50dbfcdc856b7d91162f7af
    # await crane.moveExtendonTo(0.223151, speed=0.15, acceleration=config.default_extension_acceleration)  # @crane:2287e4f4360b2ceda86c5b18
    # await crane.moveExtendonTo(0.382446, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:9e95e6b39bd7a6871c610f49
    # await crane.moveTo(0.798739, 0.049597, 1.908576, yaw_speed=config.default_yaw_speed, extendon_speed=config.default_extension_speed, end_speed=200, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:82fbcf6c4758732a2199813c
    # await crane.moveExtendonAndEnd(0.898539, 20.271776, extendon_speed=0.3, end_speed=90)  # @crane:7619bac057191755bc403361
    # await crane.moveYawAndEnd(13.672682, 35.524038, yaw_speed=config.default_yaw_speed, end_speed=200, yaw_acceleration=config.default_yaw_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:166b2e46df6d6ccb214cf708
    # await crane.moveEndTo(135.88832, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:0fa532e08d3a09e0dca9d5e8
    # await crane.moveExtendonTo(0.662554, speed=config.default_extension_speed, acceleration=config.default_extension_acceleration)  # @crane:7871a13c315a8154825fde49
    # await crane.moveTo(0.034054, 0.45775, 126.033551, yaw_speed=30, extendon_speed=0.3, end_speed=config.default_end_motor_speed, yaw_acceleration=config.default_yaw_acceleration, extendon_acceleration=config.default_extension_acceleration, end_acceleration=config.default_end_acceleration)  # @crane:2ac1938fbfc69801f419b8e2
    # await crane.moveEndTo(192.099215, speed=config.default_end_motor_speed, acceleration=config.default_end_acceleration)  # @crane:4cb0c3875c695f72d56db4c4
    # await helper.checkColor(0.30, 5)  # @crane:a2d15ad9bfd38fe736ed0e67

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
