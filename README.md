# Paper Manager v1.0

Notionと連携して論文管理を自動化するツールです。
DOIやPDFからメタデータを取得し、翻訳付きでNotionに追加します。また、Notion上のデータをNatureの引用形式に合わせたtxtファイルやBibTeX形式でエクスポートすることも可能です。

## 機能
- **論文インポート**: DOIを入力するか、PDFファイルをドロップするだけで、書誌情報（タイトル、著者、アブストラクトなど）を自動取得。
- **自動翻訳**: アブストラクトを日本語（常体・学術調）に自動翻訳してNotionに保存。
- **Notion連携**: データベースに自動でページを作成。
- **エクスポート**: Notionに保存した論文を「Natureの引用形式に合わせたtxtファイル」や「BibTeX」で出力（引用キー検索対応）。
- **GUI完備**: わかりやすい操作画面（ダブルクリックで起動可能）。

## 必要要件
- OS: macOS (推奨), Linux, Windows
- Python 3.11以上
- Notion アカウント & インテグレーション取得
- Google Gemini API キー (翻訳用)

## セットアップ手順

### 1. インストール
リポジトリをクローンし、Conda環境を作成します。

```bash
git clone https://github.com/fugash-i/paper-manager.git
cd paper-manager

# 環境作成 (初回のみ)
conda env create -f environment.yml

# 環境の有効化
conda activate paper-manager
```

### 2. 環境変数の設定
プロジェクトルートに `.env` ファイルを作成し、以下の情報を記述してください。

```bash
NOTION_TOKEN=your_notion_integration_token
DATABASE_ID=your_notion_database_id
GEMINI_API_KEY=your_gemini_api_key

# エクスポートファイルのデフォルト保存先（任意）
EXPORT_DIR=/Users/username/Documents/citation
```

### 3. Notionデータベースの準備
Notionでデータベースを作成し、以下のプロパティ（カラム）を設定してください。
あるいは, 以下の[リンク]([https://www.notion.so/31d834ce8c7d801fa7d6edd236c08e8d?v=31d834ce8c7d8175a337000ccde6ade0&source=copy_link](https://grey-brake-854.notion.site/Paper-manager-template-31d834ce8c7d80bfa5a2d948aa95cf2c))からページテンプレートをコピーしてください. 
※プロパティ名は大文字小文字を含めて正確に合わせてください。

| プロパティ名 | 種類 (Type) | 備考 |
| --- | --- | --- |
| **名前** (Title) | タイトル | デフォルトのタイトル列 |
| **First Author** | テキスト (Text) | 第一著者 |
| **Authors** | マルチセレクト (Multi-select) | 全著者 |
| **Journal** | セレクト (Select) | 掲載誌 |
| **Publication Date** | 日付 (Date) | 出版日 |
| **Volume** | 数値 (Number) | 巻号 |
| **Pages** | テキスト (Text) | ページ番号 |
| **DOI** | テキスト (Text) | DOIリンク |
| **URL** | URL | 論文URL |
| **PMID** | テキスト (Text) | PubMed ID |
| **cite key** | マルチセレクト (Multi-select) | 引用エクスポート時の検索キー |
| **read** | チェックボックス (Checkbox) | 既読管理用 |

**注意**: Notonインテグレーション（APIキー）をこのデータベースのあるページ（親ページ含む）に招待（Connect）することを忘れないでください。

## 使い方

### GUIで使う (推奨)
- **Mac / Linux の場合**: `paper-manager.command` ファイルをダブルクリックしてください。
- **Windows の場合**: `paper-manager.bat` ファイルをダブルクリックしてください。
ブラウザが立ち上がり、操作画面が表示されます。

#### 画面説明
1.  **Import Paper タブ**:
    *   DOIを入力するか、PDFをドラッグ＆ドロップして「Fetch & Save」をクリック。
    *   **Translate Abstract**: チェックを外すと、Geminiによる自動翻訳をスキップできます。
2.  **Export Citations タブ**:
    *   Notion側で設定した `cite key` （例: `paper2023`）を入力して検索。
    *   プレビュー確認後、ファイルをダウンロード。

### コマンドライン (CLI) で使う
ターミナルから詳細な操作が可能です。

```bash
# 論文の追加 (DOI指定)
python main.py 10.1038/s41586-023-06291-2

# 論文の追加 (PDFファイル指定)
python main.py /path/to/paper.pdf

# 論文の追加 (翻訳なし)
python main.py {DOI} --no-translate

# エクスポート (Nature形式) -> 指定フォルダまたは標準出力へ
python main.py --export citation_key

# エクスポート (BibTeX形式)
python main.py --export citation_key --format bib
```

## ディレクトリ構成
- `modules/`: 各機能のモジュール
- `config/`: 設定関連
- `app.py`: GUIアプリ本体
- `main.py`: CLIエントリーポイント
- `paper-manager.command`: Mac用ランチャー
- `paper-manager.bat`: Windows用ランチャー

## ライセンス
MIT License
