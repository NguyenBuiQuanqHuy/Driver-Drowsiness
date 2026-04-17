import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp

# 1. Khởi tạo CUDA Session cho Hopenet
cuda_providers = [('CUDAExecutionProvider', {'device_id': 0}), 'CPUExecutionProvider']
hopenet_sess = ort.InferenceSession("hopenet_lite.onnx", providers=cuda_providers)

# 2. Khởi tạo MediaPipe cho EAR/MAR
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

def get_head_pose(face_img):
    img = cv2.resize(face_img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = img.astype(np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    img = (img - mean) / std
    img = img.transpose(2, 0, 1)[np.newaxis, ...]

    output = hopenet_sess.run(None, {hopenet_sess.get_inputs()[0].name: img})

    idx_tensor = np.arange(66, dtype=np.float32)
    results = []

    for i in range(3):
        logits = output[i][0]
        exp = np.exp(logits - np.max(logits))
        probs = exp / np.sum(exp)

        angle = np.sum(probs * idx_tensor) * 3 - 99
        results.append(angle)

    return results

# 3. Vòng lặp chính
cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, frame = cap.read()
    
    
    frame = cv2.flip(frame, 1)
    results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            # TÍNH EAR/MAR TẠI ĐÂY (Dùng tọa độ MediaPipe)
            # ... (code tính EAR/MAR của bạn) ...
            
            # TÍNH HEAD POSE BẰNG DEEP LEARNING (CUDA)
            # Cắt mặt
            h, w, _ = frame.shape
            x_min = int(min([lm.x for lm in landmarks.landmark]) * w)
            y_min = int(min([lm.y for lm in landmarks.landmark]) * h)
            x_max = int(max([lm.x for lm in landmarks.landmark]) * w)
            y_max = int(max([lm.y for lm in landmarks.landmark]) * h)
            
            face_roi = frame[max(0, y_min):y_max, max(0, x_min):x_max]
            if face_roi.size > 0:
                yaw, pitch, roll = get_head_pose(face_roi)
                
                # Logic cảnh báo tổng hợp
                if pitch < -20: # Tài xế đang gục đầu
                    cv2.putText(frame, "CANH BAO: GUC DAU!", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    cv2.imshow("Hopenet CUDA + EAR/MAR", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break