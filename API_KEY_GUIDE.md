# API キー取得ガイド - ネタDB

**このガイドでは、ネタDB に必要な 3 つの API キーを取得する手順を説明します。**

---

## 1. YouTube Data API キー取得 (10～15分)

### ステップ 1.1: Google Cloud Console にアクセス
1. https://console.cloud.google.com/ にアクセス
2. 右上でプロジェクトを選択 → **「新しいプロジェクト」**
3. プロジェクト名: `neta-db` を入力
4. 「作成」をクリック

### ステップ 1.2: YouTube Data API を有効化
1. **左メニュー** → **「API とサービス」** → **「ライブラリ」**
2. 検索ボックスで `YouTube Data API v3` を検索
3. 「YouTube Data API v3」をクリック
4. **「有効にする」** をクリック

### ステップ 1.3: API キーを作成
1. **「認証情報」** をクリック
2. **「認証情報を作成」** → **「API キー」**
3. **「キーを表示」** をコピー
   - 形式: `AIza...` (39文字程度)

### ステップ 1.4: API キーの制限を設定（推奨）
1. 作成した API キーをクリック
2. **「API キーの制限」**
   - アプリケーションの制限: **「IP アドレス」** または **「HTTP リファラー」**
   - API の制限: **「YouTube Data API v3」** のみ
3. 「保存」をクリック

---

## 2. Claude API キー取得 (5～10分)

### ステップ 2.1: Anthropic Console にアクセス
1. https://console.anthropic.com/ にアクセス
2. **「サインアップ」** または **「ログイン」**

### ステップ 2.2: API キーを生成
1. 左メニュー → **「API Keys」**
2. **「Create Key」** をクリック
3. キー名: `neta-db-production` を入力
4. **「Create」** をクリック
5. **キーをコピー**
   - 形式: `sk-ant-...` (100文字以上)
   - ⭐ **再度表示されません。必ず保存してください**

### ステップ 2.3: 使用限度額を設定（推奨）
1. 左メニュー → **「Billing」**
2. **「Usage Limits」**
3. 月額制限を設定（例: 100ドル）
4. 保存

---

## 3. Supabase プロジェクト作成 (5～10分)

### ステップ 3.1: Supabase にサインアップ
1. https://supabase.com/ にアクセス
2. **「Start your project」**
3. GitHub または Email でサインアップ

### ステップ 3.2: 新規プロジェクト作成
1. **「New Project」**
2. 以下を入力:
   - **Organization**: デフォルト
   - **Project name**: `neta-db`
   - **Database Password**: 強いパスワード (コピーして保存)
   - **Region**: `Tokyo` (asia-northeast-1)
3. **「Create new project」**

### ステップ 3.3: プロジェクト情報を取得
1. **プロジェクトのダッシュボード** が開く（3～5分待つ）

#### Supabase URL を取得
1. 左メニュー → **「Settings」** → **「API」**
2. **「Project URL」** をコピー
   - 形式: `https://xxxxx.supabase.co`

#### Anon Public キーを取得
1. 同じ **「Settings」** → **「API」** ページ
2. **「anon public」** キーをコピー
   - 形式: `eyJ...` (150文字程度)

#### Service Role Secret キーを取得
1. 同じページの **「service_role secret」** をコピー
   - 形式: `eyJ...` (150文字以上)

#### Database Connection URL を取得
1. 左メニュー → **「Settings」** → **「Database」**
2. **「Connection string」** → **「Connection pooling」**
3. **「Connection string」** をコピー
   - 形式: `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres`
   - `[PASSWORD]` をステップ 3.2 で設定したパスワードに置き換える

### ステップ 3.4: DDL を実行 (スキーマ作成)
1. 左メニュー → **「SQL Editor」**
2. **「New query」** をクリック
3. `db/migrations/001_init.sql` の内容をコピー＆ペースト
4. **「Run」** をクリック
5. ✅ テーブルが作成される

---

## 📝 取得したキーをメモ

以下の情報をテキストエディタに保存してください：

```
YouTube Data API キー:
  AIza...

Claude API キー:
  sk-ant-...

Supabase URL:
  https://xxxxx.supabase.co

Supabase Anon Key:
  eyJ...

Supabase Service Role Key:
  eyJ...

Database URL:
  postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:6543/postgres
```

---

## 🚀 セットアップスクリプト実行

すべてのキーを取得したら、以下を実行：

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
python setup_interactive.py
```

**セットアップスクリプトが求めてくるときに、上記のキーをコピー＆ペースト してください。**

---

## ⚠️ セキュリティ注意

- **API キーを公開しない**: Git にコミットしない
- **GitHub Secrets に登録**: 本番環境では必須
- **.env ファイルを保護**: `.gitignore` に含める
- **API キーを定期的に再生成**: 90～180日ごと

---

## 🔍 トラブルシューティング

### ❌ YouTube API キー作成ができない
→ Google Cloud Console の支払い方法を登録してください
→ 新規プロジェクトを作成して再度試してください

### ❌ Claude API キーが表示されない
→ 一度だけ表示されます。スクリーンショットで保存するか、新しいキーを作成してください

### ❌ Supabase のパスワードを忘れた
→ **「Settings」** → **「Database」** → **「Reset password」** から再設定できます

### ❌ DDL の実行に失敗した
→ SQL Editor で下記を実行:
```sql
DROP TABLE IF EXISTS neta_work_tags CASCADE;
-- ... (他のテーブルも)
```
その後、DDL を再度実行

---

## 📞 サポート

- **YouTube API**: https://developers.google.com/youtube/v3
- **Claude API**: https://docs.anthropic.com/
- **Supabase**: https://supabase.com/docs

---

**🎉 すべてのキーを取得しましたら、`python setup_interactive.py` を実行してください！**
