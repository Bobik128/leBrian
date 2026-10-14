def show_image(path: str, size: str = "console", back_button: str | None = None) -> None:
    """
    Loads a JPEG or PNG image from the SD card and displays it on screen instead of the running console.

    Must be called while a MicroPython program is running.

    :param path: Path to the image file on the SD card (e.g. "/images/logo.jpg").
    :param size: How the image is sized and positioned:
        - ``"fullscreen_fit"``  — scaled to fit the full 320×240 screen while preserving aspect ratio
          (black background fills any empty space). Status bar is hidden.
        - ``"fullscreen_fill"`` — scaled to fill the full 320×240 screen while preserving aspect ratio
          (edges may be cropped to fill). Status bar is hidden.
        - ``"console"``         — scaled to fit within the console area, with margins and status bar visible;
          program file name and icon stay visible. Without ``back_button``, the left+right interrupt/kill hint
          is shown as during a normal program run.
    :param back_button: If a non-empty string, a physical left back button with this label is displayed
        so the user can dismiss the image and return to the console view. ``None`` or ``""`` hides the button.
    :raises OSError: If the image file cannot be found or decoded.
    :raises ValueError: If ``size`` is not one of the accepted values.
    """
    ...


def clear_image() -> None:
    """
    Clears the image currently shown by :func:`show_image` and returns to the console view.

    No-op if no image is being displayed.
    """
    ...


def wait_until_image_closed() -> None:
    """
    Blocks until the user dismisses the image with the back button.

    Returns immediately if no image is displayed, or if the image has no back button
    (see :func:`show_image`). Also returns once the image has been cleared (e.g. by :func:`clear_image`).

    Raises KeyboardInterrupt if the program is interrupted while waiting (e.g. left+right buttons).
    """
    ...


def clear_console(lines: int | None = None) -> None:
    """
    Clears program console output. Effect is visible both on screen and in the web console.

    With no argument, clears the entire console.
    With a negative integer (e.g. -1, -5), removes that many lines from the end (-5 removes the last 5 lines).
    """
    ...
