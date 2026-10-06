import cv2
import numpy as np
from pathlib import Path

from row_warp import row_interpolated_warp


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT = Path(__file__).resolve().parent.parent

TEXTURE = PROJECT / "textures" / "body_tiled.png"
MASK = PROJECT / "base_models" / "front" / "masks" / "top.png"
OUTPUT_DIR = PROJECT / "outputs"
OUTPUT = OUTPUT_DIR / "top_tps.png"


# ============================================================
# MASK BOUNDARY
# ============================================================

def get_boundary(mask, y):
    """
    Get the left and right boundaries of the mask at row y.
    """

    row = mask[y]

    xs = np.where(row > 127)[0]

    # Ignore rows with very little mask content
    if len(xs) < 20:
        return None

    left = int(xs.min())
    right = int(xs.max())

    # Ignore extremely narrow rows
    if right - left < 10:
        return None

    return left, right


# ============================================================
# BUILD TPS CONTROL POINTS
# ============================================================

def build_control_points(mask, texture_width, texture_height):

    H, W = mask.shape

    # --------------------------------------------------------
    # Find rows that ACTUALLY contain mask pixels
    # --------------------------------------------------------

    valid_rows = np.where(
        np.any(mask > 127, axis=1)
    )[0]

    if len(valid_rows) < 4:
        raise RuntimeError(
            f"Top mask has only {len(valid_rows)} valid rows."
        )

    print(
        f"Top mask rows: "
        f"{valid_rows[0]} -> {valid_rows[-1]}"
    )

    print(
        f"Total valid rows: {len(valid_rows)}"
    )

    # --------------------------------------------------------
    # Select rows inside the actual mask
    #
    # We use 8 rows distributed through the mask.
    # --------------------------------------------------------

    number_of_rows = min(8, len(valid_rows))

    row_indices = np.linspace(
        0,
        len(valid_rows) - 1,
        number_of_rows
    ).astype(int)

    selected_rows = valid_rows[row_indices]

    print(
        "Selected rows:",
        selected_rows.tolist()
    )

    # --------------------------------------------------------
    # Five points horizontally across the texture
    # --------------------------------------------------------

    x_norms = np.linspace(
        0.0,
        1.0,
        5
    )

    src = []
    dst = []

    # --------------------------------------------------------
    # Generate control points
    # --------------------------------------------------------

    for i, y in enumerate(selected_rows):

        boundary = get_boundary(mask, y)

        if boundary is None:
            continue

        left, right = boundary

        # Map mask row to texture Y
        sy = (
            i / max(number_of_rows - 1, 1)
        ) * (texture_height - 1)

        for xn in x_norms:

            # Source texture coordinate
            sx = xn * (texture_width - 1)

            # Destination coordinate inside mask
            dx = left + xn * (right - left)
            dy = y

            src.append([
                sx,
                sy
            ])

            dst.append([
                dx,
                dy
            ])

    # --------------------------------------------------------
    # Validate control points
    # --------------------------------------------------------

    if len(src) < 20:
        raise RuntimeError(
            f"Only {len(src)} TPS control points generated."
        )

    src = np.asarray(
        src,
        dtype=np.float32
    )

    dst = np.asarray(
        dst,
        dtype=np.float32
    )

    print(
        f"Generated {len(src)} control points"
    )

    return src, dst


# ============================================================
# TPS WARP
# ============================================================

