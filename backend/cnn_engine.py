# Project VISION - Neural Classification Engine
# Matches Braile/CNN_predictor.py (training-time transform + checkpoint mapping)

import os
import uuid

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms

DEBUG_DIR = "debug_cnn_inputs"
os.makedirs(DEBUG_DIR, exist_ok=True)
SAVE_CNN_DEBUG = os.getenv("CNN_DEBUG", "0") == "1"


class BrailleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 26),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


device = torch.device("cpu")
cnn_model = BrailleCNN()
idx_to_class: dict[int, str] = {i: chr(ord("A") + i) for i in range(26)}

# Same transform as CNN_predictor.predict_letter (no Otsu / pad / custom binarize)
cnn_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Grayscale(),
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),
])

_loaded = False
for _weight_path in ("model/braille_cnn_real_epoch6.pth", "braille_cnn_real_epoch6.pth"):
    if not os.path.isfile(_weight_path):
        continue
    try:
        checkpoint = torch.load(_weight_path, map_location=device, weights_only=False)
        cnn_model.load_state_dict(checkpoint["model_state_dict"])
        cnn_model.eval()

        class_to_idx = checkpoint.get("class_to_idx")
        if class_to_idx:
            idx_to_class = {int(v): str(k) for k, v in class_to_idx.items()}

        _loaded = True
        print(f"✅ CNN Brain Online ({_weight_path})")
        break
    except Exception as e:
        print(f"⚠️ CNN load failed ({_weight_path}): {e}")

if not _loaded:
    print("⚠️ CNN FATAL ERROR: no weights file found")
    cnn_model = None


def predict_letter(cell_img_bgr: np.ndarray) -> str:
    """Identical inference path to Braile/CNN_predictor.predict_letter."""
    if cnn_model is None or cell_img_bgr is None or cell_img_bgr.size == 0:
        return "?"

    img = cnn_transform(cell_img_bgr).unsqueeze(0)

    with torch.no_grad():
        output = cnn_model(img)
        pred = torch.argmax(output, dim=1).item()

    return idx_to_class.get(pred, "?")


def predict_cell_cnn(cell_img_bgr: np.ndarray) -> str:
    """FastAPI entry point (alias for predict_letter)."""
    if SAVE_CNN_DEBUG:
        rid = str(uuid.uuid4())[:6]
        cv2.imwrite(os.path.join(DEBUG_DIR, f"raw_crop_{rid}.png"), cell_img_bgr)
        tensor = cnn_transform(cell_img_bgr)
        torchvision.utils.save_image(
            tensor * 0.5 + 0.5,
            os.path.join(DEBUG_DIR, f"final_tensor_{rid}.png"),
        )

    return predict_letter(cell_img_bgr)
