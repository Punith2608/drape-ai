import json
import cv2
import numpy as np
import os

with open("model.json", "r") as f:
    data = json.load(f)

h = data["imageHeight"]
w = data["imageWidth"]

os.makedirs("masks", exist_ok=True)

for shape in data["shapes"]:
    label = shape["label"].lower().replace(" ", "_")

    mask = np.zeros((h, w), dtype=np.uint8)

    pts = np.array(shape["points"], dtype=np.int32)

    cv2.fillPoly(mask, [pts], 255)

    cv2.imwrite(f"masks/{label}.png", mask)

    print(f"Saved masks/{label}.png")