from brian import *
import asyncio
import time
import sys

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

    gyro.set_mode(gyro.Mode.ANGLE_AND_SPEED)

    start = time.ticks_ms()
    while not gyro.is_ready():
        if time.ticks_diff(time.ticks_ms(), start) > 10000:
            raise RuntimeError("Gyro readiness timed out")
        await asyncio.sleep(0.02)

    gyro.set_zero_point()

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
        await asyncio.sleep(0.01)

def isPressed():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
    return knob.just_pressed

async def waitForPressWithGyroCheck():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(gyroAngle()) > 5:
            print("GYRO DRIFT")
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break
        await asyncio.sleep(0.01)

async def waitForAnyPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        if abs(gyroAngle()) > 5:
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
        await asyncio.sleep(0.01)

def gyroAngleAndSpeed():
    if gyro is None or not gyro.is_ready():
        raise RuntimeError("Gyro not ready")
    return gyro.angle_and_speed()

def gyroAngle():
    return gyroAngleAndSpeed()[0]