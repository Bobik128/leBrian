from brian import *
from brian.sensors.EV3 import ColorSensorEV3
import brick

default_yaw_speed: float = 40
default_extension_speed: float = 0.23
default_end_motor_speed: float = 100
default_yaw_acceleration: float = 500.0
default_extension_acceleration: float = 100.0
default_end_acceleration: float = 1000.0

brick_orientations: dict[int, ColorSensorEV3.Color] = {
    1: ColorSensorEV3.Color.YELLOW,
    2: ColorSensorEV3.Color.GREEN,
    3: ColorSensorEV3.Color.BLUE,
    4: ColorSensorEV3.Color.RED,
    5: ColorSensorEV3.Color.GREEN,
    6: ColorSensorEV3.Color.YELLOW,
    7: ColorSensorEV3.Color.YELLOW,
    8: ColorSensorEV3.Color.GREEN,
    9: ColorSensorEV3.Color.RED,
    10: ColorSensorEV3.Color.YELLOW,
    11: ColorSensorEV3.Color.BLUE,
    12: ColorSensorEV3.Color.YELLOW,
    13: ColorSensorEV3.Color.RED,
    14: ColorSensorEV3.Color.RED,
    15: ColorSensorEV3.Color.RED,
    16: ColorSensorEV3.Color.BLUE,
}