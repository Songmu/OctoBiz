# OctoBiz build & dev tasks.
#
# - Font build runs under FontForge's bundled Python (provides the `fontforge`
#   module, which is NOT installable from PyPI).
# - Dev tools (ruff / mypy) are managed by uv.

UNAME := $(shell uname -s)

ifeq ($(UNAME),Darwin)
	# Homebrew's fontforge installs the Python module against its own Python.
	FONTFORGE_PYTHON ?= /opt/homebrew/bin/python3
else
	FONTFORGE_PYTHON ?= python3
endif

.PHONY: setup build package lint fmt clean

## setup: install system tools (fontforge, ttfautohint) and dev tools (uv)
setup:
ifeq ($(UNAME),Darwin)
	brew install fontforge ttfautohint uv
else ifeq ($(UNAME),Linux)
	sudo apt-get update
	sudo apt-get install -y fontforge python3-fontforge ttfautohint
	command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
else
	@echo "Unsupported OS: $(UNAME). Install fontforge, ttfautohint and uv manually." >&2
	@exit 1
endif
	uv sync

## build: build dist/OctoBiz-*.ttf
build:
	$(FONTFORGE_PYTHON) build.py

## package: bundle the built fonts into dist/OctoBiz_v*.zip
package: build
	uv run python package.py

## lint: run ruff and mypy
lint:
	uv run ruff check build.py package.py
	uv run ruff format --check build.py package.py
	uv run mypy build.py package.py

## fmt: auto-format with ruff
fmt:
	uv run ruff format build.py package.py
	uv run ruff check --fix build.py package.py

## clean: remove build artifacts
clean:
	rm -rf build_tmp dist
