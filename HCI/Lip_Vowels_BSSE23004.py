import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

print(cv2.getBuildInformation())

# ==============================
# Load Face Landmarker model
# ==============================
model_path = "face_landmarker.task"   # download from MediaPipe site

BaseOptions = python.BaseOptions
FaceLandmarker = vision.FaceLandmarker
FaceLandmarkerOptions = vision.FaceLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)

# ==============================
# Lip indices (important points)
# ==============================
UPPER_LIP = [13, 14]
LOWER_LIP = [14, 17]
LEFT_LIP = 61
RIGHT_LIP = 291

# ==============================
# Vowel Classification Function
# ==============================
def classify_vowel(width, height):
    ratio = height / width if width != 0 else 0

    if ratio > 0.6:
        return "A (Open Mouth)"
    elif ratio > 0.4:
        return "E (Wide)"
    elif ratio < 0.2:
        return "I (Narrow)"
    elif 0.2 <= ratio <= 0.35:
        return "O/U (Round)"
    else:
        return "Unknown"

# ==============================
# Callback Function
# ==============================
def process_result(result, output_image, timestamp_ms):
    global frame

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            h, w, _ = frame.shape

            # Extract lip points
            left = face_landmarks[LEFT_LIP]
            right = face_landmarks[RIGHT_LIP]
            top = face_landmarks[13]
            bottom = face_landmarks[14]

            # Convert to pixel coords
            lx, ly = int(left.x * w), int(left.y * h)
            rx, ry = int(right.x * w), int(right.y * h)
            tx, ty = int(top.x * w), int(top.y * h)
            bx, by = int(bottom.x * w), int(bottom.y * h)

            # Draw points
            cv2.circle(frame, (lx, ly), 3, (0, 255, 0), -1)
            cv2.circle(frame, (rx, ry), 3, (0, 255, 0), -1)
            cv2.circle(frame, (tx, ty), 3, (0, 0, 255), -1)
            cv2.circle(frame, (bx, by), 3, (0, 0, 255), -1)

            # Calculate lip width & height
            width = np.linalg.norm(np.array([lx, ly]) - np.array([rx, ry]))
            height = np.linalg.norm(np.array([tx, ty]) - np.array([bx, by]))

            # Classify vowel
            vowel = classify_vowel(width, height)

            # Display result
            cv2.putText(frame, f"Vowel: {vowel}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

# ==============================
# Initialize Landmarker
# ==============================
landmarker = FaceLandmarker.create_from_options(options)

# ==============================
# Webcam
# ==============================
cap = cv2.VideoCapture(0)

timestamp = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # 🔥 GET RESULT (important)
    result = landmarker.detect_for_video(mp_image, timestamp)

    timestamp += 1

    # 🔥 PROCESS RESULT HERE (NOT in callback)
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            h, w, _ = frame.shape

            left = face_landmarks[61]
            right = face_landmarks[291]
            top = face_landmarks[13]
            bottom = face_landmarks[14]

            lx, ly = int(left.x * w), int(left.y * h)
            rx, ry = int(right.x * w), int(right.y * h)
            tx, ty = int(top.x * w), int(top.y * h)
            bx, by = int(bottom.x * w), int(bottom.y * h)

            # Draw lips
            cv2.circle(frame, (lx, ly), 3, (0, 255, 0), -1)
            cv2.circle(frame, (rx, ry), 3, (0, 255, 0), -1)
            cv2.circle(frame, (tx, ty), 3, (0, 0, 255), -1)
            cv2.circle(frame, (bx, by), 3, (0, 0, 255), -1)

            # Compute width & height
            width = np.linalg.norm(np.array([lx, ly]) - np.array([rx, ry]))
            height = np.linalg.norm(np.array([tx, ty]) - np.array([bx, by]))

            vowel = classify_vowel(width, height)

            cv2.putText(frame, f"Vowel: {vowel}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Lip Detection & Vowel Classification", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()