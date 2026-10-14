from typing import Optional
from brian.motors.MotorPort import MotorPort
from brian.motors.EndReason import EndReason
from brian.motors.motor_types import MotorType
from enum import Enum


class MotorWaitOptimismLevel(Enum):
    """
    Optimism level for wait_until_ready() calls.

    - WAIT_UNTIL_CORRECT_TYPE: Wait only until the motor type is confirmed correct.
      Use this immediately after motor construction to quickly verify the motor is connected
      and is of the expected type, without waiting for full initialization.

    - WAIT_UNTIL_FULLY_READY: Wait until the motor is fully initialized and ready for normal use.
      You may use this before commanding the motor to ensure it is fully ready for normal use.
    """
    WAIT_UNTIL_CORRECT_TYPE = 0
    """Wait only until the motor type is confirmed correct"""
    WAIT_UNTIL_FULLY_READY = 1
    """Wait until the motor is fully initialized and ready for normal use"""

class Motor:
    """
    A class to manage and control motor operations.
    """

    @property
    def motor_type(self) -> 'MotorType':
        """
        Check what motor type was this object initialized with.

        :return: Properties and default settings of the connected motor type.
        """
        ...

    def __init__(self, port: MotorPort):
        """
        Tries to autodetect a motor, connected to the given port and initialize a new motor class.
        :raises MotorInitializationFailedError: If autodetect fails (motor is not connected, unknown type of the connected motor).

        :param port: Motor port to use.

        :raises MotorPortAlreadyInUse: When trying to create new Motor on a port that is already in use.
        """
        ...

    def __del__(self):
        """
        Release the motor port for other uses.
        """
        ...

    def close_motor(self):
        """
        Release the motor port for other uses.
        """
        ...

    def is_connected(self) -> bool:
        """
        Check if something is connected to the port.

        :return: True if a non-empty port was detected; False otherwise.
        """
        ...

    def is_ready(self) -> bool:
        """
        Check if the motor is connected, of the correct type, and ready to be controlled.

        Ready-state indicates that the attempt to control the motor will succeed.

        When the motor is not connected, this function returns False.
        When the wrong motor type is connected, this function raises an exception.

        :return: True if the motor meets the readiness criteria, False if not connected.

        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        """
        ...

    def wait_until_ready(self, timeout_ms: Optional[int] = None, optimism_level: Optional[MotorWaitOptimismLevel] = None) -> bool:
        """
        Waits until the motor is ready. This function is blocking.

        :param timeout_ms: Milliseconds to wait for readiness.
            - If None, there is no per-call wall-clock limit (wait until ready).
            - If 0 or negative, return/raise immediately without waiting.
            - If positive, wait at most that many milliseconds.
        :param optimism_level: Level of optimism to use when checking readiness.
            - WAIT_UNTIL_CORRECT_TYPE: More optimistic - returns as soon as correct type is detected.
            - WAIT_UNTIL_FULLY_READY: Less optimistic - waits until motor is fully ready (default).

        :return success:
            - True: The motor is ready at the specified optimism level.

        :raises brian.motors.MotorNotConnectedError: If no motor is connected to the port.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready for other reasons.
        """
        ...

    def current_angle(self) -> int:
        """
        Query the current motor angle.

        This function will wait for the motor to be ready before returning.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :return: Motor axle angle in degrees.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def reset_angle(self, new_value: int = 0) -> None:
        """
        Set the accumulated angle to the provided position.

        Assuming that the motor will not move, current_angle() will
        start returning the value in newValue.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param new_value: New motor position in degrees.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def current_speed(self) -> int:
        """
        Query the current motor rotational speed.

        This function will wait for the motor to be ready before returning.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :return: Motor axle speed in degrees/second.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def current_torque(self) -> int:
        """
        Query the current estimated motor torque.

        This function will wait for the motor to be ready before returning.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :return: Motor torque in milli-newton-meters.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def is_stalled(self) -> bool:
        """
        Check if the motor is currently stalled.

        This function will wait for the motor to be ready before checking.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :return: True if the motor is exceeding some limit, False otherwise.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def coast(self) -> None:
        """
        Let the motor spin freely.

        This will float the motor windings.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def brake(self) -> None:
        """
        Passively brake the motor.

        This will short the motor windings.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def hold(self) -> None:
        """
        Actively brake the motor at the current position.

        This will actively control the motor to stay at the current position.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def run_unregulated(self, fraction: float) -> None:
        """
        Run the motor at a given fraction of the maximum available voltage.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param fraction: Value between -1.0 and +1.0 that determines the duty cycle.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def run_at_voltage(self, volts: float) -> None:
        """
        Run the motor at the given voltage.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param volts: Desired voltage on the motors, in volts. Useful range is
                      -battery voltage to +battery voltage (this is cca. -8V to +8V).
                      The maximum range accepted by this function is -12V to +12V.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def run_at_speed(self, deg_per_sec: int) -> None:
        """
        Run the motor at a constant speed.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param deg_per_sec: Desired rotational speed, in degrees per second.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def rotate(self, angle: int, speed: int, timeout_ms: Optional[int] = None) -> 'EndReason':
        """
        Turn the motor to a new position, relative to the current position.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param angle: Angle to rotate by, in degrees.
        :param speed: Speed to use for the maneuver, in degrees per second.
                      If the provided speed is negative, absolute value is used.
        :param timeout_ms: How long to wait for the maneuver to complete, in milliseconds.
                        If None, wait until the move completes (no wall-clock cap).
                        If 0 or negative, return from the wait immediately (typically ``TIMED_OUT`` if still moving).
                        If the timeout expires, the motor is not stopped.
        :return: Whether the wait-for-end was successful or why it ended, if it ended early.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def rotate_to(self, position: int, speed: int, timeout_ms: Optional[int] = None) -> 'EndReason':
        """
        Turn the motor to a new position, relative to the zero position.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param position: Angle to rotate to, in degrees.
        :param speed: Speed to use for the maneuver, in degrees per second.
                      If the provided speed is negative, absolute value is used.
        :param timeout_ms: How long to wait for the maneuver to complete, in milliseconds.
                        If None, wait until the move completes (no wall-clock cap).
                        If 0 or negative, return from the wait immediately (typically ``TIMED_OUT`` if still moving).
                        If the timeout expires, the motor is not stopped.
        :return: Whether the wait-for-end was successful or why it ended, if it ended early.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def rotate_to_angle_without_speed_control(self, position: int) -> None:
        """
        Try to get as fast as possible to the specified position.

        This will ignore any speed and acceleration limits - you must provide these
        yourself by periodically calling this function with new positions.

        This function will wait for the motor to be ready before executing.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param position: Angle to rotate to relative to the zero position, in degrees.
        :raises brian.motors.MotorPortAlreadyInUse: If the port is currently controlled by Pilot.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def is_done(self) -> bool:
        """
        Check whether the last invoked position command has completed.

        This function will wait for the motor to be ready before checking.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :return: True if the motor has reached the goal.
                 True if the maneuver had to be interrupted (e.g., motor was unplugged).
                 False if the motor is still moving.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def wait_until_done(self, timeout_ms: Optional[int] = None) -> 'EndReason':
        """
        Wait for the motor to complete the last position command.

        This function will wait for the motor to be ready before waiting for movement.
        The wait timeout is controlled by set_wait_until_timeout_ms().

        :param timeout_ms: How long to wait for the maneuver to complete, in milliseconds.
                        If None, wait until the move completes (no wall-clock cap).
                        If 0 or negative, return from the wait immediately (typically ``TIMED_OUT`` if still moving).
                        If the timeout expires, the motor is not stopped.
        :return: Whether the wait-for-end was successful or why it ended, if it ended early.
        :raises brian.motors.MotorNotConnectedError: If no motor is connected.
        :raises brian.motors.MotorIncompatibleTypeError: If wrong motor type is connected.
        :raises brian.motors.MotorIsNotReadyError: If motor is not ready after timeout.
        """
        ...

    def get_acceleration_limit(self) -> int:
        """
        Query the acceleration limit.

        This acceleration is used for ramping speed in position and speed commands.

        :return: Maximum acceleration in degrees per second squared.
        """
        ...

    def set_acceleration_limit(self, deg_per_sec_sq: int) -> None:
        """
        Set the acceleration limit.

        This acceleration is used for ramping speed in position and speed commands.

        :param deg_per_sec_sq: Maximum acceleration in degrees per second squared.
                               Use brian.motors.UNLIMITED_ACCELERATION to disable speed ramping.
        """
        ...

    def get_torque_limit(self) -> int:
        """
        Query the torque limit.

        :return: Maximum torque that will be applied to the motor axle, in milli-newton-meters.
        """
        ...

    def set_torque_limit(self, mNm: int) -> None:
        """
        Set the torque limit.

        :param mNm: Maximum torque that will be applied to the motor axle, in milli-newton-meters.
                    Use brian.motors.UNLIMITED_TORQUE to remove the limit.
        """
        ...

    def get_battery_power_limit(self) -> int:
        """
        Query the power draw limit.

        :return: Battery power consumption limit, in milli-watts.
        """
        ...

    def set_battery_power_limit(self, mW: int) -> None:
        """
        Set the power draw limit.

        :param mW: Maximum power allowed to draw from the battery, in milli-watts.
                   Use brian.motors.UNLIMITED_POWER to remove the limit.
        """
        ...
