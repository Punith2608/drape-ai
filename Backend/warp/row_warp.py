"""Low-memory row-based fabric warp helpers."""

import cv2
import numpy as np


def row_interpolated_warp(
    texture: np.ndarray,
    src_points: np.ndarray,
    dst_points: np.ndarray,
    out_h: int,
    out_w: int,
    points_per_row: int = 5,
) -> np.ndarray:
    """Map a regular source grid to smoothly interpolated destination rows.

    The VTO stages create five evenly spaced control points for every garment
    row. Interpolating those row boundaries directly avoids the temporary
    allocations made by SciPy's general TPS implementation.
    """
    rows = len(src_points) // points_per_row
    if rows < 2 or len(src_points) != rows * points_per_row:
        raise RuntimeError("Warp needs at least two complete control rows.")

    row_y = dst_points[::points_per_row, 1]
    left_edge = dst_points[::points_per_row, 0]
    right_edge = dst_points[points_per_row - 1::points_per_row, 0]
    source_y = src_points[::points_per_row, 1]

    target_y = np.arange(out_h, dtype=np.float32)
    # np.interp returns float64, so cast immediately before any image-sized
    # operation to avoid silently doubling the temporary-memory requirement.
    left = np.interp(target_y, row_y, left_edge).astype(np.float32)
    right = np.interp(target_y, row_y, right_edge).astype(np.float32)
    source_row_y = np.interp(target_y, row_y, source_y).astype(np.float32)

    output = np.empty((out_h, out_w, 3), dtype=np.uint8)
    target_x = np.arange(out_w, dtype=np.float32)[None, :]
    rows_per_chunk = 32

    for y0 in range(0, out_h, rows_per_chunk):
        y1 = min(y0 + rows_per_chunk, out_h)
        width = np.maximum(right[y0:y1] - left[y0:y1], 1.0)[:, None]
        map_x = (target_x - left[y0:y1, None]) / width
        map_x *= texture.shape[1] - 1
        np.clip(map_x, 0, texture.shape[1] - 1, out=map_x)

        map_y = np.empty((y1 - y0, out_w), dtype=np.float32)
        map_y[:] = source_row_y[y0:y1, None]
        np.clip(map_y, 0, texture.shape[0] - 1, out=map_y)

        output[y0:y1] = cv2.remap(
            texture,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )

    return output
