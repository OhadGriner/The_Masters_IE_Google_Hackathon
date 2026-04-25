![Orbit](assets/Orbit-Logo-Caption.png)

# Head Movement Tracker: Corporate Performance Assessment

> A satirical head-movement game that evaluates your focus — and fires you if you lose it.

<!-- SCREENSHOT: Full welcome/title screen showing the corporate branding and "Begin Assessment" button -->
<!-- Insert screenshot here: assets/screenshots/welcome.png -->

---

## What is this?

A real-time gaze-tracking game built with **MediaPipe** and **PyQt5**. Your webcam tracks your head pose and translates it into a gaze position on screen. Your job: keep your eyes on the moving target while a fake corporate OS emails you, asks you to type buzzwords, and ultimately judges your performance.

Three escalating levels. Three increasingly unhinged environments. One HR verdict.

---

## Demo

<!-- SCREENSHOT: All three levels side-by-side or a GIF showing the target moving against the spreadsheet/Gmail/Slides backgrounds -->
<!-- Insert screenshot here — ideally a GIF or a 3-panel image showing Level 1 (Sheets), Level 2 (Gmail), Level 3 (Slides) -->

| Level | Theme | Target Behavior |
|-------|-------|-----------------|
| 1 | Google Sheets | Slow, predictable DVD bounce |
| 2 | Gmail Inbox | Faster bounce + dripping emails |
| 3 | Google Slides | Chaotic stochastic movement |

<!-- SCREENSHOT: Game Over / "YOU'RE FIRED" screen -->
<!-- Insert screenshot here: assets/screenshots/game_over.png -->

---

## Features

- **Real-time head pose tracking** via MediaPipe FaceMesh (468 3D facial landmarks, no eye hardware needed)
- **Three escalating difficulty levels** with distinct visual environments
- **Danger vignette** — a red edge glow that intensifies the longer you look away
- **Bonus quiz** — pop-up asks you to type corporate buzzwords mid-game for extra points
- **HR verdict** on game over, scaled to your score
- **Mouse mode** for testing without a webcam
- **Calibration** — press `C` to set your current head pose as screen center

---

## Requirements

- Python >= 3.9
- A connected webcam
- [`uv`](https://github.com/astral-sh/uv) (fast Python package manager)

Tested on macOS. Should work on Windows/Linux with minor dependency adjustments.

---

## Installation

```bash
git clone https://github.com/OhadGriner/eye_tracking_poc.git
cd eye_tracking_poc

uv sync                        # installs dependencies into .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

---

## Running

### Game

```bash
python main.py
```

> To test without a camera, open `main.py` and swap `MediaPipeGazeProvider` for `MouseGazeProvider` (see the comment in that file).

### Standalone Gaze Debug Tool

```bash
python MonitorTracking.py
```

Opens two OpenCV windows showing facial landmark detection and moves your system mouse based on head pose. Useful for verifying your webcam setup and tuning calibration.

<!-- SCREENSHOT: MonitorTracking.py OpenCV windows showing facial landmarks overlaid on the webcam feed -->
<!-- Insert screenshot here: assets/screenshots/debug_tool.png -->

---

## Controls

| Key | Action |
|-----|--------|
| `C` | Calibrate — sets current head pose as screen center |
| `Esc` | Quit |
| `R` | Restart (on game over screen) |

---

## Scoring & Progression

You score **1 point per second** your gaze is within the target radius.

| Milestone | Event |
|-----------|-------|
| Score ≥ 100 | Advance to Level 2 |
| Score ≥ 200 | Advance to Level 3 |
| 3s off-target | Game over |

**Bonus phrases** appear periodically — type the displayed corporate buzzword exactly to earn +30 points each.

### HR Verdicts

| Score | Verdict |
|-------|---------|
| < 5 | Terminated |
| 5 – 19 | Needs Improvement |
| 20 – 59 | Meets Expectations |
| ≥ 60 | Peak Performer |

---

## Architecture

```
GazeProvider  →  GameEngine  →  GameRenderer
(webcam/mouse)   (logic/state)   (PyQt5 UI)
```

```
eye_tracking_poc/
├── main.py                        # Entry point
├── MonitorTracking.py             # Standalone gaze debug tool
├── game/
│   ├── config.py                  # Constants (radius, timing, asset paths)
│   ├── gaze_providers/
│   │   ├── base.py                # GazeProvider ABC
│   │   ├── mediapipe_gaze.py      # Head pose via MediaPipe (daemon thread)
│   │   └── mouse_gaze.py          # Mouse fallback for testing
│   ├── engine/
│   │   ├── state.py               # GameState / Target dataclasses
│   │   └── engine.py              # Game loop, level logic, scoring
│   └── renderer/
│       ├── base.py                # GameRenderer ABC
│       └── pyqt_renderer.py       # Fullscreen PyQt5 UI (all screens + HUD)
└── assets/
    ├── target.png
    ├── slide.png
    ├── gmail_logo.webp
    ├── bonus/
    └── *.mp3                      # Music, countdown, level stingers, alerts
```

### How gaze tracking works

1. MediaPipe FaceMesh detects 468 3D facial landmarks each frame.
2. Five key landmarks (nose tip, chin, left/right cheeks, forehead) define a head orientation.
3. Yaw and pitch angles are extracted and smoothed over 16 frames to reduce jitter.
4. Angles are mapped linearly to screen coordinates (±35° yaw / ±18° pitch spans the full display).
5. Press `C` to set the current pose as the "looking straight ahead" reference.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `mediapipe` | Face mesh & head pose detection |
| `opencv-python` | Webcam capture & frame processing |
| `pyqt5` | Game UI and event loop |
| `numpy` | Numerical operations |
| `scipy` | Scientific computing |
| `pyautogui` | Mouse position (testing mode) |
| `keyboard` | Global key handling |

---

## License

MIT
