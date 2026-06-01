#!/usr/bin/env python3
"""
Visualize CNN_predictor-style inputs on saved YOLO crops.

Use api_env, NOT system python3:
  cd backend && source api_env/bin/activate
  python compare_thresholds.py --limit 10

Writes debug_cnn_inputs/compare_<stem>.png
Columns: RAW CROP | GRAY 64x64 | NORMALIZED (denorm preview)
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cnn_engine import cnn_transform, predict_letter  # noqa: E402

PANEL_H = 140
LABEL_H = 26


def _fit_height(bgr_or_gray: np.ndarray, target_h: int) -> np.ndarray:
    if bgr_or_gray.ndim == 2:
        vis = cv2.cvtColor(bgr_or_gray, cv2.COLOR_GRAY2BGR)
    else:
        vis = bgr_or_gray.copy()
    h, w = vis.shape[:2]
    if h == 0:
        return vis
    scale = target_h / h
    return cv2.resize(vis, (max(1, int(w * scale)), target_h), interpolation=cv2.INTER_AREA)


def _label_bar(text: str, width: int) -> np.ndarray:
    bar = np.zeros((LABEL_H, width, 3), dtype=np.uint8)
    cv2.putText(bar, text, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    return bar


def build_panel(cell_bgr: np.ndarray) -> np.ndarray:
    tensor = cnn_transform(cell_bgr)
    gray64 = (tensor[0].numpy() * 0.5 + 0.5) * 255
    gray64 = gray64.astype(np.uint8)
    letter = predict_letter(cell_bgr)

    columns = [
        (f"RAW", cell_bgr),
        (f"64x64 norm", gray64),
        (f"pred={letter}", gray64),
    ]

    panels = []
    for label, img in columns:
        vis = _fit_height(img, PANEL_H)
        panels.append(np.vstack([_label_bar(label, vis.shape[1]), vis]))
    return np.hstack(panels)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="debug_cnn_inputs")
    parser.add_argument("--glob", default="raw_crop_*.png")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    paths = sorted(glob.glob(os.path.join(args.input, args.glob)))
    if args.limit > 0:
        paths = paths[: args.limit]
    if not paths:
        print(f"No files: {args.input}/{args.glob}")
        sys.exit(1)

    for path in paths:
        bgr = cv2.imread(path)
        if bgr is None:
            continue
        stem = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(args.input, f"compare_{stem}.png")
        cv2.imwrite(out, build_panel(bgr))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
