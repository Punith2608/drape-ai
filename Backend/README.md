# Saree virtual try-on prototype

This project builds a deterministic saree try-on image from a model photo,
supplier garment assets, and manually prepared masks. It produces intermediate
images in `outputs/`, finishing at `outputs/vto_stage10_pallu_border.png`.

## Setup

Python 3.10 or newer is recommended. Create and activate a virtual environment,
then install the project dependencies:

```powershell
py -m venv vto_env
.\vto_env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The included `requirements.txt` covers the deterministic renderer and the
optional SAM, OpenPose, and ComfyUI helper scripts. For CUDA acceleration,
install the matching PyTorch build from the official PyTorch installer before
installing the remaining requirements.

## Run

Use the bundled environment from the project root:

```powershell
.\vto_env\Scripts\python.exe .\run_pipeline.py
```

Check the expected files and render order without changing outputs:

```powershell
.\vto_env\Scripts\python.exe .\run_pipeline.py --dry-run
```

To retry only a later portion, use `--from-stage realism` or another listed
stage. The optional `warp/run_comfy_refinement.py` requires a running local
ComfyUI instance and is deliberately not part of the deterministic run.

## Web portal

The portal is served by the dependency-free local web application in
`app.py`. It exposes the fixed signature model and the prepared sarees in the
portal catalogue. When a visitor selects a saree, the application creates a
background job, runs the existing deterministic renderer, and returns the
generated final image to the browser.

Start it from the project root:

```powershell
.\vto_env\Scripts\python.exe .\app.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). The original
standalone HTML file should be opened through this server rather than directly
from disk, because its live API requests require an HTTP origin.

The current repository has one prepared supplier saree, so the API exposes one
catalogue entry. Add more prepared garment asset sets before adding more
catalogue records; otherwise different catalogue choices would incorrectly
produce the same rendered garment.

## Inputs

- `base_models/front/model.png`: model image
- `base_models/front/masks/`: top, bottom, blouse, pallu, and arm masks
- `supplier/blouse.png`, `supplier/border.png`, and `supplier/pallu.png`:
  garment source assets
- `supplier/body.png`: body fabric source; the pipeline creates
  `textures/body_tiled.png` from it automatically

Every full pipeline run regenerates `textures/body_tiled.png` from
`supplier/body.png` before warping the garment. This makes a new body fabric
take effect automatically.

## Optional tools

- `segment_test.py` creates a full-body mask with Segment Anything and expects
  `weights/sam_vit_h.pth` to be present.
- `pose/detect_pose.py` and `pose/save_landmarks.py` download OpenPose model
  files on first use.
- `warp/run_comfy_refinement.py` requires a separately running local ComfyUI
  server and an `sd-v1-5-inpainting.ckpt` checkpoint. It is not part of the
  deterministic pipeline.

## Current limitations

The masks are input-specific and the current deformation is 2D. Results will
be most reliable for a front-facing, upright model. Use quality review for
hands, shoulder drape, hem alignment, texture scale, and garment colour before
sharing a render.
