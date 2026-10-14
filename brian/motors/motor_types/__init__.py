from enum import Enum

class DeviceClass(Enum):
    """Device detected on a motor port using only ADC readings. Valid only when the port mode is not POWER_OFF."""

    NONE = 0
    """No device is detected"""
    ERROR = 1
    """Some device was detected, but it is not clear which"""
    EV3_ANALOG_MOTOR = 2
    """NXT/EV3 motor was detected; the device type contains the ID"""
    EV3_UART_DEVICE = 3
    """Unknown EV3 UART device was detected; further active probing is needed"""


class DeviceType(Enum):
    """More detailed type of a device detected as DeviceClass.EV3_ANALOG_MOTOR."""
    UNKNOWN = 0
    """Motor type is not known (yet)"""
    NXT_EV3_LARGE_MOTOR = 7
    """NXT or EV3 large motor (these are not distinguishable)"""
    EV3_MEDIUM_MOTOR = 8
    """EV3 medium motor"""
class MotorType:
    """
    Description of a supported motor type and its default control parameters.
    """

    @property
    def name(self) -> str:
        """
        :return: Human-readable name of the motor
        """
        ...

    @property
    def identification(self) -> 'Identification':
        """
        :return: What will Brian report as the ID when this motor is connected
        """
        ...

    @property
    def default_constants(self) -> 'DefaultConstants':
        """
        :return: Default controller configuration
        """
        ...

    @property
    def default_acceleration_limit(self) -> int:
        """
        :return: Acceleration limit a new Motor of this type starts with, in degrees per second squared
        """
        ...

    class Identification:
        """
        Results of auto-detection
        """
        @property
        def device_type(self) -> 'DeviceType':
            """
            :return: More detailed device type
            """
            ...

        @property
        def device_class(self) -> 'DeviceClass':
            """
            :return: Detected device class (portMode must not be POWER_OFF)
            """
            ...

    class DefaultConstants:
        """
        Control loop parameters that are typically not changed much
        """
        @property
        def motor(self) -> 'Motor':
            """
            :return: Linear dynamic model of the motor
            """
            ...

        @property
        def controller(self) -> 'Controller':
            """
            :return: Constants of the position/speed controller
            """
            ...

        @property
        def observer(self) -> 'Observer':
            """
            :return: Configuration of the state observer
            """
            ...

        class Motor:
            """
            Linear dynamic model of the connected motor.
            This model can be used for estimating various internal states of the motor.
            """

            @property
            def Kt_NmPerA(self) -> float:
                """
                :return: Torque constant, in N*m/A
                """
                ...

            @property
            def Kb_VPerRadPerSec(self) -> float:
                """
                :return: Torque constant in V/(rad/sec)
                """
                ...

            @property
            def B_NmPerRadPerSec(self) -> float:
                """
                :return: Friction constant, in N*m/(rad/sec)
                """
                ...

            @property
            def Udeadzone_Volts(self) -> float:
                """
                :return: Voltage needed to make the motor moves
                """
                ...

            @property
            def R_Ohm(self) -> float:
                """
                :return: Armature resistance, in ohms
                """
                ...

            @property
            def L_Henry(self) -> float:
                """
                :return: Armature inductance, in henry
                """
                ...

            @property
            def Cp_Farad(self) -> float:
                """
                :return: Capacity of a EMI-eliminating capacitor across motor terminals, in farads
                """
                ...

            @property
            def ticksPerRevolution(self) -> float:
                """
                :return: Number of encoder ticks per one revolution.
                """
                ...

        class Controller:
            """
            Constants of the position/speed controller
            Brian implements these two controllers:
            - a parallel-form 2-degrees-of-freedom PI controller for motor speed [1], and
            - a cascaded P controller for motor position.
            [1]: https://www.mathworks.com/help/control/ug/two-degree-of-freedom-2-dof-pid-controllers.html
            """

            @property
            def speedKp(self) -> float:
                """
                :return: Proportional constant of the speed PI controller
                """
                ...

            @property
            def speedKi(self) -> float:
                """
                :return: Integral constant of the speed PI controller
                """
                ...

            @property
            def speedBeta(self) -> float:
                """
                :return: Setpoint weight in the proportional branch of the PI controller (see [1])
                """
                ...

            @property
            def positionKp(self) -> float:
                """
                :return: Proportional constant of the cascaded position P controller (its output is target speed in ticks/s)
                """
                ...

            @property
            def positionToleranceTicks(self) -> int:
                """
                :return: Tolerate up to this deviation with zero output (needed for EV3 medium motor)
                """
                ...
        class Observer:
            """
            Additional configuration of state observer.
            """

            @property
            def current(self) -> 'Current':
                """Current"""
                ...

            @property
            def speed(self) -> 'Speed':
                """Speed"""
                ...

            class Current:
                """
                Current observer parameters.
                Brian has to estimate motor winding current from H-bridge
                current measurements. These are not equal (PWM=0 makes the
                winding current impossible to directly measure).
                The way it does so is by simulating the current response
                using the provided model and then correcting the predicted
                value using real measurements (when they're available).

                """
                @property
                def measurementWeight_pct(self) -> int:
                    """
                    :return: Correction step: How much weight to give to measurements vs. model prediction
                    """
                    ...

                @property
                def minimumPwmOnTime_pct(self) -> int:
                    """
                    :return: Only trust measurements if the PWM has at least this duty cycle
                    """
                    ...

            class Speed:
                """
                Speed tracking loop parameters
                Brian estimates motor speed using a tracking loop/observer inspired by
                figure 3 and equations (6) in [2]. These constants specify the parameters
                of the loop.
                [2]: https://www.sciencedirect.com/science/article/pii/S2405896319326618
                """
                @property
                def Kp(self) -> int:
                    """
                    :return: Proportional gain of the speed tracking loop
                    """
                    ...

                @property
                def Ki(self) -> int:
                    """
                    :return: Integral gain of the speed tracking loop
                    """
                    ...
