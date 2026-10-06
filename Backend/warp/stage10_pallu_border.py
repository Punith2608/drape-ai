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

def load_image(path: str) -> np.ndarray:
    """
    Load a color image.
    """
    image = cv2.imread(path, cv2.IMREAD_COLOR)

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    return image


def load_mask(path: str, shape) -> np.ndarray:
    """
    Load a grayscale mask and resize it to the target image size.
    """
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


def fill_missing_boundary(values: np.ndarray) -> np.ndarray:
    """
    Fill missing values in a 1D boundary array by interpolation.
    """

    values = values.astype(np.float32)

    valid = np.where(values >= 0)[0]

    if len(valid) == 0:
        raise RuntimeError(
            "Could not find any valid boundary points."
        )

    all_x = np.arange(len(values))

    values = np.interp(
        all_x,
        valid,
        values[valid]
    )

    return values


def alpha_blend(
    base: np.ndarray,
    layer: np.ndarray,
    mask: np.ndarray
) -> np.ndarray:
    """
    Blend layer onto base using grayscale mask.
    """

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


def add_pallu_fold_shading(layer: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Add restrained lengthwise light variation to keep the pallu dimensional."""
    binary = (mask > 127).astype(np.uint8)
    if not np.any(binary):
        return layer

    h, w = binary.shape
    yy, xx = np.mgrid[0:h, 0:w]
    # A subtle, vertically drifting fold profile prevents uniform flat colour
    # without redrawing or obscuring the supplier's zari pattern.
    profile = np.cos((xx / max(w - 1, 1) * 5.5 + yy / max(h - 1, 1) * 0.55) * np.pi * 2)
    gain = 1.0 + 0.025 * profile
    result = layer.astype(np.float32)
    result[binary > 0] *= gain[binary > 0, None]
    return np.clip(result, 0, 255).astype(np.uint8)


# ============================================================
# HANGING PALLU
# ============================================================

def build_hanging_pallu(
    source: np.ndarray,
    mask: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Map the complete supplier pallu image into the existing
    hanging-pallu mask.

    IMPORTANT:
    We preserve the supplier pallu's own:
      - green fabric
      - zari design
      - decorative borders
      - large end motif

    The mask controls ONLY where the pallu appears.
    """

    H, W = mask.shape
    sh, sw = source.shape[:2]

    ys, xs = np.where(mask > 127)

    if len(xs) == 0:
        raise RuntimeError(
            "Pallu mask is empty."
        )

    y_min = int(ys.min())
    y_max = int(ys.max())

    # --------------------------------------------------------
    # Find left/right edge at every valid row.
    # --------------------------------------------------------

    left = np.full(
        H,
        -1,
        dtype=np.float32
    )

    right = np.full(
        H,
        -1,
        dtype=np.float32
    )

    for y in range(
        y_min,
        y_max + 1
    ):

        row_x = np.where(
            mask[y] > 127
        )[0]

        if len(row_x) > 0:
            left[y] = float(row_x.min())
            right[y] = float(row_x.max())

    # --------------------------------------------------------
    # Fill gaps in the boundaries.
    # --------------------------------------------------------

    left_segment = left[y_min:y_max + 1]
    right_segment = right[y_min:y_max + 1]

    left[y_min:y_max + 1] = fill_missing_boundary(
        left_segment
    )

    right[y_min:y_max + 1] = fill_missing_boundary(
        right_segment
    )

    # --------------------------------------------------------
    # Build inverse warp maps.
    #
    # Target model pallu -> supplier pallu
    # --------------------------------------------------------

    map_x = np.zeros(
        (H, W),
        dtype=np.float32
    )

    map_y = np.zeros(
        (H, W),
        dtype=np.float32
    )

    valid_height = max(
        y_max - y_min,
        1
    )

    for y in range(
        y_min,
        y_max + 1
    ):

        l = left[y]
        r = right[y]

        width = max(
            r - l,
            1.0
        )

        # Target x coordinate -> source x coordinate.
        u = (
            np.arange(
                W,
                dtype=np.float32
            ) - l
        ) / width

        u = np.clip(
            u,
            0.0,
            1.0
        )

        map_x[y] = (
            u * (sw - 1)
        )

        # Target y -> source y.
        v = (
            y - y_min
        ) / valid_height

        map_y[y] = (
            v * (sh - 1)
        )

    # --------------------------------------------------------
    # Warp supplier pallu.
    # --------------------------------------------------------

    warped = cv2.remap(
        source,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT
    )

    # --------------------------------------------------------
    # Apply target mask.
    # --------------------------------------------------------

    result = cv2.bitwise_and(
        warped,
        warped,
        mask=mask
    )

    return result, mask


# ============================================================
# BOTTOM BORDER
# ============================================================

def build_bottom_border(
    border_source: np.ndarray,
    bottom_mask: np.ndarray,
    pallu_mask: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Warp the actual supplier border.png along the lower
    body-saree hem.

    The pallu is excluded so the bottom border does not
    overwrite the hanging pallu.
    """

    H, W = bottom_mask.shape
    bh, bw = border_source.shape[:2]

    # --------------------------------------------------------
    # Body saree only.
    # --------------------------------------------------------

    body_mask = cv2.bitwise_and(
        bottom_mask,
        cv2.bitwise_not(pallu_mask)
    )

    # --------------------------------------------------------
    # Find the bottom-most body-saree pixel at each x.
    # --------------------------------------------------------

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
            hem[x] = float(ys.max())

    valid = np.where(
        hem >= 0
    )[0]

    if len(valid) < 20:
        raise RuntimeError(
            "Could not determine saree bottom hem."
        )

    first_x = int(valid.min())
    last_x = int(valid.max())

    # --------------------------------------------------------
    # Fill missing hem positions.
    # --------------------------------------------------------

    hem_segment = hem[
        first_x:last_x + 1
    ]

    hem[
        first_x:last_x + 1
    ] = fill_missing_boundary(
        hem_segment
    )

    # --------------------------------------------------------
    # Create inverse maps.
    # --------------------------------------------------------

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

    # border.png is a thin strip.
    # Keep its complete available height.
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

    # --------------------------------------------------------
    # Warp border source.
    # --------------------------------------------------------

    warped = cv2.remap(
        border_source,
        np.maximum(map_x, 0),
        np.maximum(map_y, 0),
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT
    )

    border_mask = (
        valid_pixels.astype(np.uint8) * 255
    )

    # Keep border inside actual saree.
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
    print("     STAGE 10 — PALLU + BOTTOM BORDER")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Load base image.
    # --------------------------------------------------------

    base = load_image(
        BASE
    )

    # --------------------------------------------------------
    # Load supplier sources.
    # --------------------------------------------------------

    pallu_source = load_image(
        PALLU_SOURCE
    )

    border_source = load_image(
        BORDER_SOURCE
    )

    # --------------------------------------------------------
    # Load masks.
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

    # ========================================================
    # 1. Rebuild hanging pallu ONLY.
    #
    # IMPORTANT:
    # There is NO artificial shoulder rectangle.
    # ========================================================

    print("[1/3] Rebuilding hanging pallu...")

    hanging_pallu, hanging_mask = (
        build_hanging_pallu(
            pallu_source,
            pallu_mask
        )
    )
    hanging_pallu = add_pallu_fold_shading(hanging_pallu, hanging_mask)

    # ========================================================
    # 2. Composite pallu.
    # ========================================================

    print("[2/3] Compositing pallu...")

    result = base.copy()

    result = alpha_blend(
        result,
        hanging_pallu,
        hanging_mask
    )

    # ========================================================
    # 3. Add bottom body border.
    #
    # IMPORTANT:
    # border.png is ONLY used here.
    # ========================================================

    print("[3/3] Aligning bottom border...")

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

    # ========================================================
    # Restore original arms/hands.
    # ========================================================

    foreground = cv2.bitwise_or(
        left_arm,
        right_arm
    )

    foreground = cv2.morphologyEx(
        foreground,
        cv2.MORPH_CLOSE,
        np.ones((3, 3), np.uint8)
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

    # ========================================================
    # Save final.
    # ========================================================

    cv2.imwrite(
        OUTPUT,
        result,
        [
            cv2.IMWRITE_PNG_COMPRESSION,
            3
        ]
    )

    # ========================================================
    # Debug image: pallu only.
    # ========================================================

    pallu_debug = np.zeros_like(
        base
    )

    pallu_debug = alpha_blend(
        pallu_debug,
        hanging_pallu,
        hanging_mask
    )

    cv2.imwrite(
        PALLU_DEBUG,
        pallu_debug
    )

    # ========================================================
    # Debug image: border only.
    # ========================================================

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

    # ========================================================
    # Done.
    # ========================================================

    print()
    print("=" * 60)
    print("✅ STAGE 10 COMPLETE")
    print("=" * 60)
    print()
    print(f"Final : {OUTPUT}")
    print(f"Pallu : {PALLU_DEBUG}")
    print(f"Border: {BORDER_DEBUG}")
    print()


if __name__ == "__main__":
    main()
