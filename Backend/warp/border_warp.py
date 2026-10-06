import cv2
import numpy as np
import os


BORDER = "../supplier/border.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"
BASE_IMAGE = "../outputs/vto_stage2_occlusion.png"

OUTPUT = "../outputs/vto_stage3_border.png"


def get_bottom_contour(mask):
    """
    Find the lowest white pixel for each x position.
    This gives us the approximate saree hemline.
    """
    h, w = mask.shape

    contour = []

    for x in range(w):
        ys = np.where(mask[:, x] > 127)[0]

        if len(ys) == 0:
            contour.append(-1)
        else:
            contour.append(int(ys.max()))

    return np.asarray(contour, dtype=np.int32)


def resize_border(border, target_width):
    """
    Resize border while preserving its height.
    """
    h, w = border.shape[:2]

    new_h = max(12, int(h * target_width / w))

    return cv2.resize(
        border,
        (target_width, new_h),
        interpolation=cv2.INTER_LINEAR
    )


def place_border(base, border, contour):
    """
    Follow the lower contour of the saree.
    """
    H, W = base.shape[:2]
    bh, bw = border.shape[:2]

    result = base.copy()

    # Center the border horizontally.
    x0 = max(0, (W - bw) // 2)
    x1 = min(W, x0 + bw)

    for x in range(x0, x1):

        border_x = x - x0

        y = contour[x]

        if y < 0:
            continue

        # Place border slightly inside the saree.
        top_y = y - bh + 2

        if top_y < 0:
            continue

        bottom_y = min(H, top_y + bh)

        source_h = bottom_y - top_y

        if source_h <= 0:
            continue

        result[top_y:bottom_y, x] = border[
            0:source_h,
            border_x
        ]

    return result


def main():

    os.makedirs("../outputs", exist_ok=True)

    base = cv2.imread(BASE_IMAGE)
    border = cv2.imread(BORDER)
    mask = cv2.imread(
        BOTTOM_MASK,
        cv2.IMREAD_GRAYSCALE
    )

    if base is None:
        raise FileNotFoundError(BASE_IMAGE)

    if border is None:
        raise FileNotFoundError(BORDER)

    if mask is None:
        raise FileNotFoundError(BOTTOM_MASK)

    # Crop border to useful width.
    ys, xs = np.where(mask > 127)

    if len(xs) == 0:
        raise RuntimeError("Bottom mask is empty.")

    left = int(xs.min())
    right = int(xs.max())

    target_width = right - left + 1

    border = resize_border(
        border,
        target_width
    )

    contour = get_bottom_contour(mask)

    result = place_border(
        base,
        border,
        contour
    )

    cv2.imwrite(
        OUTPUT,
        result
    )

    print("✅ Bottom border added")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
