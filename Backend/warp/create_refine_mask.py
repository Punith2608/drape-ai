import cv2
import numpy as np
import os

TOP = "../base_models/front/masks/top.png"
BOTTOM = "../base_models/front/masks/bottom.png"
BLOUSE = "../base_models/front/masks/blouse.png"
PALLU = "../base_models/front/masks/pallu.png"

OUTPUT = "../outputs/refine_mask.png"


def load_mask(path, shape):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise FileNotFoundError(path)

    if mask.shape != shape:
        mask = cv2.resize(
            mask,
            (shape[1], shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def main():
    first = cv2.imread(TOP, cv2.IMREAD_GRAYSCALE)

    if first is None:
        raise FileNotFoundError(TOP)

    shape = first.shape

    top = load_mask(TOP, shape)
    bottom = load_mask(BOTTOM, shape)
    blouse = load_mask(BLOUSE, shape)
    pallu = load_mask(PALLU, shape)

    mask = cv2.bitwise_or(top, bottom)
    mask = cv2.bitwise_or(mask, blouse)
    mask = cv2.bitwise_or(mask, pallu)

    # Slight expansion so refinement can smooth tiny seams.
    kernel = np.ones((7, 7), np.uint8)

    mask = cv2.dilate(
        mask,
        kernel,
        iterations=1
    )

    # Soft edge.
    mask = cv2.GaussianBlur(
        mask,
        (7, 7),
        0
    )

    os.makedirs("../outputs", exist_ok=True)

    cv2.imwrite(
        OUTPUT,
        mask
    )

    print("✅ Refinement mask created")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()