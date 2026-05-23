"""
Smart Surveillance System - Python Implementation
Features: Motion Detection, Face Detection, Hand Gesture Recognition
License: MIT
"""

import cv2, os, time, datetime, threading, argparse, numpy as np
from pathlib import Path

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

class Config:
    CAPTURE_DIR      = "captures"
    RECORD_DIR       = "recordings"
    MOTION_THRESHOLD = 25
    MIN_CONTOUR_AREA = 5000
    ALARM_COOLDOWN   = 5
    FPS              = 20
    FACE_SCALE       = 1.1
    FACE_NEIGHBORS   = 5

def trigger_alarm():
    print("\a")
    try:
        import winsound; winsound.Beep(1000, 500)
    except ImportError:
        pass

class GestureRecognizer:
    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            self.hands = None
            return
        self.mp_hands  = mp.solutions.hands
        self.mp_draw   = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.hands     = self.mp_hands.Hands(
            static_image_mode=False, max_num_hands=2,
            min_detection_confidence=0.7, min_tracking_confidence=0.6)

    def _fingers_up(self, lms):
        # Baş parmak: x yerine MCP'ye göre kontrol (ayna sorununu çözer)
        thumb_up = abs(lms[4].x - lms[0].x) > abs(lms[3].x - lms[0].x)
        up = [thumb_up]
        # Diğer 4 parmak: y ekseninde (uç, 2. eklemden yukarda mı?)
        for tip, joint in zip([8,12,16,20],[6,10,14,18]):
            up.append(lms[tip].y < lms[joint].y)
        return up

    def classify(self, lms):
        up    = self._fingers_up(lms)
        total = sum(up)
        # Yumruk: hiç parmak yok (baş parmak dahil)
        if total == 0:                                          return "TAS (Yumruk)"
        # Açık el: 4 veya 5 parmak açık
        if total >= 4:                                          return "KAGIT (Acik El)"
        # Makas: sadece işaret + orta
        if up[1] and up[2] and not up[3] and not up[4]:        return "MAKAS"
        # Beğendim: sadece baş parmak
        if up[0] and not up[1] and not up[2] and not up[3] and not up[4]: return "BEGENDIM"
        # Bir: sadece işaret
        if up[1] and not up[2] and not up[0]:                  return "BIR"
        # Üç: işaret + orta + yüzük
        if up[1] and up[2] and up[3] and not up[4]:            return "UC"
        # Dört: baş parmak kapalı, diğerleri açık
        if not up[0] and up[1] and up[2] and up[3] and up[4]:  return "DORT"
        return f"{total} parmak"

    def process(self, frame):
        if self.hands is None:
            return [], frame
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        detections = []
        if results.multi_hand_landmarks:
            h, w = frame.shape[:2]
            for hand_lms in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style())
                lms = hand_lms.landmark
                xs  = [lm.x*w for lm in lms]
                ys  = [lm.y*h for lm in lms]
                box = (int(min(xs))-15, int(min(ys))-15,
                       int(max(xs))+15, int(max(ys))+15)
                detections.append((box, self.classify(lms)))
        return detections, frame

