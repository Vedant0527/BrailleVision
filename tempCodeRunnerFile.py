import cv2
from ultralytics import YOLO

from Braile.cell_extractor import extract_pattern
from Braile.translate import translate_cells

# Load model
model = YOLO("model/best.pt")

# Load image
image_path = "testing.jpeg"
img = cv2.imread(image_path)

# Detect Braille cells
results = model.predict(
    source=image_path,
    conf=0.25,
    verbose=False
)

# Extract boxes
cells = []

for box in results[0].boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cells.append((x1, y1, x2, y2))

# Sort left-to-right, top-to-bottom
cells.sort(key=lambda b: (b[1] // 50, b[0]))

print(f"\nDetected {len(cells)} cells\n")

patterns = []

for i, (x1, y1, x2, y2) in enumerate(cells):

    # Optional padding
    pad_x = 5
    pad_y = 5

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(img.shape[1], x2 + pad_x)
    y2 = min(img.shape[0], y2 + pad_y)

    cell_img = img[y1:y2, x1:x2]

    # Save crop for inspection
    cv2.imwrite(f"cells/cell_{i+1}.png", cell_img)

    pattern = extract_pattern(cell_img)

    patterns.append(pattern)

    print(f"Cell {i+1}: {pattern}")

print("\n====================")
print("ALL PATTERNS")
print("====================")

for i, p in enumerate(patterns):
    print(f"{i+1}: {p}")

# -----------------------------
# Translate patterns
# -----------------------------
translated_text = translate_cells(patterns)

print("\n====================")
print("TRANSLATED TEXT")
print("====================")
print(translated_text)