# 📖 Detailed Setup Guide

## Python — Step by Step

### 1. Python Kur (3.8 veya üstü)

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Windows
# https://python.org/downloads adresinden indir
```

### 2. OpenCV Kur

```bash
pip install opencv-python numpy
```

### 3. Kameranı Test Et

```python
import cv2
cap = cv2.VideoCapture(0)   # 0 = ilk kamera
ret, frame = cap.read()
print("Kamera çalışıyor:", ret)
cap.release()
```

### 4. Çalıştır

```bash
cd python
python surveillance.py
```

---

## C++ — Step by Step

### Ubuntu/Debian

```bash
# Gerekli paketleri kur
sudo apt update
sudo apt install -y build-essential cmake libopencv-dev

# Proje klasörüne git
cd cpp

# Build et
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Çalıştır
./surveillance
```

### Windows (Visual Studio)

1. [OpenCV İndir](https://opencv.org/releases/) → Windows binary
2. [CMake İndir](https://cmake.org/download/)
3. CMake GUI aç:
   - Source: `cpp/` klasörü
   - Build: `cpp/build/` klasörü
   - Configure → `OpenCV_DIR` = `C:/opencv/build`
   - Generate → Open Project
4. Visual Studio'da `Release` modda build et

### macOS

```bash
brew install opencv cmake
cd cpp
mkdir build && cd build
cmake ..
make -j$(nproc)
./surveillance
```

---

## Raspberry Pi (Headless / Sunucu Modu)

```bash
# OpenCV kur
pip install opencv-python-headless numpy

# Headless çalıştır (ekran yok, sadece kayıt)
python surveillance.py --no-window --record
```

---

## Sorun Giderme

### "Cannot open camera 0"
- Kameranın takılı olduğundan emin ol
- `--camera 1` veya `--camera 2` dene
- Linux'ta: `ls /dev/video*` ile mevcut kameraları gör

### OpenCV Import Hatası
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

### C++ Build Hatası: "OpenCV not found"
```bash
# OpenCV path'ini manuel belirt
cmake .. -DOpenCV_DIR=/usr/lib/x86_64-linux-gnu/cmake/opencv4
```

### Yavaş FPS
- `Config.FPS` değerini düşür
- `Config.FACE_NEIGHBORS` değerini artır (yüz tespiti daha hızlı ama daha az hassas)
- Çözünürlüğü düşür: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`