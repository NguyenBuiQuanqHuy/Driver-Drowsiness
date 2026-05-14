# 🚗 Driver Drowsiness Detection System

> A real-time desktop application that monitors driver fatigue through facial analysis from webcam or video input — helping prevent road accidents caused by drowsy driving.

---

## 🎓 Nha Trang University — Student Project

<p align="left">
  <img src="https://github.com/user-attachments/assets/59a4bc7a-598b-4ff9-a396-77cfb5e75cf2" width="180" style="border-radius:50%;" />
</p>

| Field | Details |
|---|---|
| **Name** | Nguyễn Bùi Quang Huy |
| **Student ID** | 64130854 |
| **Date of Birth** | 21/08/2004 |
| **Major** | Information Technology |
| **Phone** | (+84) 364 454 522 |
| **Email** | huybui2108@gmail.com |

---

## 📌 Overview

Driver fatigue is one of the leading causes of traffic accidents worldwide. This project builds a **real-time drowsiness detection desktop app** (built with PyQt5) that uses a camera feed to monitor the driver's face and raises voice alerts when signs of fatigue or distraction are detected.

The system analyzes three key signals simultaneously:

| Signal | What it detects |
|---|---|
| 👁️ Eye Aspect Ratio (EAR) | Eyes closed for too long → drowsiness |
| 😮 Mouth Aspect Ratio (MAR) | Mouth open for too long → yawning |
| 🙆 Head Pose (x, y, z angles) | Head tilted down → microsleep; looking left/right/up → distracted |

---

## ✨ Features

- 🎥 **Live camera & video file support** — switch between webcam and any video file
- 👁️ **Eye monitoring** — detects prolonged eye closure using EAR calculation
- 😮 **Yawn detection** — identifies yawning using MAR calculation
- 🙆 **Head pose estimation** — detects head-down (microsleep) and sideways distraction using 3D angle tracking
- 🔊 **Voice alerts** — real-time text-to-speech warnings using `pyttsx3`
- ⏸️ **Pause / Resume** — full playback control
- 📊 **Alert History** — log of past drowsiness events
- 📈 **Performance Dashboard** — visualizes detection metrics over time

---

## 🛠️ Technologies Used

| Category | Library |
|---|---|
| Language | Python 3.x |
| Desktop GUI | PyQt5 |
| Computer Vision | OpenCV (`opencv-python`) |
| Face Landmark Detection | MediaPipe Face Mesh (468 landmarks) |
| Head Pose Estimation | OpenCV `solvePnP` + `RQDecomp3x3` |
| Voice Alert | pyttsx3 |
| Numerical Processing | NumPy |

---

## 📁 Project Structure

```
Driver-Drowsiness/
│
├── main.py                      # Entry point — launches the PyQt5 app
│
├── config/
│   └── config.py                # All thresholds (EAR, MAR, head angles, timing)
│
├── detection/
│   ├── face_mesh.py             # MediaPipe FaceMesh wrapper
│   ├── eye.py                   # EAR calculation + eye state logic
│   ├── mouth.py                 # MAR calculation + yawn detection logic
│   └── head_pose.py             # Head pose pipeline (3D angle estimation)
│
├── ui/
│   ├── app.py                   # Main window (QWidget)
│   ├── video_thread.py          # Background thread for video processing (QThread)
│   ├── voice.py                 # Voice alert module (pyttsx3, threaded)
│   ├── layout.py                # UI layout builder
│   ├── components.py            # Reusable UI components
│   ├── styles.py                # Stylesheet definitions
│   ├── handlers.py              # Signal handlers (image update, data update)
│   ├── history/                 # Alert history window & manager
│   └── performance/             # Performance dashboard window
│
├── utils/
│   └── g_helper.py              # Utility functions (BGR↔RGB, mirror image)
│
├── requirements.txt             # Python dependencies
└── README.md
```

---

## ⚙️ How It Works

```
Camera/Video
     ↓
MediaPipe Face Mesh (468 landmarks)
     ↓
┌────────────────────────────────────┐
│  EAR (Eye Aspect Ratio)           │ → Eyes closed > 1s  → DROWSY alert
│  MAR (Mouth Aspect Ratio)         │ → Mouth open > 1s   → YAWN alert
│  Head Pose (solvePnP → x, y, z)   │ → Head down > 2s    → MICROSLEEP alert
│                                    │   Head left/right   → DISTRACTED alert
└────────────────────────────────────┘
     ↓
PyQt5 UI — live video + real-time metrics
     ↓
pyttsx3 Voice Alert (cooldown: 3s between alerts)
```

### Detection thresholds (configurable in `config/config.py`)

| Parameter | Default | Meaning |
|---|---|---|
| `EYE_CLOSED_THRESHOLD` | 0.20 | EAR below this = eyes closed |
| `DROWSY_EYE_TIME` | 1.0 s | Eyes closed for this long = drowsy |
| `MAR_THRESHOLD` | 0.45 | MAR above this = mouth open |
| `YAWN_TIME` | 1.0 s | Mouth open for this long = yawn |
| `HEAD_DOWN_THRESHOLD` | -8.5° | Head tilt angle for "looking down" |
| `MICROSLEEP_TIME` | 2.0 s | Head down for this long = microsleep |
| `DISTRACTED_TIME` | 2.0 s | Head turned for this long = distracted |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A webcam (for live detection)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/NguyenBuiQuanqHuy/Driver-Drowsiness.git
cd Driver-Drowsiness

# 2. Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
python main.py
```

The app window will open. Click **📷 Camera** to start live detection, or **📂 Open Video** to load a video file.

---

## 🖥️ UI Overview

The desktop window includes:

- **Left panel** — live video feed with bounding box around the face, eye/mouth region highlights, and nose direction arrow
- **Right panel** — real-time metrics:
  - `EAR` value + time eyes have been closed
  - `MAR` value + time mouth has been open
  - `HEAD` direction (Forward / Left / Right / Down / Up) + duration
  - `ANGLE (x, y, z)` — raw head rotation angles
  - Status label: `AWAKE` / `EYES CLOSED` / `YAWN` / `NO FACE`
- **Bottom buttons** — Camera, Open Video, Pause/Resume, Alert History, Performance

---

## 🔮 Future Improvements

- [ ] Add alarm sound (`.wav`) as an alternative to voice alerts
- [ ] Support for multiple faces
- [ ] Package as a standalone executable (`.exe`) for easy deployment
- [ ] Mobile or embedded version (Raspberry Pi / Android)
- [ ] Export alert history as a PDF report

---

## 📄 License

This project is developed for academic purposes at **Nha Trang University**.  
Free to use and build upon with proper credit.

---

## 🙌 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) — real-time face landmark detection (468 points)
- [OpenCV](https://opencv.org/) — image processing and head pose estimation
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) — cross-platform desktop GUI framework
- [pyttsx3](https://pyttsx3.readthedocs.io/) — offline text-to-speech engine
