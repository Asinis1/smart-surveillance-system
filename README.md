# 🎥 Smart Surveillance System

> Real-time camera surveillance with **motion detection**, **face detection**, **auto-capture**, **recording**, and **alarm** — built with OpenCV in both Python and C++.

![CI](https://github.com/YOUR_USERNAME/smart-surveillance/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=c%2B%2B)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔴 **Motion Detection** | Frame-diff algorithm; draws bounding boxes around moving areas |
| 👤 **Face Detection** | Haar Cascade classifier — no internet, works offline |
| 📸 **Auto Capture** | Saves a `.jpg` every time motion is detected |
| 🎥 **Manual Recording** | Press `R` to toggle video recording (`.avi`) |
| 🔔 **Alarm System** | Plays a system beep on motion (cooldown configurable) |
| 🖥️ **HUD Overlay** | Live timestamp, face count, recording status on-screen |
| ⌨️ **CLI flags** | Camera index, headless mode, auto-record, disable alarm |

---

## 📂 Project Structure

```
smart-surveillance/
├── python/
│   ├── surveillance.py       # Python implementation
│   └── requirements.txt
├── cpp/
│   ├── surveillance.cpp      # C++ implementation
│   └── CMakeLists.txt
├── docs/
│   └── SETUP.md              # Detailed setup guide
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI
├── captures/                 # Auto-created: motion captures
├── recordings/               # Auto-created: video recordings
└── LICENSE
```

---

## 🚀 Quick Start

### Python

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/smart-surveillance.git
cd smart-surveillance/python

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python surveillance.py
```

### C++

```bash
cd smart-surveillance/cpp

# Install OpenCV (Ubuntu/Debian)
sudo apt-get install libopencv-dev cmake

# Build
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Run
./surveillance
```

**Windows (C++):**
```
# Install OpenCV via vcpkg or download pre-built binaries from opencv.org
cmake .. -DCMAKE_BUILD_TYPE=Release -DOpenCV_DIR=C:/opencv/build
cmake --build . --config Release
```

---

## ⌨️ Controls (both versions)

| Key | Action |
|-----|--------|
| `Q` / `ESC` | Quit |
| `S` | Save screenshot manually |
| `R` | Toggle video recording |

---

## 🔧 CLI Options

```
--camera N       Camera index to use (default: 0)
--no-window      Headless mode — no GUI window (server use)
--record         Start recording immediately on launch
--no-alarm       Disable audio alarm
```

**Examples:**

```bash
# Use second camera, start recording immediately
python surveillance.py --camera 1 --record

# Headless server mode (e.g. Raspberry Pi)
python surveillance.py --no-window --no-alarm

# C++ with flags
./surveillance --camera 0 --record
```

---

## ⚙️ Configuration

Edit the `Config` class at the top of either file:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MOTION_THRESHOLD` | `25` | Pixel difference to count as change |
| `MIN_CONTOUR_AREA` | `500` | Min area (px²) to count as motion |
| `ALARM_COOLDOWN` | `5` | Seconds between alarm triggers |
| `FPS` | `20` | Recording frame rate |

---

## 🧠 How It Works

```
Camera Frame
     │
     ▼
Convert to Grayscale + Gaussian Blur
     │
     ├──► Frame Difference → Threshold → Contours ──► Motion Boxes
     │
     └──► Haar Cascade ──────────────────────────────► Face Boxes
                │
                ▼
         Draw HUD Overlay
                │
         ┌──────┴──────┐
         ▼             ▼
    Show Window    Save / Record / Alarm
```

**Motion Detection Algorithm:**
1. Convert frame to grayscale and blur (removes noise)
2. Compute absolute difference with previous frame
3. Threshold → binary mask
4. Dilate to fill gaps
5. Find contours; filter by area

**Face Detection:**  
Uses OpenCV's pre-trained Haar Cascade (`haarcascade_frontalface_default.xml`) — ships with OpenCV, no additional download needed.

---

## 📸 Output Files

```
captures/
├── motion_20250615_143022.jpg    ← auto-saved on motion
├── manual_20250615_143155.jpg    ← saved when pressing S
recordings/
└── rec_20250615_143022.avi       ← video recordings
```

---

## 🖥️ Tested On

- Ubuntu 22.04 / 24.04
- Windows 10 / 11
- macOS 13+
- Raspberry Pi OS (headless mode)

---

## 🗺️ Roadmap

- [ ] Email / Telegram notification on motion
- [ ] Web dashboard (Flask/FastAPI)
- [ ] RTSP stream support (IP cameras)
- [ ] Deep learning face recognition (dlib / face_recognition)
- [ ] Object detection (YOLO)
- [ ] Multi-camera support

---

## 📄 License

MIT © [YOUR_USERNAME](https://github.com/YOUR_USERNAME)