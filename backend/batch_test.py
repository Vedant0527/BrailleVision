#!/usr/bin/env python3
"""
Batch-evaluate Braille images with dynamic, resolution-aware parameters.

Run from backend/ with api_env:
  cd backend && source api_env/bin/activate
  python batch_test.py
  python batch_test.py --samples ../test_samples --out debug_batch

Does not start FastAPI. Imports pipeline helpers from main.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np

# Ensure model paths resolve when launched from backend/
_BACKEND = Path(__file__).resolve().parent
os.chdir(_BACKEND)
sys.path.insert(0, str(_BACKEND))

import main as pipeline  # noqa: E402


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def compute_dynamic_params(
    img: np.ndarray, boxes: np.ndarray | None = None
) -> dict:
    """
    Scale border padding and row tolerance from image size and (if available)
    average YOLO cell geometry — avoids fixed 80px / 35px breaking on new resolutions.

    Reference calibration (~primary demo image):
      short_side ~1200px, avg cell ~40px  ->  border ~72px, row_thresh ~34px
    """
    h, w = img.shape[:2]
    short_side = min(h, w)
    long_side = max(h, w)

    # ~6% of short edge, clamped (replaces fixed YOLO_BORDER_PAD=80)
    border_pad = int(np.clip(short_side * 0.06, 24, 120))

    row_threshold = float(np.clip(short_side * 0.028, 18, 55))
    cell_pad = max(1, int(short_side * 0.002))
    word_gap_factor = pipeline.WORD_GAP_FACTOR

    avg_cell_h = avg_cell_w = None
    if boxes is not None and len(boxes) > 0:
        heights = boxes[:, 3] - boxes[:, 1]
        widths = boxes[:, 2] - boxes[:, 0]
        avg_cell_h = float(np.mean(heights))
        avg_cell_w = float(np.mean(widths))
        # Follow curved-row logic: tolerance tracks cell height
        row_threshold = max(row_threshold, avg_cell_h * 0.85)
        cell_pad = max(cell_pad, int(min(avg_cell_w, avg_cell_h) * 0.08))

    # Slightly lower conf on very large images (cells appear smaller in frame)
    yolo_conf = pipeline.YOLO_CONF
    if long_side > 2000:
        yolo_conf = min(yolo_conf, 0.12)
    elif long_side < 800:
        yolo_conf = max(yolo_conf, 0.08)

    return {
        "border_pad": border_pad,
        "row_threshold": int(round(row_threshold)),
        "cell_pad": cell_pad,
        "word_gap_factor": word_gap_factor,
        "yolo_conf": yolo_conf,
        "avg_cell_h": avg_cell_h,
        "avg_cell_w": avg_cell_w,
        "image_size": f"{w}x{h}",
    }


def apply_dynamic_config(params: dict) -> None:
    pipeline.YOLO_BORDER_PAD = params["border_pad"]
    pipeline.ROW_THRESHOLD = params["row_threshold"]
    pipeline.CELL_PAD = params["cell_pad"]
    pipeline.WORD_GAP_FACTOR = params["word_gap_factor"]
    pipeline.YOLO_CONF = params["yolo_conf"]


def run_yolo_on_image(img: np.ndarray, border_pad: int) -> np.ndarray:
    h_img, w_img = img.shape[:2]
    padded = pipeline.add_white_border(img, border_pad)
    boxes_on_padded, _ = pipeline.run_yolo_boxes(padded)
    return pipeline.offset_boxes_to_original(boxes_on_padded, border_pad, w_img, h_img)


def save_sort_debug(img: np.ndarray, ordered_boxes: np.ndarray, out_path: Path) -> None:
    vis = img.copy()
    for i, box in enumerate(ordered_boxes):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = str(i)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(vis, (x1, y1 - th - 8), (x1 + tw + 6, y1), (0, 255, 0), -1)
        cv2.putText(
            vis, label, (x1 + 3, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2,
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), vis)


def process_one_image(img_path: Path, out_dir: Path) -> dict:
    img = cv2.imread(str(img_path))
    if img is None:
        return {"name": img_path.name, "error": "could not read image"}

    # Pass 1: border from resolution only
    params = compute_dynamic_params(img)
    apply_dynamic_config(params)

    boxes = run_yolo_on_image(img, params["border_pad"])

    # Pass 2: refine row/cell params from detections
    params = compute_dynamic_params(img, boxes)
    apply_dynamic_config(params)

    yolo_count = len(boxes)
    stem = img_path.stem

    if yolo_count == 0:
        save_sort_debug(img, np.empty((0, 4)), out_dir / f"{stem}_sort.jpg")
        return {
            "name": img_path.name,
            "params": params,
            "yolo_count": 0,
            "raw_cnn": "",
            "fuzzy": "",
        }

    rows = pipeline.group_boxes_into_rows(boxes)
    ordered = [box for row in rows for box in row]
    save_sort_debug(img, np.array(ordered), out_dir / f"{stem}_sort.jpg")

    row_strings = [pipeline.build_row_text(img, row) for row in rows]
    raw_cnn = " ".join(t for t in row_strings if t).upper()
    fuzzy = pipeline.apply_spellcheck(raw_cnn) if pipeline.ENABLE_SPELL else raw_cnn

    return {
        "name": img_path.name,
        "params": params,
        "yolo_count": yolo_count,
        "raw_cnn": raw_cnn,
        "fuzzy": fuzzy,
    }


def find_sample_images(samples_dir: Path) -> list[Path]:
    if not samples_dir.is_dir():
        return []
    files = [p for p in samples_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    return sorted(files, key=lambda p: p.name.lower())


def print_summary(result: dict) -> None:
    print("=" * 72)
    print(f"Image:              {result.get('name', '?')}")
    if "error" in result:
        print(f"Error:              {result['error']}")
        return

    p = result.get("params", {})
    print(f"Resolution:         {p.get('image_size', '?')}")
    print(
        f"Dynamic params:     border={p.get('border_pad')}px  "
        f"row_thresh={p.get('row_threshold')}px  "
        f"cell_pad={p.get('cell_pad')}px  "
        f"yolo_conf={p.get('yolo_conf')}"
    )
    if p.get("avg_cell_h"):
        print(
            f"Avg cell size:      {p.get('avg_cell_w', 0):.1f}w x {p.get('avg_cell_h', 0):.1f}h px"
        )
    print(f"YOLO detections:    {result.get('yolo_count', 0)}")
    print(f"Raw CNN string:     {result.get('raw_cnn', '')}")
    print(f"Fuzzy-matched:      {result.get('fuzzy', '')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="VISION batch Braille pipeline test")
    parser.add_argument(
        "--samples",
        default="test_samples",
        help="Folder of test images (default: backend/test_samples)",
    )
    parser.add_argument(
        "--out",
        default="debug_batch",
        help="Output folder for sort debug JPEGs",
    )
    args = parser.parse_args()

    samples_dir = Path(args.samples)
    if not samples_dir.is_absolute():
        samples_dir = _BACKEND / samples_dir

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = _BACKEND / out_dir

    if pipeline.VISION_MODEL is None:
        print("FATAL: YOLO model failed to load. Run from backend/ with api_env active.")
        sys.exit(1)

    images = find_sample_images(samples_dir)
    if not images:
        print(f"No images found in {samples_dir}")
        print(f"Place .jpg/.png files in that folder and re-run.")
        sys.exit(1)

    print(f"Samples: {samples_dir} ({len(images)} images)")
    print(f"Debug output: {out_dir}\n")

    results = []
    for img_path in images:
        results.append(process_one_image(img_path, out_dir))

    print("\n")
    for r in results:
        print_summary(r)

    print("\n" + "=" * 72)
    print("DYNAMIC SCALING (for main.py later)")
    print("- YOLO_BORDER_PAD: 6% of min(width,height), clamp 24–120px")
    print("- ROW_THRESHOLD:   max(2.8% of short side, 0.85 × avg cell height)")
    print("- CELL_PAD:        max(2px, 8% of avg cell size)")
    print("- YOLO_CONF:       slight adjust by image long edge (<800 / >2000)")
    print(f"Inspect: {out_dir}/*_sort.jpg")


if __name__ == "__main__":
    main()
