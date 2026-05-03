"""
=============================================================
  HCI Assignment-4: Multi-Modal Human Detection System
  Course: Human Computer Interaction (SE305T / MD445T)
  Instructor: Dr. Muhammad Asif
  Semester: Spring-26 | Section: BSSE23 & BSCE22
=============================================================
  Group Members:
    - bsse23053  (Lips Detection + Eyes Detection)
    - bsse23004  (Hand Detection + Input Handling)
    - bsse23091  (Face Detection + Main Menu + Integration)
=============================================================
  Required Libraries:
    pip install opencv-python mediapipe deepface numpy
=============================================================
"""

import os
import cv2
import mediapipe as mp
import numpy as np
import time
import random
from collections import Counter
from deepface import DeepFace

# ── Linux/Wayland display fix ─────────────────────────────────────────────────
# Forces OpenCV windows to use XCB (X11) backend instead of Wayland,
# which does not render cv2.imshow properly on many Ubuntu setups.
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")


def _open_capture(source):
    """
    Open a cv2.VideoCapture with the correct backend for the given source.

    On Linux, integer sources (webcam) use the V4L2 backend explicitly to
    avoid blank-frame issues that can occur with the default GStreamer backend.

    Parameters:
        source : int | str  — camera index or video file path

    Returns:
        cv2.VideoCapture
    """
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
        if not cap.isOpened():          # V4L2 not available — fall back
            cap = cv2.VideoCapture(source)
        return cap
    return cv2.VideoCapture(source)


