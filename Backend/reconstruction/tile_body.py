import cv2
import numpy as np
import os

BODY = "../supplier/body.png"

OUT = "../textures/body_tiled.png"

os.makedirs("../textures", exist_ok=True)

img = cv2.imread(BODY)

if img is None:
    raise FileNotFoundError(BODY)

# Repeat counts
repeat_x = 5
repeat_y = 10

tiled = np.tile(img, (repeat_y, repeat_x, 1))

cv2.imwrite(OUT, tiled)

print("Saved:", OUT)
print("Shape:", tiled.shape)