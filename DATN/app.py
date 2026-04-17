import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

from g_helper import bgr2rgb, rgb2bgr, mirrorImage
from fp_helper import pipelineHeadTiltPose, draw_face_bbox_fp

# ===== IMPORT THÊM =====
from eye import process_eye_state
from mouth import process_mouth_state
from config import *

# Initiate Camera
cap = cv2.VideoCapture(0)

# ===== BIẾN TIME =====
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 25

frame_time = 1 / fps

eye_closed_time = 0
mouth_open_time = 0

with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Mirror image (Optional)
        image = mirrorImage(image)

        # Generate face mesh
        results = face_mesh.process(bgr2rgb(image))

        # ===== RESET ALERT =====
        drowsy_alert = False
        yawn_alert = False

        # Processing Face Landmarks
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:

                # FACE MESH ----------------------------------------
                img_h, img_w, _ = image.shape
                draw_face_bbox_fp(image, face_landmarks, img_w, img_h)

                # HEAD TILT POSE -----------------------------------
                head_tilt_pose = pipelineHeadTiltPose(image, face_landmarks)

                # ===== MẮT =====
                eye_closed_time, drowsy_alert = process_eye_state(
                    image, face_landmarks, img_w, img_h,
                    eye_closed_time, frame_time,
                    EYE_CLOSED_THRESHOLD, DROWSY_EYE_TIME
                )

                # ===== MIỆNG =====
                mouth_open_time, yawn_alert = process_mouth_state(
                    image, face_landmarks, img_w, img_h,
                    mouth_open_time, frame_time,
                    MAR_THRESHOLD, YAWN_TIME
                )

        # ===== TRẠNG THÁI CHUNG =====
            h, w, _ = image.shape
            if drowsy_alert:    
                cv2.putText(image, "BUON NGU", (30,h-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)

            elif yawn_alert:
                cv2.putText(image, "NGAP", (30,h-80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,0,255), 3)

            else:
                cv2.putText(image, "TINH TAO", (30,h-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)

        # Show Image
        cv2.imshow('Face Mesh', image)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()