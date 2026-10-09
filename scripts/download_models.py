"""
scripts/download_models.py — Download AI Model Weights
=======================================================
Downloads GroundingDINO and SAM ViT-B checkpoint files into the
local  models/  directory (which is git-ignored).

Usage
-----
    python scripts/download_models.py

After running, configure backend/.env with these paths:
    GROUNDING_DINO_CHECKPOINT_PATH=<repo_root>/models/grounding_dino/groundingdino_swint_ogc.pth
    SAM_CHECKPOINT_PATH=<repo_root>/models/sam/sam_vit_b_01ec64.pth
"""

import os
import sys
import urllib.request
from pathlib import Path

# ── Model URLs ────────────────────────────────────────────────────────────────
MODELS = [
    {
        "name": "GroundingDINO SwinT OGC",
        "url": "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth",
        "dest": "models/grounding_dino/groundingdino_swint_ogc.pth",
        "size_hint": "~694 MB",
    },
    {
        "name": "SAM ViT-B",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        "dest": "models/sam/sam_vit_b_01ec64.pth",
        "size_hint": "~375 MB",
    },
]

# ── Resolve paths relative to the repo root (parent of scripts/) ──────────────
REPO_ROOT = Path(__file__).resolve().parent.parent


def _progress_hook(block_num: int, block_size: int, total_size: int) -> None:
    """Simple CLI download progress bar."""
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(downloaded / total_size * 100, 100)
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        print(
            f"\r  [{bar}] {pct:5.1f}%  {mb_done:.1f}/{mb_total:.1f} MB",
            end="",
            flush=True,
        )
    else:
        mb_done = downloaded / 1_048_576
        print(f"\r  Downloaded {mb_done:.1f} MB", end="", flush=True)


def download_model(model: dict) -> None:
    dest_path = REPO_ROOT / model["dest"]
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        size_mb = dest_path.stat().st_size / 1_048_576
        print(f"  ✓  Already exists ({size_mb:.0f} MB): {dest_path}")
        return

    print(f"\n→  Downloading {model['name']}  ({model['size_hint']})")
    print(f"   From: {model['url']}")
    print(f"   To:   {dest_path}")

    try:
        urllib.request.urlretrieve(model["url"], dest_path, _progress_hook)
        print()  # newline after progress bar
        size_mb = dest_path.stat().st_size / 1_048_576
        print(f"  ✓  Saved {size_mb:.0f} MB → {dest_path}")
    except Exception as exc:
        print(f"\n  ✗  Failed: {exc}", file=sys.stderr)
        if dest_path.exists():
            dest_path.unlink()
        raise


def main() -> None:
    print("=" * 60)
    print("  DesignVerse AI — Model Weight Downloader")
    print("=" * 60)
    print(f"  Repo root: {REPO_ROOT}")

    for model in MODELS:
        download_model(model)

    print("\n" + "=" * 60)
    print("  All models downloaded.")
    print()
    print("  Next steps:")
    print("  1.  Copy backend/.env.example → backend/.env")
    print("  2.  Set these paths in backend/.env:")
    for model in MODELS:
        dest_abs = (REPO_ROOT / model["dest"]).resolve()
        env_key = (
            "GROUNDING_DINO_CHECKPOINT_PATH"
            if "grounding_dino" in model["dest"]
            else "SAM_CHECKPOINT_PATH"
        )
        print(f"       {env_key}={dest_abs}")
    print("=" * 60)


if __name__ == "__main__":
    main()
