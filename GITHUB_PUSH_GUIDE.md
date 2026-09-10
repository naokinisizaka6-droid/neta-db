# 🚀 GitHub へのプッシュガイド

## ステップ 1: GitHub Personal Access Token を作成

### 1.1 GitHub にログイン
1. https://github.com/settings/tokens にアクセス
2. 右上のプロフィール → **Settings** → **Developer settings** → **Personal access tokens**

### 1.2 新規トークン作成
1. **Generate new token** → **Generate new token (classic)**
2. **Note**: `neta-db-push`
3. **Expiration**: 90 days（3ヶ月）
4. **Scopes** でチェック:
   - ✅ `repo` (フルコントロール)
   - ✅ `admin:repo_hook` (webhook 管理)
5. **Generate token** をクリック
6. **トークンをコピー** → メモしておく（再度表示されません）⭐

---

## ステップ 2: ローカルで Git 認証を設定

### 2.1 Git Credential Manager を設定（Windows）

```bash
git config --global credential.helper manager
```

### 2.2 または、Git に Token を設定

以下のコマンドで URL にトークンを埋め込む：

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
git remote set-url origin https://USERNAME:TOKEN@github.com/USERNAME/neta-db.git
```

**置き換え：**
- `USERNAME`: GitHub ユーザー名（naokinisizaka6）
- `TOKEN`: Personal Access Token（コピーしたもの）

---

## ステップ 3: GitHub にプッシュ

```bash
cd c:\Users\User\Desktop\youtube切り抜き\neta-db
git push -u origin master
```

ブランチを `main` に変更する場合：

```bash
git branch -M main
git push -u origin main
```

---

## 確認

プッシュ成功後：

```bash
git remote -v
# origin	https://github.com/naokinisizaka6/neta-db.git (fetch)
# origin	https://github.com/naokinisizaka6/neta-db.git (push)

git log -1
# GitHub へのプッシュが完了したコミットが表示される
```

---

## 🔐 セキュリティ注意

- ✅ Personal Access Token は **シェルの履歴に残らない**ように注意
- ✅ トークンを **コードやログに含めない**
- ✅ 必要に応じて Token を **削除・再生成**できます

---

## 📍 次のステップ

プッシュ完了後：

```
1. GitHub リポジトリを確認: https://github.com/naokinisizaka6/neta-db
2. Secrets を設定
   Settings → Secrets and variables → Actions
   - YOUTUBE_API_KEY
   - CLAUDE_API_KEY
   - DATABASE_URL
3. setup_interactive.py を実行
   python setup_interactive.py
```

---

💡 **トラブルシューティング**

### ❌ "Authentication failed"
→ Token が正しく設定されているか確認
→ `git config credential.helper` で確認

### ❌ "Repository not found"
→ GitHub ユーザー名またはリポジトリ名を確認
→ https://github.com/naokinisizaka6/neta-db が存在するか確認

### ❌ "Permission denied (publickey)"
→ SSH キーの問題（HTTPS を使用してください）
→ `git remote set-url origin https://...` で確認

---

**準備ができたら以下を実行してください：**

```bash
# オプション 1: Git Credential Manager を使用
git config --global credential.helper manager
git push -u origin master

# オプション 2: Token を URL に埋め込む
git remote set-url origin https://naokinisizaka6:TOKEN@github.com/naokinisizaka6/neta-db.git
git push -u origin master
```

**Happy Hacking! 🎭**
