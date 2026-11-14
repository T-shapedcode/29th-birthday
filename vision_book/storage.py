"""Tiny JSON storage: one private file holds the whole book."""
import json
import os
import tempfile
from pathlib import Path

DATA_DIR = Path(os.environ.get("VISION_BOOK_DATA", Path(__file__).resolve().parent.parent / "data"))
DATA_FILE = DATA_DIR / "vision_book.json"
IMAGE_DIR = DATA_DIR / "images"


def load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            backup = DATA_FILE.with_suffix(".corrupt.json")
            DATA_FILE.replace(backup)
    return {}


def save(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # write atomically so a crash never leaves half a journal behind
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def save_image(name: str, content: bytes) -> str:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in name if c.isalnum() or c in "._-") or "image.png"
    path = IMAGE_DIR / safe
    i = 1
    while path.exists():
        path = IMAGE_DIR / f"{path.stem}_{i}{path.suffix}"
        i += 1
    path.write_bytes(content)
    return str(path.relative_to(DATA_DIR))


def image_path(rel: str) -> Path:
    return DATA_DIR / rel
