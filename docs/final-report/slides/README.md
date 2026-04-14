# Slides Workspace

This deck is authored in editable JavaScript with `pptxgenjs`, following the `$slides` workflow.

## Local setup

Use the repo's `uv` environment plus the slide-specific dependency group:

```bash
make slides-env
```

That installs the Python packages needed for slide rendering and validation without relying on
Poppler. The repo-local scripts use:

- LibreOffice / `soffice` for PPTX -> PDF conversion
- PyMuPDF for PDF -> PNG rasterization
- `python-pptx`, `numpy`, and Pillow for overflow checks and montage generation
- `fc-list` plus LibreOffice for font detection

## Build and verify

Build the deck:

```bash
make slides-build
```

Render slide images:

```bash
make slides-render
```

Run the verification suite:

```bash
make slides-verify
```

That will:

- check for out-of-bounds content
- detect missing/substituted fonts
- create a montage at `tmp/final_slide_review/montage.png`

## Main files

- `final_slides.js`: editable PowerPoint source
- `scripts/render_slides.py`: repo-local rasterizer without Poppler
- `scripts/slides_test.py`: overflow checker
- `scripts/detect_font.py`: LibreOffice/fontconfig-based font check
- `assets/`: Berkeley template-derived art assets
