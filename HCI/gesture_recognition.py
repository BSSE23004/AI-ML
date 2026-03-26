import cv2
import mediapipe as mp
import time
import os
import urllib.request


# Notes to run this code
# use the following command in an python virtual environment 
# pip install opencv-python mediapipe
# then run the following command
# python gesture_recognition.py




# ── Model Download ──────────────────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
if not os.path.exists(MODEL_PATH):
    print("Downloading model (~25 MB)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Done.")

# ── Auto-detect working camera ──────────────────────────────────────────────
def find_camera():
    for index in range(5):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"Using camera index: {index}")
                return cap
            cap.release()
    return None

# ── MediaPipe Setup ─────────────────────────────────────────────────────────
BaseOptions        = mp.tasks.BaseOptions
HandLandmarker     = mp.tasks.vision.HandLandmarker
HandLandmarkerOpts = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode  = mp.tasks.vision.RunningMode

options = HandLandmarkerOpts(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.5,
)

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

# ── Feature Extraction ──────────────────────────────────────────────────────
def count_fingers(lm):
    fingers = []
    fingers.append(abs(lm[4].x - lm[5].x) > abs(lm[3].x - lm[5].x))  # Thumb
    for tip_id, pip_id in [(8,6),(12,10),(16,14),(20,18)]:
        fingers.append(lm[tip_id].y < lm[pip_id].y)
    return fingers

# ── Rule Engine ─────────────────────────────────────────────────────────────
def recognize_gesture(fingers):
    thumb, index, middle, ring, pinky = fingers
    total = sum(fingers)
    if total == 5:                                                       return "Stop"
    if index and middle and not thumb and not ring and not pinky:        return "Peace"
    if thumb and not index and not middle and not ring and not pinky:    return "Thumbs Up"
    return "Unknown"

# ── Drawing ─────────────────────────────────────────────────────────────────
def draw_landmarks(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (255, 100, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 5, (0, 255, 255), -1)
        cv2.circle(frame, (x, y), 5, (0, 0, 0), 1)

def draw_overlay(frame, gesture, fingers):
    h, w = frame.shape[:2]
    color_map = {
        "Peace":     (0, 255, 150),
        "Thumbs Up": (0, 200, 255),
        "Stop":      (0, 100, 255),
        "Unknown":   (180, 180, 180),
    }
    color = color_map.get(gesture, (255, 255, 255))
    label = f"Gesture: {gesture}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 3)
    cv2.rectangle(frame, (10, 10), (tw + 20, th + 25), (0, 0, 0), -1)
    cv2.putText(frame, label, (15, th + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
    names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    bw, bh = 80, 30
    sx = (w - len(names) * (bw + 8)) // 2
    sy = h - 55
    for i, (name, state) in enumerate(zip(names, fingers)):
        x  = sx + i * (bw + 8)
        bg = (0, 210, 80) if state else (50, 50, 50)
        cv2.rectangle(frame, (x, sy), (x + bw, sy + bh), bg, -1)
        cv2.putText(frame, name, (x + 4, sy + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    cap = find_camera()
    if cap is None:
        print("\n========================================")
        print("ERROR: No working camera found.")
        print("Try these fixes:")
        print("  1. Run:  ls /dev/video*")
        print("  2. Run:  sudo usermod -aG video $USER  then re-login")
        print("  3. If on a VM, enable USB/webcam passthrough in VM settings")
        print("  4. Run this script directly from terminal, NOT Jupyter")
        print("========================================")
        return

    print("Running... press Q in the window to quit.")

    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lost camera feed.")
                break

            frame  = cv2.flip(frame, 1)
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts_ms  = int(time.time() * 1000)
            result = landmarker.detect_for_video(mp_img, ts_ms)

            if result.hand_landmarks:
                lm      = result.hand_landmarks[0]
                fingers = count_fingers(lm)
                gesture = recognize_gesture(fingers)
                draw_landmarks(frame, lm)
                draw_overlay(frame, gesture, fingers)
            else:
                cv2.putText(frame, "No Hand Detected", (15, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 100), 2)

            cv2.imshow("Hand Gesture Recognition - ITU HCI CA3", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()