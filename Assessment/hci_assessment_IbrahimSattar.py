"""
HCI Vision Assessment — SE305T (Spring-26)
Student : Ibrahim Sattar   |   BSSE23004
Date    : 6-May-2026
Contains:
    Task 1  — Blink Detection       (Challenge A, 15 marks)
    Task 3  — Gesture Recognition   (Challenge C, 25 marks)
Run: python hci_assessment_IbrahimSattar.py
     Then choose 1 or 3 at the prompt.
"""

import cv2
import mediapipe as mp
import numpy as np
import sys


# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def euclidean(p1, p2):
    """Euclidean distance between two (x, y) tuples."""
    return np.linalg.norm(np.array(p1, dtype=float) - np.array(p2, dtype=float))


# =============================================================================
# TASK 1 — BLINK DETECTION
# =============================================================================

# Landmark indices as specified in the assessment sheet
LEFT_EYE_IDX  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33,  160, 158, 133, 153, 144]

EAR_THRESHOLD = 0.2


def compute_ear(landmarks, indices, img_w, img_h):
    """
    Eye Aspect Ratio (EAR):
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    indices = [p1, p2, p3, p4, p5, p6]
    """
    pts = [
        (landmarks[i].x * img_w, landmarks[i].y * img_h)
        for i in indices
    ]
    A = euclidean(pts[1], pts[5])   # vertical — outer pair
    B = euclidean(pts[2], pts[4])   # vertical — inner pair
    C = euclidean(pts[0], pts[3])   # horizontal
    return (A + B) / (2.0 * C)


