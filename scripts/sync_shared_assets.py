#!/usr/bin/env python3
from pathlib import Path
import shutil


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
ASSETS = ROOT / "neutrinohit-map" / "assets"

COPIES = [
    ("reveal/neutrinohit-reveal-footer.js", PROJECT / "shared" / "reveal"),
    ("reveal/neutrinohit-timed-captions.js", PROJECT / "shared" / "reveal"),
    ("reveal/neutrinohit-reveal-quiz.css", PROJECT / "shared" / "reveal"),
    ("reveal/dvnlogo.png", PROJECT / "shared" / "reveal"),
    ("reveal/neutrinohit-reveal.scss", PROJECT / "shared" / "styles"),
    ("books/neutrinohit-book.css", PROJECT / "ru" / "book" / "assets" / "styles"),
    ("books/neutrinohit-book.lua", PROJECT / "ru" / "book" / "assets" / "filters"),
    ("books/neutrinohit-book.tex", PROJECT / "shared" / "latex"),
]


def main() -> None:
    for relative_source, target_dir in COPIES:
        source = ASSETS / relative_source
        if not source.exists():
            raise FileNotFoundError(f"Missing shared asset: {source}")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        shutil.copy2(source, target)
        print(f"{source} -> {target}")


if __name__ == "__main__":
    main()
