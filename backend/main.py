from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import time
from ultralytics import YOLO  
import pathlib                
import platform               

from translate import translate_cells
from cell_extractor import extract_pattern  

if platform.system() != 'Windows':
    pathlib.WindowsPath = pathlib.PosixPath

app = FastAPI(title="BrailleVision_Engine_v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    VISION_MODEL = YOLO("model/best.pt")
except Exception as e:
    print(f"⚠️ MODEL LOADING ERROR: {e}")
    VISION_MODEL = None

def sort_boxes_reading_order(boxes):
    if len(boxes) == 0: return []
    box_data = []
    for b in boxes:
        cx = (b[0] + b[2]) / 2
        cy = (b[1] + b[3]) / 2
        h = b[3] - b[1]
        box_data.append((b, cx, cy, h))
        
    box_data.sort(key=lambda x: x[2])
    avg_h = np.mean([x[3] for x in box_data])
    row_threshold = avg_h * 0.8
    
    rows = []
    for item in box_data:
        box, cx, cy, h = item
        inserted = False
        for row in rows:
            row_cy_avg = np.mean([x[2] for x in row])
            if abs(cy - row_cy_avg) < row_threshold:
                row.append(item)
                inserted = True
                break
        if not inserted:
            rows.append([item])
            
    rows.sort(key=lambda r: np.mean([x[2] for x in r]))
    ordered_boxes = []
    for row in rows:
        row.sort(key=lambda x: x[1])
        for item in row:
            ordered_boxes.append(item[0])
    return ordered_boxes

@app.post("/api/v1/translate")
async def translate_braille(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format.")
        
    start_time = time.time()
    if VISION_MODEL is None:
        raise HTTPException(status_code=500, detail="AI Brain Offline.")
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Decoding failure.")

        results = VISION_MODEL(img)
        raw_boxes = results[0].boxes.xyxy.cpu().numpy()
        
        if len(raw_boxes) == 0:
            return {
                "success": True,
                "metrics": {"latency_ms": 0, "token_count": 0},
                "data": {"translated_text": "[ NO BRAILLE CELL FOUND ]", "confidence_score": 0.0}
            }

        ordered_boxes = sort_boxes_reading_order(raw_boxes)
        extracted_bits = []
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # --- THE CENTER-DISTANCE SPACE DETECTOR ---
        avg_w = np.mean([b[2] - b[0] for b in ordered_boxes])
        avg_h = np.mean([b[3] - b[1] for b in ordered_boxes])
        
        # Store exact center coordinates of every box
        centers = [((b[0]+b[2])/2, (b[1]+b[3])/2) for b in ordered_boxes]

        for i, box in enumerate(ordered_boxes):
            if i > 0:
                cx_curr, cy_curr = centers[i]
                cx_prev, cy_prev = centers[i-1]
                
                # Are they on the same line?
                if abs(cy_curr - cy_prev) < avg_h * 0.8:
                    dist = cx_curr - cx_prev
                    # If the distance between letter centers is > 1.6x a normal cell, it's a space!
                    if dist > avg_w * 1.6:
                        extracted_bits.append("000000") 
                else:
                    # Line break = space
                    extracted_bits.append("000000")

            x1, y1, x2, y2 = map(int, box)
            h, w = gray_frame.shape
            cell_crop = gray_frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
            
            bits = extract_pattern(cell_crop)
            extracted_bits.append(bits)

        actual_text = translate_cells(extracted_bits)
        
        if not actual_text or actual_text.strip() == "":
            actual_text = "UNKNOWN MATRIX SEQUENCE"

        return {
            "success": True,
            "metrics": {
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "token_count": len(extracted_bits)
            },
            "data": {
                "translated_text": actual_text,
                "confidence_score": float(results[0].boxes.conf.mean().cpu().numpy()) if len(results[0].boxes.conf) > 0 else 0.95
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))