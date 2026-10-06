import cv2
import numpy as np
import os

BODY = "../textures/body_tiled.png"
BORDER = "../supplier/border.png"
PALLU = "../supplier/pallu.png"

OUTPUT = "../textures/saree_texture.png"

body = cv2.imread(BODY)
border = cv2.imread(BORDER)
pallu = cv2.imread(PALLU)

if body is None:
    raise FileNotFoundError(BODY)

if border is None:
    raise FileNotFoundError(BORDER)

if pallu is None:
    raise FileNotFoundError(PALLU)

body_h, body_w = body.shape[:2]

# Resize pallu to body width
new_pallu_h = int(pallu.shape[0] * body_w / pallu.shape[1])
pallu = cv2.resize(pallu, (body_w, new_pallu_h))

# Resize border to body width
new_border_h = int(border.shape[0] * body_w / border.shape[1])
border = cv2.resize(border, (body_w, new_border_h))

# Stack everything
texture = np.vstack([
    pallu,
    body,
    border
])

os.makedirs("../textures", exist_ok=True)

cv2.imwrite(OUTPUT, texture)

print("Saved:", OUTPUT)
print("Final Size:", texture.shape)