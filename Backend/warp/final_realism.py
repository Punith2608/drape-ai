import cv2
import numpy as np
import os


MODEL = "../base_models/front/model.png"
INPUT = "../outputs/vto_stage8_border.png"

TOP_MASK = "../base_models/front/masks/top.png"
BOTTOM_MASK = "../base_models/front/masks/bottom.png"
PALLU_MASK = "../base_models/front/masks/pallu.png"
BLOUSE_MASK = "../base_models/front/masks/blouse.png"

OUTPUT = "../outputs/vto_stage9_realism.png"


def load_mask(path, shape):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise FileNotFoundError(path)

    h, w = shape[:2]

    if mask.shape != (h, w):
        mask = cv2.resize(
            mask,
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )

    return mask


def create_garment_mask(shape):
    top = load_mask(TOP_MASK, shape)
    bottom = load_mask(BOTTOM_MASK, shape)
    pallu = load_mask(PALLU_MASK, shape)
    blouse = load_mask(BLOUSE_MASK, shape)

    mask = cv2.bitwise_or(top, bottom)
    mask = cv2.bitwise_or(mask, pallu)
    mask = cv2.bitwise_or(mask, blouse)

    return mask


def create_light_map(model, garment_mask):
    gray = cv2.cvtColor(
        model,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    region = garment_mask > 30

    if not np.any(region):
        raise RuntimeError("Garment mask is empty.")

    values = gray[region]

    low, high = np.percentile(
        values,
        [5, 95]
    )

    global_light = (
        (gray - low) /
        max(high - low, 1.0)
    )

    global_light = np.clip(
        global_light,
        0.0,
        1.0
    )

    # Keep the effect subtle.
    global_light = (
        0.78 +
        global_light * 0.30
    )

    blurred = cv2.GaussianBlur(
        gray,
        (0, 0),
        18
    )

    local_ratio = gray / (
        blurred + 1e-6
    )

    local_light = 1.0 + (
        local_ratio - 1.0
    ) * 0.65

    local_light = np.clip(
        local_light,
        0.78,
        1.22
    )

    light = (
        global_light * 0.6 +
        local_light * 0.4
    )

    return np.clip(
        light,
        0.70,
        1.25
    )


def add_pleats(image, bottom_mask):
    h, w = image.shape[:2]

    yy, xx = np.mgrid[0:h, 0:w]

    # Only affect lower portion.
    y_norm = yy.astype(np.float32) / max(h - 1, 1)

    # Start the effect around the waist and become
    # slightly stronger toward the hem.
    strength = np.clip(
        (y_norm - 0.35) / 0.65,
        0.0,
        1.0
    )

    # Use a few broad, slightly irregular folds instead of a perfectly
    # repeating full-frame stripe pattern.  This preserves the supplier weave
    # while making the drape look less synthetic.
    x_norm = xx.astype(np.float32) / max(w - 1, 1)
    phase = 0.65 * np.sin(y_norm * np.pi * 3.0)
    broad = np.cos((x_norm * 7.0 + phase) * np.pi * 2.0)
    fine = np.cos((x_norm * 15.0 - y_norm * 1.7) * np.pi * 2.0)
    wave = 0.75 * broad + 0.25 * fine

    shading = (
        1.0
        + 0.040 * wave * strength
    )

    region = bottom_mask > 127

    result = image.astype(np.float32)

    result[region] *= shading[region, None]

    return np.clip(
        result,
        0,
        255
    ).astype(np.uint8)


def apply_lighting(image, light_map, garment_mask):
    alpha = (
        garment_mask.astype(np.float32) /
        255.0
    )

    alpha = alpha[:, :, None]

    lit = (
        image.astype(np.float32)
        * light_map[:, :, None]
    )

    result = (
        image.astype(np.float32) * (1.0 - alpha)
        + lit * alpha
    )

    return np.clip(
        result,
        0,
        255
    ).astype(np.uint8)


def cleanup_edges(image, garment_mask):
    """
    Very mild edge smoothing.
    We don't want to blur the entire saree.
    """

    soft = cv2.GaussianBlur(image, (3, 3), 0)
    binary = (garment_mask > 127).astype(np.uint8)
    # Limit smoothing to a narrow interior/outside ring; blurring the whole
    # garment softens its weave and makes it appear painted on.
    inside = cv2.distanceTransform(binary, cv2.DIST_L2, 3)
    outside = cv2.distanceTransform(1 - binary, cv2.DIST_L2, 3)
    edge_ring = np.maximum(inside, outside)
    alpha = np.clip((2.5 - edge_ring) / 2.5, 0.0, 1.0) * 0.16

    alpha = alpha[:, :, None]

    result = (
        image.astype(np.float32) * (1.0 - alpha)
        + soft.astype(np.float32) * alpha
    )

    return np.clip(
        result,
        0,
        255
    ).astype(np.uint8)


def main():

    os.makedirs("../outputs", exist_ok=True)

    model = cv2.imread(
        MODEL,
        cv2.IMREAD_COLOR
    )

    image = cv2.imread(
        INPUT,
        cv2.IMREAD_COLOR
    )

    if model is None:
        raise FileNotFoundError(MODEL)

    if image is None:
        raise FileNotFoundError(INPUT)

    if image.shape[:2] != model.shape[:2]:
        image = cv2.resize(
            image,
            (model.shape[1], model.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )

    garment_mask = create_garment_mask(
        model.shape
    )

    bottom_mask = load_mask(
        BOTTOM_MASK,
        model.shape
    )

    # 1. Subtle pleats.
    result = add_pleats(
        image,
        bottom_mask
    )

    # 2. Re-use real photographic lighting.
    light_map = create_light_map(
        model,
        garment_mask
    )

    result = apply_lighting(
        result,
        light_map,
        garment_mask
    )

    # 3. Mild edge cleanup.
    result = cleanup_edges(
        result,
        garment_mask
    )

    cv2.imwrite(
        OUTPUT,
        result,
        [cv2.IMWRITE_PNG_COMPRESSION, 3]
    )

    print("✅ Final realism pass complete")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
