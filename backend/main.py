from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import time

# --- 🤝 PERSON 2 INTEGRATION ---
from translate import translate_cells
# -------------------------------

app = FastAPI(title="BrailleVision_Engine_v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "online", "engine": "FastAPI Core"}

@app.post("/api/v1/translate")
async def translate_braille(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Use JPG or PNG.")
        
    start_time = time.time()
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Failed to decode image data.")

        # -----------------------------------------------------------------
        # ⚠️ INTEGRATION GAP FOR PERSON 1 (YOLO)
        # Person 1's code will eventually run here to slice the image into 
        # cells and generate the 6-bit strings. 
        # -----------------------------------------------------------------
        
        time.sleep(2) # CSS Scanner visual delay
        
        # We are feeding Person 2's function an array of actual 6-bit Braille 
        # strings that spell "ACCESSIBILITY" (with a Capital sign at the front).
        yolo_simulated_bits = [
            "000001", "100000", "100100", "100100", "100010", "011100", 
            "011100", "010100", "110000", "010100", "111000", "010100", 
            "011110", "101111"
        ]

        # EXECUTING PERSON 2'S TRANSLATOR
        actual_text = translate_cells(yolo_simulated_bits)
        token_count = len(yolo_simulated_bits)
        
        latency = (time.time() - start_time) * 1000

        return {
            "success": True,
            "metrics": {
                "latency_ms": round(latency, 2),
                "token_count": token_count
            },
            "data": {
                "translated_text": actual_text,
                "confidence_score": 0.98
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))