.PHONY: env smoke data train generate score search eval audit figures results-summary package slides-env slides-build slides-render slides-verify

env:
	uv sync --locked --dev

smoke:
	uv run factuality-rerank-xsum env

data:
	uv run factuality-rerank-xsum data

train:
	uv run factuality-rerank-xsum train

generate:
	uv run factuality-rerank-xsum generate

score:
	uv run factuality-rerank-xsum score

search:
	uv run factuality-rerank-xsum search

eval:
	uv run factuality-rerank-xsum evaluate

audit:
	uv run factuality-rerank-xsum audit

figures:
	uv run factuality-rerank-xsum figures

results-summary:
	uv run factuality-rerank-xsum results-summary

package:
	uv run factuality-rerank-xsum package

slides-env:
	uv sync --locked --dev --group slides

slides-build:
	node docs/final-report/slides/final_slides.js
	uv run --group slides python docs/final-report/slides/scripts/normalize_pptx_fonts.py outputs/final/submission/final_slides.pptx
	soffice --headless --convert-to pdf --outdir outputs/final/submission outputs/final/submission/final_slides.pptx

slides-render:
	rm -rf tmp/final_slide_review
	mkdir -p tmp/final_slide_review
	uv run --group slides python docs/final-report/slides/scripts/render_slides.py outputs/final/submission/final_slides.pptx --output_dir tmp/final_slide_review

slides-verify:
	$(MAKE) slides-render
	uv run --group slides python docs/final-report/slides/scripts/slides_test.py outputs/final/submission/final_slides.pptx
	uv run --group slides python docs/final-report/slides/scripts/detect_font.py outputs/final/submission/final_slides.pptx --json
	uv run --group slides python docs/final-report/slides/scripts/create_montage.py --input_dir tmp/final_slide_review --output_file tmp/final_slide_review/montage.png --label_mode filename