def run_blink_detection():
    """Task 1: real-time blink counter using FaceMesh EAR."""
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        face_mesh.close()
        return

    blink_count = 0
    eyes_closed = False          # tracks the closed phase of a blink cycle

    print("[INFO] Blink Detection running. Press ESC to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Empty frame received, skipping.")
            continue

        img_h, img_w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = face_mesh.process(rgb)
        rgb.flags.writeable = True

        ear_avg = 1.0   # default "open"

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            left_ear  = compute_ear(lm, LEFT_EYE_IDX,  img_w, img_h)
            right_ear = compute_ear(lm, RIGHT_EYE_IDX, img_w, img_h)
            ear_avg = (left_ear + right_ear) / 2.0

            # ── Blink transition detector ──────────────────────────────────
            if ear_avg < EAR_THRESHOLD:
                # Eyes are currently closed → enter or stay in closed phase
                eyes_closed = True
            elif eyes_closed:
                # Eyes just reopened → complete open→close→open cycle
                blink_count += 1
                eyes_closed = False

        # ── HUD overlay ───────────────────────────────────────────────────
        status_text  = "CLOSED" if eyes_closed else "OPEN"
        status_color = (0, 0, 255) if eyes_closed else (0, 255, 0)

        cv2.putText(frame, f"Blinks: {blink_count}",
                    (30, 55), cv2.FONT_HERSHEY_SIMPLEX,
                    1.4, (0, 255, 0), 3, cv2.LINE_AA)

        cv2.putText(frame, f"EAR: {ear_avg:.3f}",
                    (30, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 0), 2, cv2.LINE_AA)

        cv2.putText(frame, f"Eyes: {status_text}",
                    (30, 135), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, status_color, 2, cv2.LINE_AA)

        cv2.putText(frame, "Press ESC to exit",
                    (30, img_h - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Task 1: Blink Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:   # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()
    print(f"[INFO] Session ended. Total blinks detected: {blink_count}")


# =============================================================================
# TASK 3 — GESTURE RECOGNITION
# =============================================================================

# MediaPipe hand landmark indices
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 2
FINGER_TIPS = [8,  12, 16, 20]   # index, middle, ring, pinky tips
FINGER_PIPS = [6,  10, 14, 18]   # corresponding PIP joints

# Gesture lookup table: (total_finger_count, thumb_extended) → label
GESTURE_MAP = {
    (0, False): "Fist",
    (1, False): "One",
    (2, False): "Peace",
    (5, False): "Open Hand",
    (1, True):  "Thumbs Up",
    (5, True):  "High Five",
}


def count_extended_fingers(hand_landmarks, handedness_label):
    """
    Return (total_count: int, thumb_extended: bool).

    Thumb  — compared along x-axis, accounting for handedness.
    Others — TIP.y < PIP.y  ⟹  extended.
    """
    lm = hand_landmarks.landmark
    thumb_extended = False
    count = 0

    # ── Thumb (x-axis, handedness-aware) ──────────────────────────────────
    # MediaPipe's "Right"/"Left" labels are from the model's view (mirrored).
    # For "Right" hand (person's left in mirrored view):
    #   thumb tip is extended when its x < MCP x  (tip points left on screen)
    # For "Left" hand (person's right in mirrored view):
    #   thumb tip is extended when its x > MCP x  (tip points right on screen)
    if handedness_label == "Right":
        if lm[THUMB_TIP].x < lm[THUMB_MCP].x:
            thumb_extended = True
            count += 1
    else:  # "Left"
        if lm[THUMB_TIP].x > lm[THUMB_MCP].x:
            thumb_extended = True
            count += 1

    # ── Four fingers (y-axis) ──────────────────────────────────────────────
    for tip_idx, pip_idx in zip(FINGER_TIPS, FINGER_PIPS):
        if lm[tip_idx].y < lm[pip_idx].y:   # tip above PIP  →  extended
            count += 1

    return count, thumb_extended


def classify_gesture(count, thumb_extended):
    key = (count, thumb_extended)
    return GESTURE_MAP.get(key, f"{count} fingers")


def run_gesture_recognition():
    """Task 3: real-time hand gesture recognition for up to 2 hands."""
    mp_hands = mp.solutions.hands
    mp_draw  = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        hands.close()
        return

    print("[INFO] Gesture Recognition running. Press ESC to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Empty frame received, skipping.")
            continue

        img_h, img_w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        rgb.flags.writeable = True

        if results.multi_hand_landmarks:
            for hand_lm, hand_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness,
            ):
                # Draw skeleton
                mp_draw.draw_landmarks(
                    frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

                handedness_label = hand_info.classification[0].label  # "Left" / "Right"
                count, thumb_ext = count_extended_fingers(hand_lm, handedness_label)
                gesture = classify_gesture(count, thumb_ext)

                # Anchor text near the wrist landmark
                wrist = hand_lm.landmark[0]
                wx = int(wrist.x * img_w)
                wy = int(wrist.y * img_h)

                # Background rect for readability
                label_lines = [
                    f"{handedness_label} hand",
                    f"Fingers: {count}",
                    gesture,
                ]
                x_off = max(wx - 60, 5)
                y_base = max(wy - 80, 10)

                for i, line in enumerate(label_lines):
                    y_pos = y_base + i * 30
                    # shadow
                    cv2.putText(frame, line,
                                (x_off + 1, y_pos + 1),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.85, (0, 0, 0), 3, cv2.LINE_AA)
                    # foreground
                    color = (0, 255, 255) if i < 2 else (0, 255, 0)
                    cv2.putText(frame, line,
                                (x_off, y_pos),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.85, color, 2, cv2.LINE_AA)

        cv2.putText(frame, "Press ESC to exit",
                    (30, img_h - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Task 3: Gesture Recognition", frame)
        if cv2.waitKey(1) & 0xFF == 27:   # ESC 
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("[INFO] Gesture recognition session ended.")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("=" * 56)
    print("  HCI Vision Assessment  |  SE305T Spring-26")
    print("  Ibrahim Sattar  —  BSSE23004  —  ITU Lahore")
    print("=" * 56)
    print("  1 → Task 1 : Blink Detection      (Challenge A)")
    print("  3 → Task 3 : Gesture Recognition  (Challenge C)")
    print("=" * 56)

    choice = input("Enter task number (1 or 3): ").strip()

    if choice == "1":
        run_blink_detection()
    elif choice == "3":
        run_gesture_recognition()
    else:
        print("[ERROR] Invalid choice. Please run again and enter 1 or 3.")
        sys.exit(1)
