import cv2
from cell_extractor import extract_pattern
from translate import translate_cells


def process_braille(data):

    img = cv2.imread(
        data["processed_path"],
        cv2.IMREAD_GRAYSCALE
    )

    pattern = extract_pattern(img)

    text = translate_cells([pattern])

    return text


if __name__ == "__main__":

    data = {
        "bbox": [142, 88, 640, 392],
        "cropped_path": "outputs/braille_crop_001.png",
        "processed_path": "outputs/braille_thresh_001.png"
    }

    result = process_braille(data)

    print("Detected Text:", result)