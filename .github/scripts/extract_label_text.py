#!/usr/bin/env python3
"""
Extract text from TTB label images using OCR and append to README.md files.

This script uses multiple OCR engines to extract text from label images and
appends the results to the README.md file in each label directory. This enables
full-text searching of label content.

OCR Engines (used in parallel; best quality result is kept per image):
  - Tesseract (pytesseract) with multiple PSM modes — required
  - EasyOCR — optional; improves results on decorative and curved label text

Multiple Tesseract PSM (Page Segmentation Mode) configurations are tried for
each image and the best result is selected using a text quality score. If
EasyOCR is installed it is also run and compared against the Tesseract result.
Text that does not meet a minimum English readability threshold is excluded to
avoid storing garbled or machine-readable content (barcodes, measurements, etc).

Proof and age statements detected in the OCR text are extracted and shown at
the top of the extracted section for quick reference.

Usage:
    # Extract text for all labels
    python3 .github/scripts/extract_label_text.py

    # Extract text for a specific TTB ID
    python3 .github/scripts/extract_label_text.py --ttbid 24050001000497

    # Re-process labels that already have extracted text
    python3 .github/scripts/extract_label_text.py --force

Options:
    --ttbid TTBID   Process a specific TTB ID only
    --force         Re-extract text even if README already has extracted text
    --help          Show this help message

Dependencies:
    Required:  pip install pytesseract Pillow
               sudo apt-get install tesseract-ocr
    Optional:  pip install easyocr   (improves quality for stylised label text)
"""

import argparse
import re
import sys
from pathlib import Path


EXTRACTED_TEXT_HEADER = "## Extracted Label Text"

# Tesseract PSM modes to try, in order of preference.
# 11 = Sparse text (best for labels with scattered text)
# 3  = Fully automatic page segmentation (good for structured text)
# 6  = Assume a single uniform block of text (good for dense paragraphs)
PSM_MODES = [11, 3, 6]

# Quality thresholds for deciding whether extracted text is usable.
# Score = (words with 3+ alpha chars) / total whitespace-separated tokens.
# Text scoring below this ratio is mostly noise (symbols, measurements, barcodes).
QUALITY_SCORE_THRESHOLD = 0.30
# Minimum number of 3+ letter words required even when score is above threshold.
MIN_WORD_COUNT = 5

# Proof value bounds: US law requires whiskey to be at least 80 proof, but we
# set the lower bound to 60 to catch edge cases where OCR garbles a digit.
# Upper bound 200 is well above the highest known barrel strength bottling.
MIN_PROOF = 60
MAX_PROOF = 200

# Age bounds: whiskey can technically be unaged, but age statements on labels
# are at least 2 years; 50 years is a generous upper bound for labeled whiskey.
MIN_AGE = 2
MAX_AGE = 50

# Regex to find proof values in OCR text (case-insensitive):
#   "125 PROOF", "PROOF 125", "PROOF | 120.00", "63.55% ALC/VOL" (ABV doubled → proof)
#   Standalone ABV "63.55%" also accepted when the value appears alone on a line
_PROOF_RE = re.compile(
    r"(\d{2,3}(?:\.\d+)?)\s*PROOF\b"
    r"|\bPROOF\s*[|:.]?\s*(\d{2,3}(?:\.\d+)?)"
    r"|\b(\d{1,2}(?:\.\d+)?)\s*%\s*ALC"
    r"|\bALC\.?(?:/|\.| BY )?VOL\.?\s*[|:]?\s*(\d{1,2}(?:\.\d+)?)\s*%"
    r"|^\s*(\d{1,2}(?:\.\d+)?)\s*%\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Regex to find age statements in OCR text:
#   "7 YEAR OLD", "7 YRS", "AGED 12 YEARS", "25 Year-Old"
_AGE_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(?:YEAR)[S-]?\s*(?:-\s*)?(?:OLD)?\b"
    r"|\bAGED\s+(\d+(?:\.\d+)?)\s*(?:YEARS?|YRS?)"
    r"|\b(\d+(?:\.\d+)?)\s*YRS?\.?\s*(?:OLD)?\b",
    re.IGNORECASE,
)

# Module-level EasyOCR reader cache so the model is only loaded once per run.
_easyocr_reader = None
_easyocr_unavailable = False  # set True after first failed import attempt


def _get_easyocr_reader():
    """Return a cached EasyOCR Reader instance, or None if unavailable."""
    global _easyocr_reader, _easyocr_unavailable
    if _easyocr_unavailable:
        return None
    if _easyocr_reader is not None:
        return _easyocr_reader
    try:
        import easyocr  # noqa: PLC0415
        _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        return _easyocr_reader
    except Exception:
        _easyocr_unavailable = True
        return None


