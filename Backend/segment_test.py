import cv2
import torch
import numpy as np

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

IMAGE_PATH = "base_models/front/model.png"
CHECKPOINT = "weights/sam_vit_h.pth"

device = "cpu"

print("Loading SAM...")
sam = sam_model_registry["vit_h"](checkpoint=CHECKPOINT)
sam.to(device)

mask_generator = SamAutomaticMaskGenerator(sam)

image = cv2.imread(IMAGE_PATH)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

print("Generating masks...")
masks = mask_generator.generate(image_rgb)

largest = max(masks, key=lambda x: x["area"])

mask = largest["segmentation"].astype(np.uint8) * 255

cv2.imwrite(
    "base_models/front/masks/full_body.png",
    mask
)

print("Saved full_body.png")