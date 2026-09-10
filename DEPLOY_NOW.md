# 🚀 今すぐデプロイメント実行ガイド

ネタDB を **本番環境に公開するまでの全ステップ**

---

## 📍 現在地

```
✅ ローカル開発環境が完全に動作中
   - Next.js サイト: http://localhost:3001
   - Streamlit 管理画面: http://localhost:8501

⏳ クラウドデプロイメント: 準備完了
```

---

## 🎯 デプロイメント手順（3ステップ）

### ステップ 1️⃣: API キー取得（10～30分）

#### 1.1 YouTube Data API キー
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクト作成 → 名前: `neta-db`
3. **API とサービス** → **ライブラリ** → 「YouTube Data API v3」検索
4. **有効にする** をクリック
5. **認証情報** → **+認証情報を作成** → **API キー**
6. **キーをコピー** → テキストエディタに保存 ⭐

#### 1.2 Claude API キー
1. [Anthropic Console](https://console.anthropic.com) にアクセス
2. **API Keys** をクリック
3. **Create Key** をクリック
4. **キーをコピー** → テキストエディタに保存 ⭐

#### 1.3 Supabase プロジェクト
1. [Supabase](https://supabase.com) にアクセス
2. **新規プロジェクト** をクリック
3. **プロジェクト名**: neta-db
4. **リージョン**: 東京 (ap-northeast-1)
5. **DB パスワード**: 安全なパスワード設定 ⭐
6. プロジェクト作成後、以下をテキストエディタに保存 ⭐
   - Project URL (Settings → API)
   - anon public キー (Settings → API)
   - service_role secret キー (Settings → API)
   - Database 接続文字列 (Settings → Database → Connection Pooling)

#### 1.4 Supabase DDL 実行
1. Supabase ダッシュボード → **SQL Editor**
2. **New Query** をクリック
3. `db/migrations/001_init.sql` の内容をコピー＆ペースト
4. **Run** をクリック
5. ✅ テーブル 15個が作成されたことを確認

---

### ステップ 2️⃣: 自動セットアップ実行（5～15分）

準備ができたら、このコマンドを実行：

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
python setup_interactive.py
```

**スクリプトが行うこと:**
1. API キーを入力
2. Supabase 情報を入力
3. .env ファイルを自動生成
4. Python・Node.js パッケージをインストール
5. 環境検証を自動実行
6. GitHub リモートリポジトリを設定
7. GitHub Secrets を設定するための指示を表示
8. Vercel デプロイのための指示を表示

---

### ステップ 3️⃣: クラウドデプロイメント（5～10分）

#### 3.1 GitHub Secrets 設定

スクリプト完了後、以下の手順で Secrets を設定：

1. GitHub リポジトリを開く
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** で以下を追加：

```
名前: YOUTUBE_API_KEY
値: sk-xxxxxxxx... (コピーペースト)

名前: CLAUDE_API_KEY
値: sk-ant-xxxxxxxx... (コピーペースト)

名前: DATABASE_URL
値: postgresql://postgres:password@db.supabase.co:5432/postgres
```

#### 3.2 Vercel デプロイ

1. [Vercel](https://vercel.com) にアクセス
2. GitHub でサインアップ
3. **Add New...** → **Project**
4. GitHub リポジトリ `neta-db` を選択
5. **Root Directory**: `web/` に設定
6. **Environment Variables** を設定：
   ```
   NEXT_PUBLIC_SUPABASE_URL: https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY: eyJ...
   ```
7. **Deploy** をクリック
8. ✅ URL が払い出される

---

## 📊 デプロイメント チェックリスト

### API キー取得 ✅
- [ ] YouTube API キー取得
- [ ] Claude API キー取得
- [ ] Supabase プロジェクト作成
- [ ] Supabase DDL 実行
- [ ] 接続情報を4つ取得

### セットアップスクリプト実行 ✅
- [ ] `python setup_interactive.py` 実行
- [ ] API キー入力
- [ ] Supabase 情報入力
- [ ] パッケージインストール完了
- [ ] 環境検証成功

### GitHub デプロイ ✅
- [ ] GitHub リポジトリ作成
- [ ] `git push -u origin main` 実行
- [ ] GitHub Secrets 3個設定
- [ ] GitHub Actions 実行開始

### Vercel デプロイ ✅
- [ ] Vercel でリポジトリ連携
- [ ] Environment Variables 2個設定
- [ ] デプロイ実行
- [ ] 公開 URL 確認

---

## ⏱️ 全体の所要時間

```
API キー取得:        10～30分
Supabase セットアップ: 5～10分
スクリプト実行:       5～15分
GitHub 設定:        5分
Vercel デプロイ:     5～10分
───────────────────────
合計:              30～70分
```

---

## 🚨 重要な注意事項

### セキュリティ
- ✅ `.env` は **リポジトリにコミットしない** (.gitignore で除外済み)
- ✅ API キーは **絶対に GitHub に含めない**
- ✅ GitHub Secrets に設定すること（コミット前）
- ✅ Database URL は **service_role キー** を使用

### API クォーター
- YouTube: 10,000単位/日（Phase 1 では 2,200/日で十分）
- Claude: 従量課金（Haiku は低コスト）

---

## 🎯 デプロイメント後

### 自動実行（毎日）
- **08:00 UTC**: `collect.py` (新規動画取得)
- **09:00 UTC**: `classify.py` (LLM分類)
- **23:00 UTC**: `refresh.py` (クリーンアップ)

### 手動操作
1. Streamlit で pending ネタを確認
2. 承認・却下・修正を実行
3. 承認済みネタが公開サイトに表示

### 結果
- 🌐 公開サイト: Vercel で自動公開
- 📺 管理画面: ローカルで操作可能
- 🔄 バッチ: GitHub Actions で自動実行

---

## 💡 便利なコマンド

```bash
# Git の状態確認
git status

# コミット確認
git log --oneline

# リモート確認
git remote -v

# ローカルサーバー再起動
cd web && npm run dev

# Streamlit 再起動
streamlit run admin/app.py

# 検証スクリプト実行
python batch/test_setup.py
```

---

## 📞 トラブルシューティング

### GitHub Actions が失敗した場合
→ **Secrets** が正しく設定されているか確認

### Vercel デプロイが失敗した場合
→ **Root Directory** が `web/` に設定されているか確認

### Streamlit が起動しない場合
```bash
pip install streamlit python-dotenv
streamlit run admin/app.py
```

### Next.js が起動しない場合
```bash
cd web
npm install
npm run dev
```

---

## 🎉 完成！

すべてのステップが完了すると：

```
📱 公開 URL
   https://neta-db.vercel.app

📊 管理画面
   ローカルの Streamlit で操作

🔄 自動更新
   毎日 08:00, 09:00, 23:00 UTC に実行
```

---

## 🚀 今すぐ実行！

```bash
# API キーを取得してから...
python setup_interactive.py

# これですべてが自動設定されます！
```

**Happy Hacking! 🎭**
