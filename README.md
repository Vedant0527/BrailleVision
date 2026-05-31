# 👁️ VISION | The Architecture of Accessibility

**BrailleVision Hackathon 2026 - Final Submission**

VISION is an enterprise-grade, edge-inference platform designed to translate physical Braille matrices into human-readable digital text. Moving beyond simple prototypes, this project features a fully decoupled architecture ensuring high performance, scalability, and strict local reproducibility for judging evaluation.

---

## 🚀 The Architecture
The platform is split into two independent nodes communicating via REST API:
1. **The Ingestion & Decryption Node (Frontend):** A high-contrast, brutalist React application built for maximum accessibility and visual clarity. 
2. **The Edge Engine (Backend):** A lightning-fast Python FastAPI server housing our custom YOLO structural cell extractor and tactile-to-digital translation dictionary.

### 🛠️ Tech Stack
* **Frontend:** React, Vite, Tailwind CSS v4
* **Backend:** Python 3.11, FastAPI, Uvicorn
* **AI/CV Engine:** YOLOv8 (Ultralytics), OpenCV, NumPy
* **Translation Logic:** Custom Python 6-bit binary mapping

---

## ⚙️ Local Setup & Run Instructions (Judge Verification)

To satisfy the official hackathon submission rules, follow these exact commands to clone, run, and verify this platform locally on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/Vedant0527/BrailleVision.git](https://github.com/Vedant0527/BrailleVision.git)
cd BrailleVision
