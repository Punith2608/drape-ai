from controlnet_aux import OpenposeDetector
from PIL import Image

print("Loading OpenPose...")

detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

image = Image.open("../base_models/front/model.png")

pose = detector(image)

pose.save("pose_output.png")

print("Done.")