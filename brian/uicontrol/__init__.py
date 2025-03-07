from typing import List
from enum import Enum
from UiEventsListener import *

class UiEventsListenerAlreadyClosedError(Exception):
    """Thrown when trying to access closed UiEventsListener"""

class LedColor:
    def __init__(self, red: int, green: int, blue:int):
        """"""
        ...
    red: int
    """"""
    green: int
    """"""
    blue: int
    """"""


class ButtonId(Enum):
    """"""
    TOP_LEFT = 0
    """"""
    TOP_RIGHT = 1
    """"""
    BOTTOM_LEFT = 2
    """"""
    BOTTOM_RIGHT = 3
    """"""
    KNOB = 4
    """"""
    _length = 5
    """"""


class LedButtonAnimation(Enum):
    """Constants for selecting behavior of button LEDs. Only in use when LED animations are handled by Brian OS."""

    OFF = 0
    """LED is fully off"""

    STANDBY = 1
    """LED is pulsing at low brightness level"""

    SELECTABLE = 2
    """LED is pulsing at medium brightness level"""

    SELECTED = 3
    """LED is pulsing at high brightness level"""

    _inherit = 4
    """LED behavior is not set at this level; Behavior of a previous (system) level is used."""


@staticmethod
def set_button_led(target: ButtonId, animation: LedButtonAnimation,
                   color: LedColor = 'DEFAULT_COLOR_FROM_SETTINGS') -> None:
    """
    Set desired animation and color for a specific button (target). These settings override the animation
    requested by the `PhysButtonOverlay` and the default os button effect, unless `LedButtonAnimation._inherit`
    is used.
    """
    ...


@staticmethod
def enable_knob_rotation_animation(enabled: bool) -> None:
    """
    If enabled, OS automatically animates the LEDs under the knob when it rotates. The user program starts in the enabled state.
    """
    ...


@staticmethod
def get_num_of_leds() -> int:
    """
    :return: number of available leds
    """
    ...
