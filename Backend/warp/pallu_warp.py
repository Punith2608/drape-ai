import cv2
import numpy as np
import os

from row_warp import row_interpolated_warp

TEXTURE = "../supplier/pallu.png"
MASK = "../base_models/front/masks/pallu.png"
OUTPUT = "../outputs/pallu_tps.png"


def find_boundary(mask, y):
    row = mask[y]
    xs = np.where(row > 127)[0]

    if len(xs) < 10:
        return None

    return int(xs.min()), int(xs.max())


def build_control_points(mask, texture_w, texture_h):
    H, W = mask.shape

    # More points because pallu has a long drape.
    ys = np.linspace(0.02, 0.98, 12)
    xs = np.linspace(0.0, 1.0, 5)

    src = []
    dst = []

    valid_rows = []

    for yn in ys:
        y = int(yn * (H - 1))

        boundary = find_boundary(mask, y)

        if boundary is None:
            continue

        left, right = boundary
        valid_rows.append((y, left, right))

    if len(valid_rows) < 5:
        raise RuntimeError(
            "Pallu mask does not contain enough valid rows."
        )

    for i, (y, left, right) in enumerate(valid_rows):

        v = i / max(len(valid_rows) - 1, 1)

        source_y = v * (texture_h - 1)

        for u in xs:

            source_x = u * (texture_w - 1)

            target_x = left + u * (right - left)
            target_y = y

            src.append([source_x, source_y])
            dst.append([target_x, target_y])

    return (
        np.asarray(src, dtype=np.float32),
        np.asarray(dst, dtype=np.float32)
    )


def warp_tps(texture, src, dst, H, W):

    return row_interpolated_warp(texture, src, dst, H, W)

    inverse_tps = RBFInterpolator(
        dst,
        src,
        kernel="thin_plate_spline",
        smoothing=2.0
    )

    map_x = np.zeros((H, W), dtype=np.float32)
    map_y = np.zeros((H, W), dtype=np.float32)

    chunk = 32

    for y0 in range(0, H, chunk):

        y1 = min(y0 + chunk, H)

        yy, xx = np.mgrid[y0:y1, 0:W]

        query = np.column_stack([
            xx.ravel(),
            yy.ravel()
        ])

        mapped = inverse_tps(query)

        map_x[y0:y1] = mapped[:, 0].reshape(
            y1 - y0,
            W
        )

        map_y[y0:y1] = mapped[:, 1].reshape(
            y1 - y0,
            W
        )

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

    texture = cv2.imread(TEXTURE)
    mask = cv2.imread(MASK, cv2.IMREAD_GRAYSCALE)

    if texture is None:
        raise FileNotFoundError(
            f"Could not load: {TEXTURE}"
        )

    if mask is None:
        raise FileNotFoundError(
            f"Could not load: {MASK}"
        )

    H, W = mask.shape

    src, dst = build_control_points(
        mask,
        texture.shape[1],
        texture.shape[0]
    )

    print(
        f"Using {len(src)} pallu TPS control points"
    )

    warped = warp_tps(
        texture,
        src,
        dst,
        H,
        W
    )

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
