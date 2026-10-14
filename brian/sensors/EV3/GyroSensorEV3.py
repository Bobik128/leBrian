from enum import Enum
from typing import Tuple
from brian.sensors.Sensor import Sensor
from brian.sensors.SensorPort import SensorPort


class GyroSensorEV3(Sensor):
    """
    Class for interacting with EV3 gyro sensor.

    Sensor is automatically registered in the constructor of the base class
    and un-registered in its destructor. It can also be unregistered with the GyroSensorEV3.close_sensor() function.

    There can be at most one instance at any given time, of any sensor class per port in the entire program.
    """
    def __init__(self, port: SensorPort):
        """
        Initialize a EV3 gyro sensor at the given port.
        :param port: Sensor port to which the sensor is attached.
        """
        ...

    from enum import Enum

    class Mode(Enum):
        """Sensor modes for set_mode()."""
        ANGLE = 0
        """Angle, used by angle()"""
        SPEED = 1
        """Angular speed, used by speed()"""
        SPEED_COARSE = 2
        """Coarse angular speed with a wider range, used by speed_coarse()"""
        ANGLE_AND_SPEED = 3
        """Angle and angular speed together, used by angle_and_speed()"""
        TILT_SPEED = 5
        """Tilt angular speed, used by tilt_speed()"""
        TILT_ANGLE = 6
        """Tilt angle, used by tilt_angle()"""

    def set_mode(self, mode: Mode) -> None:
        """
        This function sets the sensor to the desired mode. While it’s not mandatory, it is recommended to call this
        function before accessing values from the sensor in a specific mode to prevent SensorNotReady exceptions.

        :param mode: desired mode to be set
        """

    def angle(self) -> int:
        """
        Sets the sensor mode to `ANGLE` and returns the last value.

        :return: angle (int) in degrees (-32768 to 32768).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>ANGLE mode:</b>
        Measures the tilt angle and returns the value in degrees in range -32768 to 32767.

        Clockwise is positive when looking at the side of the sensor with the arrows.

        If you spin around too many times in `ANGLE`,`ANGLE_AND_SPEED` or `TILT_ANGLE` mode,
        it will get stuck at 32767 or overflow through -32768 depending on when the sensor was manufactured.
        """
        ...

    def speed(self) -> int:
        """
        Sets the sensor mode to `SPEED` and returns the last value.

        :return: angular speed in degrees/s (-500 to 500).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>SPEED mode:</b>
        Measures angular speed and returns the value in degrees/second in range -500 to 500.

        Clockwise is positive when looking at the side of the sensor with the arrows.
        """
        ...

    def tilt_speed(self) -> int:
        """
        Sets the sensor mode to `Modes::TILT_SPEED` and returns the last value.

        :return: angular speed in degrees/s (-500 to 500).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>TILT_SPEED mode:</b>
        Measures angular speed around a second axis and returns the value in degrees/second in range -500 to 500
        Clockwise is positive when looking at the side of the sensor opposite the cable jack.

        """
        ...

    def is_tilt_available(self) -> bool:
        """
        Checks whether the gyro sensor is compatible with second axis measurements (TILT_ANGLE and TILT_SPEED).

        :return: True if tilt modes are available, False otherwise.

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.
        """
        ...

    def tilt_angle(self) -> int:
        """
        Sets the sensor mode to `TILT_ANGLE` and returns the last value.

        :return: angle (int) in degrees (-32768 to 32768).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>TILT_ANGLE mode:</b>
        Measures the tilt angle around a second axis and returns the value in degrees in range -32768 to 32767.

        This mode is not present in older sensors (date code ending with 2 or 3).
        Clockwise is positive when looking at the side of the sensor opposite the cable jack.

        If you spin around too many times in "ANGLE", "ANGLE_AND_SPEED" or "TILT_ANGLE" mode,
        it will get stuck at 32767 or overflow through -32768 depending on when the sensor was manufactured.
        """
        ...

    def speed_coarse(self) -> int:
        """
        Sets the sensor mode to `SPEED_COARSE` and returns the last value.

        :return: angular speed in degrees/s (-1464 to 1535).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>SPEED_COARSE mode:</b>
        Measures angular speed and returns the value in degrees/second in range -1464 to 1535.
        Lower resolution, but wider range than the "SPEED" mode.

        Clockwise is positive when looking at the side of the sensor with the arrows.
        """
        ...

    def angle_and_speed(self) -> Tuple[int, int]:
        """
        Sets the sensor mode to `ANGLE_AND_SPEED` and returns the last value.

        :return: Tuple consisting of two integers:
                - The first integer represents the angle (deg) measurement.
                - The second integer represents the speed (deg/s) measurement.

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>ANGLE_AND_SPEED mode:</b>
        Measures the tilt angle and angular speed and returns the value in degrees in range -32768 to 32767 for angle and -500 to 500 for speed.

        Clockwise is positive when looking at the side of the sensor with the arrows.
        If you spin around too many times in "ANGLE", "ANGLE_AND_SPEED" or "TILT_ANGLE" mode,
        it will get stuck at 32767 or overflow through -32768 depending on when the sensor was manufactured.
        """
        ...

    def set_zero_point(self) -> None:
        """
        Adjusts the angle readings to create new zero point angle.
        Adjusts angle only in "ANGLE", "ANGLE_AND_SPEED" and "TILT_ANGLE" modes.
        Does not fix drift (for drift fixing, reboot the sensor using the reboot() function).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.
        """
        ...

    def reboot(self) -> None:
        """
        Reboots the sensor to force recalibration.

        During the recalibration, keep the sensor steady to minimize drifting.

        <b>Reboot</b>
        Turn off power to the port and turn it back on. This will forcibly reboot the sensor.

        The powered-down state lasts about 100ms. In case of some (mostly digital) sensors, there can be
        some additional time (~1s or more) to boot up and process connection handshake with Brian.
        """
        ...
