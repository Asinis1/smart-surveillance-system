/**
 * Smart Surveillance System — C++ Implementation
 * Requires: OpenCV 4.x
 * Build:    see CMakeLists.txt
 */

#include <opencv2/opencv.hpp>
#include <opencv2/objdetect.hpp>
#include <iostream>
#include <filesystem>
#include <chrono>
#include <thread>
#include <ctime>
#include <sstream>
#include <iomanip>

namespace fs = std::filesystem;
using namespace cv;
using namespace std;

// ─────────────────────────────────────────────
//  CONFIG
// ─────────────────────────────────────────────
struct Config {
    static constexpr int    MOTION_THRESHOLD = 25;
    static constexpr double MIN_CONTOUR_AREA = 500.0;
    static constexpr int    ALARM_COOLDOWN   = 5;   // seconds
    static constexpr int    FPS              = 20;
    static constexpr double FACE_SCALE       = 1.1;
    static constexpr int    FACE_NEIGHBORS   = 5;
    static const string     CAPTURE_DIR;
    static const string     RECORD_DIR;
};
const string Config::CAPTURE_DIR = "captures";
const string Config::RECORD_DIR  = "recordings";

// ─────────────────────────────────────────────
//  UTILITIES
// ─────────────────────────────────────────────
string timestamp() {
    auto now   = chrono::system_clock::now();
    time_t t   = chrono::system_clock::to_time_t(now);
    tm local   = *localtime(&t);
    ostringstream ss;
    ss << put_time(&local, "%Y%m%d_%H%M%S");
    return ss.str();
}

string currentDateTime() {
    auto now   = chrono::system_clock::now();
    time_t t   = chrono::system_clock::to_time_t(now);
    tm local   = *localtime(&t);
    ostringstream ss;
    ss << put_time(&local, "%Y-%m-%d  %H:%M:%S");
    return ss.str();
}

void triggerAlarm() {
    // Cross-platform bell
    cout << "\a" << flush;
}

// ─────────────────────────────────────────────
//  SURVEILLANCE CLASS
// ─────────────────────────────────────────────
class SmartSurveillance {
public:
    SmartSurveillance(int cameraIndex = 0,
                      bool showWindow = true,
                      bool enableRecording = false,
                      bool alarmOnMotion = true)
        : cameraIndex_(cameraIndex),
          showWindow_(showWindow),
          enableRecording_(enableRecording),
          alarmOnMotion_(alarmOnMotion),
          recording_(false),
          lastAlarmTime_(0)
    {
        fs::create_directories(Config::CAPTURE_DIR);
        fs::create_directories(Config::RECORD_DIR);

        // Load Haar cascade (ships with OpenCV)
        string cascadePath = string(getenv("OPENCV_HAARCASCADES") ? getenv("OPENCV_HAARCASCADES") : "")
                             + "/haarcascade_frontalface_default.xml";
        // Fallback: current dir
        if (!faceCascade_.load(cascadePath)) {
            faceCascade_.load("haarcascade_frontalface_default.xml");
        }
    }

