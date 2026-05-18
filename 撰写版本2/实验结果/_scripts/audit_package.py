"""Audit every CSV and PNG in Results_Master_Package.

For CSV:
- count rows
- count rows with any empty cell
- count rows with all-empty data columns
For PNG:
- decode header
- measure image dimensions
- detect "almost-blank" images by checking the variance of pixel values
  (a near-uniform image has variance < 50; a real plot has variance > 2000).
"""
from pathlib import Path
import csv
import struct
import sys

try:
    from PIL import Image
    import numpy as np
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parents[1] / "Results_Master_Package"

# Section-layer audit_mirror/ folders are verbatim copies of files already
# audited under Results_By_Experiment/. Skip them to avoid double-counting.
SKIP_DIR_PARTS = {"audit_mirror"}


def _should_skip(p: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in p.parts)

def audit_csv(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
    except Exception as e:
        return {"error": str(e), "path": str(path)}
    if not rows:
        return {"empty": True, "path": str(path)}
    header = rows[0]
    body = [r for r in rows[1:] if any(c.strip() for c in r)]
    empty_cells = sum(1 for r in body for c in r if not c.strip())
    return {
        "path": path.name,
        "n_data_rows": len(body),
        "n_cols": len(header),
        "empty_cells": empty_cells,
        "blank_rows": sum(1 for r in body if sum(1 for c in r if c.strip()) <= 1),
    }


def audit_png(path: Path) -> dict:
    if not HAVE_PIL:
        with open(path, "rb") as fh:
            head = fh.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return {"path": path.name, "error": "not a PNG"}
        w, h = struct.unpack(">II", head[16:24])
        return {"path": path.name, "size": f"{w}x{h}", "var": "no-PIL"}
    try:
        img = Image.open(path).convert("RGB")
        arr = np.array(img, dtype=float)
        var = float(arr.var())
        nonwhite = float((arr.sum(axis=2) < 700).mean())
        return {
            "path": path.name,
            "size": f"{img.size[0]}x{img.size[1]}",
            "var": round(var, 1),
            "nonwhite_frac": round(nonwhite, 4),
            "BLANK?": "YES" if var < 200 else ("MAYBE" if var < 1500 else "no"),
        }
    except Exception as e:
        return {"path": path.name, "error": str(e)}


def main() -> None:
    csv_issues = []
    png_issues = []
    print("=" * 90)
    print("CSV AUDIT")
    print("=" * 90)
    for p in sorted(ROOT.rglob("*.csv")):
        if _should_skip(p):
            continue
        rel = p.relative_to(ROOT)
        info = audit_csv(p)
        if info.get("n_data_rows", 0) == 0 or info.get("empty_cells", 0) > 0 or info.get("blank_rows", 0) > 0:
            csv_issues.append((rel, info))
            print(f"[ISSUE] {rel} -> {info}")
    if not csv_issues:
        print("(no CSV issues found)")

    print()
    print("=" * 90)
    print("PNG AUDIT")
    print("=" * 90)
    for p in sorted(ROOT.rglob("*.png")):
        if _should_skip(p):
            continue
        rel = p.relative_to(ROOT)
        info = audit_png(p)
        blank = info.get("BLANK?")
        if blank in ("YES", "MAYBE") or "error" in info:
            png_issues.append((rel, info))
            tag = "BLANK" if blank == "YES" else ("SUSPECT" if blank == "MAYBE" else "ERROR")
            print(f"[{tag}] {rel} -> {info}")
    if not png_issues:
        print("(no PNG issues found)")

    print()
    print("=" * 90)
    print(f"SUMMARY: {len(csv_issues)} CSV issues, {len(png_issues)} PNG issues")
    print("=" * 90)


if __name__ == "__main__":
    main()
