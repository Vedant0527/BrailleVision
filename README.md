````markdown
# 👁️ BrailleVision

### AI-Powered Real-Time Braille-to-Text Translation Engine

BrailleVision is an end-to-end accessibility platform that converts physical Braille into readable English text using Computer Vision, Deep Learning, and Natural Language Processing. The system detects Braille cells from an image, preserves their spatial arrangement, translates them into text, and delivers results in real time through a modern web interface.

---

## 🚀 Overview

Millions of visually impaired individuals rely on Braille for communication and education. However, most people cannot read Braille, creating a significant accessibility barrier.

BrailleVision bridges this gap by enabling anyone to capture an image of Braille text and instantly receive a readable English translation.

### ✨ Key Features

- Real-Time Braille Recognition
- YOLOv8-Based Braille Cell Detection
- Custom CNN Character Classification
- Curved-Line Spatial Sorting for Warped Documents
- Automatic Word Segmentation
- NLP-Based Error Correction
- FastAPI + React Full-Stack Architecture
- Optimized Low-Latency Processing Pipeline

---

## 🏗️ System Architecture

```text
[ React Frontend ]
        │
        ▼
[ FastAPI Backend ]
        │
        ▼
[ YOLOv8 Braille Detection ]
        │
        ▼
[ Spatial Sorting Engine ]
        │
        ▼
[ CNN Character Classification ]
        │
        ▼
[ NLP Error Correction ]
        │
        ▼
[ English Text Output ]
````

---

## 🧠 Technical Pipeline

### 1. Image Ingestion

The React frontend allows users to upload Braille images.

The FastAPI backend receives the image and performs preprocessing before passing it to the detection pipeline.

To improve detection near image boundaries, an additional border is injected around the image before inference.

### 2. Braille Cell Detection (YOLOv8)

A custom-trained YOLOv8 model identifies individual Braille cells.

**Model File**

```text
backend/model/best.pt
```

#### Features

* High-sensitivity detection threshold
* Optimized Non-Maximum Suppression (NMS)
* Robust performance on low-contrast and shadowed images
* Edge-cell recovery using image padding

### 3. Spatial Sorting Engine

Braille documents are often photographed at angles or on curved surfaces.

Traditional OCR sorting fails under these conditions.

BrailleVision uses a custom spatial tracking algorithm that:

* Groups cells into rows dynamically
* Tracks curved reading lines
* Maintains proper reading order
* Automatically detects word boundaries

### 4. CNN Character Classification

Each detected Braille cell is cropped and passed to a custom PyTorch Convolutional Neural Network.

**Model File**

```text
backend/model/braille_cnn_real_epoch6.pth
```

#### Preprocessing Pipeline

```text
Image
 ↓
Grayscale
 ↓
Resize (64x64)
 ↓
Tensor Conversion
 ↓
Normalization
 ↓
CNN Prediction
```

#### CNN Architecture

```text
Input (1 × 64 × 64)

Conv2D (1 → 32)
BatchNorm
ReLU
MaxPool

Conv2D (32 → 64)
BatchNorm
ReLU
MaxPool

Conv2D (64 → 128)
BatchNorm
ReLU
MaxPool

Conv2D (128 → 256)
BatchNorm
ReLU
MaxPool

Flatten
Linear (4096 → 512)
Dropout (0.3)
Linear (512 → 26)
```

The network predicts one of 26 English alphabet classes for each Braille cell.

### 5. NLP Post-Processing

Minor classification errors are corrected using a custom fuzzy-matching layer powered by Python's `difflib`.

Examples:

```text
INDIE → INDIA
GREASPRODECS → GREATPROJECT
```

This improves readability while preserving the original translation intent.

---

## 📊 Dataset & Training

### Dataset

Roboflow Universe – Braille Detection Dataset

### Training Statistics

* 137,000+ augmented training samples
* 6 training epochs
* 95.6% validation accuracy

---

## 💻 Technology Stack

### Frontend

* React.js
* Vite
* JavaScript
* HTML5
* CSS3

### Backend

* FastAPI
* Uvicorn
* Python

### AI & Computer Vision

* YOLOv8
* PyTorch
* OpenCV
* NumPy
* Pillow

### NLP

* difflib

### Development Tools

* Git
* GitHub
* Virtual Environment (venv)

---

## 📁 Project Structure

```text
BrailleVision-Prod/

├── frontend/
│   ├── src/
│   ├── public/
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── cnn_engine.py
│   ├── translate.py
│   ├── cell_extractor.py
│   ├── braille_dict.py
│   │
│   ├── model/
│   │   ├── best.pt
│   │   └── braille_cnn_real_epoch6.pth
│   │
│   ├── debug_crops/
│   └── api_env/
│
└── README.md
```

---

## ⚙️ Installation

### Backend Setup

```bash
cd backend

python -m venv api_env
source api_env/bin/activate

pip install -r requirements.txt
```

### Place Model Weights

```text
backend/model/best.pt
backend/model/braille_cnn_real_epoch6.pth
```

### Run Backend

```bash
YOLO_CONF=0.08 \
YOLO_IOU_NMS=0.30 \
ENABLE_SPELL=1 \
uvicorn main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔧 Environment Variables

| Variable      | Default | Purpose                            |
| ------------- | ------- | ---------------------------------- |
| YOLO_CONF     | 0.10    | Detection confidence threshold     |
| YOLO_IOU_NMS  | 0.35    | Non-Maximum Suppression threshold  |
| ROW_THRESHOLD | 35      | Curved-line row tracking threshold |
| ENABLE_SPELL  | 1       | Enables NLP correction engine      |

---

## 🌍 Future Enhancements

* Multi-language support
* Real-time camera scanning
* Text-to-Speech output
* Mobile application deployment
* Offline edge inference
* Grade-2 Braille support
* Accessibility analytics dashboard

---

## 🎯 Impact

BrailleVision demonstrates how Artificial Intelligence can be leveraged to build inclusive technologies that improve accessibility and communication. By converting physical Braille into instantly readable text, the platform empowers educators, caregivers, students, and the broader community to interact more effectively with Braille-based content.

---

## 👥 Team

### Team Walrus

Built using Computer Vision, Deep Learning, and Accessibility-First Design.

#### Contributors

* YOLO Detection & Vision Pipeline
* CNN Classification & Translation Engine
* Frontend Development & System Integration

---

# 🦭 Built by Team Walrus

```
```
