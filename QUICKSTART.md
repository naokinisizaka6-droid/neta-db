# 🚀 クイックスタートガイド

ネタDB を最短で動かすためのガイドです。

## ステップ 0: 前提条件

以下をまだ準備していない場合は、先に取得してください：

### 1️⃣ YouTube Data API キー
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクト作成
3. **API とサービス** → **ライブラリ** → 「YouTube Data API v3」
4. **有効にする** を押す
5. **認証情報** → **+認証情報を作成** → **API キー** を選択
6. **キーをコピー** → メモしておく ⭐

### 2️⃣ Claude API キー
1. [Anthropic Console](https://console.anthropic.com) にアクセス
2. **API Keys** → **Create Key** を押す
3. キーをコピー → メモしておく ⭐

### 3️⃣ Supabase プロジェクト
1. [Supabase](https://supabase.com) にアクセス
2. **新規プロジェクト** を作成
3. リージョン: **東京** を選択
4. プロジェクト作成後、以下の情報をコピー → メモしておく ⭐
   - **Project URL**
   - **anon public キー**
   - **service_role secret キー**
   - **接続文字列** (Settings → Database → Connection Pooling)

---

## ステップ 1: セットアップスクリプトを実行

準備ができたら、このコマンドを実行してください：

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
python setup_interactive.py
```

### スクリプトが実行する内容：

✅ **環境変数設定** (.env ファイル作成)
✅ **Python パッケージインストール** (batch/requirements.txt)
✅ **Node.js パッケージインストール** (web/package.json)
✅ **環境検証** (データベース接続確認)
✅ **GitHub セットアップ** (リモートリポジトリ設定)
✅ **GitHub Secrets 設定** (API キー管理)
✅ **Vercel デプロイ準備** (ホスティング設定)

---

## ステップ 2: インタラクティブセットアップを進める

スクリプト実行後、画面の指示に従って以下を入力します：

### フェーズ 1: API キー入力
```
YouTube Data API キーを入力: sk-xxxxxxxx...
Claude API キーを入力: sk-ant-xxxxxxxx...
使用モデル [claude-haiku-4-5-20251001]:
```

### フェーズ 2: Supabase 情報入力
```
Supabase URL (例: https://xxx.supabase.co): https://xxx.supabase.co
Anon キーを入力: eyJhbGc...
Service Role キーを入力: eyJhbGc...
接続文字列を入力: postgresql://postgres:password@xxx.supabase.co:5432/postgres
```

### フェーズ 3: 依存パッケージインストール
```
Python パッケージをインストールしますか？ [Y/n]: y
Node.js パッケージをインストールしますか？ [Y/n]: y
```

### フェーズ 4: 環境検証
```
検証スクリプトを実行しますか？ [Y/n]: y
```

### フェーズ 5: GitHub セットアップ
```
GitHub にリポジトリを作成してください
1. https://github.com/new にアクセス
2. Repository name: neta-db
3. Create repository ボタンを押す

GitHub リポジトリを作成しましたか？ [Y/n]: y
リポジトリ URL を入力: https://github.com/username/neta-db.git
```

### フェーズ 6: GitHub Secrets 設定
```
GitHub リポジトリ → Settings → Secrets で以下を追加：
- YOUTUBE_API_KEY: sk-xxxxxxxx...
- CLAUDE_API_KEY: sk-ant-xxxxxxxx...
- DATABASE_URL: postgresql://...

GitHub Secrets 設定完了しましたか？ [Y/n]: y
```

### フェーズ 7: Vercel デプロイ
```
https://vercel.com にアクセス
→ 「Add New...」→ 「Project」
→ GitHub リポジトリ neta-db を選択
→ Root Directory: web/
→ Environment Variables を設定

Vercel デプロイを完了しましたか？ [Y/n]: y
```

---

## ステップ 3: ローカルで動作確認

セットアップ完了後、ローカルで動作確認できます：

### 📺 管理画面を起動
```bash
streamlit run admin/app.py
# http://localhost:8501 でアクセス
```

### 🌐 公開サイトを起動
```bash
cd web
npm run dev
# http://localhost:3000 でアクセス
```

### 🔄 バッチ処理を実行
```bash
# 差分更新
python batch/collect.py

# LLM 分類
python batch/classify.py

# リフレッシュ・削除
python batch/refresh.py
```

---

## ✅ セットアップ完了チェックリスト

- [ ] YouTube API キーを取得
- [ ] Claude API キーを取得
- [ ] Supabase プロジェクトを作成
- [ ] `setup_interactive.py` を実行
- [ ] API キーを入力
- [ ] Supabase 情報を入力
- [ ] Python・Node.js パッケージをインストール
- [ ] 環境検証に成功
- [ ] GitHub にリポジトリをプッシュ
- [ ] GitHub Secrets を設定
- [ ] GitHub Actions が実行開始
- [ ] Vercel にデプロイ
- [ ] 管理画面が起動
- [ ] 公開サイトが起動

---

## 🔧 トラブルシューティング

### ❌ "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### ❌ "git remote already exists"
```bash
git remote remove origin
# その後、スクリプトを再実行
```

### ❌ Streamlit が起動しない
```bash
pip install streamlit
streamlit run admin/app.py
```

### ❌ npm install に失敗
```bash
cd web
npm install --force
```

---

## 📞 詳細情報

- **詳細セットアップ**: [SETUP.md](SETUP.md)
- **技術仕様**: [CLAUDE.md](CLAUDE.md)
- **プロジェクト概要**: [README.md](README.md)
- **実装サマリー**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🚀 次のステップ

1. **API 申請・承認待機** (推定 1週間)
   - YouTube Data API の API 申請がある場合

2. **初期データ 500 件収集** (推定 1週間)
   - `collect.py` で差分更新
   - `classify.py` で LLM 分類
   - 管理画面で承認

3. **LLM 精度測定** (推定 3～5日)
   - 承認済みデータで精度を測定
   - 必要に応じてプロンプト調整

4. **公開準備完了！**
   - Vercel で自動公開
   - GitHub Actions で自動更新

---

Happy Hacking! 🎭
