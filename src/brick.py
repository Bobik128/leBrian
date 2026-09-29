from brian import *
import asyncio
import time
import sys

gyro: sensors.EV3.GyroSensorEV3
color: sensors.EV3.ColorSensorEV3
sonar: sensors.EV3.UltrasonicSensorEV3

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


async def initSonic(port: sensors.SensorPort):
    global sonar
    sonar = sensors.EV3.UltrasonicSensorEV3(port)

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def waitForPressWithGyroCheck():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(gyro.angle()) > 5:
            print("GYRO DRIFT")
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def waitForAnyPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(gyro.angle()) > 5:
            print("GYRO DRIFT")
        buttons: uicontrol.UiEventsListener.ButtonsEvent = listener.buttons_event_since_last()
        if buttons.top_right.just_pressed:
            return 1
        elif buttons.top_left.just_pressed:
            return 2
        elif buttons.bottom_right.just_pressed:
            return 3
        elif buttons.bottom_left.just_pressed:
            return 4

def gyroAngle():
    if gyro is None:
        raise Exception("Gyro not initialized")
    return gyro.angle()