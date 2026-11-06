from brian import *
from brian.sensors.EV3 import ColorSensorEV3
import brick

default_yaw_speed: float = 40
default_extension_speed: float = 0.23
default_end_motor_speed: float = 100
default_yaw_acceleration: float = 500.0
default_extension_acceleration: float = 100.0
default_end_acceleration: float = 1000.0
default_synced_move_time: float = 2.0
default_end_motor_speed_off_pivot: float = 100

brick_orientations: dict[int, ColorSensorEV3.Color] = {
    1: (ColorSensorEV3.Color.YELLOW, ColorSensorEV3.Color.GREEN),
    2: (ColorSensorEV3.Color.GREEN, ColorSensorEV3.Color.RED)
}