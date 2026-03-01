#!/usr/bin/env python3
"""
Extract text from TTB label images using OCR and append to README.md files.

This script uses Tesseract OCR to extract text from label images and appends
the extracted text to the README.md file in each label directory. This enables
full-text searching of label content.

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
"""

import argparse
import os
import sys
from pathlib import Path


EXTRACTED_TEXT_HEADER = "## Extracted Label Text"


def extract_text_from_image(image_path):
    """Extract text from an image using OCR. Returns the extracted text or None on error."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("  ⚠️  pytesseract or Pillow not installed. Skipping OCR.")
        return None

    try:
        img = Image.open(image_path)
        # Use sparse text mode (PSM 11) which works well for labels with
        # mixed layouts - it finds text anywhere without assuming a single block
        text = pytesseract.image_to_string(img, config="--psm 11")
        # Clean up the text: strip leading/trailing whitespace, collapse multiple blank lines
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
    except Exception as e:
        print(f"  ⚠️  OCR error on {image_path.name}: {e}")
        # Return empty string so the caller can continue processing other images
        return ""


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

    for img_file in image_files:
        text = extract_text_from_image(img_file)
        if text is None:
            # OCR tooling not available - abort
            return "failed"
        if text:
            any_text_found = True
            display_name = img_file.stem.replace("_", " ").title()
            text_sections.append(f"### {display_name}\n\n{text}")
        # Empty string means this image had an error but we continue with others

    if not any_text_found:
        # No text was found in any image - still mark as processed to avoid re-running
        extracted_section = (
            f"\n\n{EXTRACTED_TEXT_HEADER}\n\n"
            "*No text could be extracted from the label images.*\n"
        )
    else:
        extracted_section = (
            f"\n\n{EXTRACTED_TEXT_HEADER}\n\n"
            "*Text extracted via OCR - may contain errors*\n\n"
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

    # Verify OCR dependencies are available before starting
    try:
        import pytesseract
        from PIL import Image  # noqa: F401
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install pytesseract Pillow")
        print("Also ensure tesseract-ocr is installed: sudo apt-get install tesseract-ocr")
        return 1

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
