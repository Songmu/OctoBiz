#!/usr/bin/env python3
"""Package the built OctoBiz fonts into a distributable zip archive.

This script uses only the Python standard library so it runs portably on any
platform (macOS / Linux / Windows) and does NOT require FontForge. Run it after
`build.py` has produced the fonts in ``dist/``.

The archive layout follows the convention used by similar merged-font projects
(e.g. UDEV Gothic): a single top-level directory named after the archive so the
contents stay tidy when extracted::

    OctoBiz_v0.1.0.zip
    └── OctoBiz_v0.1.0/
        ├── OctoBiz-Regular.ttf
        ├── OctoBiz-Bold.ttf
        ├── LICENSE
        └── README.md
"""

import tomllib
import zipfile
from pathlib import Path
from typing import Any

MANIFEST = "fontproject.toml"
DIST_DIR = Path("dist")
LICENSE_FILE = Path("LICENSE")


def load_manifest(path: str = MANIFEST) -> dict[str, Any]:
    """プロジェクトのメタデータを TOML から読み込む。"""
    with open(path, "rb") as f:
        return tomllib.load(f)


def build_readme(project: dict[str, Any], font_paths: list[Path]) -> str:
    """配布物に同梱するエンドユーザー向けの README を manifest から生成する。"""
    font = project["font"]
    name = font["name"]
    lines = [
        f"# {name} v{font['version']}",
        "",
        font["description"],
        "",
        "## Fonts",
        "",
    ]
    lines += [f"- {p.name}" for p in font_paths]
    lines += [
        "",
        "## Credits",
        "",
    ]
    for dep in project.get("dependencies", []):
        repo = dep.get("repository", "")
        suffix = f" ({repo})" if repo else ""
        lines.append(f"- {dep['name']}{suffix}")
    lines += [
        "",
        "## License",
        "",
        "SIL Open Font License 1.1. See the bundled `LICENSE` file for the "
        "full text and all copyright notices.",
        "",
    ]
    return "\n".join(lines)


def package() -> Path:
    """dist/ のフォントと LICENSE / README をまとめた zip を生成しパスを返す。"""
    project = load_manifest()
    version = project["font"]["version"]
    arcname = f"{project['font']['name']}_v{version}"
    zip_path = DIST_DIR / f"{arcname}.zip"

    # build.py が dist/ に出力したフォントをそのまま同梱する。
    font_paths = sorted(DIST_DIR.glob("*.ttf"))
    if not font_paths:
        raise FileNotFoundError(
            f"no built fonts found in {DIST_DIR}/. Run build.py first."
        )
    if not LICENSE_FILE.exists():
        raise FileNotFoundError(f"missing {LICENSE_FILE}")

    readme = build_readme(project, font_paths)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in font_paths:
            zf.write(path, f"{arcname}/{path.name}")
        zf.write(LICENSE_FILE, f"{arcname}/LICENSE")
        zf.writestr(f"{arcname}/README.md", readme)

    return zip_path


def main() -> None:
    zip_path = package()
    print(f"packaged: {zip_path}")


if __name__ == "__main__":
    main()
