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
