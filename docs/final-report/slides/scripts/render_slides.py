#!/usr/bin/env python3
"""Render PPTX or PDF slides to PNG without Poppler.

This is a repo-local variant of the slide skill helper that keeps the same CLI
surface but swaps pdf2image/Poppler for PyMuPDF so it works without admin
installed `pdfinfo` / `pdftoppm`.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from os import makedirs
from os.path import abspath, basename, exists, expanduser, join, splitext
from zipfile import ZipFile

import fitz

EMU_PER_INCH = 914_400
fitz.TOOLS.mupdf_display_errors(False)


def calc_dpi_via_ooxml(input_path: str, max_w_px: int, max_h_px: int) -> int:
    """Calculate DPI from OOXML `ppt/presentation.xml` slide size."""
    with ZipFile(input_path, "r") as zf:
        xml = zf.read("ppt/presentation.xml")
    root = ET.fromstring(xml)
    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    sld_sz = root.find("p:sldSz", ns)
    if sld_sz is None:
        raise RuntimeError("Slide size not found in presentation.xml")
    cx = int(sld_sz.get("cx") or 0)
    cy = int(sld_sz.get("cy") or 0)
    if cx <= 0 or cy <= 0:
        raise RuntimeError("Invalid slide size values in presentation.xml")
    width_in = cx / EMU_PER_INCH
    height_in = cy / EMU_PER_INCH
    return round(min(max_w_px / width_in, max_h_px / height_in))


def calc_dpi_via_pdf(input_path: str, max_w_px: int, max_h_px: int) -> int:
    """Calculate DPI from the first PDF page size using PyMuPDF."""
    with fitz.open(input_path) as doc:
        if doc.page_count == 0:
            raise RuntimeError("PDF has no pages")
        rect = doc[0].rect
    width_in = rect.width / 72.0
    height_in = rect.height / 72.0
    if width_in <= 0 or height_in <= 0:
        raise RuntimeError("Invalid PDF page size")
    return round(min(max_w_px / width_in, max_h_px / height_in))


def run_cmd_no_check(cmd: list[str]) -> None:
    subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
    )


def convert_to_pdf(
    pptx_path: str,
    user_profile: str,
    convert_tmp_dir: str,
    stem: str,
) -> str:
    """Convert PPTX to PDF with a best-effort LibreOffice fallback via ODP."""
    cmd_pdf = [
        "soffice",
        "-env:UserInstallation=file://" + user_profile,
        "--invisible",
        "--headless",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        convert_tmp_dir,
        pptx_path,
    ]
    run_cmd_no_check(cmd_pdf)

    pdf_path = join(convert_tmp_dir, f"{stem}.pdf")
    if exists(pdf_path):
        return pdf_path

    cmd_odp = [
        "soffice",
        "-env:UserInstallation=file://" + user_profile,
        "--invisible",
        "--headless",
        "--norestore",
        "--convert-to",
        "odp",
        "--outdir",
        convert_tmp_dir,
        pptx_path,
    ]
    run_cmd_no_check(cmd_odp)

    odp_path = join(convert_tmp_dir, f"{stem}.odp")
    if exists(odp_path):
        cmd_odp_pdf = [
            "soffice",
            "-env:UserInstallation=file://" + user_profile,
            "--invisible",
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            convert_tmp_dir,
            odp_path,
        ]
        run_cmd_no_check(cmd_odp_pdf)
        if exists(pdf_path):
            return pdf_path

    return ""


def _render_pdf_to_pngs(pdf_path: str, out_dir: str, dpi: int) -> list[str]:
    makedirs(out_dir, exist_ok=True)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    paths: list[str] = []
    with fitz.open(pdf_path) as doc:
        for index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix, alpha=True)
            path = join(out_dir, f"slide-{index}.png")
            pix.save(path)
            paths.append(path)
    return paths


def rasterize(input_path: str, out_dir: str, dpi: int) -> list[str]:
    """Rasterize PPTX/PDF to PNG files placed in out_dir and return image paths."""
    makedirs(out_dir, exist_ok=True)
    input_path = abspath(input_path)
    stem = splitext(basename(input_path))[0]

    if input_path.lower().endswith(".pdf"):
        return _render_pdf_to_pngs(input_path, out_dir, dpi)

    with tempfile.TemporaryDirectory(prefix="soffice_profile_") as user_profile:
        with tempfile.TemporaryDirectory(prefix="soffice_convert_") as convert_tmp_dir:
            pdf_path = convert_to_pdf(input_path, user_profile, convert_tmp_dir, stem)
            if not pdf_path or not exists(pdf_path):
                raise RuntimeError(
                    "Failed to produce PDF for rasterization (direct and ODP fallback)."
                )
            return _render_pdf_to_pngs(pdf_path, out_dir, dpi)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render slides to images.")
    parser.add_argument("input_path", type=str, help="Path to the input PowerPoint or PDF file.")
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help=(
            "Output directory for the rendered images. Defaults to a folder next to the input "
            "named after the input file without its extension."
        ),
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1600,
        help="Approximate maximum width in pixels after isotropic scaling.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=900,
        help="Approximate maximum height in pixels after isotropic scaling.",
    )
    args = parser.parse_args()

    input_path = abspath(expanduser(args.input_path))
    output_dir = (
        abspath(expanduser(args.output_dir))
        if args.output_dir
        else join(
            os.path.dirname(input_path),
            re.sub(r"[^A-Za-z0-9._-]+", "_", splitext(basename(input_path))[0]),
        )
    )

    if input_path.lower().endswith(".pdf"):
        dpi = calc_dpi_via_pdf(input_path, args.width, args.height)
    else:
        dpi = calc_dpi_via_ooxml(input_path, args.width, args.height)

    paths = rasterize(input_path, output_dir, dpi)
    print("\n".join(paths))


if __name__ == "__main__":
    main()
