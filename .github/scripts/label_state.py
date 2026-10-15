"""Shared, persistent download and OCR state for TTB label directories."""

import json
import re
from pathlib import Path


STATE_FILE = "label_state.json"
OCR_HEADER = "## Extracted Label Text"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def has_ocr_text(section):
    blocks = re.findall(r"^### [^\n]+\n(.*?)(?=^### |\Z)", section,
                        re.MULTILINE | re.DOTALL)
    return any(block.strip() and not block.strip().startswith("*No readable text")
               for block in blocks)


def image_files(directory):
    return sorted(p for p in Path(directory).iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)


def valid_image(directory, name):
    path = Path(directory) / name
    return (Path(name).name == name and path.is_file() and path.stat().st_size > 0)


def load_state(directory):
    """Read state, or infer legacy expectations from the README's image inventory."""
    directory = Path(directory)
    path = directory / STATE_FILE
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("State must be an object")
            if not all(isinstance(state.get(key), dict) for key in ("download", "ocr")):
                raise ValueError("Missing download or OCR state")
            return state
        except (ValueError, OSError):
            # A corrupt state is not evidence of completion.
            return {"version": 1, "download": {"status": "pending"}, "ocr": {"status": "pending"}}

    readme = directory / "README.md"
    content = readme.read_text(encoding="utf-8", errors="replace") if readme.exists() else ""
    expected = list(dict.fromkeys(re.findall(
        r"!\[[^\]]*\]\((?:\./)?([^)\n]+\.(?:jpg|jpeg|png))\)", content, re.IGNORECASE)))
    # Old publicViewImage downloads sometimes have headings but no image embeds.
    # Only migrate untracked legacy inventories; known manifest/README gaps win.
    if (not expected and "## Label Images" in content
            and not re.search(r"!\[[^\]]*\]\(", content)):
        expected = [image.name for image in image_files(directory)]
    downloaded = [name for name in expected if valid_image(directory, name)]
    complete = bool(expected) and len(downloaded) == len(expected)
    section = content.partition(OCR_HEADER)[2]
    readable = has_ocr_text(section)
    return {
        "version": 1,
        "download": {
            "status": "complete" if complete else "pending",
            "expected_images": expected,
            "downloaded_images": downloaded,
            "legacy_inventory": bool(expected),
        },
        "ocr": {"status": "complete" if complete and readable else "pending",
                "images": downloaded if complete and readable else []},
    }


def save_state(directory, state):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / STATE_FILE
    staging = path.with_suffix(".json.part")
    staging.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    staging.replace(path)


def download_complete(directory, state=None):
    state = load_state(directory) if state is None else state
    download = state["download"]
    expected = download.get("expected_images", [])
    return (download.get("status") == "complete" and bool(expected)
            and all(name in download.get("downloaded_images", [])
                    and valid_image(directory, name) for name in expected))


def ocr_complete(directory, state=None):
    state = load_state(directory) if state is None else state
    if not download_complete(directory, state):
        return False
    ocr = state["ocr"]
    readme = Path(directory) / "README.md"
    if not readme.exists():
        return False
    section = readme.read_text(encoding="utf-8", errors="replace").partition(OCR_HEADER)[2]
    return (ocr.get("status") == "complete"
            and sorted(ocr.get("images", [])) == sorted(state["download"]["expected_images"])
            and has_ocr_text(section))


def read_ids_file(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = data.get("new_ttb_ids") if isinstance(data, dict) else data
    if not isinstance(ids, list) or any(
            not isinstance(value, str) or not value.isdigit() for value in ids):
        raise ValueError("IDs file must contain a list of numeric strings or new_ttb_ids")
    return list(dict.fromkeys(ids))
