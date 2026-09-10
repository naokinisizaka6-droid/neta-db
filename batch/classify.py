"""
Claude API を用いたネタ分類スクリプト
pending ステータスの performances を LLM で分類
"""

import os
import json
import logging
import psycopg2
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import anthropic

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class VideoClassifier:
    def __init__(self, api_key: str, db_connection_string: str, model: str = "claude-haiku-4-5-20251001"):
        """
        分類器初期化

        Args:
            api_key: Claude API キー
            db_connection_string: PostgreSQL 接続文字列
            model: 使用するモデル
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.db_conn_string = db_connection_string
        self.db_conn = None
        self.stats = {
            "videos_processed": 0,
            "netas_classified": 0,
            "non_netas": 0,
            "errors": 0,
            "tags_created": 0
        }

    def connect_db(self):
        """DB接続"""
        try:
            self.db_conn = psycopg2.connect(self.db_conn_string)
            logger.info("DB connection established")
        except Exception as e:
            logger.error(f"DB connection failed: {e}")
            raise

    def close_db(self):
        """DB接続終了"""
        if self.db_conn:
            self.db_conn.close()

    def run(self, limit: int = 50):
        """
        メイン処理を実行

        Args:
            limit: 処理対象の最大動画数
        """
        logger.info(f"Starting classification (limit: {limit})...")

        try:
            self.connect_db()

            # pending 状態の performances を取得
            pending_videos = self._get_pending_videos(limit)
            logger.info(f"Found {len(pending_videos)} pending videos")

            for video_id, start_sec, end_sec in pending_videos:
                try:
                    self._classify_video(video_id, start_sec, end_sec)
                except Exception as e:
                    logger.error(f"Error classifying {video_id}: {e}")
                    self.stats["errors"] += 1

            self._report_stats()

        finally:
            self.close_db()

    def _get_pending_videos(self, limit: int) -> List[tuple]:
        """
        pending 状態の performances を取得

        Returns:
            (video_id, start_sec, end_sec) のリスト
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT p.video_id, p.start_sec, p.end_sec
                FROM performances p
                WHERE p.review_status = 'pending'
                AND p.source = 'llm'
                ORDER BY p.created_at ASC
                LIMIT %s
                """,
                (limit,)
            )
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Failed to get pending videos: {e}")
            return []

    def _classify_video(self, video_id: str, start_sec: int, end_sec: Optional[int]):
        """
        動画を分類

        Args:
            video_id: YouTube 動画ID
            start_sec: 開始秒数
            end_sec: 終了秒数
        """
        logger.info(f"Classifying {video_id} [{start_sec}:{end_sec}]")

        # 一段階目: 寸法チェック (90秒以内)
        if end_sec and (end_sec - start_sec) > 90:
            logger.info(f"  Skipped: duration > 90 sec")
            return

        # 動画情報とチャンネル情報を取得
        video_info = self._get_video_info(video_id)
        if not video_info:
            logger.warning(f"  No video info found for {video_id}")
            self.stats["errors"] += 1
            return

        # 芸人情報を取得
        channel_id = video_info.get("channel_id")
        performers = self._get_channel_comedians(channel_id)

        # 既存タグを取得
        existing_tags = self._get_existing_tags()

        # LLM に分類を依頼
        classification = self._call_llm_classifier(
            video_id=video_id,
            title=video_info.get("title"),
            description=video_info.get("description"),
            channel_name=video_info.get("channel_title"),
            channel_kind=video_info.get("channel_kind"),
            duration_sec=(end_sec - start_sec) if end_sec else video_info.get("duration_sec", 0),
            performer_names=performers,
            existing_tags=existing_tags
        )

        if not classification:
            logger.warning(f"  Classification failed for {video_id}")
            self.stats["errors"] += 1
            return

        # 結果を保存
        self._save_classification(video_id, classification)

        # is_neta の場合のみタグを作成
        if classification.get("is_neta", False):
            self.stats["netas_classified"] += 1
            self._create_tags(classification.get("new_tag_proposals", []))
        else:
            self.stats["non_netas"] += 1

        self.stats["videos_processed"] += 1

    def _get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        動画情報を取得

        Returns:
            動画情報の辞書
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                SELECT
                    v.title, v.description, v.channel_id, v.duration_sec,
                    c.kind as channel_kind,
                    yt_ch.title as channel_title
                FROM yt_videos v
                LEFT JOIN channels c ON v.channel_id = c.channel_id
                LEFT JOIN yt_channels yt_ch ON v.channel_id = yt_ch.channel_id
                WHERE v.video_id = %s
                """,
                (video_id,)
            )
            result = cursor.fetchone()
            cursor.close()

            if result:
                return {
                    "title": result[0],
                    "description": result[1],
                    "channel_id": result[2],
                    "duration_sec": result[3],
                    "channel_kind": result[4],
                    "channel_title": result[5]
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None

    def _get_channel_comedians(self, channel_id: str) -> List[str]:
        """
        チャンネルに関連する芸人を取得

        Returns:
            芸人名のリスト
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                SELECT c.name
                FROM comedians c
                WHERE c.id = (
                    SELECT comedian_id FROM channels WHERE channel_id = %s
                )
                """,
                (channel_id,)
            )
            result = cursor.fetchone()
            cursor.close()

            if result:
                return [result[0]]
            return []

        except Exception as e:
            logger.warning(f"Failed to get comedians: {e}")
            return []

    def _get_existing_tags(self) -> List[str]:
        """
        既存タグのリストを取得

        Returns:
            タグスラッグのリスト
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT slug FROM tags")
            result = cursor.fetchall()
            cursor.close()
            return [row[0] for row in result]

        except Exception as e:
            logger.warning(f"Failed to get existing tags: {e}")
            return []

    def _call_llm_classifier(
        self,
        video_id: str,
        title: str,
        description: str,
        channel_name: str,
        channel_kind: str,
        duration_sec: int,
        performer_names: List[str],
        existing_tags: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Claude API を用いて分類

        Returns:
            分類結果の JSON
        """
        # プロンプトを構築
        prompt = self._build_prompt(
            title=title,
            description=description,
            channel_name=channel_name,
            channel_kind=channel_kind,
            duration_sec=duration_sec,
            performer_names=performer_names,
            existing_tags=existing_tags
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # JSON を抽出
            response_text = message.content[0].text
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                classification = json.loads(json_str)
                return classification
            else:
                logger.warning(f"No JSON found in response for {video_id}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def _build_prompt(
        self,
        title: str,
        description: str,
        channel_name: str,
        channel_kind: str,
        duration_sec: int,
        performer_names: List[str],
        existing_tags: List[str]
    ) -> str:
        """
        LLM 用プロンプトを構築
        """
        return f"""
以下の動画情報から、漫才・コント・ピン芸の分類を行ってください。

【動画情報】
- タイトル: {title}
- チャンネル: {channel_name} ({channel_kind})
- 尺: {duration_sec}秒
- 説明文: {description[:500]}
- 出演者: {', '.join(performer_names)}

【既存タグリスト】
{', '.join(existing_tags[:20])}...

以下のJSONスキーマで返してください:
{{
  "is_neta": true/false,
  "confidence": 0.0-1.0,
  "format": "manzai" | "conte" | "pin" | "other",
  "performers": ["名前1", "名前2"],
  "segments": [{{
    "start_sec": 0,
    "end_sec": 120,
    "neta_title": "ネタ名またはnull"
  }}],
  "setting_tags": ["タグスラッグ"],
  "new_tag_proposals": [{{
    "slug": "tag_slug",
    "name": "表示名",
    "category": "place|relation|job|theme|style"
  }}],
  "contest": null
}}

本編のネタかメイキング・フリートークかを区別してください。タイトルと説明だけでなく、内容を推測して判定してください。
"""

    def _save_classification(self, video_id: str, classification: Dict[str, Any]):
        """
        分類結果をデータベースに保存

        Args:
            video_id: 動画ID
            classification: 分類結果
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO llm_classifications (
                    video_id, model, prompt_version, output, created_at
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    video_id,
                    self.model,
                    "v1",
                    json.dumps(classification),
                    datetime.utcnow()
                )
            )
            self.db_conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to save classification: {e}")
            self.db_conn.rollback()

    def _create_tags(self, new_tag_proposals: List[Dict[str, str]]):
        """
        新規タグを作成

        Args:
            new_tag_proposals: 新規タグ提案のリスト
        """
        if not new_tag_proposals:
            return

        try:
            cursor = self.db_conn.cursor()

            for tag_proposal in new_tag_proposals:
                cursor.execute(
                    """
                    INSERT INTO tags (slug, name, category)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (slug) DO NOTHING
                    """,
                    (
                        tag_proposal.get("slug"),
                        tag_proposal.get("name"),
                        tag_proposal.get("category")
                    )
                )
                self.stats["tags_created"] += 1

            self.db_conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to create tags: {e}")
            self.db_conn.rollback()

    def _report_stats(self):
        """統計情報を報告"""
        logger.info("=" * 50)
        logger.info("Classification Statistics:")
        logger.info(f"  Videos processed: {self.stats['videos_processed']}")
        logger.info(f"  Netas classified: {self.stats['netas_classified']}")
        logger.info(f"  Non-netas: {self.stats['non_netas']}")
        logger.info(f"  Tags created: {self.stats['tags_created']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 50)


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("CLAUDE_API_KEY")
    db_conn = os.getenv("DATABASE_URL")

    if not api_key or not db_conn:
        logger.error("CLAUDE_API_KEY and DATABASE_URL are required in .env")
        exit(1)

    classifier = VideoClassifier(api_key, db_conn)
    classifier.run(limit=50)
