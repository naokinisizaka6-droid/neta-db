# ネタDB - YouTube 漫才・コント動画検索サイト

**ビジョン**：YouTubeの公式漫才・コント動画から芸人・形式・設定・賞レースで検索できるデータベース

## プロジェクト構成

```
neta-db/
├── CLAUDE.md                    # このファイル
├── db/
│   └── migrations/
│       └── 001_init.sql         # PostgreSQL DDL (Supabase)
├── batch/
│   ├── yt_client.py             # YouTube Data API クライアント
│   ├── collect.py               # 差分更新・新規動画収集
│   ├── classify.py              # Claude API による LLM 分類
│   ├── refresh.py               # 30日超のリフレッシュ・削除
│   ├── prompts/
│   │   └── classify_v1.md       # LLM プロンプトテンプレート
│   └── requirements.txt          # Python 依存パッケージ
├── admin/
│   └── app.py                   # Streamlit 管理画面
├── web/                         # Next.js 公開サイト
│   ├── package.json
│   ├── next.config.js
│   └── app/
└── .env.example                 # 環境変数テンプレート
```

## 技術スタック

| 役割 | 採用 | 理由 |
|---|---|---|
| 収集・分類 | Python 3.12 + GitHub Actions cron | 無料で十分、Python で十分 |
| DB | Supabase (Postgres + PGroonga) | 日本語全文検索、管理画面代わりの Studio |
| LLM 分類 | Claude API (Haiku/Sonnet) | JSON 出力の確実性 |
| 管理画面 | Streamlit | ローカル実行、簡易で充分 |
| 公開サイト | Next.js App Router + ISR on Vercel | SEO のため生成、Vercel で自動デプロイ |

## データモデル（3層設計）

### A. 自動データ（無期限保持）
- `comedians`, `comedian_members`: 芸人・メンバー基本情報
- `channels`: チャンネル（ホワイトリスト）
- `contests`, `contest_editions`, `contest_entries`: 賞レース
- `neta_works`: ネタ作品
- `performances`: パフォーマンス（どの動画の何秒～何秒か）
- `tags`, `neta_work_tags`: タグ体系

### B. YouTube API データ（30日ルール）
- `yt_channels`, `yt_videos`: API メタデータ
- `fetched_at` が 25日超 → 50件ずつ `videos.list` で更新
- 更新時に `unavailable_at` なら削除・非公開へ

### C. LLM 派生データ（申請承認後のみ公開）
- `llm_classifications`: 分類結果の生 JSON
- タグ・パフォーマンス候補 → 人手で承認後に A に反映

## 処理パイプライン

```
[GitHub Actions 日次 cron]
   ↓
   ├─ collect.py  → YouTube Data API → yt_channels, yt_videos
   ├─ classify.py → Claude API → llm_classifications
   └─ refresh.py  → 25日超の yt_* を更新・消去、動画を非公開へ
                ↓
        Supabase (Postgres + PGroonga)
           ↓                      ↓
    [Streamlit 管理画面]    [Next.js 公開サイト]
     レビュー・承認・統合    承認済みデータのみ表示
```

## フェーズ別ロードマップ

| フェーズ | 期間 | 内容 | 完了条件 |
|---|---|---|---|
| Phase 0 | ～2週間 | API 申請、初期ネタ 500件、LLM 精度測定 | 承認済みネタ 500件で精度測定済み |
| Phase 1 | ～1.5ヶ月 | 公開サイト＋ M-1・ロングランコント等 | 承認済みネタ 2,000件で公開 |
| Phase 2 | 公開後 | ユーザーフィードバック対応、オフィシャル提携 | 提携確定 |
| Phase 3 | 権利許諾後 | 公開字幕起こし・小説検索対応 | 1社以上 |

## API クォーター（約 10,000単位/日 ベース）

Phase 1想定（承認済み 200ch、動画 2,000本）

| 処理 | 計算 | 単位/日 |
|---|---|---|
| 差分更新 playlistItems | 200ch × 1回 | 200 |
| 新規 videos.list | 新規200本 ÷ 50 | 4 |
| リフレッシュ videos.list | 2000本 ÷ 25日 ÷ 50 | 16 |
| チャンネル情報更新 | 200ch ÷ 25日 ÷ 50 | 1 |
| 新規チャンネル検出 search.list | 20回 × 100 | 2,000 |
| **合計** | | **約 2,200** |

検出は search のみで、単位は少なめ。本体は「200ch × 平均 500本」で約 4,000単位。1日に収まる。

## 制約・ポリシー

| 制約 | 内容 | 設計への反映 |
|---|---|---|
| 著作権 | ネタは言語の著作物（実演や書き起こし公開は複製・公開配信） | 小説は無表示・エントリー説明は自分の言葉で句読点なし |
| YouTube 利用規約 | 動画・音声のダウンロード禁止 | 取得は Data API のメタデータのみ、映像は公式埋め込みプレイヤー |
| API (30日ルール) | API データ（タイトル・概要本文・統計）は 30日以前に更新・削除 | API データは `yt_` テーブルに隔離、25日周期で自動リフレッシュ |
| API (派生データ禁止) | 標準では API データから独自統計・問題を作ってはいけない | 申請・修正条項の承認まで人手みたぎ |
| API (表示ルール) | 独自データは YouTube 由来でないと表示 | タグ等に「当サイト独自の問題」と表記 |
| 無断転載の混入 | 検索で放ったTV番組の違法アップ混むら | チャンネルのホワイトリスト制で申請ひ確認済みch の動画のみ対象 |

## セットアップ

1. リポジトリのクローン・.env 設定
2. Supabase プロジェクト作成 → `db/migrations/001_init.sql` 実行
3. YouTube Data API キー取得 → `.env` に設定
4. Claude API キー取得 → `.env` に設定
5. ローカルで `batch/` と `admin/` を開発・テスト
6. Next.js 開発サーバー起動 (`npm run dev`)
7. GitHub Actions で自動実行パイプライン設定

## 開発ガイドライン

- **Python 環境**: `python -m venv venv && source venv/bin/activate && pip install -r batch/requirements.txt`
- **DB 管理**: Supabase Studio でブラウザから操作、マイグレーション必須 (DDL は `001_init.sql` に集約)
- **LLM プロンプト**: `batch/prompts/classify_v1.md` で管理、バージョン管理
- **デバッグ**: 本番前に `admin/app.py` で Streamlit 上で承認・修正、精度測定

## 今後の検討事項

- **Meilisearch への移行**: 規模が大きくなったら PGroonga から切り替え
- **字幕起こし**: 権利許諾後に実装
- **ユーザー投稿**: Phase 2 以降の検討
