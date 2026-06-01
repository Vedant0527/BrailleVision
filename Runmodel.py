
from ultralytics import YOLO
import cv2
import numpy as np
import os


class BrailleDetector:

    def __init__(self, model_path="best.pt"):
        self.model = YOLO(model_path)

    def detect_braille_cells(self, image_path, conf=0.25):

        results = self.model.predict(
            source=image_path,
            conf=conf,
            verbose=False
        )

        boxes = results[0].boxes.xyxy.cpu().numpy()

        return boxes

    def sort_boxes_reading_order(self, boxes):

        boxes = sorted(boxes, key=lambda b: b[1])

        heights = [b[3] - b[1] for b in boxes]

        avg_height = np.mean(heights)

        row_threshold = avg_height * 0.7

        rows = []

        for box in boxes:

            if not rows:
                rows.append([box])
                continue

            current_y = box[1]
            row_y = rows[-1][0][1]

            if abs(current_y - row_y) < row_threshold:
                rows[-1].append(box)
            else:
                rows.append([box])

        for row in rows:
            row.sort(key=lambda b: b[0])

        ordered_boxes = []

        for row in rows:
            ordered_boxes.extend(row)

        return ordered_boxes

    def crop_cells(self, image_path, ordered_boxes):

        image = cv2.imread(image_path)

        crops = []

        for box in ordered_boxes:

            x1, y1, x2, y2 = map(int, box)

            crop = image[y1:y2, x1:x2]

            crops.append(crop)

        return crops

    def run(self, image_path):

        boxes = self.detect_braille_cells(image_path)

        ordered_boxes = self.sort_boxes_reading_order(boxes)

        crops = self.crop_cells(image_path, ordered_boxes)

        return crops, ordered_boxes


if __name__ == "__main__":

    MODEL_PATH = "best.pt"
    IMAGE_PATH = "test.jpg"

    detector = BrailleDetector(MODEL_PATH)

    crops, boxes = detector.run(IMAGE_PATH)

    print(f"Detected {len(crops)} braille cells")

    os.makedirs("cropped_cells", exist_ok=True)

    for i, crop in enumerate(crops):

        cv2.imwrite(
            f"cropped_cells/cell_{i:03d}.png",
            crop
        )

    print("Saved cropped cells to ./cropped_cells")
