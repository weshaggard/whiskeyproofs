#!/usr/bin/env python3
"""Download TTB label images with independent, resumable image and OCR state."""

import argparse
import csv
import errno
import html
import http.client
import http.cookiejar
import json
import re
import ssl
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from label_state import download_complete, load_state, read_ids_file, save_state, valid_image

TTB_BASE_URL = "https://ttbonline.gov/colasonline"
DETAIL_URL = f"{TTB_BASE_URL}/viewColaDetails.do?action=publicFormDisplay&ttbid="
ATTACHMENT_URL = f"{TTB_BASE_URL}/publicViewAttachment.do"
ssl_context = ssl._create_unverified_context()
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar),
    urllib.request.HTTPSHandler(context=ssl_context))


def get_unique_ttbids(csv_file):
    with open(csv_file, encoding="utf-8") as stream:
        return sorted({row["TTB_ID"].strip() for row in csv.DictReader(stream)
                       if row.get("TTB_ID", "").strip()})


def fetch_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with opener.open(request, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                transient = exc.code in (408, 429) or 500 <= exc.code < 600
            else:
                reason = getattr(exc, "reason", exc)
                transient = isinstance(reason, (TimeoutError, ConnectionError, http.client.IncompleteRead)) or (
                    isinstance(reason, OSError) and reason.errno in
                    (errno.ECONNRESET, errno.ECONNREFUSED, errno.ETIMEDOUT, socket.EAI_AGAIN))
            if not transient or attempt == 3:
                raise
            time.sleep(2 ** attempt)


def download_file(url, output_path):
    """Validate a response before atomically replacing an image."""
    try:
        data = fetch_bytes(url)
        if (len(data) < 1000 or not data.startswith(
                (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a"))):
            raise ValueError("Attachment response is empty, truncated, or not an image")
        output_path = Path(output_path)
        staging = output_path.with_suffix(output_path.suffix + ".part")
        staging.write_bytes(data)
        staging.replace(output_path)
        return True
    except Exception as exc:
        print(f"Error downloading {output_path}: {exc}", file=sys.stderr)
        return False


def extract_label_images_and_metadata(ttbid):
    content = fetch_bytes(DETAIL_URL + ttbid).decode("utf-8", errors="replace")
    if re.search(r"captcha|recaptcha", content, re.IGNORECASE):
        return "CAPTCHA_DETECTED", {}
    if re.search(r"unable to process request|access denied|session expired", content, re.IGNORECASE):
        raise ValueError("Registry returned an error instead of label details")
    matches = re.findall(r'publicViewAttachment\.do\?filename=([^"&]+)&(?:amp;)?filetype=l', content)
    images = [{"filename": urllib.parse.unquote(html.unescape(value)), "url_param": value}
              for value in dict.fromkeys(matches)]
    metadata = {}
    patterns = {
        "brand_name": r'6\.\s*BRAND NAME.*?<div class="data">([^<]+)</div>',
        "fanciful_name": r'7\.\s*FANCIFUL NAME.*?<div class="data">([^<]+)</div>',
        "issue_date": r'(?:Issue Date|Approval Date|Date Issued).*?<div class="data">([^<]+)</div>',
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            metadata[field] = html.unescape(match.group(1).strip())
    for label, value in re.findall(
            r'<div class="label">([^<]+)</div>\s*<div class="data">([^<]+)</div>', content):
        key = {"OR": "origin_code", "CT": "product_class_type"}.get(
            html.unescape(label).strip().rstrip(":").strip())
        if key:
            metadata[key] = html.unescape(value.strip())
    return images, metadata


def image_inventory(images):
    """Assign deterministic unique names even for multiple front/back attachments."""
    inventory = []
    used = set()
    seen = set()
    for index, image in enumerate(images, 1):
        filename = image["filename"]
        if filename in seen:
            continue
        seen.add(filename)
        upper = filename.upper()
        if any(token in upper for token in ("FL", "FRONT", "FRT")):
            base = "front_label"
        elif any(token in upper for token in ("BL", "BACK")):
            base = "back_label"
        else:
            base = f"label_{index}"
        name = f"{base}.jpg"
        suffix = 2
        while name in used:
            name = f"{base}_{suffix}.jpg"
            suffix += 1
        used.add(name)
        inventory.append({"filename": filename, "output_name": name})
    return inventory


def write_readme(directory, ttbid, metadata, expected):
    lines = [f"# TTB COLA Label Images - TTBID {ttbid}", ""]
    for field, title in (("brand_name", "Brand Name"), ("fanciful_name", "Fanciful Name"),
                         ("issue_date", "Issue Date"), ("origin_code", "Origin Code"),
                         ("product_class_type", "Product Class/Type")):
        if metadata.get(field):
            lines.extend([f"**{title}:** {metadata[field]}", ""])
    lines.extend([f"**Source:** [TTB Public COLA Registry]({DETAIL_URL}{ttbid})", "", "## Label Images", ""])
    # Include missing expected images too, so legacy inventory cannot hide a partial download.
    for name in expected:
        title = Path(name).stem.replace("_", " ").title()
        lines.extend([f"### {title}", "", f"![{title}](./{name})", ""])
    (directory / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def download_ttb_labels(ttbid, labels_dir, skip_existing=True):
    if not isinstance(ttbid, str) or not ttbid.isdigit():
        raise ValueError("TTB ID must be a numeric string")
    directory = Path(labels_dir) / ttbid
    directory.mkdir(parents=True, exist_ok=True)
    state = load_state(directory)
    if skip_existing and download_complete(directory, state):
        save_state(directory, state)
        return "skipped"
    download = state["download"]
    download.update(status="pending", error=None)
    save_state(directory, state)
    try:
        images, metadata = extract_label_images_and_metadata(ttbid)
        if images == "CAPTCHA_DETECTED":
            download.update(status="failed", error="CAPTCHA detected")
            save_state(directory, state)
            return "captcha"
        if not images:
            raise ValueError("No label images found")
        inventory = image_inventory(images)
        expected = [item["output_name"] for item in inventory]
        old_attachments = {item["output_name"]: item["filename"]
                           for item in download.get("attachments", [])}
        old_expected = download.get("expected_images", [])
        download.update(expected_images=expected, attachments=inventory, metadata=metadata)
        # Changing or re-downloading images invalidates OCR, not download completion.
        state["ocr"] = {"status": "pending", "images": []}
        download["downloaded_images"] = []
        save_state(directory, state)
        errors = []
        for item in inventory:
            name = item["output_name"]
            previous_matches = (old_attachments.get(name) == item["filename"] or
                                not old_attachments)
            if skip_existing and previous_matches and valid_image(directory, name):
                download["downloaded_images"].append(name)
            else:
                url = f"{ATTACHMENT_URL}?filename={urllib.parse.quote(item['filename'], safe='')}&filetype=l"
                if download_file(url, directory / name):
                    download["downloaded_images"].append(name)
                else:
                    errors.append(f"Failed attachment: {item['filename']} ({name})")
            save_state(directory, state)
        complete = len(download["downloaded_images"]) == len(expected)
        download.update(status="complete" if complete else "partial" if download["downloaded_images"] else "failed",
                        error="; ".join(errors) or None)
        write_readme(directory, ttbid, metadata, expected)
        save_state(directory, state)
        return "success" if complete else "failed"
    except Exception as exc:
        download.update(status="partial" if download.get("downloaded_images") else "failed", error=str(exc))
        save_state(directory, state)
        print(f"Error processing {ttbid}: {exc}", file=sys.stderr)
        return "failed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ttbid")
    group.add_argument("--ids-file", help="JSON array or discovery JSON containing new_ttb_ids")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--no-skip-existing", action="store_false", dest="skip_existing")
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--labels-dir", type=Path, default=root / "labels")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"status": "failed", "error": None, "completed_ttb_ids": [],
              "failed_ttb_ids": [], "partial_ttb_ids": [], "partial_count": 0, "count": 0}
    try:
        ids = ([args.ttbid] if args.ttbid else read_ids_file(args.ids_file)
               if args.ids_file else get_unique_ttbids(root / "_data" / "whiskeyindex.csv"))
        if args.limit is not None:
            if args.limit < 0:
                raise ValueError("--limit must be nonnegative")
            ids = ids[:args.limit]
        errors = []
        for index, ttbid in enumerate(ids):
            outcome = download_ttb_labels(ttbid, args.labels_dir, args.skip_existing)
            if outcome in ("success", "skipped"):
                result["completed_ttb_ids"].append(ttbid)
            else:
                result["failed_ttb_ids"].append(ttbid)
                state = load_state(args.labels_dir / ttbid)
                if state["download"].get("downloaded_images"):
                    result["partial_ttb_ids"].append(ttbid)
                errors.append(f"{ttbid}: {state['download'].get('error', outcome)}")
                if outcome == "captcha":
                    result["failed_ttb_ids"].extend(ids[index + 1:])
                    break
        result.update(status="complete" if not result["failed_ttb_ids"] else
                      "partial" if result["completed_ttb_ids"] or result["partial_ttb_ids"] else "failed",
                      error="; ".join(errors) or None, count=len(ids))
    except Exception as exc:
        result["error"] = str(exc)
    result["partial_count"] = len(result["partial_ttb_ids"])
    encoded = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
