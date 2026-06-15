#!/usr/bin/env python3
"""Build OctoBiz: BIZ UDPGothic (JP) + Mona Sans (EN) merged font.

This script is a derivative work of the build script in yuru7/BIZTER
(https://github.com/yuru7/BIZTER), licensed under SIL OFL 1.1.

  Copyright (c) 2022, Yuko OTAWARA, with Reserved Font Name "BIZTER".
  Copyright (c) 2026, Masayuki Matsuki (Songmu).

Both the upstream BIZTER project and OctoBiz are distributed under the
SIL Open Font License 1.1, which explicitly covers "source files, build
scripts and documentation". See the LICENSE file in the repository root
for the full license text.

Requirements: FontForge's Python bindings and the `ttfautohint` CLI.

On macOS with Homebrew::

    brew install fontforge ttfautohint
    /opt/homebrew/bin/python3 build.py

(Homebrew's fontforge formula installs the Python module against its bundled
Python, so use that interpreter rather than a virtualenv `python3`.)
"""

import math
import os
import re
import shutil
import subprocess
import tomllib
from typing import Any
from unicodedata import east_asian_width

import fontforge
import psMat

MANIFEST = "fontproject.toml"


def load_manifest(path: str = MANIFEST) -> dict[str, Any]:
    """プロジェクトのメタデータ(バージョン・依存情報)を TOML から読み込む。"""
    with open(path, "rb") as f:
        return tomllib.load(f)


def font_revision(version: str) -> str:
    """semver "MAJOR.MINOR.PATCH" を OpenType の version 文字列 "X.MMP" に変換する。
    制約: minor は 0–99、patch は 0–9。
    これを超える場合は桁上げ(上位を増やす)運用とする。
    """
    major, minor, patch = (int(x) for x in version.split("."))
    if not (0 <= minor <= 99):
        raise ValueError(f"minor must be 0-99 for X.MMP scheme: {version}")
    if not (0 <= patch <= 9):
        raise ValueError(f"patch must be 0-9 for X.MMP scheme: {version}")
    return f"{major}.{minor:02d}{patch:01d}"


PROJECT = load_manifest()
DEPENDENCIES: list[dict[str, Any]] = PROJECT.get("dependencies", [])

FONT_NAME = PROJECT["font"]["name"]
VERSION = PROJECT["font"]["version"]
VENDOR_ID = PROJECT["font"]["vendor_id"]
WEIGHTS = PROJECT["font"]["weights"]
FONT_REVISION = font_revision(VERSION)

BUILD_TMP = "build_tmp"
DIST_DIR = "dist"
SOURCE_DIR = "source_fonts"
SOURCE_FONT_JP = "BIZUDPGothic-{}.ttf"
SOURCE_FONT_EN = "MonaSans-{}.ttf"

# em は BIZ UDPGothic に合わせて 2048。ベースライン分割も実フォントの値に倣う。
# (font.ascent/descent はベースライン=0 を動かさず、主にメタ情報として使われる)
EM_ASCENT = 1802
EM_DESCENT = 246
UPEM = EM_ASCENT + EM_DESCENT  # 2048

# 行送りに使う縦メトリクス(typo / hhea)。和欧混植で詰まり過ぎないよう、
# BIZ UDPGothic の em(2048)よりやや広めの約 1.11em に取る(BIZTER 系の運用を踏襲)。
# USE_TYPO_METRICS を立てるので、これが全プラットフォームでの行送りの正本になる。
LINE_ASCENT = 1822
LINE_DESCENT = 456

# Bold 時に Mona Sans のどのウェイトを当てるか。
# BIZ UDPGothic Bold の太さに視覚的に近いのは SemiBold〜Bold。まずは SemiBold で運用し、
# 実機で見て要調整。
EN_WEIGHT_FOR_JP_BOLD = "SemiBold"


def _copyright_block(entry: dict[str, Any]) -> str:
    section = entry.get("copyright_section", entry["name"])
    return f"[{section}]\n{entry['copyright']}"


