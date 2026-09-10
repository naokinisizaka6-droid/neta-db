# ネタDB - YouTube 漫才・コント検索サイト

YouTubeの公式漫才・コント動画から芸人・形式・設定・賞レースで検索できるデータベースサイト。

## 🎯 ビジョン

YouTubeには多数の公式漫才・コント動画がアップロードされているが、YouTube本体の検索では：
- 類似のキーワードが多く、漫才・コントの本編を見つけづらい
- 形式（漫才/コント/ピン芸）での分類がない
- 設定（コンビニ、デパート、インタビューなど）での検索ができない
- 賞レース（M-1など）と映像の対応がわかりにくい

**ネタDB** はこれらの課題を解決し、「あのネタ、もう一度見たい！」「こんな設定のコント、他にある？」という要望に応えます。

## 📋 機能

- **漫才・コント・ピン芸の形式分類**
- **設定タグ** (place, relation, job, theme, style)
- **賞レース対応** (M-1、キング・オブ・コント等)
- **公式チャンネルのホワイトリスト管理** (無断転載を排除)
- **30日ルール遵守** (YouTube APIメタデータの自動更新・削除)

## 🛠️ 技術スタック

| 役割 | 採用 |
|---|---|
| バッチ処理 | Python 3.12 + GitHub Actions |
| DB | Supabase (PostgreSQL + PGroonga) |
| LLM分類 | Claude API (Haiku/Sonnet) |
| 管理画面 | Streamlit |
| 公開サイト | Next.js 14 (App Router + ISR) |
| ホスティング | Vercel |

## 📁 ディレクトリ構成

```
neta-db/
├── CLAUDE.md                    # プロジェクト設計書
├── db/
│   └── migrations/
│       └── 001_init.sql         # PostgreSQL DDL
├── batch/
│   ├── yt_client.py             # YouTube API クライアント
│   ├── collect.py               # 差分更新スクリプト
│   ├── classify.py              # LLM 分類スクリプト
│   ├── refresh.py               # リフレッシュ・削除スクリプト
│   ├── prompts/
│   │   └── classify_v1.md       # LLM プロンプト
│   └── requirements.txt
├── admin/
│   └── app.py                   # Streamlit 管理画面
├── web/                         # Next.js 公開サイト
│   ├── app/
│   ├── lib/
│   └── package.json
├── .github/
│   └── workflows/
│       ├── collect.yml          # 毎日 08:00 UTC
│       ├── classify.yml         # 毎日 09:00 UTC
│       └── refresh.yml          # 毎日 23:00 UTC
└── .env.example
```

## 🚀 セットアップ手順

### 前提条件
- Python 3.12 以上
- Node.js 18 以上
- Supabase アカウント
- YouTube Data API キー
- Claude API キー

### 1. リポジトリクローン
```bash
git clone <repository-url>
cd neta-db
```

### 2. 環境変数設定
```bash
cp .env.example .env
# .env を編集して以下を設定：
# - YOUTUBE_API_KEY
# - CLAUDE_API_KEY
# - DATABASE_URL (Supabase)
```

### 3. DB初期化
```bash
# Supabase のSQL Editor で以下を実行：
# db/migrations/001_init.sql の内容をコピー＆ペースト
```

### 4. Python 環境構築
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r batch/requirements.txt
```

### 5. 管理画面を実行（ローカルテスト）
```bash
streamlit run admin/app.py
# http://localhost:8501 でアクセス
```

### 6. Next.js 開発サーバー起動
```bash
cd web
npm install
npm run dev
# http://localhost:3000 でアクセス
```

### 7. GitHub Secrets 設定
リポジトリの Settings → Secrets に以下を追加：
- `YOUTUBE_API_KEY`
- `CLAUDE_API_KEY`
- `DATABASE_URL`

## 📊 データフロー

```
[GitHub Actions 毎日 cron]
   ↓
   ├─ 08:00 UTC: collect.py  → YouTube API → yt_videos
   ├─ 09:00 UTC: classify.py → Claude API → llm_classifications
   └─ 23:00 UTC: refresh.py  → 古いデータ更新・削除
                ↓
        Supabase (Postgres)
           ↓                      ↓
    [Streamlit 管理画面]    [Next.js 公開サイト]
     レビュー・承認・統合    承認済みデータ表示
```

## 🔄 処理パイプライン

### 1. collect.py (差分更新)
- 承認済みチャンネルから新規動画を取得
- `last_seen_published_at` より新しい動画のみを処理
- YouTube `videos.list` API で詳細情報を取得
- `yt_videos` に保存

**実行**: 毎日 08:00 UTC

### 2. classify.py (LLM分類)
- `pending` ステータスのパフォーマンスを取得
- Claude API (Haiku 4.5) で分類
- `llm_classifications` に結果を保存
- 新規タグ提案を `tags` テーブルに追加

**実行**: 毎日 09:00 UTC

### 3. refresh.py (リフレッシュ・削除)
- 25日超の `fetched_at` を持つ動画を更新
- 削除・非公開化された動画を `unavailable_at` に記録
- 30日超の古いデータを削除

**実行**: 毎日 23:00 UTC

## 📝 API クォーター予算

Phase 1 (承認済み 200ch、動画 2,000本) での日次消費：

| 処理 | 単位/日 |
|---|---|
| 差分更新 playlistItems | 200 |
| 新規 videos.list | 4 |
| リフレッシュ videos.list | 16 |
| チャンネル更新 | 1 |
| 新規チャンネル検出 search | 2,000 |
| **合計** | **約 2,200** |

10,000単位/日の制限内に収まる

## 🎬 UI/UX

### 公開サイト
- `/` - ホーム（検索窓、ナビゲーション）
- `/search?q=` - 横断検索
- `/geinin/[slug]` - 芸人ページ
- `/neta/[id]` - ネタ詳細
- `/tag/[slug]` - タグ別一覧
- `/contest/[slug]/[year]` - 賞レース一覧

### 管理画面 (Streamlit)
- pending パフォーマンス一覧
- 確信度の低い順に表示
- 動画プレイヤー (開始・終了秒指定)
- 承認・却下・修正機能

## ⚖️ 著作権・規約

- **YouTube 利用規約**: 動画・音声ダウンロードなし、メタデータのみ保存
- **30日ルール**: API メタデータは 25日超で更新・削除
- **ホワイトリスト制**: 申請・承認されたチャンネルのみ対象
- **設定説明文**: 当サイト独自の説明は「当サイト独自」と表記

## 🐛 既知の制限事項

- 字幕起こし機能は Phase 3 (権利許諾後)
- ユーザー投稿は Phase 2 以降の検討
- Meilisearch への移行は規模に応じて検討

## 🤝 貢献

見落としているネタ、誤分類、改善提案は以下までお知らせください：

- X (Twitter): [@neta_db](https://twitter.com/neta_db) (予定)
- メール: contact@neta-db.example.com (予定)
- GitHub Issues

## 📄 ライセンス

当プロジェクトはこちらのライセンスに従います。
（詳細は LICENSE ファイルを参照）

## 🙏 謝辞

- YouTube Data API を提供する Google
- Claude API を提供する Anthropic
- Supabase コミュニティ