class SmartSurveillance:
    def __init__(self, camera_index=0, show_window=True,
                 enable_recording=False, alarm_on_motion=True):
        self.camera_index     = camera_index
        self.show_window      = show_window
        self.enable_recording = enable_recording
        self.alarm_on_motion  = alarm_on_motion
        self.running = self.recording = False
        self.last_alarm_time = 0
        self._motion_boxes   = []
        self.prev_gray       = None
        self.writer          = None
        Path(Config.CAPTURE_DIR).mkdir(exist_ok=True)
        Path(Config.RECORD_DIR).mkdir(exist_ok=True)
        cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade)
        self.gesture = GestureRecognizer()
        print("="*55)
        print("  Smart Surveillance System  |  Python + OpenCV")
        print(f"  El Algılama: {'AKTIF' if MEDIAPIPE_AVAILABLE else 'DEVRE DISI (mediapipe kurunuz)'}")
        print("  S=Ekran  R=Kayit  Q=Cikis")
        print("="*55)

    def _timestamp(self): return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def _save_capture(self, frame, reason="motion"):
        path = f"{Config.CAPTURE_DIR}/{reason}_{self._timestamp()}.jpg"
        cv2.imwrite(path, frame)
        print(f"[FOTO] {path}")

    def _start_recording(self, frame):
        if self.writer: return
        h,w  = frame.shape[:2]
        path = f"{Config.RECORD_DIR}/rec_{self._timestamp()}.avi"
        self.writer    = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"XVID"), Config.FPS, (w,h))
        self.recording = True
        print(f"[KAYIT BASLADI] {path}")

    def _stop_recording(self):
        if self.writer:
            self.writer.release(); self.writer = None; self.recording = False
            print("[KAYIT DURDURULDU]")

    def _detect_motion(self, gray):
        if self.prev_gray is None:
            self.prev_gray = gray; return False, []
        diff   = cv2.absdiff(self.prev_gray, gray)
        thresh = cv2.threshold(diff, Config.MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.prev_gray = gray
        boxes = [cv2.boundingRect(c) for c in cnts if cv2.contourArea(c) > Config.MIN_CONTOUR_AREA]
        return len(boxes)>0, boxes

    def _detect_faces(self, gray):
        return self.face_cascade.detectMultiScale(gray, Config.FACE_SCALE, Config.FACE_NEIGHBORS, minSize=(30,30))

    def _draw_hud(self, frame, motion, faces, hands):
        h,w  = frame.shape[:2]
        now  = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        ov   = frame.copy()
        cv2.rectangle(ov,(0,0),(w,40),(0,0,0),-1)
        cv2.addWeighted(ov,0.6,frame,0.4,0,frame)
        cv2.putText(frame, now, (8,26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)
        sc = (0,60,255) if motion else (0,210,80)
        cv2.putText(frame, "HAREKET!" if motion else "IZLENIYOR", (w-200,26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, sc, 2)
        for (x,y,bw,bh) in self._motion_boxes:
            cv2.rectangle(frame,(x,y),(x+bw,y+bh),(0,60,255),2)
        for (fx,fy,fw,fh) in faces:
            cv2.rectangle(frame,(fx,fy),(fx+fw,fy+fh),(80,255,80),2)
            cv2.putText(frame,"YUZ",(fx,fy-8),cv2.FONT_HERSHEY_SIMPLEX,0.55,(80,255,80),2)
        for ((x1,y1,x2,y2), gesture) in hands:
            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,200,0),2)
            sz = cv2.getTextSize(gesture, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
            cv2.rectangle(frame,(x1,y1-34),(x1+sz[0]+8,y1),(255,200,0),-1)
            cv2.putText(frame, gesture,(x1+4,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,0),2)
        info = f"Yuz:{len(faces)}  El:{len(hands)}  Kayit:{'EVET' if self.recording else 'HAYIR'}  [S]Ekran [R]Kayit [Q]Cikis"
        cv2.rectangle(frame,(0,h-30),(w,h),(0,0,0),-1)
        cv2.putText(frame,info,(8,h-8),cv2.FONT_HERSHEY_SIMPLEX,0.42,(160,160,160),1)
        return frame

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"[HATA] Kamera {self.camera_index} acilamadi!"); return
        self.running = True
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05); continue
            gray  = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),(21,21),0)
            motion, motion_boxes   = self._detect_motion(gray)
            faces                  = self._detect_faces(gray)
            hands, frame           = self.gesture.process(frame)
            self._motion_boxes     = motion_boxes
            if motion:
                now = time.time()
                self._save_capture(frame,"motion")
                if self.alarm_on_motion and (now-self.last_alarm_time)>Config.ALARM_COOLDOWN:
                    threading.Thread(target=trigger_alarm,daemon=True).start()
                    self.last_alarm_time = now
            if self.recording and self.writer:
                self.writer.write(frame)
            display = self._draw_hud(frame.copy(), motion, faces, hands)
            if self.show_window:
                cv2.imshow("Smart Surveillance System", display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"),27): break
            elif key == ord("s"):   self._save_capture(frame,"manual")
            elif key == ord("r"):
                self._stop_recording() if self.recording else self._start_recording(frame)
        self._stop_recording(); cap.release(); cv2.destroyAllWindows()
        print("[OK] Sistem durduruldu.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--camera",    type=int, default=0)
    p.add_argument("--no-window", action="store_true")
    p.add_argument("--record",    action="store_true")
    p.add_argument("--no-alarm",  action="store_true")
    a = p.parse_args()
    SmartSurveillance(a.camera, not a.no_window, a.record, not a.no_alarm).run()