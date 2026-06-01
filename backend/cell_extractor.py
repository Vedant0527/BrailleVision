import cv2
import numpy as np
import os
import uuid

DEBUG_DIR = "debug_crops"
os.makedirs(DEBUG_DIR, exist_ok=True)

def extract_pattern(cell_img):
    h, w = cell_img.shape
    
    blurred = cv2.GaussianBlur(cell_img, (3, 3), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    img_clahe = clahe.apply(blurred)
    
    block_size = max(11, (w // 2) | 1)
    
    # RESTORED: C=15 to kill faint paper grain and shadows
    thresh = cv2.adaptiveThreshold(
        img_clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, block_size, 15 
    )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    clean_thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    cell_w = w / 2.0
    cell_h = h / 3.0
    
    bits = ""
    debug_img = cv2.cvtColor(clean_thresh, cv2.COLOR_GRAY2BGR)
    
    grid = [
        (0, 0), (0, 1), (0, 2),  
        (1, 0), (1, 1), (1, 2)   
    ]
    
    for col, row in grid:
        # 1. Find the DEAD CENTER of the specific sector
        cx = int(col * cell_w + cell_w / 2.0)
        cy = int(row * cell_h + cell_h / 2.0)
        
        # 2. Strict 25% Safe Zone to prevent neighbor-dot bleeding
        rx = max(2, int(cell_w * 0.25))
        ry = max(2, int(cell_h * 0.25))
        
        # 3. Crop strictly from the center
        roi = clean_thresh[max(0, cy-ry) : min(h, cy+ry), max(0, cx-rx) : min(w, cx+rx)]
        
        if roi.size == 0:
            bits += "0"
            continue
            
        density = cv2.countNonZero(roi) / roi.size
        
        # 4. RESTORED: 25% density requirement for a valid physical dot
        if density > 0.25:
            bits += "1"
            cv2.rectangle(debug_img, (cx-rx, cy-ry), (cx+rx, cy+ry), (0, 255, 0), 1) # Green = Dot Found
        else:
            bits += "0"
            cv2.rectangle(debug_img, (cx-rx, cy-ry), (cx+rx, cy+ry), (0, 0, 255), 1) # Red = Empty
            
    random_id = str(uuid.uuid4())[:6]
    cv2.imwrite(f"{DEBUG_DIR}/cell_{bits}_{random_id}.png", debug_img)
    
    return bits