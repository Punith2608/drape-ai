import cv2
import json
from controlnet_aux import OpenposeDetector

print("Loading detector...")

detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

# Read image using OpenCV
image = cv2.imread("../base_models/front/model.png")

# Convert BGR → RGB
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

print("Detecting pose...")

poses = detector.detect_poses(image)

pose = poses[0]

points = {}

for i, kp in enumerate(pose.body.keypoints):
    if kp is None:
        continue

    points[i] = {
        "x": float(kp.x),
        "y": float(kp.y)
    }

with open("pose.json", "w") as f:
    json.dump(points, f, indent=4)

print("Saved pose.json")