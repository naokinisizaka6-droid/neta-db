#!/usr/bin/env python3
"""
ネタDB インタラクティブセットアップスクリプト
ユーザーの入力に基づいて自動セットアップを進行
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class SetupWizard:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.web_env_file = self.project_root / "web" / ".env"
        self.config = {}

    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60 + "\n")

    def print_section(self, title):
        print(f"\n### {title}")
        print()

    def prompt(self, message, default="", required=False):
        """ユーザーに入力を促す"""
        while True:
            prompt_text = f"{message}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "

            value = input(prompt_text).strip()

            if not value and default:
                return default
            elif value:
                return value
            elif required:
                print("❌ この項目は必須です")
            else:
                return ""

    def prompt_yes_no(self, message, default=True):
        """Yes/No 質問"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{message} [{default_str}]: ").strip().lower()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            elif response == "":
                return default
            else:
                print("y または n で答えてください")

    def step_1_introduction(self):
        """ステップ 1: イントロダクション"""
        self.print_header("🎭 ネタDB インタラクティブセットアップ")

        print("このスクリプトでは、以下を自動化します：")
        print("  ✅ 環境変数設定（.env）")
        print("  ✅ Python 依存パッケージのインストール")
        print("  ✅ Node.js 依存パッケージのインストール")
        print("  ✅ 環境検証")
        print()
        print("⚠️  事前に以下を準備してください：")
        print("  1. Supabase プロジェクト作成済み")
        print("  2. YouTube Data API キー取得済み")
        print("  3. Claude API キー取得済み")
        print()

        if not self.prompt_yes_no("セットアップを開始しますか？"):
            print("❌ セットアップをキャンセルしました")
            sys.exit(0)

    def step_2_api_keys(self):
        """ステップ 2: API キーを入力"""
        self.print_section("API キー設定")

        print("📌 以下の情報を入力してください\n")

        # YouTube API Key
        print("【YouTube Data API キー】")
        print("  取得方法: Google Cloud Console → API → YouTube Data API v3")
        self.config["YOUTUBE_API_KEY"] = self.prompt(
            "  API キーを入力",
            required=True
        )

        # Claude API Key
        print("\n【Claude API キー】")
        print("  取得方法: https://console.anthropic.com → API Keys")
        self.config["CLAUDE_API_KEY"] = self.prompt(
            "  API キーを入力",
            required=True
        )

        # Claude Model
        self.config["CLAUDE_MODEL"] = self.prompt(
            "  使用モデル",
            default="claude-haiku-4-5-20251001"
        )

    def step_3_supabase(self):
        """ステップ 3: Supabase 情報を入力"""
        self.print_section("Supabase 設定")

        print("📌 Supabase プロジェクト情報を入力してください\n")

        # Supabase URL
        print("【Supabase URL】")
        print("  取得方法: Supabase Dashboard → Settings → API")
        self.config["SUPABASE_URL"] = self.prompt(
            "  Supabase URL (例: https://xxx.supabase.co)",
            required=True
        )

        # Anon Key
        print("\n【Anon Public キー】")
        print("  取得方法: Supabase Dashboard → Settings → API → anon public")
        self.config["SUPABASE_ANON_KEY"] = self.prompt(
            "  Anon キーを入力",
            required=True
        )

        # Service Role Key
        print("\n【Service Role Secret キー】")
        print("  取得方法: Supabase Dashboard → Settings → API → service_role secret")
        self.config["SUPABASE_SERVICE_ROLE_KEY"] = self.prompt(
            "  Service Role キーを入力",
            required=True
        )

        # Database URL
        print("\n【Database Connection URL】")
        print("  取得方法: Supabase Dashboard → Settings → Database → Connection Pooling")
        print("  形式: postgresql://postgres:password@host:5432/postgres")
        self.config["DATABASE_URL"] = self.prompt(
            "  接続文字列を入力",
            required=True
        )

    def step_4_create_env_files(self):
        """ステップ 4: .env ファイルを作成"""
        self.print_section("環境変数ファイル作成")

        # ルート .env
        env_content = f"""# YouTube API
YOUTUBE_API_KEY={self.config['YOUTUBE_API_KEY']}

# Claude API
CLAUDE_API_KEY={self.config['CLAUDE_API_KEY']}
CLAUDE_MODEL={self.config['CLAUDE_MODEL']}

# Supabase
SUPABASE_URL={self.config['SUPABASE_URL']}
SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
SUPABASE_SERVICE_ROLE_KEY={self.config['SUPABASE_SERVICE_ROLE_KEY']}
DATABASE_URL={self.config['DATABASE_URL']}

# Next.js
NEXT_PUBLIC_SUPABASE_URL={self.config['SUPABASE_URL']}
NEXT_PUBLIC_SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
"""

        with open(self.env_file, "w") as f:
            f.write(env_content)
        print(f"✅ {self.env_file} を作成しました")

        # web/.env
        web_env_content = f"""# Supabase (公開用)
NEXT_PUBLIC_SUPABASE_URL={self.config['SUPABASE_URL']}
NEXT_PUBLIC_SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
"""

        with open(self.web_env_file, "w") as f:
            f.write(web_env_content)
        print(f"✅ {self.web_env_file} を作成しました")

    def step_5_install_dependencies(self):
        """ステップ 5: 依存パッケージをインストール"""
        self.print_section("依存パッケージのインストール")

        # Python
        if self.prompt_yes_no("Python パッケージをインストールしますか？"):
            print("\n📦 Python パッケージをインストール中...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", "batch/requirements.txt"],
                    cwd=self.project_root,
                    check=True,
                    timeout=120
                )
                print("✅ Python パッケージをインストール完了")
            except Exception as e:
                print(f"⚠️ Python インストール中にエラー: {e}")
                print("   手動で実行: pip install -r batch/requirements.txt")

        # Node.js
        if self.prompt_yes_no("Node.js パッケージをインストールしますか？"):
            print("\n📦 Node.js パッケージをインストール中...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=self.project_root / "web",
                    check=True,
                    timeout=300
                )
                print("✅ Node.js パッケージをインストール完了")
            except Exception as e:
                print(f"⚠️ Node.js インストール中にエラー: {e}")
                print("   手動で実行: cd web && npm install")

    def step_6_verify_setup(self):
        """ステップ 6: セットアップ検証"""
        self.print_section("セットアップ検証")

        if self.prompt_yes_no("検証スクリプトを実行しますか？"):
            print("\n🔍 環境を検証中...\n")
            try:
                subprocess.run(
                    [sys.executable, "batch/test_setup.py"],
                    cwd=self.project_root,
                    timeout=30
                )
            except Exception as e:
                print(f"⚠️ 検証エラー: {e}")

    def step_7_github_setup(self):
        """ステップ 7: GitHub セットアップ"""
        self.print_section("GitHub セットアップ")

        print("📌 GitHub にリポジトリを作成してください\n")
        print("  1. https://github.com/new にアクセス")
        print("  2. Repository name: neta-db")
        print("  3. Create repository ボタンを押す")
        print()

        if self.prompt_yes_no("GitHub リポジトリを作成しましたか？"):
            repo_url = self.prompt(
                "  リポジトリ URL を入力 (例: https://github.com/username/neta-db.git)",
                required=True
            )

            print("\n📤 リポジトリにプッシュ中...\n")
            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_url],
                    cwd=self.project_root,
                    check=True
                )
            except subprocess.CalledProcessError:
                # すでに存在する場合
                subprocess.run(
                    ["git", "remote", "remove", "origin"],
                    cwd=self.project_root
                )
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_url],
                    cwd=self.project_root,
                    check=True
                )

            try:
                subprocess.run(
                    ["git", "push", "-u", "origin", "main"],
                    cwd=self.project_root,
                    check=True,
                    timeout=60
                )
                print("✅ GitHub にプッシュしました")
            except Exception as e:
                print(f"⚠️ プッシュエラー: {e}")
                print("   手動で実行: git push -u origin main")

    def step_8_github_secrets(self):
        """ステップ 8: GitHub Secrets 設定"""
        self.print_section("GitHub Secrets 設定")

        print("📌 以下の手順で Secrets を設定してください\n")
        print("  1. GitHub リポジトリ → Settings → Secrets and variables → Actions")
        print("  2. 「New repository secret」で以下を追加：\n")

        secrets = {
            "YOUTUBE_API_KEY": self.config["YOUTUBE_API_KEY"],
            "CLAUDE_API_KEY": self.config["CLAUDE_API_KEY"],
            "DATABASE_URL": self.config["DATABASE_URL"],
        }

        for secret_name, secret_value in secrets.items():
            masked_value = secret_value[:20] + "..." if len(secret_value) > 20 else secret_value
            print(f"  • Name: {secret_name}")
            print(f"    Value: {masked_value}")
            print()

        print("✅ Secrets 設定完了後、GitHub Actions が自動実行されます")

    def step_9_vercel_deployment(self):
        """ステップ 9: Vercel デプロイ"""
        self.print_section("Vercel デプロイ準備")

        print("📌 以下の手順でデプロイしてください\n")
        print("  1. https://vercel.com にアクセス")
        print("  2. GitHub でサインアップ")
        print("  3. 「Add New...」→ 「Project」")
        print("  4. GitHub リポジトリ neta-db を選択")
        print("  5. Root Directory: web/")
        print("  6. Environment Variables を設定：")
        print(f"     - NEXT_PUBLIC_SUPABASE_URL: {self.config['SUPABASE_URL']}")
        print(f"     - NEXT_PUBLIC_SUPABASE_ANON_KEY: {self.config['SUPABASE_ANON_KEY']}")
        print("  7. Deploy ボタンを押す")
        print()

        if self.prompt_yes_no("Vercel デプロイを完了しましたか？"):
            print("✅ 公開サイトが利用可能になります")

    def run(self):
        """セットアップ全体を実行"""
        try:
            self.step_1_introduction()
            self.step_2_api_keys()
            self.step_3_supabase()
            self.step_4_create_env_files()
            self.step_5_install_dependencies()
            self.step_6_verify_setup()
            self.step_7_github_setup()
            self.step_8_github_secrets()
            self.step_9_vercel_deployment()

            # 完了
            self.print_header("🎉 セットアップ完了！")
            print("ネタDB のセットアップがすべて完了しました！\n")
            print("次のステップ：")
            print("  📺 管理画面: streamlit run admin/app.py")
            print("  🌐 公開サイト: cd web && npm run dev")
            print("  🔄 バッチ処理: python batch/collect.py")
            print()
            print("詳細は README.md または SETUP.md を参照してください")
            print()

        except KeyboardInterrupt:
            print("\n❌ セットアップをキャンセルしました")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            sys.exit(1)


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
