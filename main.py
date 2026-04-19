from game.gaze_providers.mediapipe_gaze import MediaPipeGazeProvider
from game.renderer.pyqt_renderer import PyQtRenderer

# Swap MediaPipeGazeProvider for MouseGazeProvider to test without a camera:
# from game.gaze_providers.mouse_gaze import MouseGazeProvider

if __name__ == "__main__":
    gaze = MediaPipeGazeProvider(camera_index=0)
    PyQtRenderer().start(gaze)
