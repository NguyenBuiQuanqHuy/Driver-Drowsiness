import cv2
import mediapipe as mp

from config import *
from eye import process_eye
from mouth import mouth_aspect_ratio

mp_face_mesh = mp.solutions.face_mesh

video_path = r"C:\Users\huybu\Downloads\7702109485658.mp4"
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 25

frame_time = 1 / fps
delay = int(1000 / fps)

eye_closed_time = 0
mouth_open_time = 0

with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.8) as face_mesh:
    prev_landmarks = None 
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False

        results = face_mesh.process(frame_rgb)

        frame_rgb.flags.writeable = True

        microsleep_alert = False
        drowsy_alert = False
        yawn_alert = False

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]

            # ===== MẮT =====
            ear_left = process_eye(frame, lm,
                                   [33,160,158,133,153,144],
                                   w, h, (0,255,0))

            ear_right = process_eye(frame, lm,
                                    [362,385,387,263,373,380],
                                    w, h, (255,0,0))

            ear_avg = (ear_left + ear_right) / 2

            if ear_avg < EYE_CLOSED_THRESHOLD:
                eye_closed_time += frame_time
            else:
                eye_closed_time = 0

            # ===== MIỆNG =====
            mar, mouth_pts = mouth_aspect_ratio(lm, w, h)

            # BOX MIỆNG
            xs = [p[0] for p in mouth_pts]
            ys = [p[1] for p in mouth_pts]
            cv2.rectangle(frame, (min(xs), min(ys)),
                          (max(xs), max(ys)), (0,0,255), 2)

            if mar > MAR_THRESHOLD:
                mouth_open_time += frame_time
            else:
                mouth_open_time = 0

            # ===== LOGIC =====
            if eye_closed_time > DROWSY_EYE_TIME:
                drowsy_alert = True

            if mouth_open_time > YAWN_TIME:
                yawn_alert = True

            # ===== HIỂN THỊ DEBUG (GIỮ NGUYÊN) =====
            cv2.putText(frame, f"EAR: {ear_avg:.2f}", (30,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            cv2.putText(frame, f"MAR: {mar:.2f}", (30,230),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

            cv2.putText(frame, f"EyeTime: {eye_closed_time:.2f}s", (30,260),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        # ===== CẢNH BÁO =====
        if drowsy_alert:
            cv2.putText(frame, "BUON NGU", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)

        if yawn_alert:
            cv2.putText(frame, "NGAP", (50,100),  # 👈 xuống dưới
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,0,255), 3)

        if not drowsy_alert and not yawn_alert:
            cv2.putText(frame, "TINH TAO", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)

        cv2.imshow("Microsleep Detection", frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()