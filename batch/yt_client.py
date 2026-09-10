"""
YouTube Data API クライアント
search, playlistItems, videos エンドポイントのラッパー
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_httplib2 import AuthorizedHttp
import httplib2

logger = logging.getLogger(__name__)

class YouTubeClient:
    def __init__(self, api_key: str, db_connection_string: str):
        """
        YouTube Data API クライアント初期化

        Args:
            api_key: YouTube Data API キー（Simple API Key）
            db_connection_string: PostgreSQL 接続文字列
        """
        self.api_key = api_key
        self.db_conn_string = db_connection_string
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.db_conn = None

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
            logger.info("DB connection closed")

    def _log_quota(self, endpoint: str, units: int):
        """APIクォーター使用ログ"""
        if not self.db_conn:
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO api_quota_log (endpoint, units, called_at)
                VALUES (%s, %s, %s)
                """,
                (endpoint, units, datetime.utcnow())
            )
            self.db_conn.commit()
            cursor.close()
            logger.debug(f"Logged {units} units for {endpoint}")
        except Exception as e:
            logger.warning(f"Failed to log quota: {e}")

    def search_channels(self, query: str, max_results: int = 50, order: str = "relevance") -> List[Dict[str, Any]]:
        """
        チャンネルをキーワードで検索

        Args:
            query: 検索キーワード
            max_results: 最大結果数（50で1ユニット）
            order: 並び順（relevance, uploadDate, viewCount）

        Returns:
            チャンネル情報のリスト
        """
        results = []
        next_page_token = None

        while True:
            params = {
                "key": self.api_key,
                "type": "channel",
                "q": query,
                "part": "snippet",
                "maxResults": min(max_results, 50),
                "order": order,
                "pageToken": next_page_token
            }

            try:
                import requests
                response = requests.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                data = response.json()

                # クォーター: 50件で1ユニット
                units = (data.get("pageInfo", {}).get("resultsPerPage", 0) + 49) // 50
                self._log_quota("search.list", units)

                for item in data.get("items", []):
                    if item.get("id", {}).get("kind") == "youtube#channel":
                        results.append({
                            "channel_id": item["id"]["channelId"],
                            "title": item.get("snippet", {}).get("title"),
                            "thumbnail_url": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url")
                        })

                next_page_token = data.get("nextPageToken")
                if not next_page_token or len(results) >= max_results:
                    break

                time.sleep(0.1)  # レート制限対策

            except Exception as e:
                logger.error(f"Search channels failed: {e}")
                break

        return results[:max_results]

    def get_channel_uploads_playlist_id(self, channel_id: str) -> Optional[str]:
        """
        チャンネルのアップロード プレイリストID取得

        Args:
            channel_id: YouTube チャンネルID

        Returns:
            プレイリストID（見つからない場合は None）
        """
        params = {
            "key": self.api_key,
            "id": channel_id,
            "part": "contentDetails"
        }

        try:
            import requests
            response = requests.get(f"{self.base_url}/channels", params=params)
            response.raise_for_status()
            data = response.json()

            # クォーター: 1ユニット
            self._log_quota("channels.list", 1)

            items = data.get("items", [])
            if items:
                return items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

            return None

        except Exception as e:
            logger.error(f"Get uploads playlist failed for {channel_id}: {e}")
            return None

    def get_playlist_items(self, playlist_id: str, max_results: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        プレイリストアイテム取得（差分更新用）

        Args:
            playlist_id: プレイリストID
            max_results: 最大結果数（50で1ユニット）
            page_token: ページングトークン

        Returns:
            { "items": [...], "nextPageToken": "..." }
        """
        params = {
            "key": self.api_key,
            "playlistId": playlist_id,
            "part": "snippet",
            "maxResults": min(max_results, 50),
            "pageToken": page_token
        }

        try:
            import requests
            response = requests.get(f"{self.base_url}/playlistItems", params=params)
            response.raise_for_status()
            data = response.json()

            # クォーター: 50件で1ユニット
            units = (data.get("pageInfo", {}).get("resultsPerPage", 0) + 49) // 50
            self._log_quota("playlistItems.list", units)

            return {
                "items": [
                    {
                        "video_id": item.get("snippet", {}).get("resourceId", {}).get("videoId"),
                        "title": item.get("snippet", {}).get("title"),
                        "published_at": item.get("snippet", {}).get("publishedAt")
                    }
                    for item in data.get("items", [])
                ],
                "nextPageToken": data.get("nextPageToken")
            }

        except Exception as e:
            logger.error(f"Get playlist items failed for {playlist_id}: {e}")
            return {"items": [], "nextPageToken": None}

    def get_videos(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        複数の動画情報を一括取得

        Args:
            video_ids: YouTube 動画IDのリスト（最大50件）

        Returns:
            動画情報のリスト
        """
        if not video_ids:
            return []

        results = []

        # 50件ずつ分割（API制限）
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            params = {
                "key": self.api_key,
                "id": ",".join(batch),
                "part": "snippet,contentDetails,status,statistics"
            }

            try:
                import requests
                response = requests.get(f"{self.base_url}/videos", params=params)
                response.raise_for_status()
                data = response.json()

                # クォーター: 1ユニット per 50件
                self._log_quota("videos.list", 1)

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    status = item.get("status", {})
                    statistics = item.get("statistics", {})

                    # 秒数を取得（ISO 8601 Duration から変換）
                    duration_sec = self._parse_duration(content_details.get("duration", "PT0S"))

                    results.append({
                        "video_id": item["id"],
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "channel_id": snippet.get("channelId"),
                        "duration_sec": duration_sec,
                        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                        "embeddable": status.get("embeddable"),
                        "privacy_status": status.get("privacyStatus"),
                        "view_count": int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else None
                    })

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Get videos failed for batch {batch}: {e}")

        return results

    @staticmethod
    def _parse_duration(iso_duration: str) -> int:
        """ISO 8601 Duration から秒数に変換"""
        import re
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, iso_duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def get_quota_usage(self, start_date: Optional[str] = None) -> Dict[str, Any]:
        """
        API クォーター使用状況を集計

        Args:
            start_date: 集計開始日（デフォルトは今日）

        Returns:
            { "endpoint": units, ... }
        """
        if not self.db_conn:
            return {}

        try:
            cursor = self.db_conn.cursor()

            if start_date:
                cursor.execute(
                    """
                    SELECT endpoint, SUM(units) as total
                    FROM api_quota_log
                    WHERE DATE(called_at) >= %s
                    GROUP BY endpoint
                    ORDER BY total DESC
                    """,
                    (start_date,)
                )
            else:
                cursor.execute(
                    """
                    SELECT endpoint, SUM(units) as total
                    FROM api_quota_log
                    WHERE DATE(called_at) = CURRENT_DATE
                    GROUP BY endpoint
                    ORDER BY total DESC
                    """
                )

            result = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.close()
            return result

        except Exception as e:
            logger.error(f"Failed to get quota usage: {e}")
            return {}


if __name__ == "__main__":
    # テスト用
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    db_conn = os.getenv("DATABASE_URL")

    if not api_key or not db_conn:
        print("YOUTUBE_API_KEY and DATABASE_URL are required in .env")
        sys.exit(1)

    client = YouTubeClient(api_key, db_conn)
    client.connect_db()

    # テスト: 漫才のチャンネル検索
    results = client.search_channels("漫才 official", max_results=5)
    print("Search results:")
    for ch in results:
        print(f"  - {ch['title']} ({ch['channel_id']})")

    client.close_db()
