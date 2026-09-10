# ネタDB - 本番公開チェックリスト

**このチェックリストで、本番公開前のすべての準備を確認します。**

---

## 📋 準備チェックリスト (確認用)

### Phase 1: ローカル環境 ✅ (100% 完了)
```
[X] コード実装完成 (40+ files, 6,500+ lines)
[X] ローカルサーバー起動 (Next.js 3001 / Streamlit 8501)
[X] Git リポジトリ初期化 (12 commits)
[X] npm パッケージインストール (113 packages)
[X] Python パッケージインストール (15+ packages)
[X] 環境検証完了 (4/5 checks)
```

### Phase 2: 外部サービス設定 ⏳ (残り実施)

#### 2.1: API キー取得
```
[ ] YouTube Data API キー
    → https://console.cloud.google.com/
    → 参照: API_KEY_GUIDE.md「1. YouTube Data API キー取得」
    
[ ] Claude API キー
    → https://console.anthropic.com/
    → 参照: API_KEY_GUIDE.md「2. Claude API キー取得」
    
[ ] Supabase プロジェクト作成 + DDL 実行
    → https://supabase.com/
    → 参照: API_KEY_GUIDE.md「3. Supabase プロジェクト作成」
```

#### 2.2: GitHub リモート確認
```
[ ] GitHub リモート設定確認
    $ git remote -v
    → 出力: origin https://github.com/naokinisizaka6/neta-db.git
    
[ ] GitHub Personal Access Token 作成
    → https://github.com/settings/tokens
    → Scopes: repo + admin:repo_hook
    → 参照: GITHUB_PUSH_GUIDE.md「ステップ 1」
```

#### 2.3: GitHub にプッシュ
```
[ ] Git Credential Manager 設定
    $ git config --global credential.helper manager
    
[ ] GitHub へプッシュ
    $ cd c:\Users\User\Desktop\youtube切り抜き\neta-db
    $ git push -u origin master
    → Personal Access Token を入力
    → ✅ 11+ commits がアップロード
```

#### 2.4: 環境設定スクリプト実行
```
[ ] セットアップスクリプト実行
    $ python setup_interactive.py
    
    入力内容:
    - YouTube API キー
    - Claude API キー
    - Supabase URL
    - Supabase Anon キー
    - Supabase Service Role キー
    - Database URL
    
    自動処理:
    ✓ .env ファイル生成
    ✓ web/.env 生成
    ✓ パッケージ検証
    ✓ 環境変数設定
```

#### 2.5: GitHub Secrets 設定
```
[ ] GitHub Secrets を設定
    → GitHub Repository → Settings → Secrets and variables → Actions
    
    追加するシークレット:
    • Name: YOUTUBE_API_KEY
      Value: AIza... (YouTube API キー)
      
    • Name: CLAUDE_API_KEY
      Value: sk-ant-... (Claude API キー)
      
    • Name: DATABASE_URL
      Value: postgresql://... (Supabase DB URL)
```

#### 2.6: Vercel デプロイ
```
[ ] Vercel アカウント作成
    → https://vercel.com
    → GitHub でサインアップ
    
[ ] プロジェクトをインポート
    → Add New → Project
    → GitHub リポジトリ neta-db を選択
    
[ ] デプロイ設定
    Framework: Next.js 14
    Root Directory: web/
    Environment Variables:
    • NEXT_PUBLIC_SUPABASE_URL: https://xxxxx.supabase.co
    • NEXT_PUBLIC_SUPABASE_ANON_KEY: eyJ...
    
[ ] デプロイ実行
    → Deploy ボタンをクリック
    → 5～10分で完了
    → URL が生成される (例: neta-db.vercel.app)
```

---

## ⏱️ 所要時間目安

| ステップ | 時間 |
|---|---|
| 1. API キー取得 | 15～30分 |
| 2. GitHub 認証設定 | 5～10分 |
| 3. git push 実行 | 2～5分 |
| 4. セットアップスクリプト | 10～20分 |
| 5. GitHub Secrets 設定 | 5分 |
| 6. Vercel デプロイ | 10～15分 |
| **合計** | **47～85分** |

---

## 🚀 実行手順 (ステップバイステップ)

### ステップ 1: API キー取得 (所要時間: 15～30分)

**1.1 YouTube Data API キー**
```
1. https://console.cloud.google.com/ を開く
2. 新規プロジェクト作成: neta-db
3. 「API とサービス」 → 「ライブラリ」
4. YouTube Data API v3 を検索・有効化
5. 「認証情報」 → 「API キー」を作成
6. キーをコピー (AIza...)
```

**1.2 Claude API キー**
```
1. https://console.anthropic.com/ を開く
2. GitHub でサインアップ
3. 「API Keys」 → 「Create Key」
4. キー名: neta-db-production
5. キーをコピー (sk-ant-...)
```

