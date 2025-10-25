# 🎯 AI Proctored Online Examination System

![GitHub repo](https://img.shields.io/badge/AI%20Proctoring-Active-blue)  ![Python](https://img.shields.io/badge/Python-3.8%2B-green)  ![Status-Live](https://img.shields.io/badge/Status-Ready%20to%20Use-success)

A professional AI-powered online exam system with **real-time cheating detection** — built to simulate real corporate online tests.

## 🔥 Overview

An AI-powered online examination system built using **Python (Tkinter, OpenCV, YOLOv8)** that simulates real company-style proctored exams. It automatically detects and penalizes cheating while conducting and evaluating the test.

## 🚀 Key Features

* ✅ **Real-time Webcam Monitoring** (Face detection using OpenCV)
* 📵 **Phone Detection using YOLOv8 (Object Detection)**
* 🎤 **Mic-based Sound Monitoring for background noise**
* 🔄 **Window Focus Tracking – Detects tab switching**
* 📊 **Auto Scoring: +2 (Correct), -2 (Wrong), -0.25 (Cheating)**
* ✅ **Eligibility Check after completion**
* 📄 **Detailed Result with each Question & Cheating Log**

## 🛠️ Tech Stack

* **Python** (Core Logic & GUI)
* **Tkinter** — GUI Framework
* **OpenCV** — Face Detection
* **YOLOv8** — Mobile Phone Detection
* **SoundDevice + NumPy** — Audio Monitoring
* **Threading** — For real-time multitasking

## 📥 How to Run

```bash
pip install opencv-python pillow ultralytics sounddevice numpy
python exam_system.py
```

## 📌 Usage Flow

1. System starts with **live camera & rules displayed**
2. Student attempts **MCQ-based exam (10 questions)**
3. Any **cheating action is detected + penalty applied instantly**
4. At the end — **Final Score + Eligibility + Cheating Report** shown
