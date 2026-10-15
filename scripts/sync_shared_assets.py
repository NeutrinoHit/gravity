#!/usr/bin/env python3
"""Refresh or check the local copies of the shared NeutrinoHit assets.

The canonical files and copy lists live in the sibling neutrinohit-map
repository (scripts/sync_reveal_assets.py, scripts/sync_book_assets.py).
This wrapper runs both for the gravity target and passes extra arguments
through, e.g. `--check --diff`.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MAP_ROOT = Path(os.environ.get("MAP_ROOT", PROJECT.parent / "neutrinohit-map"))
SCRIPTS = ["sync_reveal_assets.py", "sync_book_assets.py"]


def main() -> int:
    status = 0
    for name in SCRIPTS:
        script = MAP_ROOT / "scripts" / name
        if not script.is_file():
            print(f"Missing canonical script: {script}", file=sys.stderr)
            return 1
        command = [sys.executable, str(script), "--target", "gravity", *sys.argv[1:]]
        status = max(status, subprocess.call(command))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
