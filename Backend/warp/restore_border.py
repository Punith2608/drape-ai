"""Add the supplier hem border to the deterministic base composite.

The border is generated from source assets and masks, rather than an old
intermediate render, so this stage works in a fresh ``outputs`` directory.
"""

import os

import cv2

from stage10_pallu_border import alpha_blend, build_bottom_border, load_mask


BASE = "../outputs/vto_stage8_base.png"
BORDER_SOURCE = "../supplier/border.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"
PALLU_MASK = "../base_models/front/masks/pallu.png"
OUTPUT = "../outputs/vto_stage8_border.png"


def main():
    os.makedirs("../outputs", exist_ok=True)

    base = cv2.imread(BASE, cv2.IMREAD_COLOR)
    border_source = cv2.imread(BORDER_SOURCE, cv2.IMREAD_COLOR)

    if base is None:
        raise FileNotFoundError(f"Base image not found: {BASE}")
    if border_source is None:
        raise FileNotFoundError(f"Border source not found: {BORDER_SOURCE}")

    bottom_mask = load_mask(BOTTOM_MASK, base.shape)
    pallu_mask = load_mask(PALLU_MASK, base.shape)
    border_layer, border_mask = build_bottom_border(
        border_source,
        bottom_mask,
        pallu_mask,
    )
    result = alpha_blend(base, border_layer, border_mask)

    if not cv2.imwrite(OUTPUT, result):
        raise RuntimeError(f"Could not save border composite: {OUTPUT}")

    print("✅ Bottom border rendered from supplier asset")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
