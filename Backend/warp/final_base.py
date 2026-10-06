import cv2
import numpy as np
import os


MODEL = "../base_models/front/model.png"

BOTTOM = "../outputs/bottom_tps_v2.png"
TOP = "../outputs/top_tps.png"
BLOUSE = "../outputs/blouse_tps.png"
PALLU = "../outputs/pallu_tps.png"

BOTTOM_MASK = "../base_models/front/masks/bottom.png"
TOP_MASK = "../base_models/front/masks/top.png"
BLOUSE_MASK = "../base_models/front/masks/blouse.png"
PALLU_MASK = "../base_models/front/masks/pallu.png"

LEFT_ARM = "../base_models/front/masks/left_arm.png"
RIGHT_ARM = "../base_models/front/masks/right_arm.png"

OUTPUT = "../outputs/vto_stage8_base.png"


def load_image(path):
    image = cv2.imread(path)

    if image is None:
        raise FileNotFoundError(path)

    return image


def load_mask(path, shape):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise FileNotFoundError(path)

    h, w = shape[:2]

    if mask.shape != (h, w):
        mask = cv2.resize(
            mask,
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def blend(base, layer, mask, feather=2):

    if feather > 0:
        k = feather * 2 + 1

        mask = cv2.GaussianBlur(
            mask,
            (k, k),
            0
        )

    # Blend in small strips. Full-image float32 blending needs several large
    # temporary arrays and fails on machines with a small Windows page file.
    result = base.copy()
    rows_per_chunk = 32

    for y0 in range(0, base.shape[0], rows_per_chunk):
        y1 = min(y0 + rows_per_chunk, base.shape[0])
        alpha = mask[y0:y1].astype(np.uint16)[:, :, None]
        inverse_alpha = 255 - alpha
        mixed = (
            base[y0:y1].astype(np.uint16) * inverse_alpha
            + layer[y0:y1].astype(np.uint16) * alpha
            + 127
        ) // 255
        result[y0:y1] = mixed.astype(np.uint8)

    return result


def main():

    os.makedirs("../outputs", exist_ok=True)

    model = load_image(MODEL)

    bottom = load_image(BOTTOM)
    top = load_image(TOP)
    blouse = load_image(BLOUSE)
    pallu = load_image(PALLU)

    bottom_mask = load_mask(
        BOTTOM_MASK,
        model.shape
    )

    top_mask = load_mask(
        TOP_MASK,
        model.shape
    )

    blouse_mask = load_mask(
        BLOUSE_MASK,
        model.shape
    )

    pallu_mask = load_mask(
        PALLU_MASK,
        model.shape
    )

    left_arm = load_mask(
        LEFT_ARM,
        model.shape
    )

    right_arm = load_mask(
        RIGHT_ARM,
        model.shape
    )

    result = model.copy()

    # --------------------------------------------------
    # 1. Bottom saree
    # --------------------------------------------------

    result = blend(
        result,
        bottom,
        bottom_mask,
        feather=3
    )

    # --------------------------------------------------
    # 2. Blouse
    # --------------------------------------------------

    result = blend(
        result,
        blouse,
        blouse_mask,
        feather=2
    )

    # --------------------------------------------------
    # 3. Top saree
    # --------------------------------------------------

    result = blend(
        result,
        top,
        top_mask,
        feather=3
    )

    # --------------------------------------------------
    # 4. Draped pallu
    # --------------------------------------------------

    result = blend(
        result,
        pallu,
        pallu_mask,
        feather=2
    )

    # --------------------------------------------------
    # 5. Restore hands / arms
    # --------------------------------------------------

    foreground = cv2.bitwise_or(
        left_arm,
        right_arm
    )

    foreground = cv2.GaussianBlur(
        foreground,
        (5, 5),
        0
    )

    result = blend(
        result,
        model,
        foreground,
        feather=0,
    )

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Final base composite created")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
