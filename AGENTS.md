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

### patch 0–99 limit in versioning
The font's internal version uses the X.MPP scheme (minor 1 digit + patch
2 digits), matching Mona Sans (e.g. `v2.0.27` → `head.fontRevision = 2.027`),
so **minor can only be 0–9 and patch 0–99** (validated at import time by
`font_revision()` in `build.py`). tagpr's default patch bump is fine up to
`x.y.99`; only when **patch reaches 99** (or minor would exceed 9) do you need
to manually switch the release PR to a minor/major bump using the
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
