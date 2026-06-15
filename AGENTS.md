# AGENTS.md

AI エージェント向けの作業ガイド。OctoBiz リポジトリで変更を行う前に必ず目を通すこと。

## プロジェクト概要

OctoBiz は **BIZ UDPGothic（和文）と GitHub の Mona Sans（欧文）を合成**した、
GitHub 関連のスライド・資料向け日本語ゴシック体。`build.py` が FontForge で
2 つのソースフォントをマージして `dist/OctoBiz-{Regular,Bold}.ttf` を生成する。

- 合成手法は [yuru7/BIZTER](https://github.com/yuru7/BIZTER) の派生実装。
- ライセンスは **SIL Open Font License 1.1**（ソース・ビルドスクリプト・ドキュメントを含む）。
- Variable Font 非対応（BIZ UDPGothic がスタティックのため Regular / Bold の 2 ウェイト固定）。

## リポジトリ構成

| パス | 役割 |
|---|---|
| `build.py` | フォント合成本体（**FontForge の Python で実行**） |
| `package.py` | ビルド済みフォントを zip 化（標準ライブラリのみ。FontForge 不要） |
| `fontproject.toml` | **メタデータの single source of truth**（バージョン・依存・著作権・説明） |
| `source_fonts/` | vendor 済みソースフォント（`BIZUDPGothic-*.ttf`, `MonaSans-*.ttf`）とライセンス |
| `Makefile` | `setup` / `build` / `package` / `lint` / `fmt` / `clean` |
| `dist/`, `build_tmp/` | ビルド成果物（**gitignore 済み。コミットしない**） |
| `.github/` | CI・リリース・tagpr・dependabot |

## ビルド・開発コマンド

ビルドには `fontforge` と `ttfautohint` が必要。`fontforge` / `psMat` は FontForge
アプリ同梱の Python が提供し **PyPI からは入らない**。Makefile が OS に応じて
`FONTFORGE_PYTHON`（macOS は `/opt/homebrew/bin/python3`）を選ぶ。

```sh
make setup     # fontforge / ttfautohint / uv と dev ツールを導入
make build     # dist/OctoBiz-*.ttf を生成（FontForge Python）
make package   # dist/OctoBiz_v*.zip を生成
make lint      # ruff check + ruff format --check + mypy（CI と同じ）
make fmt       # ruff format + ruff --fix
```

- dev ツール（ruff / mypy）は **uv** 管理。`build.py`/`package.py` は Python パッケージではない（`pyproject.toml` の `package = false`）。
- **コミット前に `make lint` を通すこと。** ソース変更時は `make build` でビルドが通ることも確認する。
- 縦メトリクスなど見た目に関わる変更は、`dist` を実測（fonttools 等）して before/after を確認すると確実。

## 重要な規約・落とし穴

### バージョニング
- **semver が正本**（`fontproject.toml` の `[font].version` と git タグ `vX.Y.Z`）。
- フォント内部（`head.fontRevision` / name ID 5）へは **X.MMP 方式**（minor 2 桁 + patch 1 桁、例 `1.2.3 → 1.023`）で写す。`build.py` の `font_revision()` 参照。
- **patch は 0–9 のみ**。`0.0.9` の次に tagpr が `0.0.10` を作ると `build.py` が import 時に `ValueError` で落ちる。**patch が 9 に達したらリリース PR を minor bump（`minor` ラベル）に手動で切り替える**こと。
- リリース自動化は **tagpr**（`versionFile = fontproject.toml`, draft release）→ `ghr` でビルド zip を添付。

### メタデータ
- 著作権・説明・依存バージョン・ウェイト一覧などはすべて `fontproject.toml` に集約。`build.py` が `tomllib` で読む。コード中にハードコードしない。
- `verify_source_versions()` が `source_fonts/*.ttf` の実バージョンと manifest の宣言を照合し、不一致ならビルドを失敗させる。ソースフォント差し替え時は manifest も更新する。

### 合成ロジック（`build.py`）
- 重複グリフは原則 **JP（BIZ UDPGothic）優先**。East Asian Ambiguous 幅の文字も JP を残し EN 側を消す。
- 欧文は `adjust_font_scale()` で **1.06 倍**に拡大して和文のサイズ感に合わせる。
- Bold 時は欧文に `MonaSans-SemiBold` を当てる（`EN_WEIGHT_FOR_JP_BOLD`）。
- 縦メトリクス: 行送り（typo / hhea）は約 1.11em の `LINE_ASCENT` / `LINE_DESCENT`。`USE_TYPO_METRICS` を有効化して全プラットフォームで行送りを統一。`usWin*`（クリップ枠）は `ink_extent()` で実グリフ範囲から算出し、欧文拡大による食み出しでも切れないようにする。**マジックナンバーを足し戻すのではなく実測ベースで決める**こと。

### GitHub Actions
- ワークフロー追加・変更時は **`ghalint run`** でポリシー検査（`timeout-minutes` 必須・`persist-credentials: false` 等）を通す。
- アクションは **`pinact run`** で full commit SHA にピンする（タグ直書きしない）。

### 配布
- Homebrew 配布は **自前 tap（Songmu/homebrew-tap）の Cask（`font` stanza）** 方針。リリース自動化を優先し、tap の自動更新は当面行わない。

## コミット / PR

- **コミットメッセージは日本語**（既存履歴に倣う）。
- コミットには以下の trailer を付ける（明示的に不要と言われない限り）:

  ```
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```

- PR は `main` をベースに作成。CI（`ci.yml`: lint + build）が通ることを確認する。
