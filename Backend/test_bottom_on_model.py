import cv2

MODEL = "../base_models/front/model.png"
WARPED = "../outputs/bottom_tps_v2.png"
MASK = "../base_models/front/masks/bottom.png"
OUTPUT = "../outputs/bottom_model_preview.jpg"

model = cv2.imread(MODEL)
warped = cv2.imread(WARPED)
mask = cv2.imread(MASK, cv2.IMREAD_GRAYSCALE)

result = model.copy()

region = mask > 127

result[region] = warped[region]

cv2.imwrite(OUTPUT, result)

print("Saved:", OUTPUT)