def build_copyright() -> str:
    """フォント埋め込み用の copyright を生成する。"""
    blocks = [_copyright_block(dep) for dep in DEPENDENCIES]
    font = PROJECT["font"]
    blocks.append(f"[{font['name']}]\n{font['copyright']}")
    return "\n\n".join(blocks) + "\n"


COPYRIGHT = build_copyright()


def parse_version_number(version_string: str) -> str:
    """name ID 5 の文字列から数値部分 (例 "Version 1.051" -> "1.051") を取り出す。"""
    m = re.search(r"(\d+\.\d+)", version_string)
    return m.group(1) if m else ""


def verify_source_versions() -> None:
    """vendor 済みソースフォントの実バージョンが manifest の宣言と一致するか検証する。

    `version` と `files` を両方持つ依存エントリのみを対象とする。不一致は
    取り違え事故を防ぐためビルドを失敗させる。
    """
    for dep in DEPENDENCIES:
        declared = dep.get("version")
        files = dep.get("files")
        if not declared or not files:
            continue
        for filename in files:
            path = f"{SOURCE_DIR}/{filename}"
            font = fontforge.open(path)
            actual = parse_version_number(read_version(font))
            font.close()
            if actual != declared:
                raise ValueError(
                    f"version mismatch for {dep['name']} ({filename}): "
                    f"manifest declares {declared!r} but the vendored font "
                    f"reports {actual!r}. Update {MANIFEST} or the source font."
                )


def read_version(font: Any) -> str:
    """フォントの name テーブルから Version 文字列を取り出す。"""
    for _lang, key, value in font.sfnt_names:
        if key == "Version":
            return value
    return ""


def open_font(weight: str) -> tuple[Any, Any]:
    """ソースフォントを開く。Bold 時は欧文側のウェイトを差し替える。"""
    jp_font = fontforge.open(f"{SOURCE_DIR}/{SOURCE_FONT_JP.format(weight)}")
    en_weight = EN_WEIGHT_FOR_JP_BOLD if weight == "Bold" else weight
    en_font = fontforge.open(f"{SOURCE_DIR}/{SOURCE_FONT_EN.format(en_weight)}")

    # 参照を解除して以後の編集が独立に効くようにする
    for glyph in jp_font.glyphs():
        if glyph.isWorthOutputting():
            jp_font.selection.select(("more", None), glyph)
    jp_font.unlinkReferences()
    for glyph in en_font.glyphs():
        if glyph.isWorthOutputting():
            en_font.selection.select(("more", None), glyph)
    en_font.unlinkReferences()
    jp_font.selection.none()
    en_font.selection.none()

    return jp_font, en_font


def remove_duplicate_glyphs(jp_font: Any, en_font: Any) -> None:
    """重複グリフは原則 JP 側を残し、East Asian Ambiguous は JP 優先で EN 側を消す。"""
    for g in en_font.glyphs():
        if not g.isWorthOutputting():
            continue
        unicode = int(g.unicode)
        if unicode < 0:
            continue
        for g_jp in jp_font.selection.select(unicode).byGlyphs:
            if east_asian_width(chr(unicode)) == "A":
                g.clear()
            else:
                g_jp.clear()


def adjust_font_scale(en_font: Any) -> None:
    """欧文側を少し拡大して JP のサイズ感に揃える。"""
    for glyph in en_font.glyphs():
        if not glyph.isWorthOutputting():
            continue
        glyph.transform(psMat.scale(1.06, 1.06))
        glyph.transform(psMat.translate(0, -10))


def merge_fonts(jp_font: Any, en_font: Any, weight: str) -> Any:
    em_size = UPEM
    jp_font.em = em_size
    en_font.em = em_size

    en_tmp = f"{BUILD_TMP}/modified_{SOURCE_FONT_EN.format(weight)}"
    en_font.generate(en_tmp)
    jp_font.mergeFonts(en_tmp)
    return jp_font


