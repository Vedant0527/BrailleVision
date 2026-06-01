import cv2
import numpy as np
import os


def extract_pattern(cell_img, debug_path=None, cell_index=None):
    """
    Extract a 6-bit Braille pattern from a single cell image.

    Braille dot layout (standard):
        dot1  dot4
        dot2  dot5
        dot3  dot6

    Returns a 6-character binary string, e.g. "101000"
    """

    # ── 1. Grayscale ──────────────────────────────────────────────────────────
    if len(cell_img.shape) == 3:
        gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cell_img.copy()

    h, w = gray.shape

    # ── 2. Upscale small cells for better blob detection ──────────────────────
    MIN_DIM = 60
    scale = 1
    if h < MIN_DIM or w < MIN_DIM:
        scale = max(MIN_DIM / h, MIN_DIM / w)
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)),
                          interpolation=cv2.INTER_CUBIC)
        h, w = gray.shape

    # ── 3. Denoise ────────────────────────────────────────────────────────────
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # ── 4. Adaptive threshold (handles uneven lighting far better) ────────────
    # block_size must be odd; use ~1/4 of the smaller dimension, minimum 11
    block = max(11, (min(h, w) // 4) | 1)          # ensure odd
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block,
        4                                           # C constant
    )

    # Small morphological close to fill gaps inside dots
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # ── 5. Find blobs ─────────────────────────────────────────────────────────
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Dot area range: at least 0.3 % and at most 20 % of cell area
    cell_area = h * w
    min_area = max(4, cell_area * 0.003)
    max_area = cell_area * 0.20

    # Also filter by aspect ratio — dots should be roughly circular
    dots = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if not (min_area <= area <= max_area):
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
        if aspect > 2.5:          # too elongated → not a dot
            continue
        cx = x + bw // 2
        cy = y + bh // 2
        dots.append((cx, cy))

    # ── 6. Map dots to Braille grid ───────────────────────────────────────────
    #
    # Standard Braille proportions:
    #   row centres at ~17 %, 50 %, 83 % of height
    #   col centres at ~30 %, 70 % of width
    #
    # We use generous bands so small misalignments don't matter.
    #
    #   row boundaries: 0–33 % → row 0, 33–66 % → row 1, 66–100 % → row 2
    #   col boundary : < 50 %  → left,             >= 50 %         → right

    bits = [0] * 6

    for cx, cy in dots:
        col = 0 if cx < w / 2 else 1          # 0 = left, 1 = right

        if cy < h / 3:
            row = 0
        elif cy < 2 * h / 3:
            row = 1
        else:
            row = 2

        # Braille bit index:  left col → bits 0,1,2 | right col → bits 3,4,5
        bit_index = col * 3 + row
        bits[bit_index] = 1

    pattern = "".join(str(b) for b in bits)

    # ── 7. Debug image ────────────────────────────────────────────────────────
    if debug_path:
        debug = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # Draw grid lines
        cv2.line(debug, (0, h // 3),     (w, h // 3),     (255, 200, 0), 1)
        cv2.line(debug, (0, 2 * h // 3), (w, 2 * h // 3), (255, 200, 0), 1)
        cv2.line(debug, (w // 2, 0),     (w // 2, h),     (255, 200, 0), 1)

        # Draw detected dot centres
        for cx, cy in dots:
            cv2.circle(debug, (cx, cy), max(4, h // 12), (0, 0, 255), -1)

        label = f"cell_{cell_index}" if cell_index is not None else "cell"
        out_file = os.path.join(debug_path, f"{label}_debug.png")
        cv2.imwrite(out_file, debug)

        # Also save the thresholded image for inspection
        cv2.imwrite(os.path.join(debug_path, f"{label}_thresh.png"), thresh)

    if cell_index is not None:
        print(f"Cell {cell_index:>3} | dots={len(dots)} | pattern={pattern}")

    return pattern


# ── Batch helper (optional) ───────────────────────────────────────────────────

def extract_patterns_from_cells(cell_images, debug_dir=None):
    """
    Given a list of cell images (numpy arrays), return a list of patterns.
    If debug_dir is provided, per-cell debug images are saved there.
    """
    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)

    patterns = []
    for i, img in enumerate(cell_images, start=1):
        pattern = extract_pattern(img,
                                  debug_path=debug_dir,
                                  cell_index=i)
        patterns.append(pattern)

    return patterns