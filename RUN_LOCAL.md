# 🚀 ローカル開発サーバー起動ガイド

ネタDB をローカルで動作させるための手順です。

## 準備完了！ ✅

以下のコンポーネントがローカルで動作可能です：

- ✅ **Next.js 公開サイト** (npm install 完了)
- ✅ **Streamlit 管理画面** (Python パッケージ準備中)
- ✅ **バッチ処理スクリプト** (すぐ実行可能)

---

## 🌐 Next.js 公開サイトを起動

### ステップ 1: ターミナルを開く
```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db\web
```

### ステップ 2: 開発サーバーを起動
```bash
npm run dev
```

### ステップ 3: ブラウザでアクセス
```
http://localhost:3000
```

### 画面に表示されるもの：
- 🎭 ネタDB ホームページ
- 🔍 検索ボックス
- 👥 芸人から探す
- 🏷️ 設定から探す
- 🏆 賞レースから探す

---

## 📺 Streamlit 管理画面を起動

### ステップ 1: 別のターミナルを開く
```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
```

### ステップ 2: 管理画面を起動
```bash
streamlit run admin/app.py
```

### ステップ 3: ブラウザでアクセス
```
http://localhost:8501
```

### 画面に表示されるもの：
- 📊 リアルタイム統計ダッシュボード
- ✅ Pending ネタ一覧
- 📹 YouTube プレイヤー（スクリーンショット用）
- 🎯 承認・却下・修正ボタン

---

## 🔄 バッチ処理スクリプトを実行

### ⚠️ 注意: これらは実際のデータベースに接続します
実行前に `.env` ファイルで **Supabase 接続情報を設定** してください。

### 差分更新を実行
```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
python batch/collect.py
```

### LLM 分類を実行
```bash
python batch/classify.py
```

### リフレッシュを実行
```bash
python batch/refresh.py
```

---

## 🎯 ローカルテストの流れ

### 推奨される手順：

1. **🌐 Next.js で サイトデザイン確認** (5分)
   ```bash
   npm run dev
   # http://localhost:3000 でホームページ確認
   ```

2. **📺 Streamlit で 管理画面デザイン確認** (5分)
   ```bash
   streamlit run admin/app.py
   # http://localhost:8501 で管理画面確認
   ```

3. **✅ セットアップスクリプトを実行**
   ```bash
   python setup_interactive.py
   # API キー・Supabase 情報を入力
   ```

4. **🔄 バッチ処理を実行**
   ```bash
   python batch/test_setup.py     # 環境検証
   python batch/collect.py         # 初期データ取得
   python batch/classify.py        # LLM 分類
   ```

5. **📺 管理画面で レビュー** 
   - pending ネタを確認
   - 承認・却下操作

6. **🌐 Next.js で 公開サイト確認**
   - 承認済みネタが表示されることを確認

---

## 🛠️ 開発中の便利なコマンド

### Next.js
```bash
cd web

# 開発サーバー起動
npm run dev

# ビルド実行
npm run build

# 本番サーバー起動
npm start

# TypeScript チェック
npm run lint
```

### Python
```bash
# 検証スクリプト実行
python batch/test_setup.py

# 対話型 Python シェル
python -i batch/yt_client.py

# テストスクリプト実行
python -m pytest batch/ (テスト追加時)
```

### Git
```bash
# 変更状況確認
git status

# 変更をコミット
git add .
git commit -m "description"

# リモートにプッシュ
git push origin main
```

---

## 🔗 URL リファレンス

| サービス | URL | 説明 |
|---|---|---|
| **Next.js** | http://localhost:3000 | 公開サイト（フロントエンド） |
| **Streamlit** | http://localhost:8501 | 管理画面 |
| **GitHub** | https://github.com/your-username/neta-db | リモートリポジトリ |
| **Supabase** | https://supabase.com/dashboard | DB 管理画面 |
| **Vercel** | https://vercel.com/dashboard | デプロイ管理 |

---

## 📊 ローカルテスト チェックリスト

- [ ] `npm install` 完了
- [ ] `npm run dev` でサーバー起動
- [ ] http://localhost:3000 でホームページ表示
- [ ] 検索ボックスが表示される
- [ ] ナビゲーションメニューが動作
- [ ] `streamlit run admin/app.py` でダッシュボード起動
- [ ] http://localhost:8501 で管理画面表示
- [ ] 統計情報が表示される

---

## ⚠️ トラブルシューティング

### ❌ "npm: command not found"
Node.js がインストールされていません
```bash
# Windows: chocolatey を使用
choco install nodejs

# または、Node.js 公式サイトからダウンロード
https://nodejs.org/
```

### ❌ "Port 3000 is already in use"
別のプロセスが Port 3000 を使用中です
```bash
# 別のポートで起動
npm run dev -- --port 3001
```

### ❌ "Module not found"
依存パッケージが不足しています
```bash
npm install
```

### ❌ Streamlit が起動しない
```bash
pip install streamlit
pip install python-dotenv
```

---

## 🎯 次のステップ

1. ✅ ローカルでサイトを確認
2. 📝 `setup_interactive.py` でセットアップ完了
3. 🚀 GitHub にプッシュ
4. 📊 GitHub Actions で自動実行確認
5. 🌐 Vercel で公開サイト公開

---

## 💡 開発Tips

### VSCode で開発する場合
```bash
cd web
code .
```

### Git で変更を確認する場合
```bash
git diff
git status
```

### API キー を .env に保存する場合
```bash
# web/.env.local に設定
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

🎭 Happy Hacking!
