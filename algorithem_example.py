import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import pyautogui
import math
import threading
import time
import signal

MONITOR_WIDTH, MONITOR_HEIGHT = pyautogui.size()
CENTER_X = MONITOR_WIDTH // 2
CENTER_Y = MONITOR_HEIGHT // 2
mouse_control_enabled = True
filter_length = 8


FACE_OUTLINE_INDICES = [
    10, 338, 297, 332, 284, 251, 389, 356,
    454, 323, 361, 288, 397, 365, 379, 378,
    400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21,
    54, 103, 67, 109
]

mouse_target = [CENTER_X, CENTER_Y]
mouse_lock = threading.Lock()

calibration_offset_yaw = 0
calibration_offset_pitch = 0

ray_origins = deque(maxlen=filter_length)
ray_directions = deque(maxlen=filter_length)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)

LANDMARKS = {
    "left": 234,
    "right": 454,
    "top": 10,
    "bottom": 152,
    "front": 1,
}

cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"avc1"), fps, (frame_w, frame_h))
print(f"Recording {frame_w}x{frame_h} @ {fps}fps — press Ctrl+C to stop.")

_stop = threading.Event()
signal.signal(signal.SIGINT, lambda *_: _stop.set())


def mouse_mover():
    while True:
        if mouse_control_enabled:
            with mouse_lock:
                x, y = mouse_target
            pyautogui.moveTo(x, y)
        time.sleep(0.01)


def landmark_to_np(landmark, w, h):
    return np.array([landmark.x * w, landmark.y * h, landmark.z * w])


threading.Thread(target=mouse_mover, daemon=True).start()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            # Draw all landmarks as dots
            for i, landmark in enumerate(face_landmarks):
                pt = landmark_to_np(landmark, w, h)
                x, y = int(pt[0]), int(pt[1])
                if 0 <= x < w and 0 <= y < h:
                    color = (155, 155, 155) if i in FACE_OUTLINE_INDICES else (255, 25, 10)
                    cv2.circle(frame, (x, y), 2, color, -1)

            # Highlight the 5 key landmarks
            key_points = {}
            for name, idx in LANDMARKS.items():
                pt = landmark_to_np(face_landmarks[idx], w, h)
                key_points[name] = pt
                x, y = int(pt[0]), int(pt[1])
                cv2.circle(frame, (x, y), 8, (255, 0, 255), -1)
                cv2.putText(frame, name, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

            left   = key_points["left"]
            right  = key_points["right"]
            top    = key_points["top"]
            bottom = key_points["bottom"]
            front  = key_points["front"]

            right_axis = right - left
            right_axis /= np.linalg.norm(right_axis)

            up_axis = top - bottom
            up_axis /= np.linalg.norm(up_axis)

            forward_axis = -np.cross(right_axis, up_axis)
            forward_axis /= np.linalg.norm(forward_axis)

            center = (left + right + top + bottom + front) / 5
            half_width  = np.linalg.norm(right - left) / 2
            half_height = np.linalg.norm(top - bottom) / 2
            half_depth  = 80

            def corner(xs, ys, zs):
                return center + xs * half_width * right_axis + ys * half_height * up_axis + zs * half_depth * forward_axis

            cube_corners = [
                corner(-1,  1, -1), corner( 1,  1, -1),
                corner( 1, -1, -1), corner(-1, -1, -1),
                corner(-1,  1,  1), corner( 1,  1,  1),
                corner( 1, -1,  1), corner(-1, -1,  1),
            ]

            def project(pt3d):
                return int(pt3d[0]), int(pt3d[1])

            cube_2d = [project(c) for c in cube_corners]
            for i, j in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
                cv2.line(frame, cube_2d[i], cube_2d[j], (255, 125, 35), 2)

            # Draw right (red) and up (blue) axes as arrows
            axis_len = half_width
            cv2.arrowedLine(frame, project(center), project(center + right_axis * axis_len), (0, 0, 255), 3, tipLength=0.2)
            cv2.arrowedLine(frame, project(center), project(center + up_axis * axis_len),    (255, 0, 0), 3, tipLength=0.2)
            cv2.putText(frame, "right", project(center + right_axis * axis_len), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, "up",    project(center + up_axis * axis_len),    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Smoothed forward ray (green)
            ray_origins.append(center)
            ray_directions.append(forward_axis)
            avg_dir = np.mean(ray_directions, axis=0)
            avg_dir /= np.linalg.norm(avg_dir)
            avg_origin = np.mean(ray_origins, axis=0)
            ray_end = avg_origin - avg_dir * (2.5 * half_depth)
            cv2.arrowedLine(frame, project(avg_origin), project(ray_end), (15, 255, 0), 3, tipLength=0.1)
            cv2.putText(frame, "forward", project(ray_end), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 255, 0), 2)

            # Angle computation + mouse control
            reference_forward = np.array([0.0, 0.0, -1.0])
            xz = np.array([avg_dir[0], 0.0, avg_dir[2]])
            xz /= np.linalg.norm(xz)
            yaw_rad = math.acos(np.clip(np.dot(reference_forward, xz), -1.0, 1.0))
            if avg_dir[0] < 0:
                yaw_rad = -yaw_rad

            yz = np.array([0.0, avg_dir[1], avg_dir[2]])
            yz /= np.linalg.norm(yz)
            pitch_rad = math.acos(np.clip(np.dot(reference_forward, yz), -1.0, 1.0))
            if avg_dir[1] > 0:
                pitch_rad = -pitch_rad

            yaw_deg   = math.degrees(yaw_rad)
            pitch_deg = math.degrees(pitch_rad)

            yaw_deg   = abs(yaw_deg) if yaw_deg < 0 else (360 - yaw_deg if yaw_deg < 180 else yaw_deg)
            pitch_deg = 360 + pitch_deg if pitch_deg < 0 else pitch_deg

            raw_yaw_deg, raw_pitch_deg = yaw_deg, pitch_deg

            yaw_deg   += calibration_offset_yaw
            pitch_deg += calibration_offset_pitch

            yawDegrees, pitchDegrees = 20, 10
            screen_x = int(((yaw_deg   - (180 - yawDegrees))   / (2 * yawDegrees))   * MONITOR_WIDTH)
            screen_y = int(((180 + pitchDegrees - pitch_deg)    / (2 * pitchDegrees)) * MONITOR_HEIGHT)
            screen_x = max(10, min(screen_x, MONITOR_WIDTH  - 10))
            screen_y = max(10, min(screen_y, MONITOR_HEIGHT - 10))

            if mouse_control_enabled:
                with mouse_lock:
                    mouse_target[0] = screen_x
                    mouse_target[1] = screen_y

        out.write(frame)
        cv2.imshow("Head-Aligned Cube", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or _stop.is_set():
            break

finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Saved to output.mp4")
