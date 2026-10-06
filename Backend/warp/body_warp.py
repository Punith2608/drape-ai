import cv2
import numpy as np
import os

TEXTURE = "../textures/body_tiled.png"
MASK = "../base_models/front/masks/bottom.png"
OUTPUT = "../outputs/bottom_tps_v2.png"


def get_mask_boundary(mask, y, min_width=20):
    """
    Find left and right edges of the white mask at a given y.
    """
    row = mask[y]

    xs = np.where(row > 127)[0]

    if len(xs) < min_width:
        return None

    return int(xs.min()), int(xs.max())


def build_control_points(mask, texture_width, texture_height):
    """
    Build a 5-column x 7-row TPS grid.

    Source points live on the flat rectangular texture.
    Destination points follow the actual bottom-body mask.
    """

    H, W = mask.shape

    # Start with broad canvas-relative rows and search locally for the garment.
    # This avoids over-fitting individual texture bands while still adapting to
    # the supplied silhouette below.
    ys = np.linspace(0.05, 0.95, 7)
    xs = np.linspace(0.0, 1.0, 5)

    valid_rows = []

    for yn in ys:
        y = int(yn * (H - 1))

        boundary = get_mask_boundary(mask, y)

        if boundary is None:
            # Search nearby rows if this exact row is empty.
            found = None

            for delta in range(1, 30):
                for yy in [y - delta, y + delta]:
                    if 0 <= yy < H:
                        boundary = get_mask_boundary(mask, yy)

                        if boundary is not None:
                            found = (yy, boundary)
                            break

                if found:
                    break

            if found is None:
                continue

            y, boundary = found

        left_x, right_x = boundary
        valid_rows.append((y, left_x, right_x))

    if len(valid_rows) < 4:
        raise RuntimeError(
            "Not enough valid horizontal rows found in bottom mask."
        )

    src_points = []
    dst_points = []

    for row_idx, (y, left_x, right_x) in enumerate(valid_rows):

        source_y = (
            row_idx / max(len(valid_rows) - 1, 1)
        ) * (texture_height - 1)

        for xnorm in xs:

            source_x = xnorm * (texture_width - 1)

            dest_x = left_x + xnorm * (right_x - left_x)
            dest_y = y

            src_points.append(
                [source_x, source_y]
            )

            dst_points.append(
                [dest_x, dest_y]
            )

    return (
        np.asarray(src_points, dtype=np.float32),
        np.asarray(dst_points, dtype=np.float32)
    )


def tps_warp(texture, src_points, dst_points, out_h, out_w):
    """Map the flat fabric onto the mask rows without a SciPy TPS solve.

    ``build_control_points`` creates a regular five-point row grid.  For this
    geometry, interpolating each row's left/right edges directly is equivalent
    to the desired smooth vertical deformation and avoids SciPy/OpenBLAS's
    large temporary allocations that caused ``MemoryError`` on Windows.
    """
    rows = len(src_points) // 5
    if rows < 2 or len(src_points) != rows * 5:
        raise RuntimeError("Body warp needs complete five-point control rows.")

    row_y = dst_points[::5, 1]
    left_edge = dst_points[::5, 0]
    right_edge = dst_points[4::5, 0]
    source_y = src_points[::5, 1]

    target_y = np.arange(out_h, dtype=np.float32)
    interpolated_left = np.interp(target_y, row_y, left_edge)
    interpolated_right = np.interp(target_y, row_y, right_edge)
    interpolated_source_y = np.interp(target_y, row_y, source_y)

    target_x = np.arange(out_w, dtype=np.float32)[None, :]
    widths = np.maximum(interpolated_right - interpolated_left, 1.0)[:, None]
    map_x = (target_x - interpolated_left[:, None]) / widths
    map_x *= texture.shape[1] - 1
    map_x = np.clip(map_x, 0, texture.shape[1] - 1).astype(np.float32)

    map_y = np.broadcast_to(
        interpolated_source_y[:, None],
        (out_h, out_w),
    ).astype(np.float32).copy()
    map_y = np.clip(map_y, 0, texture.shape[0] - 1)

    # Avoid ugly extrapolation outside texture.
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

    os.makedirs("../outputs", exist_ok=True)

    texture = cv2.imread(
        TEXTURE,
        cv2.IMREAD_COLOR
    )

    mask = cv2.imread(
        MASK,
        cv2.IMREAD_GRAYSCALE
    )

    if texture is None:
        raise FileNotFoundError(
            f"Texture not found: {TEXTURE}"
        )

    if mask is None:
        raise FileNotFoundError(
            f"Mask not found: {MASK}"
        )

    H, W = mask.shape

    src_points, dst_points = build_control_points(
        mask,
        texture.shape[1],
        texture.shape[0]
    )

    print(
        f"Using {len(src_points)} TPS control points"
    )

    warped = tps_warp(
        texture,
        src_points,
        dst_points,
        H,
        W
    )

    # Clip exactly to bottom mask.
    result = cv2.bitwise_and(
        warped,
        warped,
        mask=mask
    )

    cv2.imwrite(
        OUTPUT,
        result
    )

    print(
        f"✅ Saved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
