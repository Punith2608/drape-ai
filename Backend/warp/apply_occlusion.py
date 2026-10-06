import cv2
import numpy as np
import os

MODEL = "../base_models/front/model.png"
STAGE1 = "../outputs/vto_stage1.jpg"

LEFT_ARM = "../base_models/front/masks/left_arm.png"
RIGHT_ARM = "../base_models/front/masks/right_arm.png"

OUTPUT = "../outputs/vto_stage2_occlusion.png"


def load_mask(path, shape):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise FileNotFoundError(f"Mask not found: {path}")

    h, w = shape[:2]

    if mask.shape != (h, w):
        mask = cv2.resize(
            mask,
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def main():

    model = cv2.imread(MODEL)
    stage1 = cv2.imread(STAGE1)

    if model is None:
        raise FileNotFoundError(MODEL)

    if stage1 is None:
        raise FileNotFoundError(STAGE1)

    # Load arm masks
    left_mask = load_mask(
        LEFT_ARM,
        model.shape
    )

    right_mask = load_mask(
        RIGHT_ARM,
        model.shape
    )

    # Combine both masks
    foreground_mask = cv2.bitwise_or(
        left_mask,
        right_mask
    )

    # Clean small annotation noise
    kernel = np.ones((3, 3), np.uint8)

    foreground_mask = cv2.morphologyEx(
        foreground_mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Slight feathering for natural edges
    foreground_mask = cv2.GaussianBlur(
        foreground_mask,
        (5, 5),
        0
    )

    alpha = foreground_mask.astype(np.float32) / 255.0
    alpha = alpha[:, :, None]

    # Original model is foreground.
    result = (
        model.astype(np.float32) * alpha
        +
        stage1.astype(np.float32) * (1.0 - alpha)
    )

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    os.makedirs("../outputs", exist_ok=True)

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Occlusion applied")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
