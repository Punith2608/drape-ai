import cv2

files = [
    "../supplier/body.png",
    "../supplier/border.png",
    "../supplier/pallu.png"
]

for f in files:

    img = cv2.imread(f)

    if img is None:
        print(f"{f} NOT FOUND")
        continue

    h, w = img.shape[:2]

    print(f"{f}")

    print(f"Width : {w}")

    print(f"Height: {h}")

    print("-"*40)