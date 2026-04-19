from abc import ABC, abstractmethod

from ..gaze_providers.base import GazeProvider


class GameRenderer(ABC):
    @abstractmethod
    def start(self, gaze_provider: GazeProvider) -> None:
        """Create QApplication/window, build engine with real screen size, run event loop."""
