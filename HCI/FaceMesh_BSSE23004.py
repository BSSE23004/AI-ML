import cv2
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat 

FACE_OVAL = [
    (10,338),(338,297),(297,332),(332,284),(284,251),(251,389),(389,356),
    (356,454),(454,323),(323,361),(361,288),(288,397),(397,365),(365,379),
    (379,378),(378,400),(400,377),(377,152),(152,148),(148,176),(176,149),
    (149,150),(150,136),(136,172),(172,58),(58,132),(132,93),(93,234),
    (234,127),(127,162),(162,21),(21,54),(54,103),(103,67),(67,109),(109,10)
]

LEFT_EYE = [
    (263,249),(249,390),(390,373),(373,374),(374,380),(380,381),(381,382),
    (382,362),(362,263),(263,466),(466,388),(388,387),(387,386),(386,385),
    (385,384),(384,398),(398,362)
]

RIGHT_EYE = [
    (33,7),(7,163),(163,144),(144,145),(145,153),(153,154),(154,155),
    (155,133),(133,33),(33,246),(246,161),(161,160),(160,159),(159,158),
    (158,157),(157,173),(173,133)
]

LEFT_EYEBROW = [
    (276,283),(283,282),(282,295),(295,285),(285,300),(300,293),(293,334),
    (334,296),(296,336)
]

RIGHT_EYEBROW = [
    (46,53),(53,52),(52,65),(65,55),(55,70),(70,63),(63,105),(105,66),(66,107)
]

LIPS_OUTER = [
    (61,146),(146,91),(91,181),(181,84),(84,17),(17,314),(314,405),(405,321),
    (321,375),(375,291),(291,409),(409,270),(270,269),(269,267),(267,0),
    (0,37),(37,39),(39,40),(40,185),(185,61)
]

LIPS_INNER = [
    (78,95),(95,88),(88,178),(178,87),(87,14),(14,317),(317,402),(402,318),
    (318,324),(324,308),(308,415),(415,310),(310,311),(311,312),(312,13),
    (13,82),(82,81),(81,80),(80,191),(191,78)
]

LEFT_IRIS  = [(474,475),(475,476),(476,477),(477,474)]
RIGHT_IRIS = [(469,470),(470,471),(471,472),(472,469)]

# Simple tesselation approximation: connect each landmark to a few neighbours
# using known MediaPipe face mesh triangulation pairs (subset for speed)
TESSELATION = [
    (127,34),(34,139),(139,127),(11,0),(0,37),(37,11),(232,231),(231,120),
    (120,232),(72,37),(37,39),(39,72),(128,121),(121,47),(47,128),(232,121),
    (121,128),(128,232),(104,69),(69,67),(67,104),(175,171),(171,148),(148,175),
    (157,154),(154,155),(155,157),(118,50),(50,101),(101,118),(73,72),(72,39),
    (39,73),(122,121),(121,128),(128,122),(0,267),(267,269),(269,0),(11,302),
    (302,267),(267,11),(251,189),(189,190),(190,251),(346,280),(280,347),
    (347,346),(452,350),(350,349),(349,452),(302,325),(325,303),(303,302),
    (269,303),(303,304),(304,269),(409,291),(291,375),(375,409),(78,191),
    (191,80),(80,78),(415,310),(310,308),(308,415),(324,318),(318,325),
    (325,324),(397,288),(288,361),(361,397),(365,379),(379,397),(397,365),
    (288,435),(435,397),(397,288),(278,294),(294,279),(279,278),(294,460),
    (460,279),(279,294),(341,463),(463,464),(464,341),(453,464),(464,465),
    (465,453),(357,465),(465,412),(412,357),(343,412),(412,399),(399,343),
    (360,363),(363,440),(440,360),(420,429),(429,360),(360,420),(368,364),
    (364,394),(394,368),(395,379),(379,378),(378,395),(400,377),(377,152),
    (152,400),(170,211),(211,202),(202,170),(140,176),(176,149),(149,140),
    (150,136),(136,172),(172,150),(58,132),(132,93),(93,58),(234,227),
    (227,116),(116,234),(127,162),(162,21),(21,127),(54,103),(103,67),(67,54),
    (109,10),(10,338),(338,109),(297,332),(332,284),(284,297),(251,389),
    (389,356),(356,251),(454,323),(323,361),(361,454),(288,397),(397,365),
    (365,288),(379,378),(378,400),(400,379),(377,152),(152,148),(148,377),
    (176,149),(149,150),(150,176),(136,172),(172,58),(58,136),(132,93),
    (93,234),(234,132),(127,162),(162,21),(21,127),(54,103),(103,67),(67,54),
]

ALL_CONNECTIONS = {
    "tesselation": (TESSELATION,               (255, 255, 255),   1),
    "oval":        (FACE_OVAL,                 (255, 255, 255),  2),
    "left_eye":    (LEFT_EYE,                  (255, 255, 255),  1),
    "right_eye":   (RIGHT_EYE,                 (255, 255, 255),  1),
    "l_brow":      (LEFT_EYEBROW,              (255, 255, 255),1),
    "r_brow":      (RIGHT_EYEBROW,             (255, 255, 255),1),
    "lips_outer":  (LIPS_OUTER,                (255, 255, 255),   2),
    "lips_inner":  (LIPS_INNER,                (255, 255, 255),  1),
    "l_iris":      (LEFT_IRIS,                 (255, 255, 255),  2),
    "r_iris":      (RIGHT_IRIS,                (255, 255, 255),  2),
}

# ── Download model ─────────────────────────────────────────────────────────────
MODEL_PATH = "face_landmarker.task"
MODEL_URL  = ("https://storage.googleapis.com/mediapipe-models/"
              "face_landmarker/face_landmarker/float16/1/face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    print("Downloading face_landmarker.task (~30 MB)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Done.")

# ── Build detector ─────────────────────────────────────────────────────────────
detector = vision.FaceLandmarker.create_from_options(
    vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        num_faces=2,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
)

# ── Drawing ────────────────────────────────────────────────────────────────────
def draw_mesh(frame, landmarks):
    h, w = frame.shape[:2]
    for _, (pairs, color, thick) in ALL_CONNECTIONS.items():
        for s, e in pairs:
            if s >= len(landmarks) or e >= len(landmarks):
                continue
            x0 = int(landmarks[s].x * w); y0 = int(landmarks[s].y * h)
            x1 = int(landmarks[e].x * w); y1 = int(landmarks[e].y * h)
            cv2.line(frame, (x0, y0), (x1, y1), color, thick, cv2.LINE_AA)
    # dots on every landmark
    for lm in landmarks:
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (cx, cy), 1, (0, 255, 100), -1, cv2.LINE_AA)

# ── Main loop ──────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Running — q: quit | s: screenshot")
shot = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.detect(Image(image_format=ImageFormat.SRGB, data=rgb))

    for face_lms in result.face_landmarks:
        draw_mesh(frame, face_lms)

    # HUD
    h, w = frame.shape[:2]
    bar = frame.copy()
    cv2.rectangle(bar, (0, 0), (w, 38), (0, 0, 0), -1)
    cv2.addWeighted(bar, 0.55, frame, 0.45, 0, frame)
    cv2.putText(frame,
                f"Faces: {len(result.face_landmarks)}  |  Student: BSSE23004  |  q=quit  s=save",
                (8, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 180), 1, cv2.LINE_AA)

    cv2.imshow("Face Mesh  -  BSSE23004", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        name = f"face_mesh_capture_{shot}.png"
        cv2.imwrite(name, frame)
        print(f"Saved {name}")
        shot += 1

cap.release()
cv2.destroyAllWindows()
detector.close()