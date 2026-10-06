import cv2
import numpy as np
import os

model = cv2.imread("model.png")

mask = cv2.imread(
    "masks/bottom_body.png",
    cv2.IMREAD_GRAYSCALE
)

texture = cv2.imread(
    r"E:\vto_project\assets\saree_texture.webp"
)

print("model loaded:", model is not None)
print("mask loaded:", mask is not None)
print("texture loaded:", texture is not None)

h, w = model.shape[:2]

texture = cv2.resize(texture, (w, h))

mask3 = cv2.merge([mask, mask, mask])

result = np.where(mask3 > 0, texture, model)

os.makedirs("outputs", exist_ok=True)

cv2.imwrite("outputs/test_overlay.jpg", result)

print("Saved outputs/test_overlay.jpg")