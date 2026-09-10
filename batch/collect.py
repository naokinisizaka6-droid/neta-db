"""
YouTube データ差分収集スクリプト
approved チャンネルから新規動画を取得し yt_videos に保存
"""

import os
import logging
import psycopg2
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from yt_client import YouTubeClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class VideoCollector:
    def __init__(self, api_key: str, db_connection_string: str):
        """
        ビデオ収集器初期化

        Args:
            api_key: YouTube Data API キー
            db_connection_string: PostgreSQL 接続文字列
        """
        self.client = YouTubeClient(api_key, db_connection_string)
        self.db_conn_string = db_connection_string
        self.stats = {
            "channels_processed": 0,
            "new_videos_found": 0,
            "videos_saved": 0,
            "errors": 0
        }

    def run(self):
        """メイン処理を実行"""
        logger.info("Starting video collection...")

        try:
            self.client.connect_db()

            # 承認済みチャンネルを取得
            channels = self._get_approved_channels()
            logger.info(f"Found {len(channels)} approved channels")

            # 各チャンネルから新規動画を収集
            for channel_id, uploads_playlist_id, last_seen in channels:
                try:
                    self._collect_from_channel(channel_id, uploads_playlist_id, last_seen)
                except Exception as e:
                    logger.error(f"Error processing channel {channel_id}: {e}")
                    self.stats["errors"] += 1

            self._report_stats()

        finally:
            self.client.close_db()

    def _get_approved_channels(self) -> List[tuple]:
        """
        承認済みチャンネルを取得

        Returns:
            (channel_id, uploads_playlist_id, last_seen_published_at) のリスト
        """
        try:
            cursor = self.client.db_conn.cursor()
            cursor.execute(
                """
                SELECT channel_id, uploads_playlist_id, last_seen_published_at
                FROM channels
                WHERE status = %s AND uploads_playlist_id IS NOT NULL
                ORDER BY last_seen_published_at DESC NULLS LAST
                """,
                ("approved",)
            )
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Failed to get approved channels: {e}")
            return []

    def _collect_from_channel(
        self,
        channel_id: str,
        playlist_id: str,
        last_seen_published_at: Optional[datetime]
    ):
        """
        チャンネルから新規動画を収集

        Args:
            channel_id: YouTube チャンネルID
            playlist_id: アップロードプレイリストID
            last_seen_published_at: 前回の最後の公開日時
        """
        logger.info(f"Processing channel {channel_id}")

        # プレイリストアイテムを取得
        new_videos = []
        next_page_token = None
        newest_published_at = last_seen_published_at

        while True:
            playlist_data = self.client.get_playlist_items(
                playlist_id,
                max_results=50,
                page_token=next_page_token
            )

            for item in playlist_data.get("items", []):
                video_id = item.get("video_id")
                published_at_str = item.get("published_at")

                if not video_id or not published_at_str:
                    continue

                published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))

                # last_seen_published_at より新しいもののみ
                if last_seen_published_at is None or published_at > last_seen_published_at:
                    new_videos.append(video_id)

                    # 最新の published_at を記録
                    if newest_published_at is None or published_at > newest_published_at:
                        newest_published_at = published_at

                else:
                    # 昔のアイテムなので、ここでループ終了
                    break

            next_page_token = playlist_data.get("nextPageToken")
            if not next_page_token:
                break

        logger.info(f"Found {len(new_videos)} new videos in {channel_id}")

        # 新規動画を 50件ずつ詳細取得
        if new_videos:
            self.stats["new_videos_found"] += len(new_videos)
            self._fetch_and_save_videos(channel_id, new_videos)

        # last_seen_published_at を更新
        if newest_published_at:
            self._update_last_seen(channel_id, newest_published_at)

        self.stats["channels_processed"] += 1

    def _fetch_and_save_videos(self, channel_id: str, video_ids: List[str]):
        """
        動画詳細を取得して yt_videos に保存

        Args:
            channel_id: チャンネルID
            video_ids: 動画IDのリスト
        """
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]

            try:
                videos = self.client.get_videos(batch)
                self._save_videos_to_db(videos)
                logger.info(f"Saved {len(videos)} videos for {channel_id}")
                self.stats["videos_saved"] += len(videos)

            except Exception as e:
                logger.error(f"Failed to fetch videos {batch}: {e}")
                self.stats["errors"] += 1

    def _save_videos_to_db(self, videos: List[dict]):
        """
        動画情報をデータベースに保存（更新または挿入）

        Args:
            videos: 動画情報のリスト
        """
        try:
            cursor = self.client.db_conn.cursor()

            for video in videos:
                cursor.execute(
                    """
                    INSERT INTO yt_videos (
                        video_id, channel_id, title, description,
                        published_at, duration_sec, thumbnail_url,
                        embeddable, privacy_status, view_count, fetched_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (video_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        view_count = EXCLUDED.view_count,
                        fetched_at = EXCLUDED.fetched_at,
                        privacy_status = EXCLUDED.privacy_status
                    """,
                    (
                        video["video_id"],
                        video["channel_id"],
                        video["title"],
                        video["description"],
                        video["published_at"],
                        video["duration_sec"],
                        video["thumbnail_url"],
                        video["embeddable"],
                        video["privacy_status"],
                        video["view_count"],
                        datetime.utcnow()
                    )
                )

            self.client.db_conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to save videos: {e}")
            self.client.db_conn.rollback()
            raise

    def _update_last_seen(self, channel_id: str, published_at: datetime):
        """
        チャンネルの last_seen_published_at を更新

        Args:
            channel_id: チャンネルID
            published_at: 新しい最後の公開日時
        """
        try:
            cursor = self.client.db_conn.cursor()
            cursor.execute(
                """
                UPDATE channels
                SET last_seen_published_at = %s
                WHERE channel_id = %s
                """,
                (published_at, channel_id)
            )
            self.client.db_conn.commit()
            cursor.close()

        except Exception as e:
            logger.warning(f"Failed to update last_seen for {channel_id}: {e}")
            self.client.db_conn.rollback()

    def _report_stats(self):
        """統計情報を報告"""
        logger.info("=" * 50)
        logger.info("Collection Statistics:")
        logger.info(f"  Channels processed: {self.stats['channels_processed']}")
        logger.info(f"  New videos found: {self.stats['new_videos_found']}")
        logger.info(f"  Videos saved: {self.stats['videos_saved']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 50)


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    db_conn = os.getenv("DATABASE_URL")

    if not api_key or not db_conn:
        logger.error("YOUTUBE_API_KEY and DATABASE_URL are required in .env")
        exit(1)

    collector = VideoCollector(api_key, db_conn)
    collector.run()
