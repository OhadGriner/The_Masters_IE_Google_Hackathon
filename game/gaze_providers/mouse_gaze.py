from typing import Tuple

import pyautogui

from .base import GazeProvider


class MouseGazeProvider(GazeProvider):
    """Uses the current mouse position as the gaze point. Useful for testing without a camera."""

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_gaze_position(self) -> Tuple[int, int]:
        pos = pyautogui.position()
        return pos.x, pos.y
