import cv2
import numpy as np
import os


TOP = "../base_models/front/masks/top.png"
BOTTOM = "../base_models/front/masks/bottom.png"
PALLU = "../base_models/front/masks/pallu.png"

OUTPUT = "../outputs/ai_mask.png"


def load(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise FileNotFoundError(path)

    return img


def main():

    top = load(TOP)
    bottom = load(BOTTOM)
    pallu = load(PALLU)

    mask = cv2.bitwise_or(top, bottom)
    mask = cv2.bitwise_or(mask, pallu)

    # Shrink the mask slightly.
    # This protects edges, hands, arms and face.
    kernel = np.ones((9, 9), np.uint8)

    mask = cv2.erode(
        mask,
        kernel,
        iterations=1
    )

    # Remove tiny isolated regions.
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    os.makedirs(
        "../outputs",
        exist_ok=True
    )

    cv2.imwrite(
        OUTPUT,
        mask
    )

    print("AI mask created:")
    print(OUTPUT)


if __name__ == "__main__":
    main()