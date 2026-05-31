import cv2
import numpy as np


def extract_pattern(cell_img):

    h, w = cell_img.shape
#We are estimating the dot position here in the image
    left_x = w // 4
    right_x = 3 * w // 4

    row1 = h // 6
    row2 = h // 2
    row3 = 5 * h // 6
#list of all the dots
    positions = [
        (left_x, row1),   # dot1
        (left_x, row2),   # dot2
        (left_x, row3),   # dot3
        (right_x, row1),  # dot4
        (right_x, row2),  # dot5
        (right_x, row3),  # dot6
    ]

    bits = ""

    for x, y in positions:
#roi=Region of interest
#Instead of checking only one pixel, we check a 20×20 area around the expected dot center.
        roi = cell_img[
            max(0, y-10):y+10,
            max(0, x-10):x+10
        ]

        mean = np.mean(roi)

        if mean > 127:
            bits += "1"
        else:
            bits += "0"

    return bits