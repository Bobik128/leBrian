from brian import *
import asyncio

gyro: sensors.EV3.GyroSensorEV3
color: sensors.EV3.ColorSensorEV3

def resetGyro():
    gyro.set_zero_point()

async def initGyro(port: sensors.SensorPort):
    global gyro
    gyro = sensors.EV3.GyroSensorEV3(port)
    while not gyro.is_ready():
        asyncio.sleep(0.1)
    resetGyro()

async def initColor(port: sensors.SensorPort):
    global color
    color = sensors.EV3.ColorSensorEV3(port)
    while not color.is_ready():
        asyncio.sleep(0.1)