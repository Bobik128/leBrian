from enum import Enum
from brian.sensors.Sensor import Sensor
from brian.sensors.SensorPort import SensorPort


class ColorSensorEV3(Sensor):
    """
    Class for interacting with EV3 color sensor.

    Sensor is automatically registered in the constructor of the base class
    and un-registered in its destructor. It can also be unregistered with the ColorSensorEV3.close_sensor() function.

    There can be at most one instance at any given time, of any sensor class per port in the entire program.
    """
    def __init__(self, port: SensorPort):
        """
        Initialize a EV3 color sensor at the given port.
        :param port: Sensor port to which the sensor is attached.
        """
        ...


    class Mode(Enum):
        """Sensor modes for set_mode()."""
        REFLECT = 0
        """Reflected light intensity, used by reflected_value()"""
        AMBIENT = 1
        """Ambient light intensity, used by ambient_value()"""
        COLOR_DETECT = 2
        """Detected color, used by detected_color()"""
        REFLECT_RAW = 3
        """Raw reflected light intensity, used by reflected_value_raw()"""
        RGB_RAW = 4
        """Raw RGB values, used by rgb_values_raw()"""

    class RawRGB:
        """
        Class used to hold rgb values from ColorSensorEV3.rgb_values_raw() measurement.
        Each color channel holds values between 0-1023.
        Attributes can be accessed either directly or using an index (RawRGB[0] = RawRGB.red)
        """
        red: int
        """Red component (0-1023)"""
        green: int
        """Green component (0-1023)"""
        blue: int
        """Blue component (0-1023)"""

        def __init__(self, red: int, green: int, blue: int):
            """
            :param red: red color component [0-1023].
            :param green: green color component [0-1023].
            :param blue: blue color component [0-1023].
            """

        def __sub__(self, other):
            """
            Element wise subscription

            If resulting element would be smaller than 0, it is set to 0
            """
            ...

        def __getitem__(self, item):
            """"""
            ...

    class Color(Enum):
        """
        Constants for `ColorSensor.detected_color(self)` function.

        ``str(color)`` (and therefore ``print(color)``) gives the English name of the color, e.g. "Red".
        """
        NO_COLOR = 0
        """No color detected"""
        BLACK = 1
        """Black"""
        BLUE = 2
        """Blue"""
        GREEN = 3
        """Green"""
        YELLOW = 4
        """Yellow"""
        RED = 5
        """Red"""
        WHITE = 6
        """White"""
        BROWN = 7
        """Brown"""

    def set_mode(self, mode: Mode) -> None:
        """
        This function sets the sensor to the desired mode. While it’s not mandatory, it is recommended to call this
        function before accessing values from the sensor in a specific mode to prevent SensorNotReady exceptions.

        :param mode: desired mode to be set
        """
    def reflected_value(self) -> int:
        """
        Sets the sensor mode to `REFLECT` and returns the last value.

        :return: reflectivity in % (0-100).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>REFLECT mode:</b>
        Measure surface reflectivity for red light. The values are calibrated
        within the sensor itself. Returns the values in percent, in range 0-100.
        The measurement is corrected for the ambient light change.
        """
        ...

    def reflected_value_raw(self) -> int:
        """
        Sets the sensor mode to`REFLECT_RAW` and returns the last value.

        :return: reflectivity raw values (0-1023).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>REFLECT_RAW mode:</b>
        Measure surface reflectivity for red light. The values
        are uncalibrated. Code using this function must thus perform
        range scaling/shifting manually. Measuring in this mode should
        provide more resolution over `REFLECT` mode. Returns values in range 0-1023.
        The measurement is corrected for the ambient light change.
        """
        ...

    def ambient_value(self) -> int:
        """
        Sets the sensor mode to `AMBIENT` and returns the last value.

        :return: ambient in % (0-100).

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>AMBIENT mode:</b>
        Measure ambient light intensity. The values are calibrated
        within the sensor itself. Returns the values in percent, in range 0-100.
        """
        ...


    def detected_color(self) -> 'Color':
        """
        Sets the sensor mode to `COLOR_DETECT` and returns the last value.

        :return: color constants corresponding to Color.[COLOR].

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>COLOR_DETECT mode:</b>
        Measure and discriminate the color. The discrimination is provided by the sensor itself.
        If this works poorly for your use case, you can use `RGB_RAW` instead.
        """
        ...

    def rgb_values_raw(self) -> RawRGB:
        """
        Sets the sensor mode to `RGB_RAW` and return the last value.

        :return: RGB raw values (0-1023 each channel).
        You can access them with RGB.red, RGB.green and RGB.blue, or by using subscription (RGB[0], RGB[1], ...)

        :raises brian.sensors.SensorNotReadyError: If the sensor is not ready.

        <b>RGB_RAW mode:</b>
        Measure surface reflectivity for red, green and blue light. The values
        are uncalibrated. Code using this function must thus perform
        range scaling/shifting manually.
        The measurement is corrected for the ambient light change.
        rgb_values_raw
        """
        ...