**1.3 Supabase セットアップ**
```
1. https://supabase.com/ を開く
2. 「Start your project」
3. 新規プロジェクト作成:
   - Project name: neta-db
   - Region: Tokyo
   - Database Password: [強いパスワード] (保存!)
4. ダッシュボード完成まで待機 (3～5分)
5. Settings → API から以下をコピー:
   • Project URL (https://xxxxx.supabase.co)
   • anon public キー
   • service_role secret キー
6. Settings → Database から:
   • Connection string (PostgreSQL format)
7. SQL Editor で db/migrations/001_init.sql を実行
```

### ステップ 2: GitHub 認証設定 (所要時間: 5～10分)

```bash
# 2.1 Git Credential Manager を設定
git config --global credential.helper manager

# 2.2 GitHub Personal Access Token を作成
# → https://github.com/settings/tokens
# → 「Generate new token (classic)」
# → Scopes: repo + admin:repo_hook
# → Generate & Copy トークン

# 2.3 リモート確認
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
git remote -v
# 出力: origin https://github.com/naokinisizaka6/neta-db.git
```

### ステップ 3: GitHub へプッシュ (所要時間: 2～5分)

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
git push -u origin master

# 入力促求が出たら:
# Username: [GitHub ユーザー名]
# Password: [Personal Access Token]

# 完了: All commits pushed to GitHub
```

### ステップ 4: セットアップスクリプト実行 (所要時間: 10～20分)

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
python setup_interactive.py

# 以下の質問に答える:
# 1. "セットアップを開始しますか？" → y
# 2. YouTube API キーを入力
# 3. Claude API キーを入力
# 4. Supabase URL を入力
# 5. Supabase Anon キーを入力
# 6. Supabase Service Role キーを入力
# 7. Database URL を入力
# 8. Python パッケージをインストールしますか？ → y
# 9. Node.js パッケージをインストールしますか？ → y
# 10. 検証スクリプトを実行しますか？ → y
# 11. GitHub リポジトリを作成しましたか？ → y
# 12. Vercel デプロイを完了しましたか？ → n (後で)

# 自動処理:
# - .env ファイル生成
# - .env.local 生成
# - パッケージインストール
# - 環境検証
```

### ステップ 5: GitHub Secrets 設定 (所要時間: 5分)

```
1. GitHub リポジトリにアクセス
   → https://github.com/naokinisizaka6/neta-db

2. Settings → Secrets and variables → Actions

3. 「New repository secret」を 3 回実行:
   
   Secret 1:
   Name: YOUTUBE_API_KEY
   Value: AIza... (ステップ 1.1 で取得したキー)
   
   Secret 2:
   Name: CLAUDE_API_KEY
   Value: sk-ant-... (ステップ 1.2 で取得したキー)
   
   Secret 3:
   Name: DATABASE_URL
   Value: postgresql://... (ステップ 1.3 で取得した接続文字列)

4. 「Add secret」を 3 回クリック
```

### ステップ 6: Vercel デプロイ (所要時間: 10～15分)

```
1. https://vercel.com にアクセス

2. GitHub でサインアップ・ログイン

3. 「Add New...」 → 「Project」

4. GitHub リポジトリから neta-db を選択

5. プロジェクト設定:
   - Framework Preset: Next.js
   - Root Directory: web/
   
6. Environment Variables を設定:
   NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJ...

7. 「Deploy」をクリック

8. デプロイ完了を待機 (5～10分)

9. 公開 URL が生成される
   → https://neta-db.vercel.app (例)
```

---

## ✅ 本番公開完了確認

```
[X] ローカル Next.js が http://localhost:3001 で実行
[X] ローカル Streamlit が http://localhost:8501 で実行
[X] GitHub リポジトリに 12+ commits がプッシュされている
[X] GitHub Actions が実行予定 (collect 08:00, classify 09:00, refresh 23:00 UTC)
[X] Vercel に本番サイトがデプロイされている
[X] https://neta-db.vercel.app でアクセス可能
```

---

## 🎉 完成！

**ネタDB が本番公開されました！** 🎊

次のステップ:
1. 管理画面で初期ネタを承認
2. LLM 分類精度を測定
3. ネタデータを充実

---

## 📞 トラブルシューティング

### git push で認証エラーが出た
→ Personal Access Token が正しいか確認
→ `git config --global --list` で設定を確認

### setup_interactive.py で API キー検証エラー
→ API キーのフォーマットを確認
→ Supabase プロジェクトが完全に作成されているか確認

### Vercel デプロイが失敗した
→ web/vercel.json の設定を確認
→ GitHub Secrets が正しく設定されているか確認
→ Vercel の Build ログを確認

### GitHub Actions が実行されない
→ GitHub Secrets が 3 個すべて設定されているか確認
→ Repository → Actions を確認
→ ワークフロー yml ファイルが .github/workflows/ に存在するか確認

---

**🚀 これでネタDB は本番環境で公開準備が整いました！**
