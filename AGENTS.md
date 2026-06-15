# AGENTS.md

OctoBiz で作業する AI エージェント向けの補足ガイド。プロジェクト概要・ビルド方法・
バージョニング・リリースの詳細は [README.md](README.md) を参照し、ここには **README に
書かれていない／エージェントが間違えやすい点**だけをまとめる。

## 作業の進め方

- コードを変更したら **コミット前に `make lint` を通す**（CI と同じ: ruff + mypy）。
  フォント合成に関わる変更は `make build`（FontForge 同梱 Python が必要）でビルドが
  通ることも確認する。
- 縦メトリクスなど見た目に影響する変更は、`dist` の生成物を fonttools 等で実測し
  before/after を比較して確認する。

## 間違えやすい点

### バージョニングの patch 0–9 制限
フォント内部バージョンは X.MMP 方式（minor 2 桁 + patch 1 桁）で、**patch は 0–9 しか
持てない**（`build.py` の `font_revision()` が import 時に検証）。tagpr のデフォルトの
patch bump では `0.0.9` の次に `0.0.10` が作られて **ビルドが `ValueError` で落ちる**。
patch が 9 に達したら、リリース PR を `minor` ラベルで minor bump に手動で切り替える。

### ソースフォント差し替え時
`source_fonts/*.ttf` を更新したら `fontproject.toml` の依存 `version` も合わせる。
`build.py` の `verify_source_versions()` が不一致を検出してビルドを失敗させる。

### 合成ロジック（`build.py`）
- 重複グリフは **JP（BIZ UDPGothic）優先**。East Asian Ambiguous 幅も JP を残す。
- 縦メトリクスは **マジックナンバーを足し戻さず実測ベースで決める**
  （`usWin*` は `ink_extent()` でグリフ範囲から算出）。

## GitHub Actions

ワークフローを追加・変更したら **`ghalint run`** でポリシー検査を通し、
**`pinact run`** でアクションを full commit SHA にピンする。

## コミット / PR

- コミットメッセージは **日本語**。
- 以下の trailer を付ける（不要と明示されない限り）:

  ```
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```

- PR は `main` ベース。CI（lint + build）が通ることを確認する。
