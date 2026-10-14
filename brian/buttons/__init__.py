from typing import List, Optional
from enum import Enum
from brian.buttons.UiEventsListener import *


class UiEventsListenerAlreadyClosedError(Exception):
    """Thrown when trying to access closed UiEventsListener"""


class LedColor:
    """Color of a button LED."""

    def __init__(self, red: int, green: int, blue: int):
        """
        Holds color definition for button LEDs. Color values range from 0 to 255. When outside of this range, the values are clamped
        """
        ...

    red: int
    """Red component of the color, in range from 0 to 255. When set to a value outside of this range, the value is clamped"""
    green: int
    """Green component of the color, in range from 0 to 255. When set to a value outside of this range, the value is clamped"""
    blue: int
    """Blue component of the color, in range from 0 to 255. When set to a value outside of this range, the value is clamped"""


class LedEffect(Enum):
    """Constants for selecting the effect of button LEDs. Only in use when LED effects are handled by Brian OS."""

    OFF = 0
    """LED is fully off"""

    LOW = 1
    """LED is pulsing at low brightness level"""

    MEDIUM = 2
    """LED is pulsing at medium brightness level"""

    HIGH = 3
    """LED is pulsing at high brightness level"""

    inherit = 4
    """LED effect is not set at this level; Effect of a previous (system) level is used."""


class Button:
    """
    A physical button of the brick. Pre-existing instances are available as
    ``brian.buttons.top_left``, ``top_right``, ``bottom_left``, ``bottom_right``,
    ``any_button`` and ``any_button_incl_knob`` — the class is not instantiable.
    """

    def is_pressed(self) -> bool:
        """
        :return: True if the button is currently pressed by the user.
        """
        ...

    def wait_for_press(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits for next button press event.
        This function is blocking.

        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the desired button event was caught.
            - False: If the timeout ran out.
        """
        ...

    def wait_for_release(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits for next button release event.
        This function is blocking.

        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the desired button event was caught.
            - False: If the timeout ran out.
        """
        ...

    def wait_for_press_and_release(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits for next button press and release event.
        This function is blocking.

        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the desired button event was caught.
            - False: If the timeout ran out.
        """
        ...

    def set_led(self, effect: LedEffect, color: LedColor = 'DEFAULT_COLOR_FROM_SETTINGS') -> None:
        """
        Sets desired effect and color for the LED of this button. These settings override the effect
        requested by the OS, unless `LedEffect.inherit` is used. For `buttons.any_button` and
        `buttons.any_button_incl_knob` all respective buttons change color/effect.

        :param effect: Target LED effect.
        :param color: Target color. When unfilled default color from settings is used.
        """


class Knob(Button):
    """
    The physical knob of the brick. The pre-existing instance is available as
    ``brian.buttons.knob`` — the class is not instantiable.
    """

    def turned_to(self) -> int:
        """
        :return: Absolute turn indent count (offset-corrected). Can be reset via reset_absolute_rotation().
        """
        ...

    def wait_for_directional_turn(self, clockwise: bool = True, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits for next directional turn of the knob.
        This function is blocking.

        :param clockwise: Whether to wait for clockwise or counterclockwise turn.
        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the desired button event was caught.
            - False: If the timeout ran out.
        """
        ...

    def wait_for_any_turn(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits for next any turn of the knob.
        This function is blocking.

        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the desired button event was caught.
            - False: If the timeout ran out.
        """
        ...

    def reset_absolute_rotation(self, new_turned_to: int = 0) -> None:
        """
        Resets turned_to() back to zero (or the provided value).

        :param new_turned_to: Value that turned_to() should return immediately after this call. Defaults to 0.
        """


top_left: Button
"""Top left physical button. Live hardware state — no listener needed."""
top_right: Button
"""Top right physical button. Live hardware state — no listener needed."""
bottom_left: Button
"""Bottom left physical button. Live hardware state — no listener needed."""
bottom_right: Button
"""Bottom right physical button. Live hardware state — no listener needed."""
any_button: Button
"""Virtual button that reacts to any of the four corner buttons (knob excluded)."""
any_button_incl_knob: Button
"""Virtual button that reacts to any of the four corner buttons or the knob press."""
knob: Knob
"""The physical knob (rotation and press). Live hardware state — no listener needed."""


@staticmethod
def enable_knob_rotation_animation(enabled: bool) -> None:
    """
    If enabled, OS automatically animates the LEDs under the knob when it rotates. The user program starts in the enabled state.

    :param enabled: Whether to animate knob rotation.
    """
    ...


@staticmethod
def use_os_colors() -> None:
    """
    Returns button LED control to Brian OS (default state). Counterpart of :func:`use_raw_colors`.
    """
    ...


@staticmethod
def use_raw_colors() -> None:
    """
    Takes over full control of the button LEDs. After this call the LEDs show exactly the colors
    set by :func:`set_raw_led_colors` — no OS effects are applied.
    """
    ...


@staticmethod
def get_num_of_leds() -> int:
    """
    :return: number of individually controllable button LEDs.
    """
    ...


@staticmethod
def set_raw_led_colors(raw_colors: List[LedColor]) -> None:
    """
    Sets the raw color of every button LED. Only visible after :func:`use_raw_colors`.

    :param raw_colors: List of exactly :func:`get_num_of_leds` colors.
    """
    ...