def score_text_quality(text):
    """
    Score the quality of OCR text as a measure of English readability.

    Returns:
        (score, word_count) where:
          score      -- ratio of 3+ alpha-char words to all whitespace-separated tokens (0.0–1.0)
          word_count -- count of those meaningful words
    """
    if not text or not text.strip():
        return 0.0, 0
    tokens = text.split()
    if not tokens:
        return 0.0, 0
    words = [t for t in tokens if re.fullmatch(r"[a-zA-Z]{3,}", t)]
    return len(words) / len(tokens), len(words)


def clean_text(text):
    """Strip whitespace and collapse multiple consecutive blank lines."""
    lines = text.splitlines()
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        stripped = line.rstrip()
        if stripped == "":
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            cleaned_lines.append(stripped)
            prev_blank = False
    return "\n".join(cleaned_lines).strip()


def extract_proof_and_age(combined_text):
    """
    Parse proof and age from combined OCR text across all label images.

    Returns:
        (proof_str, age_str) where each is a human-readable string or None if
        not found.  Example: ("125.1", "7 Years")
    """
    proof_val = None
    age_val = None

    # Search full combined text for proof
    for m in _PROOF_RE.finditer(combined_text):
        raw = next((v for v in m.groups() if v is not None), None)
        if raw:
            val = float(raw)
            # US whiskey minimum is 80 proof, so any matched value below that
            # is treated as ABV — double it to derive proof.
            if val < 80:
                val = val * 2
            # Preserve integer values as integers; keep at most 1 decimal place
            if val != int(val):
                val = round(val, 1)
            if MIN_PROOF <= val <= MAX_PROOF:
                proof_val = int(val) if val == int(val) else val
                break

    # Search full combined text for age
    for m in _AGE_RE.finditer(combined_text):
        raw = next((v for v in m.groups() if v is not None), None)
        if raw:
            val = float(raw)
            if MIN_AGE <= val <= MAX_AGE:
                age_val = int(val) if val == int(val) else val
                break

    proof_str = str(proof_val) if proof_val is not None else None
    age_str = f"{age_val} {'Year' if age_val == 1 else 'Years'}" if age_val is not None else None
    return proof_str, age_str


