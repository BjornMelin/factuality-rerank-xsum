.PHONY: env smoke data train generate score search eval audit figures results-summary package

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
