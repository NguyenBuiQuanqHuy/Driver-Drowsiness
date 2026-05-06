import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

class FaceMeshDetector:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.8
        )

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None

    def release(self):
        self.face_mesh.close()