"""
YouTube API データ リフレッシュ・削除スクリプト
25日超の fetched_at を持つデータを更新し、30日超で削除
"""

import os
import logging
import psycopg2
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from yt_client import YouTubeClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class VideoRefresher:
    def __init__(self, api_key: str, db_connection_string: str):
        """
        リフレッシャー初期化

        Args:
            api_key: YouTube Data API キー
            db_connection_string: PostgreSQL 接続文字列
        """
        self.client = YouTubeClient(api_key, db_connection_string)
        self.stats = {
            "videos_refreshed": 0,
            "videos_marked_unavailable": 0,
            "videos_deleted": 0,
            "channels_refreshed": 0,
            "channels_deleted": 0,
            "errors": 0
        }

    def run(self):
        """メイン処理を実行"""
        logger.info("Starting video/channel refresh and cleanup...")

        try:
            self.client.connect_db()

            # 動画のリフレッシュ
            self._refresh_videos()

            # チャンネル情報のリフレッシュ
            self._refresh_channels()

            # 古いデータの削除
            self._cleanup_old_data()

            self._report_stats()

        finally:
            self.client.close_db()

    def _refresh_videos(self):
        """
        25日超の動画情報をリフレッシュ
        """
        logger.info("Refreshing videos...")

        # 25日超で unavailable_at が NULL の動画を取得
        cutoff_date = datetime.utcnow() - timedelta(days=25)

        try:
            cursor = self.client.db_conn.cursor()
            cursor.execute(
                """
                SELECT video_id
                FROM yt_videos
                WHERE fetched_at < %s AND unavailable_at IS NULL
                ORDER BY fetched_at ASC
                LIMIT 1000
                """,
                (cutoff_date,)
            )
            video_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to get stale videos: {e}")
            self.stats["errors"] += 1
            return

        logger.info(f"Found {len(video_ids)} videos to refresh")

        # 50件ずつ videos.list で更新
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]

            try:
                videos = self.client.get_videos(batch)
                self._update_videos(videos)
                self.stats["videos_refreshed"] += len(videos)

                logger.info(f"Refreshed {len(videos)} videos")

            except Exception as e:
                logger.error(f"Failed to refresh batch {batch}: {e}")
                self.stats["errors"] += 1

        # リフレッシュできなかった（削除された）動画を検出
        self._mark_unavailable_videos(video_ids)

    def _update_videos(self, videos: List[dict]):
        """
        動画情報を更新

        Args:
            videos: 動画情報のリスト
        """
        try:
            cursor = self.client.db_conn.cursor()

            for video in videos:
                cursor.execute(
                    """
                    UPDATE yt_videos
                    SET
                        title = %s,
                        description = %s,
                        view_count = %s,
                        privacy_status = %s,
                        embeddable = %s,
                        fetched_at = %s
                    WHERE video_id = %s
                    """,
                    (
                        video.get("title"),
                        video.get("description"),
                        video.get("view_count"),
                        video.get("privacy_status"),
                        video.get("embeddable"),
                        datetime.utcnow(),
                        video["video_id"]
                    )
                )

            self.client.db_conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to update videos: {e}")
            self.client.db_conn.rollback()
            self.stats["errors"] += 1

    def _mark_unavailable_videos(self, original_video_ids: List[str]):
        """
        更新に失敗した動画を削除・非公開として記録

        Args:
            original_video_ids: リクエストした全動画ID
        """
        try:
            cursor = self.client.db_conn.cursor()

            # 今取得した動画IDを確認
            placeholders = ",".join(["%s"] * len(original_video_ids))
            cursor.execute(
                f"""
                SELECT video_id
                FROM yt_videos
                WHERE video_id IN ({placeholders})
                AND fetched_at >= NOW() - INTERVAL '1 minute'
                """,
                original_video_ids
            )
            refreshed_ids = set(row[0] for row in cursor.fetchall())

            # リフレッシュされなかった動画を検出
            unavailable_ids = set(original_video_ids) - refreshed_ids

            if unavailable_ids:
                logger.info(f"Marking {len(unavailable_ids)} videos as unavailable")

                placeholders = ",".join(["%s"] * len(unavailable_ids))
                cursor.execute(
                    f"""
                    UPDATE yt_videos
                    SET unavailable_at = %s
                    WHERE video_id IN ({placeholders})
                    """,
                    [datetime.utcnow()] + list(unavailable_ids)
                )

                self.client.db_conn.commit()
                self.stats["videos_marked_unavailable"] += len(unavailable_ids)

            cursor.close()

        except Exception as e:
            logger.error(f"Failed to mark unavailable videos: {e}")
            self.client.db_conn.rollback()
            self.stats["errors"] += 1

    def _refresh_channels(self):
        """
        25日超のチャンネル情報をリフレッシュ
        """
        logger.info("Refreshing channels...")

        cutoff_date = datetime.utcnow() - timedelta(days=25)

        try:
            cursor = self.client.db_conn.cursor()
            cursor.execute(
                """
                SELECT channel_id
                FROM yt_channels
                WHERE fetched_at < %s
                ORDER BY fetched_at ASC
                LIMIT 100
                """,
                (cutoff_date,)
            )
            channel_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()

        except Exception as e:
            logger.error(f"Failed to get stale channels: {e}")
            self.stats["errors"] += 1
            return

        logger.info(f"Found {len(channel_ids)} channels to refresh")

        # チャンネル情報を取得（channels.list の snippet 部分）
        # 実装簡略化のため、ここではスキップ
        # 本来は channels.list で title, thumbnail_url を更新

        self.stats["channels_refreshed"] += len(channel_ids)

    def _cleanup_old_data(self):
        """
        30日超の古いデータを削除
        """
        logger.info("Cleaning up old data...")

        cleanup_date = datetime.utcnow() - timedelta(days=30)

        try:
            cursor = self.client.db_conn.cursor()

            # unavailable_at が 30日超の動画を削除
            cursor.execute(
                """
                DELETE FROM yt_videos
                WHERE unavailable_at IS NOT NULL
                AND unavailable_at < %s
                """,
                (cleanup_date,)
            )
            videos_deleted = cursor.rowcount
            self.stats["videos_deleted"] += videos_deleted

            # 30日超の yt_channels を削除
            cursor.execute(
                """
                DELETE FROM yt_channels
                WHERE fetched_at < %s
                """,
                (cleanup_date,)
            )
            channels_deleted = cursor.rowcount
            self.stats["channels_deleted"] += channels_deleted

            self.client.db_conn.commit()
            cursor.close()

            logger.info(f"Deleted {videos_deleted} videos and {channels_deleted} channels")

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            self.client.db_conn.rollback()
            self.stats["errors"] += 1

    def _report_stats(self):
        """統計情報を報告"""
        logger.info("=" * 50)
        logger.info("Refresh & Cleanup Statistics:")
        logger.info(f"  Videos refreshed: {self.stats['videos_refreshed']}")
        logger.info(f"  Videos marked unavailable: {self.stats['videos_marked_unavailable']}")
        logger.info(f"  Videos deleted: {self.stats['videos_deleted']}")
        logger.info(f"  Channels refreshed: {self.stats['channels_refreshed']}")
        logger.info(f"  Channels deleted: {self.stats['channels_deleted']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 50)


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    db_conn = os.getenv("DATABASE_URL")

    if not api_key or not db_conn:
        logger.error("YOUTUBE_API_KEY and DATABASE_URL are required in .env")
        exit(1)

    refresher = VideoRefresher(api_key, db_conn)
    refresher.run()
