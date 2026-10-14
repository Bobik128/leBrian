from typing import Optional
from brian.motors import Motor, EndReason, MotorWaitOptimismLevel


class Pilot:
    """
    Differential-drive pilot for controlling a robot with left and right wheels.

    Supports brake/hold/coast, forward/backward with optional distance,
    turn (small pivots), arc (large pivots), and travel (curved path).
    Movement methods wait for all controlled motors to become ready first (same timeout as
    ``brian.motors.Motor`` commands, via ``brian.motors.set_wait_until_timeout_ms``), then wait for
    completion by default and return ``EndReason``. ``timeout_ms`` semantics match
    ``wait_until_done()`` (``None`` = wait until done, ``0`` or negative = return from the wait immediately,
    often ``EndReason.TIMED_OUT`` if still moving). Unlimited path limits (``None`` / ``0`` / ±inf on
    distance or turn angle) also return immediately unless ``timeout_ms`` is set. Movement methods and
    ``wait_until_done()`` also share ``return_earlier_for_movement_chaining`` to return during slowdown
    (before full stop), so the next movement can be chained sooner.
    Speed and acceleration can be set once and used as defaults in movement commands.
    Odometry (distance and angle) is available with optional zeroing.
    """

    def __init__(
        self,
        left_motor: Motor,
        right_motor: Motor,
        # NOTE: Pilot (UI/type hints) shows ints; the underlying MicroPython binding still accepts floats.
        wheelbase_mm: int,
        wheel_diameter_mm: Optional[int] = None,
        gear_ratio: Optional[float] = None,
        helper_left_motor: Optional[Motor] = None,
        helper_right_motor: Optional[Motor] = None,
        left_motor_reversed: bool = False,
        right_motor_reversed: bool = False,
        helper_left_motor_reversed: bool = False,
        helper_right_motor_reversed: bool = False,
        *,
        wheel_circumference_mm: Optional[int] = None,
    ) -> None:
        """
        Create a pilot for a differential-drive chassis.

        :param left_motor: Primary left motor.
        :param right_motor: Primary right motor.
        :param wheelbase_mm: Distance between left and right wheel (centre to centre), in mm.
        :param wheel_diameter_mm: Wheel diameter in mm. Circumference is derived as π × diameter before gear ratio is applied.
                                  Provide exactly one of ``wheel_diameter_mm`` or ``wheel_circumference_mm``.
        :param gear_ratio: Optional gear ratio used by the drivetrain model.
        :param helper_left_motor: Optional helper left motor.
        :param helper_right_motor: Optional helper right motor.
        :param left_motor_reversed: Reverse primary left motor direction.
        :param right_motor_reversed: Reverse primary right motor direction.
        :param helper_left_motor_reversed: Reverse helper left motor direction.
        :param helper_right_motor_reversed: Reverse helper right motor direction.
        :param wheel_circumference_mm: Keyword-only. Wheel circumference in mm, used directly before gear ratio is applied.
                                       Provide exactly one of ``wheel_diameter_mm`` or ``wheel_circumference_mm``.
        :raises ValueError: If neither or both of ``wheel_diameter_mm`` and ``wheel_circumference_mm`` are provided, or if other numeric or topology arguments are invalid.
        :raises brian.pilot.PilotAlreadyReservedError: If another active pilot already reserves PilotSync control.
        :raises brian.pilot.PilotConfigurationError: If pilot creation fails for non-argument reasons.
        """
        ...

    def __del__(self) -> None:
        """
        Close the pilot: disable PilotSync control. Returns control to motors themselves.
        """
        ...

    def close_pilot(self) -> None:
        """
        Close the pilot: disable PilotSync control. Returns control to motors themselves.
        """
        ...

    def set_speed(self, speed_mm_per_sec: int) -> None:
        """
        Set the default linear speed used when a movement method is called without the optional speed argument.

        :param speed_mm_per_sec: Default speed in mm/s.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def get_default_speed(self) -> int:
        """
        Get the current default linear speed used when movement methods are called without ``speed``.

        :return: Default speed in mm/s.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def set_acceleration(self, acceleration_mm_per_sec_sq: int) -> None:
        """
        Set acceleration so callers do not pass it in every command.

        :param acceleration_mm_per_sec_sq: Acceleration in mm/s².
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready.
        """
        ...

    def get_acceleration(self) -> int:
        """
        Get the current acceleration used by movement commands.

        Until :meth:`set_acceleration` is called, this is the mean acceleration limit of the motors
        managed by this pilot, converted to mm/s² through the wheel circumference and gear ratio.

        :return: Acceleration in mm/s².
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def brake(self) -> None:
        """
        Apply passive braking on all registered motors (short the windings).
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def hold(self) -> None:
        """
        Actively hold all registered motors at their current positions.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def coast(self) -> None:
        """
        Let all motors spin freely (float the windings).
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def wait_until_done(
        self,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Block until the current movement reaches the requested PilotSync state or the timeout expires.

        Waits on STM32-reported ``pilotStatus`` (plan id must match the active travel plan).

        :param timeout_ms: Max wait in milliseconds. If ``None``, wait until the condition is met; if ``0`` or negative,
                           return immediately.
        :param return_earlier_for_movement_chaining: If ``False`` (default), wait until the plan has stopped.
                                                      If ``True``, return once PilotSync enters slowdown, before
                                                      full stop, so another movement can be started immediately.
        :return: A value of ``brian.motors.EndReason`` (e.g. FINISHED, TIMED_OUT).

        Movement commands (``forward``, ``backward``, ``turn``, ``arc``, ``travel``) use the same ``timeout_ms``
        rules for their internal wait and return the same kind of ``EndReason`` value.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready.
        """
        ...

    def is_done(self) -> bool:
        """
        Check whether the last movement has completed.

        :return: True if no movement is in progress, False if still moving.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def forward(
        self,
        distance_mm: Optional[int] = None,
        speed: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Drive forward and wait up to ``timeout_ms`` for the commanded move to finish.

        :param distance_mm: If None, 0, or ±inf, no limit (see class docstring). Negative finite values flip
                            direction by reversing speed; negative speed + negative distance becomes forward.
        :param speed: Speed in mm/s. If None, uses default from set_speed(). Negative values reverse travel
                      along the same circle.
        :param timeout_ms: Same as :meth:`wait_until_done`.
        :param return_earlier_for_movement_chaining: Same as :meth:`wait_until_done`.
        :return: ``EndReason.FINISHED`` or ``EndReason.TIMED_OUT`` (script abort also surfaces as TIMED_OUT if incomplete).
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def backward(
        self,
        distance_mm: Optional[int] = None,
        speed: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Drive backward and wait up to ``timeout_ms`` for the commanded move to finish.

        :param distance_mm: If None, 0, or ±inf, no limit (see class docstring). Negative finite values flip
                            direction by reversing speed; negative speed + negative distance becomes backward.
        :param speed: Speed in mm/s. If None, uses default from set_speed(). Negative values reverse travel
                      along the same circle.
        :param timeout_ms: Same as :meth:`wait_until_done`.
        :param return_earlier_for_movement_chaining: Same as :meth:`wait_until_done`.
        :return: ``EndReason`` value for how the wait ended.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def turn(
        self,
        turn_radius_mm: int,
        max_angle_deg: Optional[int] = None,
        turn_rate: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Turn and wait for completion (or timeout).

        :param turn_radius_mm: Turning radius in mm; 0 means turn on the spot (pivot).
                              Sign combines with ``turn_rate`` (same convention as :meth:`arc`).
        :param max_angle_deg: Optional cap in degrees; None, 0, or ±inf means no limit (see class docstring).
                              Negative finite values flip direction by reversing ``turn_rate``; negative
                              ``turn_rate`` + negative ``max_angle_deg`` becomes a positive turn.
        :param turn_rate: Turn rate in degrees per second. Must be non-zero. If None, it is derived from
                          the default speed (:meth:`set_speed`) and ``turn_radius_mm`` the same way
                          :meth:`arc` does, so a wider radius keeps the same speed along the path;
                          for radii below the pivot radius (wheelbase / 2) that pivot radius is used.
                          Sign combines with ``turn_radius_mm`` like normal multiplication: one negative
                          turns left (CCW), both negative cancel to turn right (CW). With pivot radius 0,
                          sign alone selects direction.
        :param timeout_ms: Same as :meth:`wait_until_done`.
        :param return_earlier_for_movement_chaining: Same as :meth:`wait_until_done`.
        :return: ``EndReason`` value for how the wait ended.
        :raises ValueError: If ``turn_rate`` is zero, or if it is omitted and the derived rate rounds to
                            zero (default speed of 0, or a radius far too large for that speed).
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def arc(
        self,
        radius_mm: int,
        max_distance_mm: Optional[int] = None,
        speed: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Drive along an arc and wait for completion (or timeout).

        :param radius_mm: Turning radius in mm (from turn centre to robot centreline).
                        - ``0`` means turn around the robot centre,
                        - ``-wheelbase_mm/2`` means the left wheel is stationary,
                        - ``+wheelbase_mm/2`` means the right wheel is stationary.
                        - Negative values turn left, positive values turn right.
        :param max_distance_mm: Optional path length in mm; None, 0, or ±inf means no limit (see class docstring).
                                Negative finite values reverse travel along the same circle (equivalent to negating speed).
        :param speed: Speed in mm/s. If None, uses default from set_speed(). Negative values reverse travel
                      along the same circle (radius sign still selects left vs right).
        :param timeout_ms: Same as :meth:`wait_until_done`.
        :param return_earlier_for_movement_chaining: Same as :meth:`wait_until_done`.
        :return: ``EndReason`` value for how the wait ended.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def travel(
        self,
        turn_rate: float,
        max_distance_mm: Optional[int] = None,
        speed: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        return_earlier_for_movement_chaining: bool = False,
    ) -> EndReason:
        """
        Drive along a curved path and wait for completion (or timeout).

        ``turn_rate`` is the ratio between the two wheel speeds, not an angular rate, so the shape of
        the path stays the same at any speed:

        - ``0`` drives straight,
        - ``0.5`` stops one wheel,
        - ``1.0`` runs the wheels in opposite directions, turning on the spot,
        - positive values turn right, negative values turn left.

        :param turn_rate: Wheel-speed ratio from -1.0 to 1.0. Values outside that range are clamped.
        :param max_distance_mm: Optional path length in mm; None, 0, or ±inf means no limit (see class docstring).
                                Negative finite values reverse travel along the same circle (equivalent to negating speed).
        :param speed: Speed in mm/s. If None, uses default from set_speed(). Negative values reverse
                      travel along the same circle (``turn_rate`` still selects left vs right).
        :param timeout_ms: Same as :meth:`wait_until_done`.
        :param return_earlier_for_movement_chaining: Same as :meth:`wait_until_done`.
        :return: ``EndReason`` value for how the wait ended.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready after the readiness wait.
        """
        ...

    def is_ready(self) -> bool:
        """
        Check whether every motor controlled by the pilot is ready to be controlled,
        without waiting (same readiness criteria as ``brian.motors.Motor.is_ready()``).

        When a motor is not connected, this function returns False.
        When a wrong motor type is connected, this function raises an exception.

        :return: True if all controlled motors meet the readiness criteria, False if any is not connected.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.motors.MotorIncompatibleTypeError: If a wrong motor type is connected.
        """
        ...

    def wait_until_ready(
        self,
        timeout_ms: Optional[int] = None,
        optimism_level: Optional[MotorWaitOptimismLevel] = None,
    ) -> bool:
        """
        Block until all configured pilot motors are ready or the timeout expires.

        :param timeout_ms: Max wait in milliseconds. If ``None``, no per-call wall-clock limit; if ``0`` or negative,
                           return/raise immediately without waiting (same as ``brian.motors.Motor.wait_until_ready``).
        :param optimism_level: Readiness strictness (same enum as brian.motors.Motor.wait_until_ready()).
        :return: True if all motors are ready.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        :raises brian.pilot.PilotNotReadyError: If a controlled motor is not ready when the wait ends.
        """
        ...

    def distance_travelled_mm(self) -> int:
        """
        Signed integrated robot path distance (odometry), in mm, relative to the last
        ``reset_distance_travelled()`` call (or pilot start heading angle if never reset).

        :return: Signed distance in mm.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def heading_angle_deg(self) -> int:
        """
        Signed integrated heading change (odometry), in degrees, relative to the last
        ``reset_heading_angle()`` call (or pilot creation if never reset).

        :return: Signed heading angle in degrees.
        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def reset_distance_travelled(self, new_value_mm: int = 0) -> None:
        """Set current integrated distance travelled to the provided value (in mm).

        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...

    def reset_heading_angle(self, new_value_deg: int = 0) -> None:
        """Set current integrated heading angle (in degrees) to the provided value.

        :raises brian.pilot.PilotAlreadyClosedError: If the pilot instance is already closed.
        """
        ...