    void run() {
        VideoCapture cap(cameraIndex_);
        if (!cap.isOpened()) {
            cerr << "[ERROR] Cannot open camera " << cameraIndex_ << "\n";
            return;
        }

        printBanner();

        Mat frame, gray, prevGray;
        VideoWriter writer;

        while (true) {
            cap >> frame;
            if (frame.empty()) {
                cerr << "[WARN] Empty frame — retrying...\n";
                this_thread::sleep_for(chrono::milliseconds(50));
                continue;
            }

            cvtColor(frame, gray, COLOR_BGR2GRAY);
            GaussianBlur(gray, gray, Size(21, 21), 0);

            // Motion
            vector<Rect> motionBoxes;
            bool motion = detectMotion(gray, prevGray, motionBoxes);

            // Faces
            vector<Rect> faces;
            detectFaces(gray, faces);

            // Reactions
            if (motion) {
                saveCapture(frame, "motion");
                auto now = time(nullptr);
                if (alarmOnMotion_ && difftime(now, lastAlarmTime_) > Config::ALARM_COOLDOWN) {
                    thread(triggerAlarm).detach();
                    lastAlarmTime_ = now;
                }
            }

            if (recording_ && writer.isOpened()) {
                writer.write(frame);
            }

            // Draw HUD
            Mat display = frame.clone();
            drawHUD(display, motion, motionBoxes, faces, recording_);

            if (showWindow_) {
                imshow("Smart Surveillance System", display);
            }

            int key = waitKey(1) & 0xFF;
            if (key == 'q' || key == 27) break;          // Q or ESC
            else if (key == 's') saveCapture(frame, "manual");
            else if (key == 'r') {
                if (recording_) {
                    writer.release();
                    recording_ = false;
                    cout << "[⏹]  Recording stopped.\n";
                } else {
                    string fname = Config::RECORD_DIR + "/rec_" + timestamp() + ".avi";
                    int    w     = frame.cols, h = frame.rows;
                    writer.open(fname, VideoWriter::fourcc('X','V','I','D'), Config::FPS, {w, h});
                    recording_ = true;
                    cout << "[🎥] Recording: " << fname << "\n";
                }
            }
        }

        if (writer.isOpened()) writer.release();
        cap.release();
        destroyAllWindows();
        cout << "[✓] Surveillance stopped.\n";
    }

private:
    // ── Motion ──────────────────────────────────
    bool detectMotion(const Mat& gray, Mat& prevGray, vector<Rect>& boxes) {
        if (prevGray.empty()) { prevGray = gray.clone(); return false; }

        Mat diff, thresh;
        absdiff(prevGray, gray, diff);
        threshold(diff, thresh, Config::MOTION_THRESHOLD, 255, THRESH_BINARY);
        dilate(thresh, thresh, Mat(), Point(-1,-1), 2);

        vector<vector<Point>> cnts;
        findContours(thresh, cnts, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

        prevGray = gray.clone();
        for (auto& c : cnts) {
            if (contourArea(c) > Config::MIN_CONTOUR_AREA)
                boxes.push_back(boundingRect(c));
        }
        return !boxes.empty();
    }

    // ── Faces ────────────────────────────────────
    void detectFaces(const Mat& gray, vector<Rect>& faces) {
        if (faceCascade_.empty()) return;
        faceCascade_.detectMultiScale(gray, faces,
            Config::FACE_SCALE, Config::FACE_NEIGHBORS,
            0, Size(30,30));
    }

    // ── Save ─────────────────────────────────────
    void saveCapture(const Mat& frame, const string& reason) {
        string fname = Config::CAPTURE_DIR + "/" + reason + "_" + timestamp() + ".jpg";
        imwrite(fname, frame);
        cout << "[📸] Saved: " << fname << "\n";
    }

    // ── HUD ──────────────────────────────────────
    void drawHUD(Mat& frame, bool motion,
                 const vector<Rect>& motionBoxes,
                 const vector<Rect>& faces,
                 bool recording) {

        int w = frame.cols, h = frame.rows;

        // Top bar
        Mat overlay = frame.clone();
        rectangle(overlay, {0,0}, {w,36}, {0,0,0}, FILLED);
        addWeighted(overlay, 0.55, frame, 0.45, 0, frame);

        // Timestamp
        putText(frame, currentDateTime(), {8,24},
                FONT_HERSHEY_SIMPLEX, 0.6, {200,200,200}, 1);

        // Status
        Scalar statusColor = motion ? Scalar(0,80,255) : Scalar(0,200,80);
        string  statusText = motion ? "MOTION DETECTED" : "MONITORING";
        putText(frame, statusText, {w-240, 24},
                FONT_HERSHEY_SIMPLEX, 0.6, statusColor, 2);

        // Motion boxes
        for (auto& r : motionBoxes)
            rectangle(frame, r, {0,80,255}, 2);

        // Face boxes
        for (auto& f : faces) {
            rectangle(frame, f, {80,255,80}, 2);
            putText(frame, "FACE", {f.x, f.y-6},
                    FONT_HERSHEY_SIMPLEX, 0.5, {80,255,80}, 1);
        }

        // Bottom bar
        string info = "Faces:" + to_string(faces.size()) +
                      "  Rec:" + (recording ? "YES" : "NO") +
                      "  [Q]Quit  [S]Screenshot  [R]Record";
        rectangle(frame, {0, h-28}, {w, h}, {0,0,0}, FILLED);
        putText(frame, info, {8, h-8},
                FONT_HERSHEY_SIMPLEX, 0.45, {160,160,160}, 1);
    }

    void printBanner() {
        cout << string(55,'=') << "\n"
             << "  Smart Surveillance System  |  C++ + OpenCV\n"
             << string(55,'=') << "\n"
             << "  Q / ESC — Quit\n"
             << "  S       — Save screenshot\n"
             << "  R       — Toggle recording\n"
             << string(55,'=') << "\n";
    }

    int     cameraIndex_;
    bool    showWindow_, enableRecording_, alarmOnMotion_, recording_;
    time_t  lastAlarmTime_;
    CascadeClassifier faceCascade_;
};

// ─────────────────────────────────────────────
//  MAIN
// ─────────────────────────────────────────────
int main(int argc, char* argv[]) {
    int  camera  = 0;
    bool noWin   = false;
    bool record  = false;
    bool noAlarm = false;

    for (int i = 1; i < argc; ++i) {
        string a(argv[i]);
        if      (a == "--camera"    && i+1 < argc) camera  = stoi(argv[++i]);
        else if (a == "--no-window") noWin   = true;
        else if (a == "--record")    record  = true;
        else if (a == "--no-alarm")  noAlarm = true;
        else if (a == "--help") {
            cout << "Usage: surveillance [--camera N] [--no-window] [--record] [--no-alarm]\n";
            return 0;
        }
    }

    SmartSurveillance sys(camera, !noWin, record, !noAlarm);
    sys.run();
    return 0;
}