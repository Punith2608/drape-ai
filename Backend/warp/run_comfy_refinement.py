import os
import time
import uuid
import requests


# ============================================================
# CONFIGURATION
# ============================================================

COMFY_URL = "http://127.0.0.1:8188"

INPUT_IMAGE = r"E:\vto_project\outputs\comfy_input.png"
INPUT_MASK = r"E:\vto_project\outputs\ai_mask.png"

OUTPUT_DIR = r"E:\vto_project\outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "comfy_refined_v2.png")

CHECKPOINT = "sd-v1-5-inpainting.ckpt"

TIMEOUT = 300


# ============================================================
# PROMPTS
# ============================================================

POSITIVE_PROMPT = (
    "photorealistic dark green silk saree, "
    "preserve the exact existing garment, "
    "preserve exact green color, "
    "preserve gold zari, "
    "preserve existing person, "
    "preserve face, "
    "preserve hands, "
    "preserve jewelry, "
    "subtle natural cloth fold, "
    "subtle realistic shadow, "
    "minimal modification"
)

NEGATIVE_PROMPT = (
     "gray fabric, "
    "gray clothing, "
    "different saree, "
    "different color, "
    "missing zari, "
    "missing border, "
    "different person, "
    "changed face, "
    "changed hands, "
    "changed hair, "
    "changed jewelry, "
    "extra limbs, "
    "cartoon, "
    "CGI, "
    "painting, "
    "blurry"
)


# ============================================================
# HELPERS
# ============================================================

def check_comfy():
    """Check whether ComfyUI API is running."""
    try:
        response = requests.get(
            f"{COMFY_URL}/system_stats",
            timeout=10
        )
        response.raise_for_status()
        print("✅ ComfyUI API is running")
        return True
    except Exception as exc:
        print(f"❌ Cannot connect to ComfyUI: {exc}")
        return False


def upload_image(path: str, filename: str) -> str:
    """Upload an image to ComfyUI and return its server-side name."""

    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    print(f"Uploading: {path}")

    with open(path, "rb") as file:
        response = requests.post(
            f"{COMFY_URL}/upload/image",
            files={
                "image": (
                    filename,
                    file,
                    "image/png"
                )
            },
            data={
                "overwrite": "true"
            },
            timeout=60
        )

    response.raise_for_status()

    result = response.json()

    if "name" not in result:
        raise RuntimeError(
            f"Unexpected ComfyUI upload response: {result}"
        )

    print(f"✅ Uploaded as: {result['name']}")

    return result["name"]


def build_workflow(image_name: str, mask_name: str) -> dict:
    """
    Build the ComfyUI API workflow.

    Nodes:
      1 - Input image
      2 - Inpainting mask
      3 - SD1.5 inpainting checkpoint
      4 - Positive prompt
      5 - Negative prompt
      6 - VAE inpainting encoder
      7 - KSampler
      8 - VAE decoder
      9 - Save image
    """

    seed = 42

    workflow = {
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_name
            }
        },

        "2": {
            "class_type": "LoadImageMask",
            "inputs": {
                "image": mask_name,
                "channel": "red"
            }
        },

        "3": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": CHECKPOINT
            }
        },

        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": POSITIVE_PROMPT,
                "clip": [
                    "3",
                    1
                ]
            }
        },

        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": NEGATIVE_PROMPT,
                "clip": [
                    "3",
                    1
                ]
            }
        },

        "6": {
            "class_type": "VAEEncodeForInpaint",
            "inputs": {
                "pixels": [
                    "1",
                    0
                ],
                "vae": [
                    "3",
                    2
                ],
                "mask": [
                    "2",
                    0
                ],
                "grow_mask_by": 8
            }
        },

        "7": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 10,
                "cfg": 4,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 0.08,

                "model": [
                    "3",
                    0
                ],

                "positive": [
                    "4",
                    0
                ],

                "negative": [
                    "5",
                    0
                ],

                "latent_image": [
                    "6",
                    0
                ]
            }
        },

        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [
                    "7",
                    0
                ],
                "vae": [
                    "3",
                    2
                ]
            }
        },

        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": [
                    "8",
                    0
                ],
                "filename_prefix": "vto_comfy"
            }
        }
    }

    return workflow


def queue_workflow(workflow: dict) -> str:
    """Send workflow to ComfyUI."""

    client_id = str(uuid.uuid4())

    response = requests.post(
        f"{COMFY_URL}/prompt",
        json={
            "prompt": workflow,
            "client_id": client_id
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if "prompt_id" not in result:
        raise RuntimeError(
            f"ComfyUI did not return prompt_id: {result}"
        )

    prompt_id = result["prompt_id"]

    print(f"✅ Workflow queued")
    print(f"Prompt ID: {prompt_id}")

    return prompt_id


def wait_for_result(prompt_id: str) -> dict:
    """Poll ComfyUI until the prompt is complete."""

    print("Waiting for ComfyUI...")

    start = time.time()

    while time.time() - start < TIMEOUT:

        response = requests.get(
            f"{COMFY_URL}/history/{prompt_id}",
            timeout=15
        )

        response.raise_for_status()

        history = response.json()

        if prompt_id in history:

            data = history[prompt_id]

            # Check for execution error
            if "status" in data:
                status = data["status"]

                if status.get("status_str") == "error":

                    messages = status.get(
                        "messages",
                        []
                    )

                    raise RuntimeError(
                        f"ComfyUI execution failed: {messages}"
                    )

            outputs = data.get(
                "outputs",
                {}
            )

            for node_id, node_output in outputs.items():

                images = node_output.get(
                    "images",
                    []
                )

                if images:
                    print(
                        f"✅ Image generated by node {node_id}"
                    )

                    return images[0]

        time.sleep(2)

    raise TimeoutError(
        f"ComfyUI did not finish within {TIMEOUT} seconds."
    )


def download_result(image_info: dict):
    """Download generated image from ComfyUI."""

    response = requests.get(
        f"{COMFY_URL}/view",
        params={
            "filename": image_info["filename"],
            "subfolder": image_info.get(
                "subfolder",
                ""
            ),
            "type": image_info.get(
                "type",
                "output"
            )
        },
        timeout=60
    )

    response.raise_for_status()

    with open(OUTPUT_FILE, "wb") as file:
        file.write(response.content)

    print(
        f"✅ Saved refined image:\n{OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("       VTO → COMFYUI INPAINTING REFINEMENT")
    print("=" * 60)

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # 1. Check ComfyUI
    if not check_comfy():
        return

    # 2. Upload input image
    image_name = upload_image(
        INPUT_IMAGE,
        "vto_input.png"
    )

    # 3. Upload refinement mask
    mask_name = upload_image(
        INPUT_MASK,
        "vto_mask.png"
    )

    # 4. Build workflow
    workflow = build_workflow(
        image_name,
        mask_name
    )

    # 5. Queue
    prompt_id = queue_workflow(
        workflow
    )

    # 6. Wait
    image_info = wait_for_result(
        prompt_id
    )

    # 7. Download
    download_result(
        image_info
    )

    print("=" * 60)
    print("✅ COMFYUI REFINEMENT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()