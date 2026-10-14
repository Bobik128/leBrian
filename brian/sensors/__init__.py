from brian.sensors.SensorPort import *
from brian.sensors.BrianBrianComm import *
from brian.sensors.Sensor import *
from brian.sensors import sensor_port_probe
import brian.sensors.NXT as NXT
import brian.sensors.EV3 as EV3
import brian.sensors.HiTec as HiTec


class SensorException(Exception):
    """Default sensor Exception"""


class SensorAlreadyClosedError(SensorException):
    """Thrown when trying to access closed Sensor"""


class SensorNotReadyError(SensorException):
    """Thrown when trying to read values from a sensor that is not ready.

    This is the base class for sensor readiness exceptions. Catching this
    exception will also catch SensorIncompatibleTypeError and SensorNotConnectedError.
    """


class SensorIncompatibleTypeError(SensorNotReadyError):
    """Thrown when a sensor of a different type than expected is connected.

    Catching this exception will also catch SensorNotConnectedError.
    """


class SensorNotConnectedError(SensorIncompatibleTypeError):
    """Thrown when no sensor is connected to the specified port."""


class SensorPortAlreadyInUseError(SensorException):
    """Thrown when trying to register sensor or sensor probe with autodetect to already used port"""


def get_wait_until_timeout_ms() -> int:
    """Get the current timeout value for waitUntilReady operations in milliseconds"""
    ...


def set_wait_until_timeout_ms(timeout_ms: int) -> None:
    """Set the default timeout value for waitUntilReady operations in milliseconds. (Wait until ready is invoked in all sensor read operations and constructor calls)

    Args:
        timeout_ms: Timeout in milliseconds for internal wait-until-ready calls.
            - positive: wait up to that many milliseconds
            - 0 or negative: return/raise immediately without waiting
    """
    ...
