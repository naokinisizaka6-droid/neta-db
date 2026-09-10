#!/bin/bash
# GitHub リモートリポジトリへの自動プッシュスクリプト
# 使用方法: bash init_github.sh <github-username>

set -e

GITHUB_USERNAME="${1:-naokinisizaka6}"
REPO_NAME="neta-db"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🚀 GitHub リモートリポジトリへのプッシュを開始..."
echo ""
echo "📌 リポジトリ情報:"
echo "   URL: $REPO_URL"
echo "   ユーザー: $GITHUB_USERNAME"
echo ""

# Git リモート設定
echo "1️⃣ Git リモート設定中..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
echo "✅ リモート設定完了"
echo ""

# ブランチ名を main に変更
echo "2️⃣ ブランチ名を確認中..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "   現在のブランチ: $CURRENT_BRANCH → main に変更"
    git branch -M main
fi
echo "✅ ブランチ: main"
echo ""

# Git プッシュ
echo "3️⃣ GitHub にプッシュ中..."
git push -u origin main
echo "✅ プッシュ完了！"
echo ""

# 確認
echo "4️⃣ リモート状態確認中..."
git remote -v
echo ""

echo "🎉 GitHub へのプッシュが完了しました！"
echo ""
echo "📍 次のステップ:"
echo "   1. GitHub リポジトリを開く:"
echo "      https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
echo "   2. Secrets を設定:"
echo "      Settings → Secrets and variables → Actions"
echo "      以下を追加:"
echo "        - YOUTUBE_API_KEY"
echo "        - CLAUDE_API_KEY"
echo "        - DATABASE_URL"
echo ""
echo "   3. setup_interactive.py を実行:"
echo "      python setup_interactive.py"
