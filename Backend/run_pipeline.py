"""Run the deterministic saree virtual try-on pipeline from the project root.

This runner makes the render sequence reproducible and stops immediately when
an expected input or stage output is missing.  AI/ComfyUI refinement remains an
optional separate step because it needs a locally running ComfyUI server.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Stage:
    name: str
    script: str
    output: str
    working_directory: str


STAGES = (
    Stage("prepare-body-texture", "tile_body.py", "textures/body_tiled.png", "reconstruction"),
    Stage("warp-body", "body_warp.py", "outputs/bottom_tps_v2.png", "warp"),
    Stage("warp-top", "top_warp.py", "outputs/top_tps.png", "warp"),
    Stage("warp-pallu", "pallu_warp.py", "outputs/pallu_tps.png", "warp"),
    Stage("warp-blouse", "blouse_warp.py", "outputs/blouse_tps.png", "warp"),
    Stage("composite", "final_base.py", "outputs/vto_stage8_base.png", "warp"),
    Stage("restore-border", "restore_border.py", "outputs/vto_stage8_border.png", "warp"),
    Stage("realism", "final_realism.py", "outputs/vto_stage9_realism.png", "warp"),
    Stage("finish-pallu-border", "stage10_pallu_border.py", "outputs/vto_stage10_pallu_border.png", "warp"),
)


def require_inputs() -> None:
    required = (
        ROOT / "base_models" / "front" / "model.png",
        ROOT / "base_models" / "front" / "masks" / "top.png",
        ROOT / "base_models" / "front" / "masks" / "bottom.png",
        ROOT / "base_models" / "front" / "masks" / "pallu.png",
        ROOT / "base_models" / "front" / "masks" / "blouse.png",
        ROOT / "base_models" / "front" / "masks" / "left_arm.png",
        ROOT / "base_models" / "front" / "masks" / "right_arm.png",
        ROOT / "supplier" / "body.png",
        ROOT / "supplier" / "blouse.png",
        ROOT / "supplier" / "border.png",
        ROOT / "supplier" / "pallu.png",
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Required input files are missing:\n- " + "\n- ".join(missing))


def run(start_at: str | None, dry_run: bool) -> None:
    require_inputs()
    OUTPUT_DIR.mkdir(exist_ok=True)
    start_index = next((i for i, stage in enumerate(STAGES) if stage.name == start_at), None)
    if start_at and start_index is None:
        choices = ", ".join(stage.name for stage in STAGES)
        raise ValueError(f"Unknown stage '{start_at}'. Choose one of: {choices}")

    selected = STAGES[start_index or 0 :]
    for stage in selected:
        command = [sys.executable, stage.script]
        print(f"\n==> {stage.name}: {' '.join(command)}")
        if not dry_run:
            # Some existing stage scripts print Unicode status symbols. Windows
            # consoles can default to cp1252, which must not turn a successful
            # render into a failed process merely while printing its status.
            environment = os.environ.copy()
            environment["PYTHONUTF8"] = "1"
            # OpenBLAS otherwise starts a worker per CPU core.  On systems with
            # a small paging file those worker stacks can prevent NumPy from
            # loading before any image work begins.
            environment["OPENBLAS_NUM_THREADS"] = "1"
            environment["OMP_NUM_THREADS"] = "1"
            environment["MKL_NUM_THREADS"] = "1"
            environment["NUMEXPR_NUM_THREADS"] = "1"
            subprocess.run(
                command,
                cwd=ROOT / stage.working_directory,
                env=environment,
                check=True,
            )
            output = ROOT / stage.output
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"Stage '{stage.name}' finished without producing {output.name}.")
            print(f"    created {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic saree VTO rendering stages.")
    parser.add_argument("--from-stage", choices=[stage.name for stage in STAGES], help="Resume from a stage.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print planned stages only.")
    args = parser.parse_args()
    run(args.from_stage, args.dry_run)
    print("\nVTO pipeline completed successfully.")


if __name__ == "__main__":
    main()
