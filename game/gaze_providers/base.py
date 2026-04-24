from abc import ABC, abstractmethod
from typing import Tuple


class GazeProvider(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def get_gaze_position(self) -> Tuple[int, int]: ...

    def calibrate(self) -> None:
        """Reset center to current gaze direction. No-op by default."""

    def set_screen_size(self, w: int, h: int) -> None:
        """Override screen dimensions (e.g. logical pixels on HiDPI). No-op by default."""
