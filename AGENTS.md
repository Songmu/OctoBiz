# AGENTS.md

Supplementary guide for AI agents working on OctoBiz. For the project overview,
build instructions, versioning, and release flow, see [README.md](README.md).
This file only captures what is **not in the README and what agents tend to get
wrong**.

## Workflow

- After changing code, **run `make lint` before committing** (same as CI: ruff +
  mypy). For changes that affect font synthesis, also confirm the build passes
  with `make build` (which requires FontForge's bundled Python).
- For changes that affect appearance (e.g. vertical metrics), measure the
  generated files under `dist` with fonttools or similar and compare before/after.

## Common pitfalls

### patch 0–9 limit in versioning
The font's internal version uses the X.MMP scheme (minor 2 digits + patch
1 digit), so **patch can only be 0–9** (validated at import time by
`font_revision()` in `build.py`). With tagpr's default patch bump, `0.0.9` is
followed by `0.0.10`, which makes the **build fail with `ValueError`**. When
patch reaches 9, manually switch the release PR to a minor bump using the
`minor` label.

### Replacing source fonts
When you update `source_fonts/*.ttf`, also update the corresponding dependency
`version` in `fontproject.toml`. `verify_source_versions()` in `build.py`
detects mismatches and fails the build.

### Synthesis logic (`build.py`)
- For duplicate glyphs, **JP (BIZ UDPGothic) takes priority**; JP is also kept
  for East Asian Ambiguous width characters.
- Decide vertical metrics from **measured values rather than re-adding magic
  numbers** (`usWin*` is computed from the glyph extent via `ink_extent()`).

## GitHub Actions

After adding or changing a workflow, run **`ghalint run`** to pass the policy
checks, and **`pinact run`** to pin actions to full commit SHAs.

## Commits / PRs

- Write commit messages in **Japanese**.
- Add the following trailer (unless explicitly told not to):

  ```
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```

- Base PRs on `main`. Confirm CI (lint + build) passes.
