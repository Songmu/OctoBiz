# OctoBiz

**OctoBiz** は、主にGitHub関連のプレゼンや資料向けに作られた日本語合成フォントです。

- 和文: [BIZ UDPGothic](https://github.com/googlefonts/morisawa-biz-ud-gothic) — UD（ユニバーサルデザイン）系の高い可読性
- 欧文: [Mona Sans](https://github.com/github/mona-sans) — GitHub が手がけた汎用書体（Web / プロダクト / 印刷向け）
- 合成手法: [BIZTER](https://github.com/yuru7/BIZTER)（BIZ UDPGothic × Inter）の FontForge ベース手法を流用

> [!IMPORTANT]
> **OctoBiz は GitHub の公式プロダクトではありません。** 個人プロジェクトとして、GitHub の OSS フォントである Mona Sans と BIZ UDPGothic を組み合わせた派生フォントを配布しているだけのものです。

## ダウンロード

[Releases](https://github.com/Songmu/OctoBiz/releases) から最新版の `.ttf` を取得してください。

提供ウェイト:

| ファイル | 用途 |
| --- | --- |
| `OctoBiz-Regular.ttf` | 本文用 |
| `OctoBiz-Bold.ttf` | 見出し・強調用 |

## クレジット

OctoBiz は以下の素晴らしいフォント／プロジェクトの上に成り立っています。

- **欧文フォント**: [Mona Sans](https://github.com/github/mona-sans) — © 2022 The Mona Sans Project Authors, with Reserved Font Name `"Mona"` (SIL OFL 1.1)
- **和文フォント**: [BIZ UDPGothic](https://github.com/googlefonts/morisawa-biz-ud-gothic) — © 2022 The BIZ UDGothic Project Authors (SIL OFL 1.1)
- **合成スクリプト (`build.py`) の派生元**: [yuru7/BIZTER](https://github.com/yuru7/BIZTER) — © 2022 Yuko OTAWARA, with Reserved Font Name `"BIZTER"` (SIL OFL 1.1)

両ソースフォントのライセンス全文は [`source_fonts/LICENSE_MonaSans`](source_fonts/LICENSE_MonaSans) と [`source_fonts/LICENSE_BIZUDPGothic`](source_fonts/LICENSE_BIZUDPGothic) を、BIZTER との関係を含む統合ライセンスは [`LICENSE`](LICENSE) を参照してください。

## ライセンス

[SIL Open Font License 1.1](LICENSE) で配布します。OFL は `"source files, build scripts and documentation"` を Font Software として扱うため、本リポジトリの **フォント本体・ソースフォント・`build.py` のすべてが OFL 1.1** で配布されます。

- OFL に従い、再配布時はこの LICENSE ファイルおよびすべての著作権表示を保持してください。

## ビルド方法

### 必要なもの

- macOS / Linux
- [FontForge](https://fontforge.org/) (Python bindings 同梱)
- [ttfautohint](https://www.freetype.org/ttfautohint/)
- [uv](https://docs.astral.sh/uv/)（開発ツール: ruff / mypy の管理用）

### セットアップ

`make setup` が OS を判別して上記ツールを導入し、開発ツールを `uv sync` で同期します。

```sh
make setup
```

> [!NOTE]
> `fontforge` / `psMat` は FontForge 同梱の Python 専用モジュールで PyPI からは入りません。そのためフォントのビルドは uv の仮想環境ではなく **システムの FontForge Python** で実行します（macOS Homebrew では `/opt/homebrew/bin/python3`）。uv が管理するのは ruff / mypy などの開発ツールのみです。

### ソースフォントの取得

`source_fonts/` 配下に以下のファイル一式を配置します（OFL のもとで再配布が許可されているためリポジトリにも同梱済みなので、通常はこの手順をスキップして `make build` だけで OK です）。

```
source_fonts/
├── BIZUDPGothic-Regular.ttf
├── BIZUDPGothic-Bold.ttf
├── MonaSans-Regular.ttf
├── MonaSans-SemiBold.ttf   # Bold ビルド時に欧文側として採用
├── MonaSans-Bold.ttf       # 予備（ウェイト調整検証用）
├── LICENSE_BIZUDPGothic
└── LICENSE_MonaSans
```

ソースフォントを差し替え/更新したい場合の取得例:

```sh
# BIZ UDPGothic
gh release download -R googlefonts/morisawa-biz-ud-gothic --pattern 'morisawa-biz-ud-gothic-fonts.zip'
unzip morisawa-biz-ud-gothic-fonts.zip
cp morisawa-biz-ud-gothic-fonts/fonts/ttf/BIZUDPGothic-{Regular,Bold}.ttf source_fonts/

# Mona Sans (Static)
gh release download -R github/mona-sans --pattern 'mona-sans-static-*.zip'
unzip mona-sans-static-*.zip
cp fonts/static/ttf/MonaSans-{Regular,SemiBold,Bold}.ttf source_fonts/
```

### ビルド

```sh
make build
```

成果物は `dist/OctoBiz-Regular.ttf` および `dist/OctoBiz-Bold.ttf` に生成されます。

### 配布用 zip の生成

```sh
make package
```

`dist/OctoBiz_v<version>.zip` を生成します。zip 内は単一ルートフォルダ `OctoBiz_v<version>/` に `.ttf` 一式・`LICENSE`・配布用 `README.md` を同梱します（バージョンは `fontproject.toml` 由来）。`package.py` は標準ライブラリのみで動作し FontForge 非依存です。

### Lint / フォーマット

```sh
make lint   # ruff (check + format --check) と mypy
make fmt    # ruff で自動整形・自動修正
```


## プロジェクトメタデータ (`fontproject.toml`)

このフォント自身のバージョンと、依存フォント（ソースフォント）のバージョン・由来は、リポジトリ直下の [`fontproject.toml`](fontproject.toml) に集約しています。`build.py` はこのファイルを唯一の真実 (single source of truth) として読み込み、

- `[font].version` を出力フォントのバージョン採番に使用
- 各依存の `version` をフォントの Description (`name` ID 10) とコピーライトへ埋め込み
- vendor 済みの `source_fonts/*.ttf` の実バージョンが宣言値と一致するか**ビルド時に照合**（不一致ならビルドを失敗させ、取り違えを防止）

します。バージョンや依存を更新する際は、まず `fontproject.toml` を編集してください。

> [!NOTE]
> 依存の厳密なピン留め（リリースタグ / コミットハッシュ単位の固定）は将来対応予定で、現状は人間が読むための `version` の記録と照合のみを行います。

## バージョニング

バージョンは、`fontproject.toml` の `[font].version` にsemver形式で記載します。git tagは `v` prefix付きの値を使用します。


一方、OpenType の数値バージョン（`name` ID 5 / `head.fontRevision`）は仕様上 `MAJOR.MINOR`（小数部ちょうど3桁）しか持てず、semver をそのまま格納できません（[OpenFV](https://github.com/openfv/openfv) でも MINOR は3桁固定）。そこで小数部3桁を **minor 2桁 + patch 1桁** に割り当てる方法を採用します。


## 既知の検討ポイント

1. **Bold ウェイトマッチング**: 現状は欧文側を `MonaSans-SemiBold` で合わせています。実プレゼン投影で太さ感を見ながら `Bold` / `ExtraBold` への切り替えを検討してください（`build.py` の `EN_WEIGHT_FOR_JP_BOLD` で変更可）。
2. **メトリクス**: ascent / descent / line height は BIZTER 由来の値を踏襲しています。Mona Sans 特有のメトリクスにより行間調整が必要になる場合があります。
3. **ヒンティング**: 最終工程で `ttfautohint --dehint` をかけています（BIZTER と同じ方針）。
4. **Variable Font 非対応**: BIZ UDPGothic がスタティックフォントのため、Variable 合成は行わず Regular / Bold の 2 ウェイト固定です。

## 関連リンク

- [BIZTER](https://github.com/yuru7/BIZTER) — 合成手法のベース実装
- [Mona Sans](https://github.com/github/mona-sans)
- [BIZ UDPGothic](https://github.com/googlefonts/morisawa-biz-ud-gothic)
- [SIL Open Font License 1.1 FAQ](https://scripts.sil.org/OFL_web)
