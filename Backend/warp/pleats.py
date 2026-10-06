import cv2
import numpy as np
import os

INPUT = "../outputs/vto_stage3_border.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"

OUTPUT = "../outputs/vto_stage4_pleats.png"


def create_pleat_shading(h, w, num_pleats=14):
    """
    Create a vertical sinusoidal light/shadow pattern.
    """

    x = np.arange(w, dtype=np.float32)

    phase = (x / w) * num_pleats * np.pi * 2

    # Smooth fold pattern.
    wave = 0.5 + 0.5 * np.cos(phase)

    # Keep variation subtle.
    brightness = 0.82 + 0.24 * wave

    shading = np.tile(
        brightness,
        (h, 1)
    )

    return shading


def main():

    os.makedirs("../output", exist_ok=True)

    image = cv2.imread(INPUT)
    mask = cv2.imread(
        BOTTOM_MASK,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise FileNotFoundError(INPUT)

    if mask is None:
        raise FileNotFoundError(BOTTOM_MASK)

    h, w = image.shape[:2]

    shading = create_pleat_shading(
        h,
        w,
        num_pleats=14
    )

    # Apply only to the lower saree.
    region = mask > 127

    result = image.astype(np.float32)

    result[region] *= shading[region, None]

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Pleat shading added")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()