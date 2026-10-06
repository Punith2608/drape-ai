import cv2
import numpy as np
import os

from row_warp import row_interpolated_warp

TEXTURE = "../supplier/blouse.png"
MASK = "../base_models/front/masks/blouse.png"
OUTPUT = "../outputs/blouse_tps.png"


def get_boundary(mask, y):
    row = mask[y]
    xs = np.where(row > 127)[0]

    if len(xs) < 10:
        return None

    left = int(xs.min())
    right = int(xs.max())

    if right - left < 10:
        return None

    return left, right


def build_control_points(mask, tex_w, tex_h):
    H, W = mask.shape

    # ---------------------------------------------------------
    # Find rows that actually contain blouse pixels
    # ---------------------------------------------------------

    valid_rows = np.where(
        np.any(mask > 127, axis=1)
    )[0]

    if len(valid_rows) < 4:
        raise RuntimeError(
            f"Blouse mask contains only {len(valid_rows)} valid rows."
        )

    print(
        f"Blouse mask row range: "
        f"{valid_rows[0]} -> {valid_rows[-1]}"
    )

    print(
        f"Total valid rows: {len(valid_rows)}"
    )

    # ---------------------------------------------------------
    # Select 8 rows INSIDE the actual blouse mask
    # ---------------------------------------------------------

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

    # 5 points across the blouse width
    x_norms = np.linspace(
        0.0,
        1.0,
        5
    )

    src = []
    dst = []

    # ---------------------------------------------------------
    # Build control points
    # ---------------------------------------------------------

    for i, y in enumerate(selected_rows):

        boundary = get_boundary(
            mask,
            y
        )

        if boundary is None:
            continue

        left, right = boundary

        # Map mask row to texture row
        v = (
            i / max(number_of_rows - 1, 1)
        )

        sy = v * (tex_h - 1)

        for u in x_norms:

            # Source texture coordinate
            sx = u * (tex_w - 1)

            # Destination coordinate
            dx = left + u * (right - left)
            dy = y

            src.append([
                sx,
                sy
            ])

            dst.append([
                dx,
                dy
            ])

    if len(src) < 20:
        raise RuntimeError(
            f"Only {len(src)} blouse TPS control points generated."
        )

    return (
        np.asarray(src, dtype=np.float32),
        np.asarray(dst, dtype=np.float32)
    )


def warp_tps(texture, src, dst, H, W):

    return row_interpolated_warp(texture, src, dst, H, W)

    print("Building inverse TPS...")

    inverse_tps = RBFInterpolator(
        dst,
        src,
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

    # Keep coordinates inside texture
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

    return cv2.remap(
        texture,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )


def main():

    # ---------------------------------------------------------
    # Correct output directory
    # ---------------------------------------------------------

    os.makedirs(
        "../outputs",
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Load texture and mask
    # ---------------------------------------------------------

    texture = cv2.imread(
        TEXTURE
    )

    mask = cv2.imread(
        MASK,
        cv2.IMREAD_GRAYSCALE
    )

    if texture is None:
        raise FileNotFoundError(
            f"Blouse texture not found: {TEXTURE}"
        )

    if mask is None:
        raise FileNotFoundError(
            f"Blouse mask not found: {MASK}"
        )

    print("Texture shape:", texture.shape)
    print("Mask shape:", mask.shape)

    # ---------------------------------------------------------
    # Mask statistics
    # ---------------------------------------------------------

    mask_pixels = np.count_nonzero(
        mask > 127
    )

    valid_rows = np.count_nonzero(
        np.any(mask > 127, axis=1)
    )

    valid_cols = np.count_nonzero(
        np.any(mask > 127, axis=0)
    )

    print("Mask pixels:", mask_pixels)
    print("Valid rows:", valid_rows)
    print("Valid columns:", valid_cols)

    if mask_pixels == 0:
        raise RuntimeError(
            "Blouse mask contains no valid pixels."
        )

    H, W = mask.shape

    # ---------------------------------------------------------
    # Build TPS control points
    # ---------------------------------------------------------

    src, dst = build_control_points(
        mask,
        texture.shape[1],
        texture.shape[0]
    )

    print(
        f"Using {len(src)} blouse TPS control points"
    )

    # ---------------------------------------------------------
    # Warp
    # ---------------------------------------------------------

    warped = warp_tps(
        texture,
        src,
        dst,
        H,
        W
    )

    # ---------------------------------------------------------
    # Apply blouse mask
    # ---------------------------------------------------------

    result = cv2.bitwise_and(
        warped,
        warped,
        mask=mask
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    success = cv2.imwrite(
        OUTPUT,
        result
    )

    if not success:
        raise RuntimeError(
            f"Failed to save output: {OUTPUT}"
        )

    print()
    print("==========================================")
    print("✅ BLOUSE TPS WARP COMPLETE")
    print("==========================================")
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
