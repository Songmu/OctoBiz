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

import os
import shutil
import subprocess
from typing import Any, Tuple
from unicodedata import east_asian_width

import fontforge
import psMat

VERSION = "v0.0.1"
FONT_NAME = "OctoBiz"

BUILD_TMP = "build_tmp"
DIST_DIR = "dist"
SOURCE_DIR = "source_fonts"
SOURCE_FONT_JP = "BIZUDPGothic-{}.ttf"
SOURCE_FONT_EN = "MonaSans-{}.ttf"

# BIZ UDPGothic の em は 2048 だが、BIZTER と同様 ascent/descent を分けて持つ。
# ここは BIZTER の値をそのまま踏襲。実機検証で調整余地あり。
EM_ASCENT = 1782
EM_DESCENT = 266

FONT_ASCENT = EM_ASCENT + 40
FONT_DESCENT = EM_DESCENT + 190

# Bold 時に Mona Sans のどのウェイトを当てるか。
# BIZ UDPGothic Bold の太さに視覚的に近いのは SemiBold〜Bold。まずは SemiBold で運用し、
# 実機で見て要調整。
EN_WEIGHT_FOR_JP_BOLD = "SemiBold"

COPYRIGHT = """[Mona Sans]
Copyright 2022 The Mona Sans Project Authors (https://github.com/github/mona-sans), with Reserved Font Name "Mona"

[BIZ UDPGothic]
Copyright 2022 The BIZ UDGothic Project Authors (https://github.com/googlefonts/morisawa-biz-ud-gothic)

[BIZTER build script, from which build.py is derived]
Copyright 2022 Yuko OTAWARA (https://github.com/yuru7/BIZTER), with Reserved Font Name "BIZTER"

[OctoBiz]
Copyright 2026 Masayuki Matsuki (Songmu)
"""


def open_font(weight: str) -> Tuple[Any, Any]:
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


def remove_duplicate_glyphs(jp_font, en_font):
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


def adjust_font_scale(en_font):
    """欧文側を少し拡大して JP のサイズ感に揃える。"""
    for glyph in en_font.glyphs():
        if not glyph.isWorthOutputting():
            continue
        glyph.transform(psMat.scale(1.06, 1.06))
        glyph.transform(psMat.translate(0, -10))


def merge_fonts(jp_font, en_font, weight: str) -> Any:
    em_size = EM_ASCENT + EM_DESCENT
    jp_font.em = em_size
    en_font.em = em_size

    en_tmp = f"{BUILD_TMP}/modified_{SOURCE_FONT_EN.format(weight)}"
    en_font.generate(en_tmp)
    jp_font.mergeFonts(en_tmp)
    return jp_font


def edit_meta_data(font, weight: str):
    font.ascent = EM_ASCENT
    font.descent = EM_DESCENT

    font.os2_typoascent = FONT_ASCENT
    font.os2_typodescent = -FONT_DESCENT
    font.os2_typolinegap = 0

    font.hhea_ascent = FONT_ASCENT
    font.hhea_descent = -FONT_DESCENT
    font.hhea_linegap = 0

    font.os2_winascent = FONT_ASCENT
    font.os2_windescent = FONT_DESCENT

    font.sfnt_names = (
        (
            "English (US)",
            "License",
            "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. This license is available with a FAQ at: "
            "https://openfontlicense.org",
        ),
        ("English (US)", "License URL", "https://openfontlicense.org"),
        ("English (US)", "Version", f"{FONT_NAME} {VERSION}"),
    )
    font.familyname = FONT_NAME
    font.fontname = f"{FONT_NAME}-{weight}"
    font.fullname = f"{FONT_NAME} {weight}"
    # 4 文字のベンダ ID。Songmu に因んだ任意の識別子。
    font.os2_vendor = "Smu "
    font.copyright = COPYRIGHT


def main():
    if os.path.exists(BUILD_TMP):
        shutil.rmtree(BUILD_TMP)
    os.makedirs(BUILD_TMP)
    os.makedirs(DIST_DIR, exist_ok=True)

    for weight in ("Regular", "Bold"):
        jp_font, en_font = open_font(weight)
        remove_duplicate_glyphs(jp_font, en_font)
        adjust_font_scale(en_font)
        font = merge_fonts(jp_font, en_font, weight)
        edit_meta_data(font, weight)

        gen_path = f"{BUILD_TMP}/gen_{FONT_NAME}-{weight}.ttf"
        out_path = f"{DIST_DIR}/{FONT_NAME}-{weight}.ttf"
        font.generate(gen_path)

        subprocess.run(
            ("ttfautohint", "--dehint", gen_path, out_path),
            check=True,
        )
        print(f"built: {out_path}")


if __name__ == "__main__":
    main()
