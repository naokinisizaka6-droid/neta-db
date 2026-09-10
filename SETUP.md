# セットアップガイド

ネタDB をセットアップするための手順を記載します。

## 📋 事前準備

以下を準備してください：
- GitHub アカウント
- Supabase アカウント（[https://supabase.com](https://supabase.com)）
- Google Cloud プロジェクト（YouTube Data API 用）
- Anthropic アカウント（Claude API 用）
- Vercel アカウント（デプロイ用）

---

## ステップ 1：Supabase プロジェクト作成

### 1.1 Supabase にサインイン
1. [https://supabase.com](https://supabase.com) にアクセス
2. GitHub アカウントでサインアップ
3. 新規プロジェクトを作成

### 1.2 プロジェクト情報
- **Project name**: `neta-db` (任意)
- **Database password**: 安全なパスワードを設定（メモしておく）
- **Region**: 東京 (ap-northeast-1) を推奨

### 1.3 DB スキーマを実行
プロジェクト作成後、SQL Editor で以下を実行：

1. [Supabase ダッシュボード](https://supabase.com/dashboard) にログイン
2. 作成したプロジェクトを選択
3. 左サイドバー → **SQL Editor**
4. **New Query** ボタンを押す
5. `db/migrations/001_init.sql` の内容をコピーペースト
6. **Run** ボタンを押す

✅ スキーマが正常に作成されたら、**Settings** → **API** から接続情報を取得します。

### 1.4 接続情報を取得
1. **Settings** → **API** を開く
2. 以下をメモ：
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role secret** (SQL EditorやBatchから使用)

---

## ステップ 2：YouTube Data API キーの取得

### 2.1 Google Cloud プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. **新しいプロジェクト** を作成
3. プロジェクト名を `neta-db` と設定

### 2.2 YouTube Data API を有効化
1. **API とサービス** → **ライブラリ** を開く
2. 検索: `YouTube Data API v3`
3. **有効にする** を押す

### 2.3 API キー作成
1. **API とサービス** → **認証情報** を開く
2. **+認証情報を作成** → **API キー** を選択
3. 表示されたキーをメモ → `YOUTUBE_API_KEY`

### 2.4 API クォータを確認（重要）
1. **YouTube Data API v3** を選択
2. **クォータ** タブで以下を確認：
   - Queries per day: **10,000** (デフォルト)
   
必要に応じて Google に申請できます（Phase 1 では 10,000/日で十分）。

---

## ステップ 3：Claude API キーの取得

### 3.1 Anthropic プラットフォームにアクセス
1. [https://console.anthropic.com](https://console.anthropic.com) にアクセス
2. アカウント作成またはサインイン

### 3.2 API キー生成
1. **API Keys** を開く
2. **Create Key** ボタンを押す
3. キーをメモ → `CLAUDE_API_KEY`

### 3.3 利用可能なモデル確認
- **Haiku** (claude-haiku-4-5-20251001): 初期分類用
- **Sonnet** (claude-sonnet-5): 精度検証用

---

## ステップ 4：ローカル環境設定

### 4.1 .env ファイルを作成
```bash
cd neta-db
cp .env.example .env
```

### 4.2 .env に値を入力
```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Claude API
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Next.js 用
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

⚠️ `.env` をリポジトリにコミットしないこと（`.gitignore` で除外済み）

### 4.3 Python 環境セットアップ
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r batch/requirements.txt
```

### 4.4 Node.js 環境セットアップ
```bash
cd web
npm install
cd ..
```

---

## ステップ 5：ローカルテスト

### 5.1 Streamlit 管理画面テスト
```bash
streamlit run admin/app.py
# ブラウザで http://localhost:8501 を開く
```

確認項目：
- ダッシュボード表示（統計情報）
- pending パフォーマンス表示（最初は0件）

### 5.2 Next.js 開発サーバーテスト
```bash
cd web
npm run dev
# ブラウザで http://localhost:3000 を開く
```

確認項目：
- ホームページ表示
- 検索ボックス機能
- レイアウト表示

### 5.3 バッチスクリプトテスト

**テスト用チャンネル登録**

Supabase の SQL Editor で以下を実行：

```sql
-- テスト用の芸人を作成
INSERT INTO comedians (slug, name, unit_type, is_active)
VALUES ('test-group', 'テストグループ', 'combi', true);

-- テスト用のチャンネルを作成
INSERT INTO channels (channel_id, comedian_id, kind, status, uploads_playlist_id)
VALUES (
  'UC_test123',
  (SELECT id FROM comedians WHERE slug = 'test-group'),
  'comedian',
  'approved',
  'UU_test123'  -- ダミーのプレイリストID
);
```

**collect.py テスト**

```bash
python batch/collect.py
# ログを確認：「Collection Statistics」が表示されることを確認
```

**classify.py テスト**

```bash
python batch/classify.py
# ログを確認：「Classification Statistics」が表示されることを確認
```

**refresh.py テスト**

```bash
python batch/refresh.py
# ログを確認：「Refresh & Cleanup Statistics」が表示されることを確認
```

---

## ステップ 6：GitHub リモート設定

### 6.1 GitHub にリポジトリ作成
1. [GitHub](https://github.com/new) で新規リポジトリ作成
2. リポジトリ名: `neta-db`
3. 説明: `YouTube 漫才・コント検索サイト`
4. **Create repository**

### 6.2 リモートを追加
```bash
cd c:/Users/User/Desktop/youtube切り抜き/neta-db
git remote add origin https://github.com/your-username/neta-db.git
git branch -M main
git push -u origin main
```

### 6.3 GitHub Secrets 設定
1. リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** で以下を追加：

| Secret 名 | 値 |
|---|---|
| `YOUTUBE_API_KEY` | YouTube API キー |
| `CLAUDE_API_KEY` | Claude API キー |
| `DATABASE_URL` | Supabase 接続文字列 |

接続文字列例：
```
postgresql://postgres:password@db.supabase.co:5432/postgres
```

Supabase の **Settings** → **Database** → **Connection Pooling** から取得できます。

---

## ステップ 7：GitHub Actions 動作確認

### 7.1 ワークフロー実行
1. リポジトリ → **Actions** タブ
2. **Collect Videos** を選択
3. **Run workflow** → **Run workflow** を押す

### 7.2 実行ログ確認
ワークフロー実行後、ログを確認：
- ✅ `✅ Video collection completed successfully` が表示されたら OK
- ❌ エラーが出た場合は Secrets 設定を確認

---

## ステップ 8：Vercel デプロイ準備

### 8.1 Vercel にログイン
1. [https://vercel.com](https://vercel.com) にアクセス
2. GitHub でサインアップ

### 8.2 新規プロジェクト作成
1. **Add New...** → **Project**
2. GitHub リポジトリ `neta-db` を選択
3. **Root Directory** を `web/` に設定
4. **Environment Variables** で以下を設定：
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5. **Deploy** ボタンを押す

### 8.3 デプロイ完了
URL が払い出されたら、公開サイトにアクセス可能です。

---

## 🔍 トラブルシューティング

### Supabase 接続エラー
```
FATAL: PAM authentication failed
```

**原因**: DB パスワードが間違っている
**解決**: Supabase ダッシュボード → **Settings** → **Database** でパスワードをリセット

### YouTube API クォータ超過
```
quotaExceeded: The request cannot be completed because you have exceeded your quota.
```

**原因**: 日次クォーター (10,000単位) を超過
**解決**: 
- 翌日を待つ（UTC 00:00 にリセット）
- Google に申請して上限を引き上げる

### Claude API エラー
```
401 Unauthorized: Invalid API key
```

**原因**: API キーが間違っている
**解決**: Anthropic コンソールで API キーを確認・再生成

### Streamlit が起動しない
```
ModuleNotFoundError: No module named 'streamlit'
```

**原因**: 依存パッケージがインストールされていない
**解決**: 
```bash
pip install -r batch/requirements.txt
streamlit run admin/app.py
```

---

## ✅ セットアップチェックリスト

- [ ] Supabase プロジェクト作成
- [ ] DDL スクリプト実行
- [ ] YouTube API キー取得
- [ ] Claude API キー取得
- [ ] `.env` ファイル設定
- [ ] Python 環境セットアップ
- [ ] Node.js 環境セットアップ
- [ ] Streamlit ローカルテスト
- [ ] Next.js ローカルテスト
- [ ] バッチスクリプトテスト
- [ ] GitHub リモート設定
- [ ] GitHub Secrets 設定
- [ ] GitHub Actions 動作確認
- [ ] Vercel デプロイ

---

## 📞 サポート

問題が発生した場合：
1. [トラブルシューティング](#-トラブルシューティング) を確認
2. CLAUDE.md の制約・ポリシーセクションを確認
3. GitHub Issues で報告（対応予定）

Happy Hacking! 🚀
