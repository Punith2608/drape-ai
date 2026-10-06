import cv2
import numpy as np
import os


MODEL = "../base_models/front/model.png"
SAREE = "../outputs/vto_stage4_pleats.png"

TOP_MASK = "../base_models/front/masks/top.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"
PALLU_MASK = "../base_models/front/masks/pallu.png"

OUTPUT = "../outputs/vto_stage5_lit.png"


def load_mask(path, shape):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise FileNotFoundError(path)

    if mask.shape != shape[:2]:
        mask = cv2.resize(
            mask,
            (shape[1], shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def create_saree_mask(shape):

    top = load_mask(TOP_MASK, shape)
    bottom = load_mask(BOTTOM_MASK, shape)
    pallu = load_mask(PALLU_MASK, shape)

    combined = cv2.bitwise_or(top, bottom)
    combined = cv2.bitwise_or(combined, pallu)

    # Smooth edges slightly.
    combined = cv2.GaussianBlur(
        combined,
        (7, 7),
        0
    )

    return combined


def create_light_map(model, mask):

    gray = cv2.cvtColor(
        model,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    # ---------------------------------------------------------
    # 1. Global brightness component
    # ---------------------------------------------------------

    region = mask > 30

    values = gray[region]

    if values.size == 0:
        raise RuntimeError("Saree mask is empty.")

    p05, p95 = np.percentile(
        values,
        [5, 95]
    )

    global_light = (
        (gray - p05) /
        max(p95 - p05, 1.0)
    )

    global_light = np.clip(
        global_light,
        0.0,
        1.0
    )

    # Don't make the cloth extremely dark or bright.
    global_light = (
        0.72 +
        global_light * 0.38
    )

    # ---------------------------------------------------------
    # 2. Local shadow/highlight component
    # ---------------------------------------------------------

    blurred = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=15
    )

    ratio = gray / (
        blurred + 1e-6
    )

    local = 1.0 + (
        ratio - 1.0
    ) * 0.8

    local = np.clip(
        local,
        0.70,
        1.30
    )

    # ---------------------------------------------------------
    # 3. Combine
    # ---------------------------------------------------------

    light = (
        global_light * 0.55 +
        local * 0.45
    )

    light = np.clip(
        light,
        0.60,
        1.30
    )

    return light


def apply_light(saree, light_map, mask):

    result = saree.astype(np.float32)

    # Apply illumination equally to RGB channels.
    lit = result * light_map[:, :, None]

    alpha = (
        mask.astype(np.float32) /
        255.0
    )[:, :, None]

    result = (
        result * (1.0 - alpha) +
        lit * alpha
    )

    return np.clip(
        result,
        0,
        255
    ).astype(np.uint8)


def main():

    os.makedirs("../output", exist_ok=True)

    model = cv2.imread(MODEL)
    saree = cv2.imread(SAREE)

    if model is None:
        raise FileNotFoundError(MODEL)

    if saree is None:
        raise FileNotFoundError(SAREE)

    # Ensure same resolution.
    if model.shape[:2] != saree.shape[:2]:
        saree = cv2.resize(
            saree,
            (model.shape[1], model.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )

    saree_mask = create_saree_mask(
        model.shape
    )

    light_map = create_light_map(
        model,
        saree_mask
    )

    result = apply_light(
        saree,
        light_map,
        saree_mask
    )

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Light transfer complete")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()