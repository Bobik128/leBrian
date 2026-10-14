from typing import Optional
from enum import Enum

from brian.sensors.SensorPort import SensorPort
from brian.sensors.sensor_port_probe import AutoDetect


class SensorWaitOptimismLevel(Enum):
    """
    Optimism level for wait_until_ready() calls.

    - WAIT_UNTIL_CORRECT_TYPE: Wait only until the sensor type is confirmed correct.
      Use this immediately after sensor construction to quickly verify the sensor is connected
      and is of the expected type, without waiting for full initialization.

    - WAIT_UNTIL_FULLY_READY: Wait until the sensor is fully initialized and ready for normal use.
      You may use this before reading sensor values to ensure all modes and data are properly initialized.
    """
    WAIT_UNTIL_CORRECT_TYPE = 0
    """Wait only until the sensor type is confirmed correct"""
    WAIT_UNTIL_FULLY_READY = 1
    """Wait until the sensor is fully initialized and ready for normal use"""


class Sensor:
    """
    Base Sensor class
    """

    def __init__(self, port: SensorPort, sensor_type: AutoDetect):
        """
        Initialize a sensor class at the given port.

        Note: The constructor does NOT wait for the sensor to be ready. After construction,
        you should call wait_until_ready() with the appropriate optimism level:

        Example usage::

            sensor = ColorSensorEV3(sensors.SensorPort.S1)
            # Quickly verify correct sensor type is connected (good after constructor)
            sensor.wait_until_ready(optimism_level=sensors.SensorWaitOptimismLevel.WAIT_UNTIL_CORRECT_TYPE)

        :param port: Sensor port to which the sensor is attached (sensors.SensorPort.S1-sensors.SensorPort.S4).
        :param sensor_type: Type of the sensor which is attached.

        sensor_port_probe.AutoDetect.ANALOG_P1 corresponds to LightSensorNXT and TouchSensorNXT
        sensor_port_probe.AutoDetect.ANALOG_P6 corresponds to TouchSensor
        sensor_port_probe.AutoDetect.PROTOCOL_UART_EV3 corresponds to ColorSensor, GyroSensor and UltrasonicSensor

        :raises SensorPortAlreadyInUseError: When trying to create new sensor on port that is already in use.
        """
        ...

    def __del__(self):
        """
        Deinitialize the sensor and free the port for other uses.
        """
        ...

    def close_sensor(self):
        """
        Deinitialize the sensor and free the port for other uses.
        """
        ...

    def is_connected(self) -> bool:
        """
        :return: True iff sensor is connected and not in the process of rebooting, False otherwise
        """
        ...

    def is_ready(self) -> bool:
        """
        Ready-state indicates that the attempt to read values will give valid results.

        Example reasons for invalid results:

        - Sensor is not connected (``is_connected`` returns False)
        - Sensor is rebooting or not initiated yet
        - Sensor is changing modes and the change is not finished yet
        - Connected sensor is incompatible with this handler (e.g. wrong type of sensor is connected)

        When the sensor is not connected, this function returns False.
        When the wrong sensor type is connected, this function raises an exception.

        :return: True if the sensor meets the readiness criteria, False if not connected.

        :raises brian.sensors.SensorIncompatibleTypeError: If wrong sensor type is connected.
        """
        ...

    def wait_until_ready(self, timeout_ms: Optional[int] = None, optimism_level: Optional[SensorWaitOptimismLevel] = WAIT_UNTIL_FULLY_READY) -> bool:
        """
        Waits until the sensor is ready. This function is blocking.

        When changing modes, the sensor enters a "not ready" state for a short period (until
        the mode change is propagated). Therefore, it is recommended to first set the correct
        mode using set_mode() before the calling this function. This only applies to sensors with modes.

        :param timeout_ms: Milliseconds to wait for readiness.
            - If None, there is no per-call wall-clock limit (wait until ready).
            - If 0 or negative, return/raise immediately without waiting.
            - If positive, wait at most that many milliseconds.

        :param optimism_level: Level of readiness to wait for.
            - SensorWaitOptimismLevel.WAIT_UNTIL_CORRECT_TYPE: Wait only until the sensor type is confirmed.
              Use this right after sensor construction to quickly verify the sensor is connected
              and of the expected type. This is faster but doesn't guarantee full initialization.
            - SensorWaitOptimismLevel.WAIT_UNTIL_FULLY_READY (default): Wait until sensor is fully ready
              for normal operation. Use this before reading sensor values. -> This is automatically called in all sensor read operations with default timeout values

        :return success:
            - True: The sensor is ready at the specified optimism level.

        :raises SensorNotConnectedException: When no sensor is connected.
        :raises SensorIncompatibleTypeException: When wrong sensor type is connected.
        :raises SensorNotReadyException: When sensor is not ready for other reasons.
        """
        ...

    def reboot(self) -> None:
        """
        Turn off power to the port and turn it back on. This will forcibly reboot the sensor.

        The powered-down state lasts about 100ms. In case of some (mostly digital) sensors, there can be
        some additional time (~1s or more) to boot up and process connection handshake with Brian.
        """
        ...
