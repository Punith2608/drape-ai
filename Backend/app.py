"""Drape AI local VTO API with a folder-based multi-saree catalogue."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
MODEL_IMAGE = ROOT / "base_models" / "front" / "model.png"
FINAL_OUTPUT = ROOT / "outputs" / "vto_stage10_pallu_border.png"
GENERATED = ROOT / "generated"
SAREE_ROOT = ROOT / "sarees"

GENERATED.mkdir(exist_ok=True)
SAREE_ROOT.mkdir(exist_ok=True)

jobs: dict[str, dict] = {}
gallery: list[dict] = []
render_lock = threading.Lock()
state_lock = threading.Lock()


def load_sarees() -> list[dict]:
    """Load every catalogue item from Backend/sarees/<id>/catalog.json."""
    items: list[dict] = []

    for folder in sorted(SAREE_ROOT.iterdir()):
        if not folder.is_dir():
            continue

        catalog_file = folder / "catalog.json"
        if not catalog_file.is_file():
            continue

        try:
            data = json.loads(catalog_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[catalogue] Skipping {folder.name}: {exc}")
            continue

        required_assets = ("body.png", "blouse.png", "border.png", "pallu.png", "product.png")
        missing = [name for name in required_assets if not (folder / name).is_file()]
        if missing:
            print(f"[catalogue] Skipping {folder.name}: missing {', '.join(missing)}")
            continue

        item = {
            "id": folder.name,
            "name": data.get("name", folder.name),
            "cat": data.get("cat", data.get("category", "Silk")),
            "col": data.get("col", data.get("color", "Burgundy")),
            "occ": data.get("occ", data.get("occasion", "Wedding")),
            "price": data.get("price", 0),
            "nw": data.get("nw", 0),
            "fabric": data.get("fabric", "Silk"),
            "care": data.get("care", "Dry clean only"),
            "short": data.get("short", data.get("description", "")),
            "v": data.get("v", [{"n": data.get("color", "Burgundy"), "b": data.get("colorHex", "#621226"), "k": "#3b0a13"}]),
            "imageUrl": f"/sarees/{folder.name}/product.png",
        }
        items.append(item)

    return items


def find_saree(saree_id: str) -> dict | None:
    return next((s for s in load_sarees() if s["id"] == saree_id), None)


def copy_saree_to_supplier(saree_id: str) -> None:
    """Copy the selected saree's renderer assets into the legacy supplier paths."""
    source = SAREE_ROOT / saree_id
    supplier = ROOT / "supplier"

    required = ("body.png", "blouse.png", "border.png", "pallu.png")
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Saree '{saree_id}' is missing renderer assets: {', '.join(missing)}"
        )

    supplier.mkdir(exist_ok=True)
    for name in required:
        shutil.copy2(source / name, supplier / name)


def public_job(job: dict) -> dict:
    return {
        key: job[key]
        for key in ("jobId", "sareeId", "status", "progress", "error", "createdAt")
        if key in job
    }


def render(job_id: str) -> None:
    """Run one renderer at a time because the existing pipeline shares supplier/output paths."""
    with render_lock:
        with state_lock:
            job = jobs[job_id]
            job.update(status="processing", progress=10)

        try:
            copy_saree_to_supplier(job["sareeId"])

            command = [sys.executable, str(ROOT / "run_pipeline.py")]
            process = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if process.returncode != 0:
                raise RuntimeError(
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "The renderer stopped unexpectedly."
                )

            if not FINAL_OUTPUT.is_file() or FINAL_OUTPUT.stat().st_size == 0:
                raise RuntimeError("The renderer completed without creating the final image.")

            filename = f"{job_id}.png"
            shutil.copy2(FINAL_OUTPUT, GENERATED / filename)

            completed = datetime.now(timezone.utc).isoformat()

            with state_lock:
                job.update(
                    status="completed",
                    progress=100,
                    imageUrl=f"/generated/{filename}",
                    completedAt=completed,
                )
                gallery.insert(
                    0,
                    {
                        "id": job_id,
                        "jobId": job_id,
                        "sareeId": job["sareeId"],
                        "name": job["sareeName"],
                        "after": job["imageUrl"],
                        "before": "/assets/model.png",
                        "at": completed,
                        "fav": False,
                    },
                )

        except Exception as exc:
            print(f"[render] {job_id} failed: {exc}")
            with state_lock:
                job.update(status="failed", progress=0, error=str(exc))


class AppHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print("[web] " + format % args)

    def send_json(self, status: int, payload: object) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/try-on":
            try:
                request = self.read_json()
            except (ValueError, json.JSONDecodeError):
                self.send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": "Send a valid JSON request."},
                )
                return

            saree = find_saree(str(request.get("sareeId", "")))
            if not saree:
                self.send_json(
                    HTTPStatus.NOT_FOUND,
                    {"error": "That saree is not available in the portal."},
                )
                return

            job_id = uuid.uuid4().hex
            job = {
                "jobId": job_id,
                "sareeId": saree["id"],
                "sareeName": saree["name"],
                "status": "queued",
                "progress": 2,
                "error": None,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }

            with state_lock:
                jobs[job_id] = job

            threading.Thread(target=render, args=(job_id,), daemon=True).start()
            self.send_json(HTTPStatus.ACCEPTED, public_job(job))
            return

        if path.startswith("/api/gallery/") and path.endswith("/favourite"):
            job_id = path.split("/")[3]

            with state_lock:
                entry = next((item for item in gallery if item["id"] == job_id), None)
                if entry:
                    entry["fav"] = not entry["fav"]

            if not entry:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "Look not found."})
            else:
                self.send_json(HTTPStatus.OK, entry)
            return

        self.send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/sarees":
            self.send_json(HTTPStatus.OK, load_sarees())
            return

        if path.startswith("/api/sarees/"):
            saree_id = unquote(path.rsplit("/", 1)[-1])
            item = find_saree(saree_id)
            self.send_json(
                HTTPStatus.OK if item else HTTPStatus.NOT_FOUND,
                item or {"error": "Saree not found."},
            )
            return

        if path.startswith("/api/try-on/"):
            pieces = path.split("/")
            job_id = pieces[3] if len(pieces) > 3 else ""

            with state_lock:
                job = jobs.get(job_id)
                if job:
                    result = public_job(job)
                    if len(pieces) == 4 and job["status"] == "completed":
                        result["imageUrl"] = job.get("imageUrl")
                        result["createdAt"] = job["completedAt"]
                else:
                    result = None

            self.send_json(
                HTTPStatus.OK if result else HTTPStatus.NOT_FOUND,
                result or {"error": "Try-on job not found."},
            )
            return

        if path == "/api/gallery":
            with state_lock:
                self.send_json(HTTPStatus.OK, gallery)
            return

        if path == "/assets/model.png":
            self.serve_file(MODEL_IMAGE)
            return

        if path.startswith("/sarees/"):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "sarees":
                saree_id, filename = unquote(parts[1]), unquote(parts[2])
                if filename == "product.png":
                    candidate = SAREE_ROOT / saree_id / "product.png"
                    if candidate.is_file():
                        self.serve_file(candidate)
                        return
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if path.startswith("/generated/"):
            candidate = GENERATED / Path(unquote(path)).name
            if candidate.is_file():
                self.serve_file(candidate)
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def serve_file(self, file_path: Path) -> None:
        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", self.guess_type(str(file_path)))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Drape AI multi-saree API ready at http://127.0.0.1:8000")
    print(f"Catalogue root: {SAREE_ROOT}")
    server.serve_forever()
