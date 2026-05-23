# 🎥 Akıllı Güvenlik Sistemi

> Gerçek zamanlı kamera takibi — **hareket algılama**, **yüz algılama**, **el hareketi tanıma**, **otomatik fotoğraf kaydetme**, **video kaydı** ve **alarm sistemi** — Python ve C++ ile geliştirildi.

![CI](https://github.com/YOUR_USERNAME/smart-surveillance-system/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=c%2B%2B)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)
![Lisans](https://img.shields.io/badge/Lisans-MIT-yellow)

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🔴 **Hareket Algılama** | Kare farkı algoritması ile hareket tespiti, kutucuk çizimi |
| 👤 **Yüz Algılama** | Haar Cascade sınıflandırıcı — internet bağlantısı gerekmez |
| 🤚 **El Hareketi Tanıma** | Taş, Kağıt, Makas, Beğendim ve daha fazlası (sadece Python) |
| 📸 **Otomatik Fotoğraf** | Hareket algılandığında `.jpg` olarak otomatik kaydeder |
| 🎥 **Video Kaydı** | `R` tuşu ile video kaydını başlatır/durdurur (`.avi`) |
| 🔔 **Alarm Sistemi** | Hareket algılandığında sesli uyarı verir |
| 🖥️ **Ekran Üstü Bilgi** | Canlı saat, yüz sayısı, kayıt durumu ekranda gösterilir |
| ⌨️ **Komut Satırı** | Kamera seçimi, sessiz mod, otomatik kayıt gibi seçenekler |

---

## 📂 Proje Yapısı

```
smart-surveillance-system/
├── python/
│   ├── surveillance.py       # Python sürümü (el hareketi dahil)
│   └── requirements.txt
├── cpp/
│   ├── surveillance.cpp      # C++ sürümü
│   └── CMakeLists.txt
├── docs/
│   └── SETUP.md              # Kurulum rehberi
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI
└── LICENSE
```

---

## 🚀 Hızlı Başlangıç

### Python

```bash
# 1. Repoyu klonla
git clone https://github.com/YOUR_USERNAME/smart-surveillance-system.git
cd smart-surveillance-system/python

# 2. Gerekli kütüphaneleri kur
pip install opencv-python numpy mediapipe==0.10.13

# 3. Çalıştır
py surveillance.py
```

### C++

```bash
cd smart-surveillance-system/cpp

# OpenCV kur (Ubuntu/Debian)
sudo apt-get install libopencv-dev cmake

# Derle
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Çalıştır
./surveillance
```

**Windows (C++):**
```bash
# vcpkg ile OpenCV kur
git clone https://github.com/microsoft/vcpkg
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install opencv:x64-windows
.\vcpkg integrate install

# Derle
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release

# Çalıştır
.\Release\surveillance.exe
```

---

## ⌨️ Kontroller

| Tuş | İşlev |
|-----|-------|
| `S` | Ekran görüntüsü al |
| `R` | Video kaydını başlat / durdur |
| `Q` / `ESC` | Programdan çık |

---

## 🤚 Tanınan El Hareketleri (Python)

| Hareket | Ekranda Görünen |
|---------|----------------|
| ✊ Yumruk | `TAS (Yumruk)` |
| ✋ Açık el | `KAGIT (Acik El)` |
| ✌️ İki parmak | `MAKAS` |
| 👍 Baş parmak | `BEGENDIM` |
| ☝️ Bir parmak | `BIR` |
| 3 parmak | `UC` |
| 4 parmak | `DORT` |

---

## ⚙️ Ayarlar

`surveillance.py` veya `surveillance.cpp` dosyasının üstündeki `Config` sınıfını düzenle:

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `MOTION_THRESHOLD` | `25` | Hareket hassasiyeti (düşük = daha hassas) |
| `MIN_CONTOUR_AREA` | `5000` | Minimum hareket alanı (px²) |
| `ALARM_COOLDOWN` | `5` | Alarmlar arası bekleme süresi (saniye) |
| `FPS` | `20` | Video kayıt hızı |

---

## 🧠 Nasıl Çalışır?

```
Kamera Görüntüsü
      │
      ▼
Gri Tonlama + Gaussian Bulanıklaştırma
      │
      ├──► Kare Farkı → Eşikleme → Konturlar ──► Hareket Kutuları
      │
      └──► Haar Cascade ────────────────────────► Yüz Kutuları
                │
         El Landmark (MediaPipe) ────────────────► Jest Tanıma
                │
          HUD Katmanı Çiz
                │
      ┌─────────┴─────────┐
      ▼                   ▼
  Pencereyi Göster    Kaydet / Kayıt Al / Alarm
```

---

## 📸 Kaydedilen Dosyalar

```
captures/
├── motion_20260523_180053.jpg    ← hareket algılandığında otomatik
├── manual_20260523_180155.jpg    ← S tuşuna basınca
recordings/
└── rec_20260523_180053.avi       ← video kayıtları
```

---

## 🖥️ Test Edildiği Sistemler

- Windows 10 / 11
- Ubuntu 22.04 / 24.04
- macOS 13+
- Raspberry Pi OS (ekransız mod)

---

## 🗺️ Gelecek Özellikler

- [ ] E-posta / Telegram bildirimi
- [ ] Web arayüzü (Flask/FastAPI)
- [ ] IP kamera desteği (RTSP)
- [ ] Derin öğrenme ile yüz tanıma
- [ ] YOLO ile nesne tespiti
- [ ] Çoklu kamera desteği

---

## 📄 Lisans

MIT © [Asinis1](https://github.com/Asinis1)
