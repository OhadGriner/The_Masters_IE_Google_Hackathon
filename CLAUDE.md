# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ignored directories

Do not read or reference files under `deprecated/`. Those are old, unused implementations.

## Environment setup

This project uses `uv` for dependency management (Python >=3.9).

```bash
uv sync           # install dependencies into .venv
source .venv/bin/activate
```

## Running

```bash
# Standalone gaze debug tool (opens OpenCV windows, moves mouse)
python MonitorTracking.py

# Gaze-tracking game
python main.py
```

Both require a connected webcam. To test the game without a camera, swap one import in `main.py` (see comment there).

## Game controls

| Key | Action |
|-----|--------|
| `C` | Calibrate — sets current head pose as screen center |
| `Esc` | Quit |

## Architecture

### MonitorTracking.py
Single-file standalone script. Opens two OpenCV windows and moves the system mouse based on head pose. Not imported by the game — it exists as an independent debug tool.

1. **MediaPipe Face Mesh** detects 468 3D facial landmarks from the webcam feed.
2. **Head pose estimation** — five key landmarks (`left`=234, `right`=454, `top`=10, `bottom`=152, `front`=1) define a right/up/forward orthonormal basis.
3. **Smoothing** — last 8 ray origins/directions averaged via `deque` to reduce jitter.
4. **Angle → screen mapping** — `yawDegrees=20` and `pitchDegrees=10` define the angular range spanning the full screen.

Coordinate convention: yaw/pitch 180° = straight ahead; <180° = left/down, >180° = right/up.

### game/ — three-layer architecture

```
GazeProvider  →  GameEngine  →  GameRenderer
(gaze_providers/)  (engine/)    (renderer/)
```

**Gaze layer** (`game/gaze_providers/`)
- `GazeProvider` ABC: `start()`, `stop()`, `get_gaze_position() -> (x, y)`, `calibrate()`.
- `MediaPipeGazeProvider` — ports MonitorTracking.py pipeline into a class; runs in a daemon thread; does NOT open any windows or move the mouse.
- `MouseGazeProvider` — reads `pyautogui.position()`; no threads; useful for testing.

**Engine** (`game/engine/`)
- `GameState` / `Target` — plain dataclasses, no logic.
- `GameEngine.update(dt)` — advances a Lissajous path (`ωx=0.7`, `ωy=0.5` rad/s) for the target, reads gaze position, increments `score` (frame count) while gaze is within `target.radius`.

**Renderer** (`game/renderer/`)
- `GameRenderer` ABC: `start(gaze_provider)` — responsible for creating `QApplication`, reading real screen dimensions, constructing `GameEngine`, and running the event loop.
- `PyQtRenderer` — fullscreen `QMainWindow`; `QTimer` at ~60 fps drives `engine.update(dt)` + repaint. Draws target (orange → green when hit), gaze crosshair, score in seconds.
