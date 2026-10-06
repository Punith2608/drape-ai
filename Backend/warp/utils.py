import json

def load_pose(path, width, height):

    with open(path) as f:
        pose = json.load(f)

    pts = {}

    for k, v in pose.items():

        pts[int(k)] = (
            int(v["x"] * width),
            int(v["y"] * height)
        )

    return pts