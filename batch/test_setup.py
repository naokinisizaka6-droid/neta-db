"""
セットアップ検証スクリプト
環境変数、DB接続、APIキーを検査
"""

import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def check_env_file():
    """環境変数ファイルを確認"""
    logger.info("🔍 Checking .env file...")

    if not os.path.exists(".env"):
        logger.error("❌ .env file not found. Run: cp .env.example .env")
        return False

    logger.info("✅ .env file exists")
    return True


def check_env_variables():
    """環境変数を確認"""
    logger.info("🔍 Checking environment variables...")

    load_dotenv()

    required_vars = {
        "YOUTUBE_API_KEY": "YouTube Data API キー",
        "CLAUDE_API_KEY": "Claude API キー",
        "DATABASE_URL": "Supabase 接続文字列",
        "NEXT_PUBLIC_SUPABASE_URL": "Supabase URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY": "Supabase Anon キー",
    }

    missing = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value:
            logger.warning(f"⚠️ {var} not set ({desc})")
            missing.append(var)
        else:
            # 値を一部マスク
            masked = value[:20] + "..." if len(value) > 20 else value
            logger.info(f"✅ {var}: {masked}")

    if missing:
        logger.error(f"❌ Missing {len(missing)} environment variables")
        return False

    logger.info("✅ All environment variables are set")
    return True


def check_db_connection():
    """DB接続を確認"""
    logger.info("🔍 Checking database connection...")

    try:
        import psycopg2

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.warning("⚠️ DATABASE_URL not set, skipping DB check")
            return False

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # テーブル一覧を確認
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )
        table_count = cursor.fetchone()[0]

        if table_count == 0:
            logger.error("❌ No tables found. Run: db/migrations/001_init.sql")
            return False

        logger.info(f"✅ DB connection OK ({table_count} tables)")

        # テーブル一覧を表示
        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"   Tables: {', '.join(tables[:5])}...")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ DB connection failed: {e}")
        return False


def check_api_keys():
    """API キーの有効性を確認"""
    logger.info("🔍 Checking API keys...")

    # YouTube API キー確認
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    if youtube_key and len(youtube_key) > 30:
        logger.info("✅ YouTube API key looks valid")
    else:
        logger.warning("⚠️ YouTube API key is missing or invalid")

    # Claude API キー確認
    claude_key = os.getenv("CLAUDE_API_KEY")
    if claude_key and len(claude_key) > 30:
        logger.info("✅ Claude API key looks valid")
    else:
        logger.warning("⚠️ Claude API key is missing or invalid")

    # Supabase キー確認
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    if supabase_url and "supabase.co" in supabase_url:
        logger.info("✅ Supabase URL looks valid")
    else:
        logger.warning("⚠️ Supabase URL is missing or invalid")

    return True


def check_dependencies():
    """必須パッケージを確認"""
    logger.info("🔍 Checking Python dependencies...")

    required_packages = {
        "psycopg2": "PostgreSQL adapter",
        "anthropic": "Claude API SDK",
        "google": "Google API client",
        "streamlit": "Streamlit",
        "dotenv": "Environment variables",
    }

    missing = []
    for package, desc in required_packages.items():
        try:
            __import__(package)
            logger.info(f"✅ {package} ({desc})")
        except ImportError:
            logger.warning(f"⚠️ {package} not installed ({desc})")
            missing.append(package)

    if missing:
        logger.error(f"❌ Missing {len(missing)} packages")
        logger.info(f"   Run: pip install -r batch/requirements.txt")
        return False

    logger.info("✅ All dependencies are installed")
    return True


def main():
    """メイン検証"""
    logger.info("=" * 50)
    logger.info("🎭 ネタDB セットアップ検証")
    logger.info("=" * 50)

    checks = [
        ("Environment file", check_env_file),
        ("Environment variables", check_env_variables),
        ("Database connection", check_db_connection),
        ("API keys", check_api_keys),
        ("Dependencies", check_dependencies),
    ]

    results = []
    for name, check_func in checks:
        logger.info("")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ {name} check failed: {e}")
            results.append((name, False))

    # サマリー
    logger.info("")
    logger.info("=" * 50)
    logger.info("📊 検証結果")
    logger.info("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        logger.info(f"{status} {name}")

    logger.info("")
    logger.info(f"🎯 {passed}/{total} チェック完了")

    if passed == total:
        logger.info("✅ すべてのセットアップが完了しています！")
        logger.info("")
        logger.info("次のステップ：")
        logger.info("  1. Streamlit: streamlit run admin/app.py")
        logger.info("  2. Next.js:  cd web && npm run dev")
        logger.info("  3. バッチ:   python batch/collect.py")
        return 0
    else:
        logger.warning("")
        logger.warning("⚠️ いくつかのチェックが失敗しました。")
        logger.warning("   SETUP.md を参照してセットアップを完了してください。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