def build_description() -> str:
    """フォントに埋め込む書体説明 (name ID 10) を manifest から取得する。"""
    return PROJECT["font"]["description"]


def ink_extent(font: Any) -> tuple[int, int]:
    """マージ後フォントの実グリフ上下端を (上方向, 下方向) の正の大きさで返す。

    usWinAscent/usWinDescent はグリフのインクを覆うクリップ枠なので、
    欧文を 1.06 倍に拡大したことで em 枠から食み出す字形があっても
    切れないよう、実測したバウンディングボックスから決める。
    """
    ymax = 0.0
    ymin = 0.0
    for glyph in font.glyphs():
        if not glyph.isWorthOutputting():
            continue
        _xmin, gymin, _xmax, gymax = glyph.boundingBox()
        ymax = max(ymax, gymax)
        ymin = min(ymin, gymin)
    return math.ceil(ymax), math.ceil(-ymin)


def edit_meta_data(font: Any, weight: str) -> None:
    font.ascent = EM_ASCENT
    font.descent = EM_DESCENT

    # 行送りの正本となる typo メトリクス。USE_TYPO_METRICS を立て、
    # Windows でも typo 系が使われるようにして全環境で行送りを揃える。
    font.os2_typoascent = LINE_ASCENT
    font.os2_typodescent = -LINE_DESCENT
    font.os2_typolinegap = 0
    font.os2_use_typo_metrics = True

    # macOS が参照する hhea も typo と同値にして行送りを一致させる。
    font.hhea_ascent = LINE_ASCENT
    font.hhea_descent = -LINE_DESCENT
    font.hhea_linegap = 0

    # win はクリップ枠。行送り(LINE_*)と実グリフ範囲の両方を必ず覆う。
    ink_ascent, ink_descent = ink_extent(font)
    font.os2_winascent = max(LINE_ASCENT, ink_ascent)
    font.os2_windescent = max(LINE_DESCENT, ink_descent)

    # OpenType の name ID 5 は "Version X.YYY" 形式が推奨。FONT_REVISION を使う。
    version_str = f"Version {FONT_REVISION}"

    font.version = FONT_REVISION
    font.sfnt_names = (
        (
            "English (US)",
            "License",
            "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. This license is available with a FAQ at: "
            "https://openfontlicense.org",
        ),
        ("English (US)", "License URL", "https://openfontlicense.org"),
        ("English (US)", "Version", version_str),
        ("English (US)", "Descriptor", build_description()),
    )
    font.familyname = FONT_NAME
    font.fontname = f"{FONT_NAME}-{weight}"
    font.fullname = f"{FONT_NAME} {weight}"
    font.os2_vendor = VENDOR_ID
    font.copyright = COPYRIGHT


def main() -> None:
    # 中間/出力ディレクトリは毎回作り直す。dist/ をクリーンにすることで、
    # 過去ビルドの成果物が残って package.py の同梱対象に混入するのを防ぐ。
    for d in (BUILD_TMP, DIST_DIR):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # vendor 済みソースフォントが manifest の宣言バージョンと一致するか先に検証。
    verify_source_versions()

    for weight in WEIGHTS:
        jp_font, en_font = open_font(weight)
        remove_duplicate_glyphs(jp_font, en_font)
        adjust_font_scale(en_font)
        font = merge_fonts(jp_font, en_font, weight)
        edit_meta_data(font, weight)

        gen_path = f"{BUILD_TMP}/gen_{FONT_NAME}-{weight}.ttf"
        out_path = f"{DIST_DIR}/{FONT_NAME}-{weight}.ttf"
        font.generate(gen_path)

        # `--no-info` で ttfautohint が version 文字列を書き換えるのを防ぐ。
        subprocess.run(
            ("ttfautohint", "--dehint", "--no-info", gen_path, out_path),
            check=True,
        )
        print(f"built: {out_path}")


if __name__ == "__main__":
    main()
