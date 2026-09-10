# GitHub リモートリポジトリへの自動プッシュスクリプト (PowerShell)

param([string]$GitHubUsername = "naokinisizaka6")

$RepoName = "neta-db"
$RepoUrl = "https://github.com/$GitHubUsername/$RepoName.git"

Write-Host "GitHub リモートリポジトリへのプッシュを開始..." -ForegroundColor Cyan
Write-Host ""

# Git リモート設定
Write-Host "1. Git リモート設定中..." -ForegroundColor Cyan
try { git remote remove origin 2>$null } catch {}
git remote add origin $RepoUrl
Write-Host "OK - リモート設定完了" -ForegroundColor Green
Write-Host ""

# ブランチ名を main に変更
Write-Host "2. ブランチ名を確認中..." -ForegroundColor Cyan
$CurrentBranch = git rev-parse --abbrev-ref HEAD
if ($CurrentBranch -ne "main") {
    git branch -M main
}
Write-Host "OK - ブランチ: main" -ForegroundColor Green
Write-Host ""

# Git プッシュ
Write-Host "3. GitHub にプッシュ中..." -ForegroundColor Cyan
git push -u origin main 2>&1
Write-Host "OK - プッシュ完了" -ForegroundColor Green
Write-Host ""

# 確認
Write-Host "4. リモート状態確認:" -ForegroundColor Cyan
git remote -v
Write-Host ""
Write-Host "完了!" -ForegroundColor Green
