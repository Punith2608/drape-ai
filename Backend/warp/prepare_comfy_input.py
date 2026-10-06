import cv2
import os


INPUT_IMAGE = "../outputs/vto_stage9_realism.png"
INPUT_MASK = "../outputs/refine_mask.png"

OUTPUT_IMAGE = "../outputs/comfy_input.png"
OUTPUT_MASK = "../outputs/comfy_mask.png"


def main():

    image = cv2.imread(INPUT_IMAGE, cv2.IMREAD_COLOR)
    mask = cv2.imread(INPUT_MASK, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(INPUT_IMAGE)

    if mask is None:
        raise FileNotFoundError(INPUT_MASK)

    # SD 1.5 friendly resolution for a 4 GB GPU.
    width = 512
    height = 768

    image = cv2.resize(
        image,
        (width, height),
        interpolation=cv2.INTER_AREA
    )

    mask = cv2.resize(
        mask,
        (width, height),
        interpolation=cv2.INTER_NEAREST
    )

    # Make sure the mask is clean.
    _, mask = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    os.makedirs("../outputs", exist_ok=True)

    cv2.imwrite(
        OUTPUT_IMAGE,
        image
    )

    cv2.imwrite(
        OUTPUT_MASK,
        mask
    )

    print("✅ ComfyUI input prepared")
    print("Image:", OUTPUT_IMAGE)
    print("Mask :", OUTPUT_MASK)
    print("Size :", image.shape[1], "x", image.shape[0])


if __name__ == "__main__":
    main()