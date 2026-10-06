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

OUTPUT = "../outputs/vto_stage7_clean.jpg"


def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(path)
    return img


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


def blend(base, layer, mask, feather=3):

    if feather > 0:
        kernel = feather * 2 + 1
        mask = cv2.GaussianBlur(
            mask,
            (kernel, kernel),
            0
        )

    alpha = mask.astype(np.float32) / 255.0
    alpha = alpha[:, :, None]

    result = (
        base.astype(np.float32) * (1.0 - alpha)
        + layer.astype(np.float32) * alpha
    )

    return np.clip(result, 0, 255).astype(np.uint8)


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

    # -----------------------------------------
    # Layer 1: original model
    # -----------------------------------------

    result = model.copy()

    # -----------------------------------------
    # Layer 2: bottom saree
    # -----------------------------------------

    result = blend(
        result,
        bottom,
        bottom_mask,
        feather=3
    )

    # -----------------------------------------
    # Layer 3: top saree
    # -----------------------------------------

    result = blend(
        result,
        top,
        top_mask,
        feather=3
    )

    # -----------------------------------------
    # Layer 4: blouse
    # -----------------------------------------

    result = blend(
        result,
        blouse,
        blouse_mask,
        feather=2
    )

    # -----------------------------------------
    # Layer 5: pallu
    # -----------------------------------------

    result = blend(
        result,
        pallu,
        pallu_mask,
        feather=2
    )

    # -----------------------------------------
    # Layer 6: restore hands / arms
    # -----------------------------------------

    foreground = cv2.bitwise_or(
        left_arm,
        right_arm
    )

    foreground = cv2.GaussianBlur(
        foreground,
        (3, 3),
        0
    )

    alpha = (
        foreground.astype(np.float32) / 255.0
    )[:, :, None]

    result = (
        model.astype(np.float32) * alpha
        + result.astype(np.float32) * (1.0 - alpha)
    )

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    cv2.imwrite(
        OUTPUT,
        result,
        [cv2.IMWRITE_JPEG_QUALITY, 95]
    )

    print("✅ Clean composite created")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()