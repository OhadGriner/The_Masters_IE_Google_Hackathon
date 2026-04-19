import math
import sys
import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from ..engine.engine import GameEngine
from ..engine.state import GamePhase, GameState
from ..gaze_providers.base import GazeProvider
from .base import GameRenderer

_FPS = 60
_TICK_MS = 1000 // _FPS

_COLOR_BG = QColor(12, 12, 18)
_COLOR_TARGET_IDLE = QColor(230, 120, 40)
_COLOR_TARGET_HIT = QColor(80, 220, 100)
_COLOR_GAZE_FILL = QColor(100, 190, 255, 120)
_COLOR_GAZE_BORDER = QColor(100, 190, 255, 220)
_COLOR_TEXT = QColor(240, 240, 240)
_COLOR_OVERLAY = QColor(0, 0, 0, 160)


class _GameWidget(QWidget):
    def __init__(self, engine: GameEngine, parent=None) -> None:
        super().__init__(parent)
        self._engine = engine
        self._last_tick = time.perf_counter()

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(_TICK_MS)

        self.setMouseTracking(False)
        self.setCursor(Qt.BlankCursor)

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = now - self._last_tick
        self._last_tick = now
        self._engine.update(dt)
        self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key_C:
            self._engine.calibrate()
        elif event.key() == Qt.Key_R:
            self._engine.reset()
            self._last_tick = time.perf_counter()

    def paintEvent(self, _event) -> None:
        state: GameState = self._engine.state
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background
        p.fillRect(self.rect(), _COLOR_BG)

        # Target
        tx, ty = int(state.target.x), int(state.target.y)
        r = int(state.target.radius)
        color = _COLOR_TARGET_HIT if state.tracking else _COLOR_TARGET_IDLE
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(tx - r, ty - r, r * 2, r * 2)

        # Gaze pointer — filled circle with border
        gx, gy = state.gaze_x, state.gaze_y
        gr = state.gaze_radius
        p.setPen(QPen(_COLOR_GAZE_BORDER, 2))
        p.setBrush(QBrush(_COLOR_GAZE_FILL))
        p.drawEllipse(gx - gr, gy - gr, gr * 2, gr * 2)

        # Score (frames on target → seconds at 60 fps)
        seconds = state.score / _FPS
        p.setPen(_COLOR_TEXT)
        font = QFont("Arial", 22, QFont.Bold)
        p.setFont(font)
        p.drawText(20, 40, f"Score: {seconds:.1f}s")

        # Controls hint
        p.setFont(QFont("Arial", 11))
        p.setPen(QColor(140, 140, 140))
        p.drawText(20, self.height() - 16, "C = calibrate   Esc = quit")

        # Countdown overlay
        if state.phase == GamePhase.COUNTDOWN:
            p.fillRect(self.rect(), _COLOR_OVERLAY)
            p.setPen(_COLOR_TEXT)
            p.setFont(QFont("Arial", 120, QFont.Bold))
            label = str(math.ceil(state.countdown)) if state.countdown > 0 else "GO!"
            p.drawText(self.rect(), Qt.AlignCenter, label)

        # Game-over overlay
        elif state.phase == GamePhase.GAME_OVER:
            p.fillRect(self.rect(), _COLOR_OVERLAY)
            p.setPen(_COLOR_TEXT)
            p.setFont(QFont("Arial", 52, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, f"GAME OVER\n{seconds:.1f}s\n\nR = restart   Esc = quit")

        p.end()


class PyQtRenderer(GameRenderer):
    def start(self, gaze_provider: GazeProvider) -> None:
        app = QApplication(sys.argv)
        screen = app.primaryScreen().geometry()
        w, h = screen.width(), screen.height()

        gaze_provider.start()
        engine = GameEngine(w, h, gaze_provider)

        win = QMainWindow()
        widget = _GameWidget(engine, win)
        win.setCentralWidget(widget)
        win.setWindowTitle("Gaze Tracker Game")
        win.showFullScreen()
        widget.setFocus()

        exit_code = app.exec_()
        gaze_provider.stop()
        sys.exit(exit_code)