def extract_text_from_image(image_path):
    """
    Extract text from an image using multiple OCR engines.

    Tries Tesseract (multiple PSM modes) and, if available, EasyOCR.  Returns
    whichever engine produces the highest-quality result.

    Returns None if the required OCR tooling (Tesseract) is unavailable —
    this signals the caller to abort.  Returns an empty string when all engines
    fail or produce only noise below the quality threshold.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("  ⚠️  pytesseract or Pillow not installed. Skipping OCR.")
        return None

    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"  ⚠️  Cannot open image {image_path.name}: {e}")
        return ""

    best_text = ""
    best_quality = 0.0  # word_count × score

    # ── Tesseract (multiple PSM modes) ──────────────────────────────────────
    for psm in PSM_MODES:
        try:
            raw = pytesseract.image_to_string(img, config=f"--psm {psm}")
            score, word_count = score_text_quality(raw)
            quality = word_count * score
            if quality > best_quality:
                best_text = raw
                best_quality = quality
        except Exception as e:
            if psm == PSM_MODES[-1] and not best_text:
                print(f"  ⚠️  Tesseract error on {image_path.name}: {e}")

    # ── EasyOCR (optional) ───────────────────────────────────────────────────
    reader = _get_easyocr_reader()
    if reader is not None:
        try:
            results = reader.readtext(str(image_path))
            raw = "\n".join(r[1] for r in results)
            score, word_count = score_text_quality(raw)
            quality = word_count * score
            if quality > best_quality:
                best_text = raw
                best_quality = quality
        except Exception as e:
            print(f"  ⚠️  EasyOCR error on {image_path.name}: {e}")

    if not best_text:
        return ""

    # Apply quality filter: exclude text that is mostly noise
    score, word_count = score_text_quality(best_text)
    if score < QUALITY_SCORE_THRESHOLD or word_count < MIN_WORD_COUNT:
        return ""

    return clean_text(best_text)


def process_label_directory(ttbid_dir, force=False):
    """
    Extract text from all images in a label directory and append to README.md.

    Returns:
        'success'  - Text was extracted and appended to README
        'skipped'  - README already has extracted text (and force=False)
        'no_images'- No image files found in directory
        'failed'   - README not found or other error
    """
    readme_path = ttbid_dir / "README.md"

    if not readme_path.exists():
        print(f"  ⚠️  No README.md found in {ttbid_dir.name}")
        return "failed"

    # Read current README content
    try:
        current_content = readme_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fall back to latin-1 which can read any byte sequence
        current_content = readme_path.read_text(encoding="latin-1")

    # Check if already processed
    if EXTRACTED_TEXT_HEADER in current_content and not force:
        return "skipped"

    # Find all image files (jpg, png) sorted for consistent ordering
    image_files = sorted(
        [f for f in ttbid_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
    )

    if not image_files:
        print(f"  ⚠️  No images found in {ttbid_dir.name}")
        return "no_images"

    # Build the extracted text section
    text_sections = []
    any_text_found = False
    excluded_count = 0

    for img_file in image_files:
        text = extract_text_from_image(img_file)
        if text is None:
            # OCR tooling not available - abort
            return "failed"
        if text:
            any_text_found = True
            display_name = img_file.stem.replace("_", " ").title()
            text_sections.append(f"### {display_name}\n\n{text}")
        else:
            # Empty string: image failed to open, had an OCR error, or failed quality check
            excluded_count += 1

    if not any_text_found:
        # No usable text found in any image
        extracted_section = (
            f"\n\n{EXTRACTED_TEXT_HEADER}\n\n"
            "*No readable text could be extracted from the label images.*\n"
        )
    else:
        # Extract proof and age from the combined OCR text
        combined_text = "\n".join(
            section.split("\n", 2)[-1] for section in text_sections
        )
        proof_str, age_str = extract_proof_and_age(combined_text)

        note_parts = ["*Text extracted via OCR - may contain errors*"]
        if excluded_count > 0:
            note_parts.append(
                f"*{excluded_count} image(s) excluded: text did not meet readability threshold*"
            )
        note = "\n\n".join(note_parts)

        detected_lines = []
        if proof_str:
            detected_lines.append(f"**Detected Proof:** {proof_str}")
        if age_str:
            detected_lines.append(f"**Detected Age:** {age_str}")
        detected_block = ("\n".join(detected_lines) + "\n\n") if detected_lines else ""

        extracted_section = (
            f"\n\n{EXTRACTED_TEXT_HEADER}\n\n"
            + note
            + "\n\n"
            + detected_block
            + "\n\n".join(text_sections)
            + "\n"
        )

    # Remove existing extracted text section if re-processing (--force)
    if EXTRACTED_TEXT_HEADER in current_content:
        # Strip everything from the header to end of file
        idx = current_content.index(EXTRACTED_TEXT_HEADER)
        # Walk back to remove the preceding blank lines
        content_before = current_content[:idx].rstrip()
        new_content = content_before + extracted_section
    else:
        # Append to existing content
        new_content = current_content.rstrip() + extracted_section

    readme_path.write_text(new_content, encoding="utf-8")
    return "success"


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from TTB label images and append to README.md files"
    )
    parser.add_argument(
        "--ttbid", type=str, help="Process a specific TTB ID only"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Re-extract text even if README already has extracted text",
    )
    args = parser.parse_args()

    # Verify required OCR dependencies are available before starting
    try:
        import pytesseract
        from PIL import Image  # noqa: F401
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install pytesseract Pillow")
        print("Also ensure tesseract-ocr is installed: sudo apt-get install tesseract-ocr")
        return 1

    # Report optional EasyOCR status
    reader = _get_easyocr_reader()
    if reader is not None:
        print("EasyOCR available — using both Tesseract and EasyOCR engines\n")
    else:
        print("EasyOCR not available — using Tesseract only (install with: pip install easyocr)\n")

    # Get repository root (two levels up from this script)
    repo_root = Path(__file__).parent.parent.parent
    labels_dir = repo_root / "labels"

    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return 1

    # Determine which directories to process
    if args.ttbid:
        ttbid_dirs = [labels_dir / args.ttbid]
        if not ttbid_dirs[0].exists():
            print(f"❌ Label directory not found: {ttbid_dirs[0]}")
            return 1
        print(f"Processing single TTB ID: {args.ttbid}\n")
    else:
        # Process all TTB ID directories (skip non-directory entries like README.md)
        ttbid_dirs = sorted(
            [d for d in labels_dir.iterdir() if d.is_dir()]
        )
        print(f"Processing {len(ttbid_dirs)} label directories\n")

    # Process each directory
    success = 0
    skipped = 0
    failed = 0
    no_images = 0

    for i, ttbid_dir in enumerate(ttbid_dirs, 1):
        if len(ttbid_dirs) > 1:
            print(f"[{i}/{len(ttbid_dirs)}] {ttbid_dir.name}...", end=" ", flush=True)

        result = process_label_directory(ttbid_dir, force=args.force)

        if result == "success":
            success += 1
            if len(ttbid_dirs) > 1:
                print("✓")
        elif result == "skipped":
            skipped += 1
            if len(ttbid_dirs) > 1:
                print("(already processed)")
        elif result == "no_images":
            no_images += 1
            if len(ttbid_dirs) > 1:
                print("(no images)")
        else:
            failed += 1
            if len(ttbid_dirs) > 1:
                print("✗")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Extracted: {success}")
    print(f"  Skipped:   {skipped}")
    print(f"  No images: {no_images}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(ttbid_dirs)}")
    print(f"{'='*60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
