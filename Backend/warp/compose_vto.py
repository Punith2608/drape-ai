import cv2
import numpy as np
import os

MODEL = "../base_models/front/model.png"

TOP = "../outputs/top_tps.png"
BOTTOM = "../outputs/bottom_tps_v2.png"
PALLU = "../outputs/pallu_tps.png"

TOP_MASK = "../base_models/front/masks/top.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"
PALLU_MASK = "../base_models/front/masks/pallu.png"

OUTPUT = "../outputs/vto_stage1.jpg"


def apply_layer(base, layer, mask):
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    alpha = mask.astype(np.float32) / 255.0
    alpha = alpha[:, :, None]

    base = base.astype(np.float32)
    layer = layer.astype(np.float32)

    result = (
        base * (1.0 - alpha) +
        layer * alpha
    )

    return np.clip(result, 0, 255).astype(np.uint8)


def main():

    model = cv2.imread(MODEL)

    top = cv2.imread(TOP)
    bottom = cv2.imread(BOTTOM)
    pallu = cv2.imread(PALLU)

    top_mask = cv2.imread(TOP_MASK, cv2.IMREAD_GRAYSCALE)
    bottom_mask = cv2.imread(BOTTOM_MASK, cv2.IMREAD_GRAYSCALE)
    pallu_mask = cv2.imread(PALLU_MASK, cv2.IMREAD_GRAYSCALE)

    if any(x is None for x in [
        model, top, bottom, pallu,
        top_mask, bottom_mask, pallu_mask
    ]):
        raise FileNotFoundError(
            "One or more input files could not be loaded."
        )

    # Layer order: bottom → top → pallu
    result = model.copy()

    result = apply_layer(
        result,
        bottom,
        bottom_mask
    )

    result = apply_layer(
        result,
        top,
        top_mask
    )

    # Pallu goes on top of body fabric.
    result = apply_layer(
        result,
        pallu,
        pallu_mask
    )

    os.makedirs("../output", exist_ok=True)

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Saved:", OUTPUT)


if __name__ == "__main__":
    main()