import cv2

mask = cv2.imread(
    "base_models/front/masks/full_body.png",
    cv2.IMREAD_GRAYSCALE
)

mask = cv2.bitwise_not(mask)

cv2.imwrite(
    "base_models/front/masks/full_body.png",
    mask
)

print("Mask inverted")