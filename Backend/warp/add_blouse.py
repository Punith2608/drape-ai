import cv2
import numpy as np

BASE = "../outputs/vto_stage5_lit.png"
BLOUSE = "../outputs/blouse_tps.png"
MASK = "../base_models/front/masks/blouse.png"

OUTPUT = "../outputs/vto_stage6_blouse.png"

base = cv2.imread(BASE)
blouse = cv2.imread(BLOUSE)
mask = cv2.imread(MASK, cv2.IMREAD_GRAYSCALE)

if base is None:
    raise FileNotFoundError(BASE)

if blouse is None:
    raise FileNotFoundError(BLOUSE)

if mask is None:
    raise FileNotFoundError(MASK)

# Slight feathering.
alpha = cv2.GaussianBlur(mask, (5, 5), 0)
alpha = alpha.astype(np.float32) / 255.0
alpha = alpha[:, :, None]

result = (
    base.astype(np.float32) * (1.0 - alpha)
    + blouse.astype(np.float32) * alpha
)

result = np.clip(result, 0, 255).astype(np.uint8)

cv2.imwrite(OUTPUT, result)

print("✅ Blouse added")
print("Saved:", OUTPUT)