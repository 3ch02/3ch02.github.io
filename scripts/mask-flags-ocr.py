#!/usr/bin/env python3
"""
Find flags that are visible in write-up screenshots and record where they are.

    python3 scripts/import-obsidian.py "/home/echo/Obsidian Vault"     # import first
    python3 scripts/mask-flags-ocr.py "/home/echo/Obsidian Vault"      # then this (slow: ~15 s per image)
    python3 scripts/mask-flags-ocr.py "/home/echo/Obsidian Vault" bike,markup   # or only some write-ups

For every write-up whose source is in MASK_FLAGS_FOR (see import-obsidian.py), each screenshot
is read by OCR; when a line contains one of the flags of that write-up, the area is added to
scripts/flag-masks.json and painted over. The importer re-applies that file on every run, so
this script (and its OCR dependency) is only needed when new screenshots are added.

Needs: pip install rapidocr-onnxruntime pillow numpy   (a virtualenv is fine)
Always look at the result — OCR can miss a flag. Add a box by hand in flag-masks.json if it does:
    "<write-up slug>/<image file>": [[x0, y0, x1, y1]]
"""
import importlib.util
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

spec = importlib.util.spec_from_file_location("importer", Path(__file__).with_name("import-obsidian.py"))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

LOOKALIKE = str.maketrans({"o": "0", "l": "1", "i": "1", "s": "5", "z": "2", "g": "9"})


def read_lines(ocr: RapidOCR, path: Path) -> list[tuple[list[float], str]]:
    """OCR lines as ([x0, y0, x1, y1] in the image's own pixels, text).

    Thin strips (a two-line terminal crop) are not detected reliably at their native size,
    so the image is enlarged and given a margin first, and the boxes are mapped back.
    """
    im = Image.open(path).convert("RGB")
    scale = 3 if im.height < 200 else 2 if im.height < 500 else 1
    margin = 60 if scale > 1 else 0
    if scale > 1:
        big = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
        canvas = Image.new("RGB", (big.width + 2 * margin, big.height + 2 * margin), big.getpixel((2, 2)))
        canvas.paste(big, (margin, margin))
        im = canvas
    # Very wide images are shrunk by the detector until the text is unreadable: read them
    # as overlapping tiles instead (the overlap keeps any flag whole in at least one tile).
    tile, step = 1000, 500
    offsets = range(0, max(1, im.width - step), step) if im.width > 1200 else [0]
    lines = []
    for off in offsets:
        part = im.crop((off, 0, min(im.width, off + tile), im.height)) if len(offsets) > 1 else im
        result, _ = ocr(np.array(part)[:, :, ::-1])  # RGB → BGR
        for quad, text, _score in result or []:
            xs = [(p[0] + off - margin) / scale for p in quad]
            ys = [(p[1] - margin) / scale for p in quad]
            lines.append(([min(xs), min(ys), max(xs), max(ys)], text))
    return lines


def flag_spans(text: str, flags: list[str]) -> list[tuple[int, int]]:
    """Character ranges of an OCR line that look like a flag (tolerant to OCR mistakes)."""
    keep = [i for i, c in enumerate(text) if not c.isspace()]
    compact = "".join(text[i] for i in keep).lower().translate(LOOKALIKE)
    found: list[tuple[int, int]] = []
    # 1. any long hexadecimal run; a shorter one is enough on a line that says "flag"
    #    (truncated flags, or text showing through a transparent terminal)
    shortest = 12 if "flag" in text.lower() else 26
    found += [m.span() for m in re.finditer(r"[0-9a-f]{%d,}" % shortest, compact)]
    # 2. something close to a flag known from the text of the write-up
    for flag in flags:
        n = len(flag)
        best = (0.0, 0, 0)
        for start in range(max(1, len(compact) - n + 1)):
            window = compact[start : start + n]
            if len(window) < 12:
                continue
            ratio = SequenceMatcher(None, window, flag[: len(window)]).ratio()
            if ratio > best[0]:
                best = (ratio, start, start + len(window))
        if best[0] >= 0.72:
            found.append(best[1:])
    return [(keep[a], keep[b - 1] + 1) for a, b in found if b > a]


def main() -> None:
    vault = Path(sys.argv[1])
    # Optional: only these write-up slugs (comma-separated), e.g. after adding one write-up
    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
    masks: dict[str, list[list[int]]] = json.loads(importer.MASKS_FILE.read_text()) if importer.MASKS_FILE.exists() else {}
    ocr = RapidOCR()
    for m in importer.collect(vault, copy=False):
        if m["ctf"] not in importer.MASK_FLAGS_FOR or (only and m["slug"] not in only):
            continue
        for rel in sorted(set(re.findall(r"\./images/obsidian/([^)\s]+)", m["body"]))):
            path = importer.IMG_DIR / rel
            if not path.exists():
                continue
            boxes = []
            for (x0, y0, x1, y1), text in read_lines(ocr, path):
                width = x1 - x0
                pad = 0.04 * width + 8
                for start, end in flag_spans(text, m["flags"]):
                    boxes.append([
                        int(max(0, x0 + width * start / len(text) - pad)),
                        int(max(0, y0 - 4)),
                        int(x0 + width * end / len(text) + pad),
                        int(y1 + 4),
                    ])
            if boxes:
                masks[rel] = sorted(map(list, {tuple(b) for b in masks.get(rel, []) + boxes}))
                print(f"masked  {rel}  ({len(boxes)})", flush=True)
    importer.MASKS_FILE.write_text(json.dumps(masks, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    importer.apply_image_masks()


if __name__ == "__main__":
    main()
