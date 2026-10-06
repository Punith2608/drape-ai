import cv2
import numpy as np
import os


# ============================================================
# INPUTS
# ============================================================

BASE = "../outputs/vto_stage9_realism.png"

PALLU_SOURCE = "../supplier/pallu.png"
BORDER_SOURCE = "../supplier/border.png"

PALLU_MASK = "../base_models/front/masks/pallu.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"

LEFT_ARM_MASK = "../base_models/front/masks/left_arm.png"
RIGHT_ARM_MASK = "../base_models/front/masks/right_arm.png"


# ============================================================
# OUTPUTS
# ============================================================

OUTPUT = "../outputs/vto_stage10_pallu_border.png"

PALLU_DEBUG = "../outputs/debug_pallu_layer.png"
BORDER_DEBUG = "../outputs/debug_bottom_border.png"


# ============================================================
# HELPERS
# ============================================================

def load_image(path):
    image = cv2.imread(path, cv2.IMREAD_COLOR)

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    return image


def load_mask(path, shape):
    mask = cv2.imread(
        path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        raise FileNotFoundError(
            f"Mask not found: {path}"
        )

    h, w = shape[:2]

    if mask.shape != (h, w):
        mask = cv2.resize(
            mask,
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def alpha_blend(base, layer, mask):
    alpha = (
        mask.astype(np.float32) / 255.0
    )

    alpha = alpha[:, :, None]

    result = (
        base.astype(np.float32) * (1.0 - alpha)
        + layer.astype(np.float32) * alpha
    )

    return np.clip(
        result,
        0,
        255
    ).astype(np.uint8)


def fill_missing_boundary(values):
    values = values.astype(np.float32)

    valid = np.where(
        values >= 0
    )[0]

    if len(valid) == 0:
        raise RuntimeError(
            "Could not determine pallu boundary."
        )

    positions = np.arange(
        len(values)
    )

    return np.interp(
        positions,
        valid,
        values[valid]
    )


# ============================================================
# PREPARE SUPPLIER PALLU
# ============================================================

def prepare_supplier_pallu(source):
    """
    The supplier pallu is photographed horizontally.

    Rotate it 90 degrees so its long dimension becomes
    the vertical dimension of the hanging pallu.

    Then crop only the useful woven pallu area.

    This avoids squeezing the complete 1774x887 image
    into a narrow vertical strip.
    """

    # Rotate clockwise.
    rotated = cv2.rotate(
        source,
        cv2.ROTATE_90_CLOCKWISE
    )

    h, w = rotated.shape[:2]

    # After rotation:
    # width  ~= 887
    # height ~= 1774
    #
    # Keep most of the image but remove a little of the
    # extreme side area that contains empty/background fabric.
    #
    # These percentages are intentionally conservative.

    x0 = int(w * 0.08)
    x1 = int(w * 0.92)

    y0 = int(h * 0.02)
    y1 = int(h * 0.98)

    cropped = rotated[
        y0:y1,
        x0:x1
    ]

    return cropped


# ============================================================
# HANGING PALLU
# ============================================================

def build_hanging_pallu(
    source,
    mask
):
    """
    Map the prepared supplier pallu into the hanging
    pallu silhouette.

    IMPORTANT:
    The source is already rotated so its long direction
    follows the vertical pallu direction.

    We preserve the original pallu aspect as much as
    the target silhouette allows.
    """

    H, W = mask.shape

    ys, xs = np.where(
        mask > 127
    )

    if len(xs) == 0:
        raise RuntimeError(
            "Pallu mask is empty."
        )

    y_min = int(ys.min())
    y_max = int(ys.max())

    x_min = int(xs.min())
    x_max = int(xs.max())

    target_h = y_max - y_min + 1
    target_w = x_max - x_min + 1

    sh, sw = source.shape[:2]

    # --------------------------------------------------------
    # IMPORTANT:
    # Rather than mapping the entire source width into the
    # target width, crop the source horizontally to the
    # portion that best matches the target aspect ratio.
    # --------------------------------------------------------

    target_ratio = (
        target_w / max(target_h, 1)
    )

    source_ratio = (
        sw / max(sh, 1)
    )

    # Source is expected to be wider than the target
    # relative to its height.
    #
    # Crop source width around the centre while keeping
    # the full vertical decorative sequence.

    desired_source_w = int(
        sh * target_ratio
    )

    # Don't crop too aggressively.
    min_source_w = int(sw * 0.30)

    desired_source_w = max(
        desired_source_w,
        min_source_w
    )

    desired_source_w = min(
        desired_source_w,
        sw
    )

    crop_x0 = (
        sw - desired_source_w
    ) // 2

    crop_x1 = (
        crop_x0 + desired_source_w
    )

    source_crop = source[
        :,
        crop_x0:crop_x1
    ]

    # --------------------------------------------------------
    # Resize source while keeping aspect ratio.
    # --------------------------------------------------------

    source_h, source_w = source_crop.shape[:2]

    scale = min(
        target_w / source_w,
        target_h / source_h
    )

    new_w = max(
        int(source_w * scale),
        1
    )

    new_h = max(
        int(source_h * scale),
        1
    )

    resized = cv2.resize(
        source_crop,
        (new_w, new_h),
        interpolation=cv2.INTER_CUBIC
    )

    # --------------------------------------------------------
    # Create a fitted texture canvas.
    # --------------------------------------------------------

    fitted = np.zeros(
        (target_h, target_w, 3),
        dtype=np.uint8
    )

    offset_x = max(
        (target_w - new_w) // 2,
        0
    )

    offset_y = max(
        (target_h - new_h) // 2,
        0
    )

    copy_w = min(
        new_w,
        target_w - offset_x
    )

    copy_h = min(
        new_h,
        target_h - offset_y
    )

    fitted[
        offset_y:offset_y + copy_h,
        offset_x:offset_x + copy_w
    ] = resized[
        :copy_h,
        :copy_w
    ]

    # --------------------------------------------------------
    # Slight perspective correction.
    #
    # The top is narrower/angled and the lower pallu
    # is slightly wider.
    # --------------------------------------------------------

    src_quad = np.array([
        [0, 0],
        [target_w - 1, 0],
        [target_w - 1, target_h - 1],
        [0, target_h - 1]
    ], dtype=np.float32)

    # Target stays close to the original mask bounding box.
    # Only a very small taper is introduced.
    dst_quad = np.array([
        [0.03 * target_w, 0],
        [0.97 * target_w, 0],
        [0.99 * target_w, target_h - 1],
        [0.01 * target_w, target_h - 1]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(
        src_quad,
        dst_quad
    )

    corrected = cv2.warpPerspective(
        fitted,
        matrix,
        (target_w, target_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT
    )

    # --------------------------------------------------------
    # Put it back at the target position.
    # --------------------------------------------------------

    canvas = np.zeros(
        (H, W, 3),
        dtype=np.uint8
    )

    canvas[
        y_min:y_max + 1,
        x_min:x_max + 1
    ] = corrected

    # --------------------------------------------------------
    # Apply exact pallu mask.
    # --------------------------------------------------------

    result = cv2.bitwise_and(
        canvas,
        canvas,
        mask=mask
    )

    return result


# ============================================================
# BOTTOM BORDER
# ============================================================

def build_bottom_border(
    border_source,
    bottom_mask,
    pallu_mask
):
    """
    Keep the existing bottom-border logic.

    border.png is used ONLY for the bottom body hem.
    """

    H, W = bottom_mask.shape
    bh, bw = border_source.shape[:2]

    body_mask = cv2.bitwise_and(
        bottom_mask,
        cv2.bitwise_not(pallu_mask)
    )

    hem = np.full(
        W,
        -1,
        dtype=np.float32
    )

    for x in range(W):

        ys = np.where(
            body_mask[:, x] > 127
        )[0]

        if len(ys) > 0:
            hem[x] = float(
                ys.max()
            )

    valid = np.where(
        hem >= 0
    )[0]

    if len(valid) < 20:
        raise RuntimeError(
            "Could not determine saree bottom hem."
        )

    first_x = int(
        valid.min()
    )

    last_x = int(
        valid.max()
    )

    hem[
        first_x:last_x + 1
    ] = fill_missing_boundary(
        hem[
            first_x:last_x + 1
        ]
    )

    map_x = np.full(
        (H, W),
        -1,
        dtype=np.float32
    )

    map_y = np.full(
        (H, W),
        -1,
        dtype=np.float32
    )

    target_width = max(
        last_x - first_x,
        1
    )

    border_height = min(
        bh,
        65
    )

    for x in range(
        first_x,
        last_x + 1
    ):

        u = (
            x - first_x
        ) / target_width

        sx = (
            u * (bw - 1)
        )

        bottom_y = hem[x]

        top_y = (
            bottom_y
            - border_height
            + 1
        )

        y_start = max(
            int(top_y),
            0
        )

        y_end = min(
            int(bottom_y) + 1,
            H
        )

        for y in range(
            y_start,
            y_end
        ):

            v = (
                y - top_y
            ) / max(
                border_height - 1,
                1
            )

            sy = (
                v * (bh - 1)
            )

            map_x[y, x] = sx
            map_y[y, x] = sy

    valid_pixels = (
        map_x >= 0
    )

    warped = cv2.remap(
        border_source,
        np.maximum(map_x, 0),
        np.maximum(map_y, 0),
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT
    )

    border_mask = (
        valid_pixels.astype(np.uint8)
        * 255
    )

    border_mask = cv2.bitwise_and(
        border_mask,
        body_mask
    )

    return warped, border_mask


# ============================================================
# MAIN
# ============================================================

def main():

    os.makedirs(
        "../outputs",
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("       STAGE 10 — CORRECT PALLU MAPPING")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Base
    # --------------------------------------------------------

    base = load_image(
        BASE
    )

    # --------------------------------------------------------
    # Supplier pallu
    # --------------------------------------------------------

    original_pallu = load_image(
        PALLU_SOURCE
    )

    print(
        "Original pallu:",
        original_pallu.shape[1],
        "x",
        original_pallu.shape[0]
    )

    prepared_pallu = prepare_supplier_pallu(
        original_pallu
    )

    print(
        "Prepared pallu:",
        prepared_pallu.shape[1],
        "x",
        prepared_pallu.shape[0]
    )

    # --------------------------------------------------------
    # Border
    # --------------------------------------------------------

    border_source = load_image(
        BORDER_SOURCE
    )

    # --------------------------------------------------------
    # Masks
    # --------------------------------------------------------

    pallu_mask = load_mask(
        PALLU_MASK,
        base.shape
    )

    bottom_mask = load_mask(
        BOTTOM_MASK,
        base.shape
    )

    left_arm = load_mask(
        LEFT_ARM_MASK,
        base.shape
    )

    right_arm = load_mask(
        RIGHT_ARM_MASK,
        base.shape
    )

    # --------------------------------------------------------
    # 1. Pallu
    # --------------------------------------------------------

    print(
        "[1/3] Mapping original supplier pallu..."
    )

    pallu_layer = build_hanging_pallu(
        prepared_pallu,
        pallu_mask
    )

    # --------------------------------------------------------
    # 2. Composite pallu
    # --------------------------------------------------------

    result = base.copy()

    result = alpha_blend(
        result,
        pallu_layer,
        pallu_mask
    )

    # --------------------------------------------------------
    # 3. Bottom border
    # --------------------------------------------------------

    print(
        "[2/3] Aligning bottom border..."
    )

    border_layer, border_mask = (
        build_bottom_border(
            border_source,
            bottom_mask,
            pallu_mask
        )
    )

    result = alpha_blend(
        result,
        border_layer,
        border_mask
    )

    # --------------------------------------------------------
    # Restore hands / arms
    # --------------------------------------------------------

    foreground = cv2.bitwise_or(
        left_arm,
        right_arm
    )

    foreground = cv2.GaussianBlur(
        foreground,
        (5, 5),
        0
    )

    result = alpha_blend(
        result,
        base,
        foreground
    )

    print(
        "[3/3] Restored hands and arms..."
    )

    # --------------------------------------------------------
    # Save final
    # --------------------------------------------------------

    cv2.imwrite(
        OUTPUT,
        result,
        [
            cv2.IMWRITE_PNG_COMPRESSION,
            3
        ]
    )

    # --------------------------------------------------------
    # Pallu debug
    # --------------------------------------------------------

    pallu_debug = np.zeros_like(
        base
    )

    pallu_debug = alpha_blend(
        pallu_debug,
        pallu_layer,
        pallu_mask
    )

    cv2.imwrite(
        PALLU_DEBUG,
        pallu_debug
    )

    # --------------------------------------------------------
    # Border debug
    # --------------------------------------------------------

    border_debug = np.zeros_like(
        base
    )

    border_debug = alpha_blend(
        border_debug,
        border_layer,
        border_mask
    )

    cv2.imwrite(
        BORDER_DEBUG,
        border_debug
    )

    print()
    print("=" * 60)
    print("✅ PALLU REBUILD COMPLETE")
    print("=" * 60)
    print()
    print(
        "Final :",
        OUTPUT
    )
    print(
        "Pallu :",
        PALLU_DEBUG
    )
    print(
        "Border:",
        BORDER_DEBUG
    )
    print()


if __name__ == "__main__":
    main()