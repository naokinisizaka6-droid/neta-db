#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive setup script - configure API keys and environment
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
        """User input prompt"""
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
                print("[REQUIRED] This field is mandatory")
            else:
                return ""

    def prompt_yes_no(self, message, default=True):
        """Yes/No question"""
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
                print("Answer with y or n")

    def step_1_introduction(self):
        """Step 1: Introduction"""
        self.print_header("NetalDB Interactive Setup")

        print("This script automates the following:")
        print("  [OK] Environment configuration (.env)")
        print("  [OK] Python package installation")
        print("  [OK] Node.js package installation")
        print("  [OK] Environment verification")
        print()
        print("[WARNING] Please prepare the following in advance:")
        print("  1. Supabase project created")
        print("  2. YouTube Data API key obtained")
        print("  3. Claude API key obtained")
        print()

        if not self.prompt_yes_no("Start setup?"):
            print("[ERROR] Setup cancelled")
            sys.exit(0)

    def step_2_api_keys(self):
        """Step 2: API Keys input"""
        self.print_section("API Keys Configuration")

        print("[PIN] Please enter the following information\n")

        # YouTube API Key
        print("[YouTube Data API Key]")
        print("  How to get: Google Cloud Console -> API -> YouTube Data API v3")
        self.config["YOUTUBE_API_KEY"] = self.prompt(
            "  Enter API key",
            required=True
        )

        # Claude API Key
        print("\n[Claude API Key]")
        print("  How to get: https://console.anthropic.com -> API Keys")
        self.config["CLAUDE_API_KEY"] = self.prompt(
            "  Enter API key",
            required=True
        )

        # Claude Model
        self.config["CLAUDE_MODEL"] = self.prompt(
            "  Model to use",
            default="claude-haiku-4-5-20251001"
        )

    def step_3_supabase(self):
        """Step 3: Supabase information"""
        self.print_section("Supabase Configuration")

        print("[PIN] Please enter Supabase project information\n")

        # Supabase URL
        print("[Supabase URL]")
        print("  How to get: Supabase Dashboard -> Settings -> API")
        self.config["SUPABASE_URL"] = self.prompt(
            "  Enter Supabase URL (example: https://xxx.supabase.co)",
            required=True
        )

        # Anon Key
        print("\n[Anon Public Key]")
        print("  How to get: Supabase Dashboard -> Settings -> API -> anon public")
        self.config["SUPABASE_ANON_KEY"] = self.prompt(
            "  Enter Anon key",
            required=True
        )

        # Service Role Key
        print("\n[Service Role Secret Key]")
        print("  How to get: Supabase Dashboard -> Settings -> API -> service_role secret")
        self.config["SUPABASE_SERVICE_ROLE_KEY"] = self.prompt(
            "  Enter Service Role key",
            required=True
        )

        # Database URL
        print("\n[Database Connection URL]")
        print("  How to get: Supabase Dashboard -> Settings -> Database -> Connection Pooling")
        print("  Format: postgresql://postgres:password@host:5432/postgres")
        self.config["DATABASE_URL"] = self.prompt(
            "  Enter connection string",
            required=True
        )

    def step_4_create_env_files(self):
        """Step 4: Create .env files"""
        self.print_section("Environment Files Creation")

        # Root .env
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
        print(f"[OK] Created {self.env_file}")

        # web/.env
        web_env_content = f"""# Supabase (public)
NEXT_PUBLIC_SUPABASE_URL={self.config['SUPABASE_URL']}
NEXT_PUBLIC_SUPABASE_ANON_KEY={self.config['SUPABASE_ANON_KEY']}
"""

        with open(self.web_env_file, "w") as f:
            f.write(web_env_content)
        print(f"[OK] Created {self.web_env_file}")

    def step_5_install_dependencies(self):
        """Step 5: Install dependencies"""
        self.print_section("Dependency Installation")

        # Python
        if self.prompt_yes_no("Install Python packages?"):
            print("\n[PACKAGE] Installing Python packages...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", "batch/requirements.txt"],
                    cwd=self.project_root,
                    check=True,
                    timeout=120
                )
                print("[OK] Python packages installed")
            except Exception as e:
                print(f"[WARNING] Error during Python installation: {e}")
                print("   Manual: pip install -r batch/requirements.txt")

        # Node.js
        if self.prompt_yes_no("Install Node.js packages?"):
            print("\n[PACKAGE] Installing Node.js packages...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=self.project_root / "web",
                    check=True,
                    timeout=300
                )
                print("[OK] Node.js packages installed")
            except Exception as e:
                print(f"[WARNING] Error during Node.js installation: {e}")
                print("   Manual: cd web && npm install")

    def step_6_verify_setup(self):
        """Step 6: Setup verification"""
        self.print_section("Setup Verification")

        if self.prompt_yes_no("Run verification script?"):
            print("\n[SEARCH] Verifying environment...\n")
            try:
                subprocess.run(
                    [sys.executable, "batch/test_setup.py"],
                    cwd=self.project_root,
                    timeout=30
                )
            except Exception as e:
                print(f"[WARNING] Verification error: {e}")

    def step_7_github_setup(self):
        """Step 7: GitHub setup"""
        self.print_section("GitHub Setup")

        print("[PIN] Please create repository on GitHub\n")
        print("  1. Visit https://github.com/new")
        print("  2. Repository name: neta-db")
        print("  3. Click Create repository button")
        print()

        if self.prompt_yes_no("Have you created the GitHub repository?"):
            repo_url = self.prompt(
                "  Enter repository URL (example: https://github.com/username/neta-db.git)",
                required=True
            )

            print("\n[UPLOAD] Pushing to repository...\n")
            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_url],
                    cwd=self.project_root,
                    check=True
                )
            except subprocess.CalledProcessError:
                # Already exists
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
                    ["git", "push", "-u", "origin", "master"],
                    cwd=self.project_root,
                    check=True,
                    timeout=60
                )
                print("[OK] Pushed to GitHub")
            except Exception as e:
                print(f"[WARNING] Push error: {e}")
                print("   Manual: git push -u origin master")

    def step_8_github_secrets(self):
        """Step 8: GitHub Secrets setup"""
        self.print_section("GitHub Secrets Configuration")

        print("[PIN] Please set Secrets using the following steps\n")
        print("  1. GitHub repository -> Settings -> Secrets and variables -> Actions")
        print("  2. Add \"New repository secret\" with:\n")

        secrets = {
            "YOUTUBE_API_KEY": self.config["YOUTUBE_API_KEY"],
            "CLAUDE_API_KEY": self.config["CLAUDE_API_KEY"],
            "DATABASE_URL": self.config["DATABASE_URL"],
        }

        for secret_name, secret_value in secrets.items():
            masked_value = secret_value[:20] + "..." if len(secret_value) > 20 else secret_value
            print(f"  * Name: {secret_name}")
            print(f"    Value: {masked_value}")
            print()

        print("[OK] After Secrets are configured, GitHub Actions will run automatically")

    def step_9_vercel_deployment(self):
        """Step 9: Vercel deployment"""
        self.print_section("Vercel Deployment Preparation")

        print("[PIN] Please deploy using the following steps\n")
        print("  1. Visit https://vercel.com")
        print("  2. Sign up with GitHub")
        print("  3. Click \"Add New...\" -> \"Project\"")
        print("  4. Select GitHub repository neta-db")
        print("  5. Root Directory: web/")
        print("  6. Set Environment Variables:")
        print(f"     - NEXT_PUBLIC_SUPABASE_URL: {self.config['SUPABASE_URL']}")
        print(f"     - NEXT_PUBLIC_SUPABASE_ANON_KEY: {self.config['SUPABASE_ANON_KEY']}")
        print("  7. Click Deploy button")
        print()

        if self.prompt_yes_no("Have you completed Vercel deployment?"):
            print("[OK] Public site is now available")

    def run(self):
        """Run entire setup"""
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

            # Complete
            self.print_header("Setup Complete!")
            print("NetalDB setup is complete!\n")
            print("Next steps:")
            print("  Admin: streamlit run admin/app.py")
            print("  Public: cd web && npm run dev")
            print("  Batch: python batch/collect.py")
            print()
            print("See README.md or SETUP.md for details")
            print()

        except KeyboardInterrupt:
            print("\n[ERROR] Setup cancelled")
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            sys.exit(1)


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