def warp_tps(
    texture,
    src_points,
    dst_points,
    H,
    W
):

    return row_interpolated_warp(texture, src_points, dst_points, H, W)

    print("Building inverse TPS...")

    inverse_tps = RBFInterpolator(
        dst_points,
        src_points,
        kernel="thin_plate_spline",
        smoothing=2.0
    )

    map_x = np.zeros(
        (H, W),
        dtype=np.float32
    )

    map_y = np.zeros(
        (H, W),
        dtype=np.float32
    )

    # Process image in chunks to reduce memory usage
    chunk = 32

    for y0 in range(
        0,
        H,
        chunk
    ):

        y1 = min(
            y0 + chunk,
            H
        )

        yy, xx = np.mgrid[
            y0:y1,
            0:W
        ]

        query = np.column_stack([
            xx.ravel(),
            yy.ravel()
        ])

        mapped = inverse_tps(
            query
        )

        map_x[
            y0:y1
        ] = mapped[
            :, 0
        ].reshape(
            y1 - y0,
            W
        )

        map_y[
            y0:y1
        ] = mapped[
            :, 1
        ].reshape(
            y1 - y0,
            W
        )

    # --------------------------------------------------------
    # Keep coordinates inside texture
    # --------------------------------------------------------

    map_x = np.clip(
        map_x,
        0,
        texture.shape[1] - 1
    )

    map_y = np.clip(
        map_y,
        0,
        texture.shape[0] - 1
    )

    # --------------------------------------------------------
    # Remap texture
    # --------------------------------------------------------

    warped = cv2.remap(
        texture,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    return warped


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("TOP BODY TPS WARP")
    print("=" * 60)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Print paths
    # --------------------------------------------------------

    print()
    print("Texture:")
    print(TEXTURE)

    print()
    print("Mask:")
    print(MASK)

    print()
    print("Output:")
    print(OUTPUT)

    # --------------------------------------------------------
    # Check files before loading
    # --------------------------------------------------------

    if not TEXTURE.exists():
        raise FileNotFoundError(
            f"Texture does not exist:\n{TEXTURE}"
        )

    if not MASK.exists():
        raise FileNotFoundError(
            f"Top mask does not exist:\n{MASK}"
        )

    # --------------------------------------------------------
    # Load texture
    # --------------------------------------------------------

    texture = cv2.imread(
        str(TEXTURE),
        cv2.IMREAD_COLOR
    )

    # --------------------------------------------------------
    # Load mask
    # --------------------------------------------------------

    mask = cv2.imread(
        str(MASK),
        cv2.IMREAD_GRAYSCALE
    )

    if texture is None:
        raise RuntimeError(
            f"OpenCV could not load texture:\n{TEXTURE}"
        )

    if mask is None:
        raise RuntimeError(
            f"OpenCV could not load mask:\n{MASK}"
        )

    print()
    print("Texture shape:", texture.shape)
    print("Mask shape:", mask.shape)

    # --------------------------------------------------------
    # Check mask contents
    # --------------------------------------------------------

    mask_pixels = np.count_nonzero(
        mask > 127
    )

    valid_rows = np.count_nonzero(
        np.any(mask > 127, axis=1)
    )

    valid_cols = np.count_nonzero(
        np.any(mask > 127, axis=0)
    )

    print()
    print("Mask pixels:", mask_pixels)
    print("Valid rows:", valid_rows)
    print("Valid columns:", valid_cols)

    if mask_pixels == 0:
        raise RuntimeError(
            "Top mask contains no foreground pixels."
        )

    # --------------------------------------------------------
    # Mask dimensions become output dimensions
    # --------------------------------------------------------

    H, W = mask.shape

    # --------------------------------------------------------
    # Build TPS control points
    # --------------------------------------------------------

    src, dst = build_control_points(
        mask,
        texture.shape[1],
        texture.shape[0]
    )

    print()
    print("Using", len(src), "control points")

    # --------------------------------------------------------
    # Perform TPS warp
    # --------------------------------------------------------

    warped = warp_tps(
        texture,
        src,
        dst,
        H,
        W
    )

    # --------------------------------------------------------
    # Apply top-body mask
    # --------------------------------------------------------

    result = cv2.bitwise_and(
        warped,
        warped,
        mask=mask
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    success = cv2.imwrite(
        str(OUTPUT),
        result
    )

    if not success:
        raise RuntimeError(
            f"OpenCV failed to save:\n{OUTPUT}"
        )

    # --------------------------------------------------------
    # Verify output exists
    # --------------------------------------------------------

    if not OUTPUT.exists():
        raise RuntimeError(
            f"Output was reported as saved, "
            f"but file does not exist:\n{OUTPUT}"
        )

    print()
    print("=" * 60)
    print("✅ TPS WARP COMPLETE")
    print("=" * 60)

    print()
    print("Saved:")
    print(OUTPUT)

    print()
    print("Output size:")
    print(result.shape)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
