from typing import Optional

from brian.buttons import LedEffect, LedColor


class UiEventsListener:
    """
    Collects button and knob events, so a program polling in a loop does not miss presses that happen between polls.
    """

    class KnobEvent:
        """Knob events since the last knob_event_since_last() call."""
        turn_delta: int
        """Turn indents since the last call; positive is clockwise"""
        turned_to: int
        """Absolute turn indent count since this listener was created"""
        is_pressed: bool
        """True if the knob is pressed"""
        just_pressed: bool
        """True if the knob was pressed since the last call"""
        just_released: bool
        """True if the knob was released since the last call"""

    class ButtonEvent:
        """Events of one button since the last buttons_event_since_last() call."""
        is_pressed: bool
        """True if the button is pressed"""
        just_pressed: bool
        """True if the button was pressed since the last call"""
        just_released: bool
        """True if the button was released since the last call"""

    class ButtonsEvent:
        """Events of all buttons since the last buttons_event_since_last() call."""
        top_left: 'UiEventsListener.ButtonEvent'
        """Top left button"""
        top_right: 'UiEventsListener.ButtonEvent'
        """Top right button"""
        bottom_left: 'UiEventsListener.ButtonEvent'
        """Bottom left button"""
        bottom_right: 'UiEventsListener.ButtonEvent'
        """Bottom right button"""
        any_button: 'UiEventsListener.ButtonEvent'
        """Any of the four corner buttons (knob excluded)"""
        any_button_incl_knob: 'UiEventsListener.ButtonEvent'
        """Any of the four corner buttons or the knob press"""

    class Button:
        """A button seen through this listener."""

        def is_pressed(self) -> bool:
            """
            :return: True if the button is currently pressed (live state, does not consume events).
            """
            ...

        def last_button_event(self) -> 'UiEventsListener.ButtonEvent':
            """
            :return: Snapshot of the last event of this button, without resetting the just_pressed / just_released flags.
            """
            ...

        def set_led(self, effect: LedEffect, color: LedColor = 'DEFAULT_COLOR_FROM_SETTINGS') -> None:
            """
            Sets desired effect and color for the LED of this button. These settings override the effect
            requested by the OS, unless `LedEffect.inherit` is used. For any_button and any_button_incl_knob
            all respective buttons change color/effect.

            :param effect: Target LED effect.
            :param color: Target color. When unfilled default color from settings is used.
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

    class Knob(Button):
        """The knob seen through this listener."""

        def turned_to(self) -> int:
            """
            :return: Absolute turn indent count since this listener was created (live state, does not consume events).
            """
            ...

        def last_button_event(self) -> 'UiEventsListener.KnobEvent':
            """
            :return: Snapshot of the last event of the knob, without resetting the just_pressed / just_released
            and turn_delta fields.
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

    top_left: Button
    """Top left button"""
    top_right: Button
    """Top right button"""
    bottom_left: Button
    """Bottom left button"""
    bottom_right: Button
    """Bottom right button"""
    any_button: Button
    """Any of the four corner buttons (knob excluded)"""
    any_button_incl_knob: Button
    """Any of the four corner buttons or the knob press"""
    knob: Knob
    """The knob"""

    def __init__(self):
        """
        Initializes a new UiEventsListener class.
        """
        ...

    def knob_event_since_last(self) -> KnobEvent:
        """
        This function will reset just_pressed, just_released fields and turn_delta fields.

        :return: KnobEvent class of events that happened since last call.
        """
        ...

    def buttons_event_since_last(self) -> ButtonsEvent:
        """
        This function will reset just_pressed and just_released fields.

        :return: ButtonsEvent class of events that happened since last call.
        """
        ...