def _show_loading(win_name):
    """
    Display a 'Loading… please wait' placeholder in an OpenCV window.

    Called before the first MediaPipe inference, which can take several
    seconds on CPU while the XNNPACK delegate warms up.

    Parameters:
        win_name : str — the cv2 window name already created by the caller

    Returns:
        None
    """
    blank = np.zeros((360, 640, 3), dtype=np.uint8)
    cv2.putText(blank, "Loading model, please wait...",
                (60, 180), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 200, 255), 2)
    cv2.putText(blank, "This may take 10-20 seconds on first run.",
                (60, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    cv2.imshow(win_name, blank)
    cv2.waitKey(1)


# ─────────────────────────────────────────────────────────────────────────────
#  MODULE 1 — LIPS DETECTION
#  Implemented by: bsse23053
#  Tasks: T1 Smile Detection | T2 MAR Tracking | T3 Lip-Sync Counter
# ─────────────────────────────────────────────────────────────────────────────

def _get_mouth_landmarks(face_landmarks, frame_w, frame_h):
    """
    Extract pixel-space coordinates for key mouth landmarks from FaceMesh output.

    Parameters:
        face_landmarks : mediapipe face landmark object for a single face
        frame_w        : int, width of the current video frame in pixels
        frame_h        : int, height of the current video frame in pixels

    Returns:
        dict: keys 'top', 'bottom', 'left', 'right', 'corner_l', 'corner_r'
              each mapping to an (x, y) integer tuple
    """
    lm = face_landmarks.landmark

    def pt(idx):
        return (int(lm[idx].x * frame_w), int(lm[idx].y * frame_h))

    return {
        "top":      pt(13),    # upper lip inner
        "bottom":   pt(14),    # lower lip inner
        "left":     pt(78),    # mouth left extremity
        "right":    pt(308),   # mouth right extremity
        "corner_l": pt(61),    # left lip corner
        "corner_r": pt(291),   # right lip corner
    }


def _compute_mar(mouth_pts):
    """
    Compute the Mouth Aspect Ratio (MAR) for a given set of mouth points.

    MAR = vertical_distance / horizontal_distance.
    Higher values indicate a more open mouth.

    Parameters:
        mouth_pts : dict returned by _get_mouth_landmarks()

    Returns:
        float: MAR value (0.0 if horizontal distance is zero)
    """
    top    = np.array(mouth_pts["top"])
    bottom = np.array(mouth_pts["bottom"])
    left   = np.array(mouth_pts["left"])
    right  = np.array(mouth_pts["right"])

    vertical   = np.linalg.norm(top - bottom)
    horizontal = np.linalg.norm(left - right)

    return float(vertical / horizontal) if horizontal > 0 else 0.0


def _is_smiling(mouth_pts):
    """
    Decide if the user is smiling based on lip-corner y-positions vs mouth centre.

    A smile is detected when both lip corners are above (smaller y) the mouth
    vertical midpoint, indicating the corners are pulled upward.

    Parameters:
        mouth_pts : dict returned by _get_mouth_landmarks()

    Returns:
        bool: True if smiling, False otherwise
    """
    mid_y    = (mouth_pts["top"][1] + mouth_pts["bottom"][1]) // 2
    corner_l = mouth_pts["corner_l"][1]
    corner_r = mouth_pts["corner_r"][1]
    return (corner_l < mid_y) and (corner_r < mid_y)


def lips_detection(source):
    """
    Run the Lips Detection module in real time.

    Performs three tasks on each frame:
      T1 – Smile detection: labels frame 'Smiling' or 'Neutral'.
      T2 – MAR tracking: displays live MAR value; red border when MAR > 0.55.
      T3 – Lip-sync counter: counts open-close cycles with hysteresis
           (open threshold 0.55, close threshold 0.35).

    Parameters:
        source : int | str | numpy.ndarray
                 0 or camera index for webcam; path string for video file;
                 BGR image array for static image mode.

    Returns:
        None
    """
    # -- MediaPipe setup -------------------------------------------------------
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh    = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    MAR_OPEN  = 0.55   # hysteresis upper threshold
    MAR_CLOSE = 0.35   # hysteresis lower threshold

    lip_sync_count = 0
    mouth_is_open  = False   # tracks current hysteresis state

    # ── Static image mode ─────────────────────────────────────────────────────
    if isinstance(source, np.ndarray):
        frame = source.copy()
        h, w  = frame.shape[:2]
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res   = face_mesh.process(rgb)

        if res.multi_face_landmarks:
            for face_lm in res.multi_face_landmarks:
                mpts = _get_mouth_landmarks(face_lm, w, h)
                mar  = _compute_mar(mpts)
                smile = _is_smiling(mpts)

                label = "Smiling" if smile else "Neutral"
                color = (0, 220, 80) if smile else (200, 200, 200)
                cv2.putText(frame, f"Expression : {label}", (10, 45),
                            cv2.FONT_HERSHEY_DUPLEX, 0.85, color, 2)
                cv2.putText(frame, f"MAR        : {mar:.2f}", (10, 82),
                            cv2.FONT_HERSHEY_DUPLEX, 0.85, (255, 220, 0), 2)
                if mar > MAR_OPEN:
                    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 10)

        cv2.imshow("Module 1 – Lips Detection (Image)", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        face_mesh.close()
        return

    # ── Video / Webcam mode ───────────────────────────────────────────────────
    cap = _open_capture(source)
    if not cap.isOpened():
        print("[ERROR] Cannot open the video source. Check your path or camera index.")
        face_mesh.close()
        return

    paused    = False
    is_file   = isinstance(source, str)   # need to loop video files
    _WIN1     = "Module 1 \u2013 Lips Detection"
    cv2.namedWindow(_WIN1, cv2.WINDOW_NORMAL)
    _show_loading(_WIN1)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

        h, w   = frame.shape[:2]
        display = frame.copy()
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res     = face_mesh.process(rgb)

        if res.multi_face_landmarks:
            for face_lm in res.multi_face_landmarks:
                mpts  = _get_mouth_landmarks(face_lm, w, h)
                mar   = _compute_mar(mpts)
                smile = _is_smiling(mpts)

                # T3 – hysteresis-based lip-sync counting
                if not mouth_is_open and mar > MAR_OPEN:
                    mouth_is_open = True
                elif mouth_is_open and mar < MAR_CLOSE:
                    mouth_is_open = False
                    lip_sync_count += 1

                # T2 – red border when mouth open
                if mar > MAR_OPEN:
                    cv2.rectangle(display, (0, 0), (w - 1, h - 1), (0, 0, 255), 10)

                # T1 – smile label
                s_label = "Smiling" if smile else "Neutral"
                s_color = (0, 220, 80) if smile else (200, 200, 200)
                cv2.putText(display, f"Expression : {s_label}", (10, 42),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, s_color, 2)

                # T2 – MAR value
                cv2.putText(display, f"MAR        : {mar:.2f}", (10, 76),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 220, 0), 2)

                # T3 – lip-sync count
                cv2.putText(display, f"Lip-Sync   : {lip_sync_count}", (10, 110),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 200, 255), 2)

                # draw a few key lip landmarks for visual feedback
                for idx in [13, 14, 61, 78, 291, 308]:
                    x_ = int(face_lm.landmark[idx].x * w)
                    y_ = int(face_lm.landmark[idx].y * h)
                    cv2.circle(display, (x_, y_), 4, (0, 128, 255), -1)

        # bottom hint bar
        cv2.rectangle(display, (0, h - 30), (w, h), (30, 30, 30), -1)
        cv2.putText(display, "ESC – Main Menu  |  P – Pause / Play", (8, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Module 1 – Lips Detection", display)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key in (ord('p'), ord('P')):
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()


# ─────────────────────────────────────────────────────────────────────────────
#  MODULE 2 — EYES DETECTION
#  Implemented by: bsse23053
#  Tasks: T1 Blink Counter | T2 EAR Display | T3 Drowsiness Alert
# ─────────────────────────────────────────────────────────────────────────────

# FaceMesh landmark indices for EAR (6-point model per eye)
_LEFT_EYE_IDXS  = [33,  160, 158, 133, 153, 144]
_RIGHT_EYE_IDXS = [362, 385, 387, 263, 373, 380]


def _compute_ear(eye_pts):
    """
    Compute Eye Aspect Ratio (EAR) from 6 eye landmark points.

    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    Low EAR (< 0.25) indicates a closed eye.

    Parameters:
        eye_pts : list of 6 (x, y) tuples [p1 … p6] in pixel space

    Returns:
        float: EAR value, or 0.0 if horizontal distance is zero
    """
    p = [np.array(pt) for pt in eye_pts]
    v1 = np.linalg.norm(p[1] - p[5])
    v2 = np.linalg.norm(p[2] - p[4])
    h  = np.linalg.norm(p[0] - p[3])
    return float((v1 + v2) / (2.0 * h)) if h > 0 else 0.0


def eyes_detection(source):
    """
    Run the Eyes Detection module in real time.

    Performs three tasks on each frame:
      T1 – Blink counter: counts complete close → open transitions.
      T2 – EAR display: shows left and right EAR to three decimal places.
      T3 – Drowsiness alert: RED banner after 20 consecutive closed frames;
           clears automatically after 5 consecutive open frames.

    Parameters:
        source : int | str | numpy.ndarray
                 Camera index, video file path, or BGR image array.

    Returns:
        None
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh    = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    EAR_THRESHOLD   = 0.25
    DROWSY_LIMIT    = 20   # consecutive closed frames before alert
    CLEAR_LIMIT     = 5    # consecutive open frames to dismiss alert

    blink_count     = 0
    eye_was_closed  = False
    consec_closed   = 0
    consec_open     = 0
    drowsy_alert    = False

    # ── Static image mode ─────────────────────────────────────────────────────
    if isinstance(source, np.ndarray):
        frame = source.copy()
        h, w  = frame.shape[:2]
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res   = face_mesh.process(rgb)

        if res.multi_face_landmarks:
            for face_lm in res.multi_face_landmarks:
                lm = face_lm.landmark
                l_pts = [(int(lm[i].x * w), int(lm[i].y * h)) for i in _LEFT_EYE_IDXS]
                r_pts = [(int(lm[i].x * w), int(lm[i].y * h)) for i in _RIGHT_EYE_IDXS]
                l_ear = _compute_ear(l_pts)
                r_ear = _compute_ear(r_pts)

                for pt in l_pts + r_pts:
                    cv2.circle(frame, pt, 2, (0, 255, 220), -1)

                cv2.putText(frame, f"Left  EAR : {l_ear:.3f}", (10, 42),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                cv2.putText(frame, f"Right EAR : {r_ear:.3f}", (10, 76),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Module 2 – Eyes Detection (Image)", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        face_mesh.close()
        return

    # ── Video / Webcam mode ───────────────────────────────────────────────────
    cap     = _open_capture(source)
    is_file = isinstance(source, str)

    if not cap.isOpened():
        print("[ERROR] Cannot open the video source.")
        face_mesh.close()
        return

    paused = False
    _WIN2  = "Module 2 \u2013 Eyes Detection"
    cv2.namedWindow(_WIN2, cv2.WINDOW_NORMAL)
    _show_loading(_WIN2)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

        h, w    = frame.shape[:2]
        display = frame.copy()
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res     = face_mesh.process(rgb)

        if res.multi_face_landmarks:
            for face_lm in res.multi_face_landmarks:
                lm    = face_lm.landmark
                l_pts = [(int(lm[i].x * w), int(lm[i].y * h)) for i in _LEFT_EYE_IDXS]
                r_pts = [(int(lm[i].x * w), int(lm[i].y * h)) for i in _RIGHT_EYE_IDXS]

                l_ear = _compute_ear(l_pts)
                r_ear = _compute_ear(r_pts)
                avg   = (l_ear + r_ear) / 2.0

                # T1 – blink detection
                if avg < EAR_THRESHOLD:
                    if not eye_was_closed:
                        eye_was_closed = True
                    consec_closed += 1
                    consec_open    = 0
                else:
                    if eye_was_closed:
                        blink_count   += 1
                        eye_was_closed = False
                    consec_open   += 1
                    consec_closed  = 0

                # T3 – drowsiness state machine
                if consec_closed >= DROWSY_LIMIT:
                    drowsy_alert = True
                if drowsy_alert and consec_open >= CLEAR_LIMIT:
                    drowsy_alert = False

                # T3 – drowsiness overlay
                if drowsy_alert:
                    overlay = display.copy()
                    cv2.rectangle(overlay,
                                  (0, h // 2 - 55), (w, h // 2 + 55),
                                  (0, 0, 200), -1)
                    cv2.addWeighted(overlay, 0.65, display, 0.35, 0, display)
                    cv2.putText(display, "DROWSY!  Wake Up!",
                                (w // 2 - 180, h // 2 + 18),
                                cv2.FONT_HERSHEY_DUPLEX, 1.3,
                                (255, 255, 255), 3)

                # draw landmarks
                for pt in l_pts + r_pts:
                    cv2.circle(display, pt, 2, (0, 255, 220), -1)

                # T2 – EAR values
                cv2.putText(display, f"Left  EAR : {l_ear:.3f}", (10, 38),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 255), 2)
                cv2.putText(display, f"Right EAR : {r_ear:.3f}", (10, 68),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 255), 2)

                # T1 – blink count
                cv2.putText(display, f"Blinks    : {blink_count}", (10, 102),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (100, 255, 100), 2)

                # eye state indicator
                st      = "CLOSED" if eye_was_closed else "OPEN"
                st_col  = (0, 0, 255) if eye_was_closed else (0, 255, 80)
                cv2.putText(display, f"Status    : {st}", (10, 136),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, st_col, 2)

        cv2.rectangle(display, (0, h - 30), (w, h), (30, 30, 30), -1)
        cv2.putText(display, "ESC – Main Menu  |  P – Pause / Play", (8, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Module 2 – Eyes Detection", display)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key in (ord('p'), ord('P')):
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()


# ─────────────────────────────────────────────────────────────────────────────
#  MODULE 3 — FACE DETECTION
#  Implemented by: bsse23091
#  Tasks: T1 Emotion Recognition | T2 Head Pose | T3 Emotion History Log
# ─────────────────────────────────────────────────────────────────────────────

def _classify_head_pose(face_landmarks, frame_w, frame_h):
    """
    Estimate head orientation using MediaPipe FaceMesh geometry.

    Compares the nose tip (landmark 1) position relative to the eye midpoint
    (landmarks 133 and 362) to produce a cardinal direction label.

    Parameters:
        face_landmarks : mediapipe face landmark object
        frame_w        : int, frame width in pixels
        frame_h        : int, frame height in pixels

    Returns:
        str: one of 'Left', 'Right', 'Up', 'Down', or 'Forward'
    """
    lm = face_landmarks.landmark

    nose_x = int(lm[1].x   * frame_w)
    nose_y = int(lm[1].y   * frame_h)
    le_x   = int(lm[133].x * frame_w)
    le_y   = int(lm[133].y * frame_h)
    re_x   = int(lm[362].x * frame_w)
    re_y   = int(lm[362].y * frame_h)

    mid_x  = (le_x + re_x) // 2
    mid_y  = (le_y + re_y) // 2

    dx = nose_x - mid_x
    dy = nose_y - mid_y

    # decide which axis dominates
    if abs(dx) > abs(dy):
        if dx > 18:
            return "Right"
        elif dx < -18:
            return "Left"
    else:
        if dy > 18:
            return "Down"
        elif dy < -18:
            return "Up"

    return "Forward"


def face_detection(source):
    """
    Run the Face Detection module in real time.

    Performs three tasks on each frame:
      T1 – Emotion recognition via DeepFace every 5 frames; displays dominant
           emotion and confidence percentage.
      T2 – Head pose estimation via MediaPipe; shows Left/Right/Up/Down/Forward.
      T3 – Emotion history log: rolling 5-second window; 'Recent Mood' label
           shows the most frequently detected emotion in that window.

    Parameters:
        source : int | str | numpy.ndarray
                 Camera index, video file path, or BGR image array.

    Returns:
        None
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh    = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    haar_path    = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(haar_path)

    cur_emotion   = "Detecting..."
    cur_conf      = 0.0
    frame_idx     = 0
    emotion_log   = []   # list of (unix_timestamp, emotion_str)
    HIST_WINDOW   = 5.0  # seconds

    # ── Static image mode ─────────────────────────────────────────────────────
    if isinstance(source, np.ndarray):
        frame = source.copy()
        h, w  = frame.shape[:2]
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(60, 60))

        for (x, y, fw, fh) in faces:
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 130, 0), 2)
            roi = frame[y:y + fh, x:x + fw]
            try:
                analysis   = DeepFace.analyze(roi, actions=["emotion"],
                                              enforce_detection=False, silent=True)
                emotion    = analysis[0]["dominant_emotion"]
                confidence = analysis[0]["emotion"][emotion]
                cv2.putText(frame, f"{emotion}  {confidence:.1f}%",
                            (x, y - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8,
                            (0, 255, 100), 2)
            except Exception:
                pass

        cv2.imshow("Module 3 – Face Detection (Image)", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        face_mesh.close()
        return

    # ── Video / Webcam mode ───────────────────────────────────────────────────
    cap     = _open_capture(source)
    is_file = isinstance(source, str)

    if not cap.isOpened():
        print("[ERROR] Cannot open the video source.")
        face_mesh.close()
        return

    paused = False
    _WIN3  = "Module 3 \u2013 Face Detection"
    cv2.namedWindow(_WIN3, cv2.WINDOW_NORMAL)
    _show_loading(_WIN3)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

        frame_idx += 1
        h, w    = frame.shape[:2]
        display = frame.copy()

        # Haar cascade face bounding box
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        for (x, y, fw, fh) in faces:
            cv2.rectangle(display, (x, y), (x + fw, y + fh), (255, 130, 0), 2)

        # T1 – DeepFace emotion every 5 frames
        if frame_idx % 5 == 0 and len(faces) > 0:
            (x, y, fw, fh) = faces[0]
            roi = frame[y:y + fh, x:x + fw]
            try:
                analysis  = DeepFace.analyze(roi, actions=["emotion"],
                                             enforce_detection=False, silent=True)
                cur_emotion = analysis[0]["dominant_emotion"]
                cur_conf    = analysis[0]["emotion"][cur_emotion]
                emotion_log.append((time.time(), cur_emotion))
            except Exception:
                pass   # face too small or obscured — keep last known emotion

        # T2 – head pose via MediaPipe
        rgb        = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mesh_res   = face_mesh.process(rgb)
        head_pose  = "Unknown"

        if mesh_res.multi_face_landmarks:
            head_pose = _classify_head_pose(
                mesh_res.multi_face_landmarks[0], w, h
            )

        # T3 – prune emotion log and compute recent mood
        now        = time.time()
        emotion_log = [(t, e) for t, e in emotion_log if now - t <= HIST_WINDOW]
        recent_mood = "N/A"
        if emotion_log:
            counts      = Counter(e for _, e in emotion_log)
            recent_mood = counts.most_common(1)[0][0]

        # draw overlays
        cv2.putText(display, f"Emotion     : {cur_emotion}  ({cur_conf:.1f}%)",
                    (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 100), 2)
        cv2.putText(display, f"Head Pose   : {head_pose}",
                    (10, 74), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 200, 0), 2)
        cv2.putText(display, f"Recent Mood : {recent_mood}  (last 5s)",
                    (10, 108), cv2.FONT_HERSHEY_DUPLEX, 0.75, (200, 100, 255), 2)

        cv2.rectangle(display, (0, h - 30), (w, h), (30, 30, 30), -1)
        cv2.putText(display, "ESC – Main Menu  |  P – Pause / Play", (8, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Module 3 – Face Detection", display)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key in (ord('p'), ord('P')):
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()


# ─────────────────────────────────────────────────────────────────────────────
#  MODULE 4 — HAND DETECTION
#  Implemented by: bsse23004
#  Tasks: T1 Finger Counter | T2 Gesture Label | T3 Gesture Game
# ─────────────────────────────────────────────────────────────────────────────

# Gesture lookup: finger state tuple → (name, emoji)
# finger state = (thumb, index, middle, ring, pinky) — 1 = extended, 0 = folded
_GESTURE_MAP = {
    (0, 0, 0, 0, 0): ("Fist",      "✊"),
    (0, 1, 0, 0, 0): ("One",       "☝️"),
    (0, 1, 1, 0, 0): ("Peace",     "✌️"),
    (0, 1, 1, 1, 0): ("Three",     "🤟"),
    (0, 1, 1, 1, 1): ("Four",      "🖖"),
    (1, 1, 1, 1, 1): ("Open Hand", "🖐️"),
    (1, 0, 0, 0, 0): ("Thumbs Up", "👍"),
    (1, 1, 0, 0, 1): ("High Five", "🖐"),
    (1, 1, 1, 0, 0): ("Gun",       "🤙"),
}

_GAME_POOL = ["Fist", "One", "Peace", "Three", "Four", "Open Hand", "Thumbs Up"]


def _count_fingers(hand_lm, hand_label):
    """
    Count extended fingers and produce a state tuple from a MediaPipe hand object.

    Uses tip-vs-PIP y-axis comparison for fingers 2–5 and x-axis comparison
    for the thumb (mirrored depending on left/right hand).

    Parameters:
        hand_lm    : mediapipe NormalizedLandmarkList for one hand
        hand_label : str, 'Left' or 'Right' from mediapipe Handedness

    Returns:
        tuple: (total_count: int, state: tuple of 5 ints)
               state order: (thumb, index, middle, ring, pinky)
    """
    lm   = hand_lm.landmark
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    state = []

    # thumb — x-axis differs for left vs right hand
    if hand_label == "Right":
        thumb_up = lm[4].x < lm[3].x
    else:
        thumb_up = lm[4].x > lm[3].x
    state.append(1 if thumb_up else 0)

    # fingers 2-5
    for tip, pip in zip(tips, pips):
        state.append(1 if lm[tip].y < lm[pip].y else 0)

    return sum(state), tuple(state)


def hand_detection(source):
    """
    Run the Hand Detection module in real time.

    Performs three tasks:
      T1 – Finger counter: counts extended fingers per hand using landmark geometry.
      T2 – Gesture label: maps finger-state tuples to named gesture labels + emoji.
      T3 – Gesture game: displays a random target; awards 1 point when the user
           holds the matching gesture for 1 continuous second; shows score and
           a progress bar timer.

    Parameters:
        source : int | str | numpy.ndarray
                 Camera index, video file path, or BGR image array.

    Returns:
        None
    """
    mp_hands  = mp.solutions.hands
    mp_draw   = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    hands_model = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    game_score    = 0
    target        = random.choice(_GAME_POOL)
    hold_start    = None
    HOLD_NEEDED   = 1.0   # seconds to hold gesture

    # ── Static image mode ─────────────────────────────────────────────────────
    if isinstance(source, np.ndarray):
        frame = source.copy()
        h, w  = frame.shape[:2]
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res   = hands_model.process(rgb)

        if res.multi_hand_landmarks:
            for idx, hand_lm in enumerate(res.multi_hand_landmarks):
                mp_draw.draw_landmarks(
                    frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )
                label  = res.multi_handedness[idx].classification[0].label
                count, state = _count_fingers(hand_lm, label)
                name, emoji  = _GESTURE_MAP.get(state, (f"{count} fingers", ""))

                wrist_x = int(hand_lm.landmark[0].x * w)
                wrist_y = int(hand_lm.landmark[0].y * h)
                cv2.putText(frame, f"{name} {emoji}  ({count})",
                            (wrist_x - 50, wrist_y - 20),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 200), 2)

        cv2.imshow("Module 4 – Hand Detection (Image)", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        hands_model.close()
        return

    # ── Video / Webcam mode ───────────────────────────────────────────────────
    cap     = _open_capture(source)
    is_file = isinstance(source, str)

    if not cap.isOpened():
        print("[ERROR] Cannot open the video source.")
        hands_model.close()
        return

    paused = False
    _WIN4  = "Module 4 \u2013 Hand Detection"
    cv2.namedWindow(_WIN4, cv2.WINDOW_NORMAL)
    _show_loading(_WIN4)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

        h, w    = frame.shape[:2]
        display = frame.copy()
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res     = hands_model.process(rgb)

        live_gesture = None   # gesture detected on first hand this frame

        if res.multi_hand_landmarks:
            for idx, hand_lm in enumerate(res.multi_hand_landmarks):
                mp_draw.draw_landmarks(
                    display, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )
                hand_label   = res.multi_handedness[idx].classification[0].label
                count, state = _count_fingers(hand_lm, hand_label)
                name, emoji  = _GESTURE_MAP.get(state, (f"{count} fingers", ""))

                # T1 & T2 – show count and gesture name near wrist
                wx = int(hand_lm.landmark[0].x * w)
                wy = int(hand_lm.landmark[0].y * h)
                cv2.putText(display, f"{name} {emoji}",
                            (wx - 60, wy - 30),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 200), 2)
                cv2.putText(display, f"Fingers: {count}",
                            (wx - 60, wy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 100), 1)

                if idx == 0:
                    live_gesture = name

        # T3 – gesture game panel (top-right corner)
        panel_x = w - 260
        cv2.rectangle(display, (panel_x - 8, 8), (w - 8, 120), (40, 40, 40), -1)
        cv2.putText(display, f"Target : {target}", (panel_x, 38),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 200, 255), 2)
        cv2.putText(display, f"Score  : {game_score}", (panel_x, 68),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 200, 0), 2)

        if live_gesture == target:
            if hold_start is None:
                hold_start = time.time()
            elapsed  = time.time() - hold_start
            progress = min(elapsed / HOLD_NEEDED, 1.0)
            bar_len  = int(220 * progress)

            # progress bar background + fill
            cv2.rectangle(display, (panel_x, 80), (panel_x + 220, 100),
                          (60, 60, 60), -1)
            cv2.rectangle(display, (panel_x, 80), (panel_x + bar_len, 100),
                          (0, 220, 80), -1)
            cv2.putText(display, f"{int(progress * 100)}%",
                        (panel_x + 90, 97),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            if elapsed >= HOLD_NEEDED:
                game_score += 1
                target      = random.choice(_GAME_POOL)
                hold_start  = None
        else:
            hold_start = None   # reset if gesture breaks

        cv2.rectangle(display, (0, h - 30), (w, h), (30, 30, 30), -1)
        cv2.putText(display, "ESC – Main Menu  |  P – Pause / Play", (8, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Module 4 – Hand Detection", display)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key in (ord('p'), ord('P')):
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()
    hands_model.close()


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT SOURCE HANDLER
#  Implemented by: bsse23004
# ─────────────────────────────────────────────────────────────────────────────

def get_input_source():
    """
    Prompt the user to choose an input mode and return the corresponding source.

    Modes:
      1 – Live Webcam (returns camera index 0)
      2 – Video File  (returns file path string)
      3 – Image File  (returns BGR numpy.ndarray)

    Parameters:
        None

    Returns:
        tuple: (source, mode_label: str)
               source is int, str, or numpy.ndarray based on choice;
               mode_label is one of 'webcam', 'video', 'image', or None on error.
    """
    print("\n" + "─" * 48)
    print("  SELECT INPUT SOURCE")
    print("─" * 48)
    print("  [1]  Live Webcam Feed")
    print("  [2]  Video File Upload")
    print("  [3]  Image Upload")
    print("─" * 48)
    choice = input("  Enter choice (1-3): ").strip()

    if choice == "1":
        return 0, "webcam"

    elif choice == "2":
        path = input("  Video file path  : ").strip().strip('"').strip("'")
        return path, "video"

    elif choice == "3":
        path = input("  Image file path  : ").strip().strip('"').strip("'")
        img  = cv2.imread(path)
        if img is None:
            print(f"\n  [ERROR] Could not load image from: {path}")
            print("  Double-check the path and try again.\n")
            return None, None
        return img, "image"

    else:
        print("  Invalid choice — defaulting to webcam.")
        return 0, "webcam"


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN MENU + ENTRY POINT
#  Implemented by: bsse23091
# ─────────────────────────────────────────────────────────────────────────────

def _print_banner():
    """
    Print the application title banner to the console.

    Parameters:
        None
    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("    HCI ASSIGNMENT-4: MULTI-MODAL HUMAN DETECTION SYSTEM")
    print("    SE305T / MD445T  |  Spring-26  |  Dr. Muhammad Asif")
    print("    Group : bsse23053  |  bsse23004  |  bsse23091")
    print("=" * 60)


def main_menu():
    """
    Display the detection mode menu, collect user input, and dispatch to the
    appropriate detection module with the chosen input source.

    Loops indefinitely until the user chooses to exit (option 0).
    Within each detection window, ESC key returns control to this menu.

    Parameters:
        None
    Returns:
        None
    """
    while True:
        _print_banner()
        print("\n  DETECTION MODES")
        print("─" * 48)
        print("  [1]  Lips Detection")
        print("       Smile detection · MAR tracking · Lip-sync counter")
        print()
        print("  [2]  Eyes Detection")
        print("       Blink counter · EAR display · Drowsiness alert")
        print()
        print("  [3]  Face Detection")
        print("       Emotion recognition · Head pose · Mood history")
        print()
        print("  [4]  Hand Detection")
        print("       Finger count · Gesture label · Gesture game")
        print()
        print("  [0]  Exit")
        print("─" * 48)

        mode = input("  Choose a mode (0-4): ").strip()

        if mode == "0":
            print("\n  Exiting... See you next time!\n")
            break

        if mode not in ("1", "2", "3", "4"):
            print("\n  [!] Invalid option. Please enter a number from 0 to 4.\n")
            continue

        source, label = get_input_source()
        if source is None:
            continue

        print(f"\n  [INFO] Starting Module {mode} with input: {label}")
        print("  Press ESC inside the detection window to return here.\n")

        if mode == "1":
            lips_detection(source)
        elif mode == "2":
            eyes_detection(source)
        elif mode == "3":
            face_detection(source)
        elif mode == "4":
            hand_detection(source)

        print("\n  [INFO] Returned to main menu.\n")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main_menu()