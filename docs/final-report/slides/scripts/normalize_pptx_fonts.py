#!/usr/bin/env python3
"""Rewrite requested font family names inside a PPTX archive.

This is used to remove inherited Office-theme font requests like Arial from the
generated deck so local font verification reflects the deck's intended final
font surface.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def normalize_pptx_fonts(pptx_path: Path, from_font: str, to_font: str) -> int:
    replacements = 0
    with tempfile.TemporaryDirectory(prefix="pptx_font_norm_") as tmpdir:
        tmp_path = Path(tmpdir) / pptx_path.name
        with ZipFile(pptx_path, "r") as zin, ZipFile(
            tmp_path, "w", compression=ZIP_DEFLATED
        ) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename.endswith(".xml") and info.filename.startswith(
                    ("ppt/", "docProps/")
                ):
                    text = data.decode("utf-8")
                    count = text.count(from_font)
                    if count:
                        text = text.replace(from_font, to_font)
                        replacements += count
                        data = text.encode("utf-8")
                zout.writestr(info, data)
        shutil.move(str(tmp_path), str(pptx_path))
    return replacements


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize requested font names inside a PPTX.")
    parser.add_argument("pptx_path", type=Path)
    parser.add_argument("--from-font", default="Arial")
    parser.add_argument("--to-font", default="Liberation Sans")
    args = parser.parse_args()

    count = normalize_pptx_fonts(args.pptx_path, args.from_font, args.to_font)
    print(f"Replaced {count} occurrences of {args.from_font!r} with {args.to_font!r}.")


if __name__ == "__main__":
    main()
