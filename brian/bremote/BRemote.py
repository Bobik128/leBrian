from typing import Optional

from brian.buttons import LedColor


class BRemote:
    """
    A paired BRemote controller. Instances are returned by brian.bremote.list().
    """

    class Button:
        """A button of the remote."""

        def is_pressed(self) -> bool:
            """
            :return: True if the button is currently pressed.
            """
            ...

        def was_just_pressed(self) -> bool:
            """
            :return: True if a press edge occurred since the last poll or wait.
            Consumes the edge (returns False on subsequent calls until the next press).
            """
            ...

        def was_just_released(self) -> bool:
            """
            :return: True if a release edge occurred since the last poll or wait.
            Consumes the edge (returns False on subsequent calls until the next release).
            """
            ...

        def wait_for_press(self, timeout_ms: Optional[int] = None) -> bool:
            """
            Waits for the next button press edge.
            This function is blocking and abortable from MicroPython.

            :param timeout_ms: Maximum number of milliseconds to wait.
                - If the timeout is not provided or is None, the function will wait indefinitely.

            :return success:
                - True: If the desired button event was caught.
                - False: If the timeout ran out or the wait was aborted.

            :raises BRemoteDisconnectedError: If the remote disconnects while waiting.
            """
            ...

        def wait_for_release(self, timeout_ms: Optional[int] = None) -> bool:
            """
            Waits for the next button release edge.
            This function is blocking and abortable from MicroPython.

            :param timeout_ms: Maximum number of milliseconds to wait.
                - If the timeout is not provided or is None, the function will wait indefinitely.

            :return success:
                - True: If the desired button event was caught.
                - False: If the timeout ran out or the wait was aborted.

            :raises BRemoteDisconnectedError: If the remote disconnects while waiting.
            """
            ...

        def wait_for_press_and_release(self, timeout_ms: Optional[int] = None) -> bool:
            """
            Waits for next button press and release event.
            This function is blocking and abortable from MicroPython.

            :param timeout_ms: Maximum number of milliseconds to wait.
                - If the timeout is not provided or is None, the function will wait indefinitely.

            :return success:
                - True: If the desired button event was caught.
                - False: If the timeout ran out or the wait was aborted.

            :raises BRemoteDisconnectedError: If the remote disconnects while waiting.
            """
            ...

    joystick_btn: Button
    """Joystick click (press-to-click) button."""
    aux_btn: Button
    """Auxiliary button."""
    power_btn: Button
    """Power button."""
    hair_trigger_20: Button
    """Virtual button: pressed when analog trigger crosses 20%"""
    hair_trigger_50: Button
    """Virtual button: pressed when analog trigger crosses 50%."""
    hair_trigger_99: Button
    """Virtual button: pressed when analog trigger crosses 99%."""

    def is_connected(self) -> bool:
        """
        :return: True when this remote is operational and the last OpInput is younger than 200 ms.
        """
        ...

    def is_reconnecting(self) -> bool:
        """
        :return: True while Brian is trying to restore a lost link (OpOutput keepalive active).

        Set atomically with ``is_connected`` when input goes stale or the driver enters
        the reconnecting session phase. Cleared when OpInput resumes or the 5-minute
        reconnecting deadline expires.
        """
        ...

    def wait_until_connected(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Waits until this remote is operational (fresh OpInput). This function is blocking.

        :param timeout_ms: Maximum number of milliseconds to wait.
            - If the timeout is not provided or is None, the function will wait indefinitely.

        :return success:
            - True: If the remote became connected.
            - False: If the timeout ran out or the wait was aborted.
        """
        ...

    def mac_str(self) -> str:
        """
        :return: Remote MAC address as an uppercase hex string (AA:BB:CC:DD:EE:FF).
        """
        ...

    def age_us(self) -> int:
        """
        :return: Age of the last received packet in microseconds.
        Returns a very large value (UINT32_MAX) when no packet has ever been received.
        """
        ...

    def total_packets_received(self) -> int:
        """
        :return: Total validated OpInput packets received while the session is operational.

        Resets when the ESP-NOW session ends (``resetSession``).
        """
        ...

    def joystick_x(self) -> float:
        """
        :return: Current joystick X axis value in range -1.0 ~ 1.0.
        """
        ...

    def joystick_y(self) -> float:
        """
        :return: Current joystick Y axis value in range -1.0 ~ 1.0.
        """
        ...

    def battery_level(self) -> int:
        """
        :return: Remote controller battery level in percents (0–100).
        Returns 0 when not connected.
        """
        ...

    def is_battery_charging(self) -> bool:
        """
        :return: True when the remote reports that its battery is charging.
        Returns False when not connected.
        """
        ...

    def is_overheating(self) -> bool:
        """
        :return: True when the remote temperature exceeds the overheating threshold.
        Returns False when not connected.
        """
        ...

    def trigger(self) -> float:
        """
        :return: Current trigger position in range 0.0 ~ 1.0 (analog input, not a digital button).
        """
        ...

    def motion(self) -> Optional[float]:
        """
        :return: Peak |ax|+|ay|+|az|+|gx|+|gy|+|gz| (g + dps) since the last packet.
        Returns None when not connected or on IMU I2C error.
        """
        ...

    def play_tone(self, tone: int, duration_ms: int) -> None:
        """
        Play a tone on the remote controller speaker.

        :param tone: Frequency in Hz.
        :param duration_ms: Tone duration in milliseconds.
        """
        ...

    def stop_tone(self) -> None:
        """Stop any tone currently playing on the remote controller."""
        ...

    def set_color(self, color: LedColor = 'DEFAULT_COLOR_FROM_SETTINGS') -> None:
        """
        Set the user LED color on this remote.

        :param color: Target color. When unfilled default color from settings is used.
        """
        ...
