from brian import *
import asyncio
import time
import sys

from brian.buttons import UiEventsListener

gyro: sensors.EV3.GyroSensorEV3
color: sensors.EV3.ColorSensorEV3
sonar: sensors.EV3.UltrasonicSensorEV3

def resetGyro():
    gyro.set_zero_point()

gyro = None

async def initGyro(port):
    global gyro
    gyro = sensors.EV3.GyroSensorEV3(port)

    await asyncio.sleep(1.0)
    gyro.reboot()
    await asyncio.sleep(1.0)

    gyro.set_mode(gyro.Mode.ANGLE)

    start = time.ticks_ms()
    while not gyro.is_ready():
        if time.ticks_diff(time.ticks_ms(), start) > 10000:
            raise RuntimeError("Gyro readiness timed out")
        await asyncio.sleep(0.02)

    gyro.set_zero_point()

async def initColor(port: sensors.SensorPort):
    global color
    color = sensors.EV3.ColorSensorEV3(port)
    color.set_mode(color.Mode.COLOR_DETECT)
    while not color.is_ready():
        asyncio.sleep(0.1)

async def getColor():
    global color
    if color is None:
        raise RuntimeError("Color sensor not initialized")
    return color.detected_color()

async def initSonic(port: sensors.SensorPort):
    global sonar
    sonar = sensors.EV3.UltrasonicSensorEV3(port)

async def waitForPress():
    listener: UiEventsListener = UiEventsListener()
    while True:
        knob: UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break
        await asyncio.sleep(0.01)

def isPressed():
    listener: UiEventsListener = UiEventsListener()
    knob: UiEventsListener.KnobEvent = listener.knob_event_since_last()
    return knob.just_pressed

async def waitForPressWithGyroCheck():
    listener: UiEventsListener = UiEventsListener()
    while True:
        if abs(gyroAngle()) > 5:
            print("GYRO DRIFT")
        knob: UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break
        await asyncio.sleep(0.01)

async def waitForAnyPress():
    listener: UiEventsListener = UiEventsListener()
    while True:
        if abs(gyroAngle()) > 5:
            print("GYRO DRIFT")
        buttons: UiEventsListener.ButtonsEvent = listener.buttons_event_since_last()
        if buttons.top_right.just_pressed:
            return 1
        elif buttons.top_left.just_pressed:
            return 2
        elif buttons.bottom_right.just_pressed:
            return 3
        elif buttons.bottom_left.just_pressed:
            return 4
        await asyncio.sleep(0.01)


def gyroAngle():
    return gyro.angle()