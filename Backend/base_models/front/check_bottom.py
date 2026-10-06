import cv2
import matplotlib.pyplot as plt

mask = cv2.imread(
    "base_models/front/masks/bottom_body.png",
    cv2.IMREAD_GRAYSCALE
)

print(mask.shape)
print(mask.max())
print(mask.min())

plt.imshow(mask, cmap="gray")
plt.title("bottom_body")
plt.show()