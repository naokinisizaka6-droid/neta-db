# -*- coding: utf-8 -*-
"""
Bulk collection script: fetch real videos from verified official single-act
comedian YouTube channels and insert into Supabase.

Each channel here is a dedicated official channel for exactly one comedy
act, so every public/embeddable upload on the channel is treated as that
act's neta content (no per-video attribution ambiguity).
"""
import os
import re
import sys
import time
import psycopg2
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.environ["YOUTUBE_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

# channel_id, comedian_slug, comedian_name, unit_type, format, max_videos
CHANNELS = [
    ("UCyOJdwv5CrDMTSzGC71DaVA", "cotton", "コットン", "combi", "conte", 300),
    ("UCTA3AFI43NQ5Y9e9pzLZ2-Q", "hanako", "ハナコ", "trio", "conte", 300),
    ("UC9UI_fNxTbfEJImAg5Y7pOw", "rainbow", "レインボー", "combi", "conte", 300),
    ("UC9Bnr-dzm6CvQJnI8qVMNlw", "bakusho-mondai", "爆笑問題", "combi", "conte", 300),
    ("UCDmgvtV_dF-jdFmIcJYabLg", "nelsons", "ネルソンズ", "combi", "conte", 300),
    ("UCM5TUWTwC4i9IIiBCGpN25w", "knights", "ナイツ", "combi", "manzai", 100),
    ("UCRaaCxSF8nEpfG3ZHesXKxw", "gerardon", "ジェラードン", "trio", "conte", 300),
    ("UCkBhsreS_wIyoL_7hqNVRWg", "baiking", "バイきんぐ", "combi", "conte", 100),
    ("UCS9TpP7vSsk3ka0muNgl05w", "tensai-pianist", "天才ピアニスト", "combi", "conte", 300),
    ("UCOg6P-Ne5Hdd5tDtcOHDd-Q", "nakagawake", "中川家", "combi", "manzai", 300),
    ("UCqQR8xA6buvf6dHJhsGwH_Q", "miki", "ミキ", "combi", "manzai", 100),
    ("UCuWdyc0Mp7zRZd6KSPguCsA", "land", "ラランド", "combi", "conte", 300),
    ("UC7KdT8g_21PNkt6AZIO86WQ", "battles", "バッテリィズ", "combi", "manzai", 100),
    ("UClttgkLnnGDILHNrSkY5A-w", "diamond", "ダイヤモンド", "combi", "conte", 300),
    ("UCj6LDjEmXxeFhSmmcYblGmQ", "torosalmon", "とろサーモン", "combi", "conte", 300),
    ("UClVzR35NB31M0lupXJ4dpfQ", "punk-booboo", "パンクブーブー", "combi", "manzai", 300),
    ("UCWpDV9u0M6H1Lu0AgdUU3Iw", "diane", "ダイアン", "combi", "conte", 300),
    ("UC4bVLuPxbvIz9fuzru97KHw", "wagaya", "我が家", "combi", "conte", 300),
    ("UCNvcNd31bA-XERO6LGy4blw", "saraba-seishun", "さらば青春の光", "combi", "conte", 300),
    ("UCjJhVH1IT11tWnKTYp8jlRQ", "nagareboshi", "流れ星", "combi", "conte", 300),
    ("UCNKU6ZxHDLgzTgiz0Wnek-Q", "tokyo-hoteison", "東京ホテイソン", "combi", "conte", 300),
    ("UCS17iKEInkBuHkxtEcCnTTQ", "new-york", "ニューヨーク", "combi", "conte", 300),
    ("UCEz6Z7EgtSi-rPes-SIKJEg", "reiwa-roman", "令和ロマン", "combi", "manzai", 300),
    ("UCDishZFfEEFw_TRee8w4WRg", "kyu", "キュウ", "combi", "conte", 300),
    ("UC910qpzjNM0l5a7OyTskkKw", "a-masso", "Aマッソ", "combi", "conte", 300),
    ("UC4y-_Xwudf7gB5sXsbipDkQ", "don-decorte", "ドンデコルテ", "combi", "conte", 300),
    ("UCIR2mQ77wHrLMreV45nYhgw", "kamaitachi", "かまいたち", "combi", "manzai", 300),
    ("UCJcyQ-N0sbvwjYpDNXP9tsw", "non-style", "NON STYLE", "combi", "manzai", 300),
    ("UCw2AIP_0OmgYqgAJU1jOH-g", "zophy", "ゾフィー", "combi", "conte", 300),
    ("UCCBz0umWMLaxtYxx8fMJOKw", "rice", "ライス", "combi", "conte", 300),
    ("UCsvQg7ihb2U10RBNNKK6ZPw", "yarenz", "ヤーレンズ", "combi", "conte", 300),
]

EXISTING_SLUGS = {"rainbow"}  # already seeded via King of Conte batch


def api_get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_uploads_playlist(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    d = api_get(url)
    return d["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_playlist_video_ids(playlist_id, max_videos):
    ids = []
    page_token = ""
    while len(ids) < max_videos:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails"
            f"&playlistId={playlist_id}&maxResults=50&key={API_KEY}"
        )
        if page_token:
            url += f"&pageToken={page_token}"
        d = api_get(url)
        for item in d.get("items", []):
            ids.append(item["contentDetails"]["videoId"])
            if len(ids) >= max_videos:
                break
        page_token = d.get("nextPageToken")
        if not page_token:
            break
    return ids


def iso8601_to_sec(dur):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur or "")
    if not m or not any(m.groups()):
        return None
    h, mnt, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mnt * 60 + s


def get_videos_details(video_ids):
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        url = (
            f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics,status"
            f"&id={','.join(batch)}&key={API_KEY}"
        )
        d = api_get(url)
        for item in d.get("items", []):
            sn = item["snippet"]
            cd = item["contentDetails"]
            st = item.get("status", {})
            stat = item.get("statistics", {})
            if "duration" not in cd:
                continue  # live broadcast / premiere without standard duration
            duration_sec = iso8601_to_sec(cd["duration"])
            if duration_sec is None:
                continue  # unparseable duration format
            if not st.get("embeddable", True):
                continue
            if st.get("privacyStatus") != "public":
                continue
            if duration_sec <= 60:
                continue  # YouTube Shorts
            title_lower = sn["title"].lower()
            if "shorts" in title_lower or "#short" in title_lower:
                continue  # YouTube Shorts
            thumb = sn["thumbnails"].get("high", sn["thumbnails"].get("default"))["url"]
            results.append(
                {
                    "video_id": item["id"],
                    "title": sn["title"],
                    "description": (sn.get("description") or "")[:500],
                    "published_at": sn["publishedAt"],
                    "duration_sec": duration_sec,
                    "thumbnail_url": thumb,
                    "view_count": int(stat.get("viewCount", 0)),
                }
            )
    return results


def main():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    total_inserted = 0
    summary = []

    for channel_id, slug, name, unit_type, fmt, max_videos in CHANNELS:
        print(f"=== {name} ({channel_id}) ===")
        try:
            uploads = get_uploads_playlist(channel_id)
        except Exception as e:
            print(f"  SKIP channel lookup failed: {e}")
            continue

        try:
            video_ids = get_playlist_video_ids(uploads, max_videos)
        except Exception as e:
            print(f"  SKIP playlist fetch failed: {e}")
            continue

        if not video_ids:
            print("  no videos found, skip")
            continue

        try:
            details = get_videos_details(video_ids)
        except Exception as e:
            print(f"  SKIP video details failed: {e}")
            continue

        print(f"  fetched {len(details)} embeddable/public videos")

        # comedian
        if slug not in EXISTING_SLUGS:
            cur.execute(
                "insert into comedians (slug, name, unit_type, is_active) values (%s,%s,%s,true) on conflict (slug) do nothing",
                (slug, name, unit_type),
            )
        cur.execute("select id from comedians where slug=%s", (slug,))
        comedian_id = cur.fetchone()[0]

        # channel whitelist entry
        cur.execute(
            """insert into channels (channel_id, comedian_id, kind, status, uploads_playlist_id, last_seen_published_at, note)
               values (%s,%s,'comedian','approved',%s, now(), %s)
               on conflict (channel_id) do update set last_seen_published_at = now()""",
            (channel_id, comedian_id, uploads, f"{name} 公式チャンネル"),
        )

        cur.execute(
            """insert into yt_channels (channel_id, title, thumbnail_url, fetched_at)
               values (%s,%s,%s, now())
               on conflict (channel_id) do update set fetched_at = now()""",
            (channel_id, name, ""),
        )

        inserted_this_channel = 0
        for v in details:
            cur.execute(
                """insert into yt_videos (video_id, channel_id, title, description, published_at,
                     duration_sec, thumbnail_url, embeddable, privacy_status, view_count, fetched_at)
                   values (%s,%s,%s,%s,%s,%s,%s,true,'public',%s, now())
                   on conflict (video_id) do update set fetched_at = now()""",
                (
                    v["video_id"],
                    channel_id,
                    v["title"],
                    v["description"],
                    v["published_at"],
                    v["duration_sec"],
                    v["thumbnail_url"],
                    v["view_count"],
                ),
            )

            cur.execute(
                """insert into neta_works (comedian_id, title, format, setting_note)
                   select %s,%s,%s,null
                   where not exists (select 1 from neta_works where comedian_id=%s and title=%s)
                   returning id""",
                (comedian_id, v["title"], fmt, comedian_id, v["title"]),
            )
            row = cur.fetchone()
            if row:
                neta_work_id = row[0]
            else:
                cur.execute(
                    "select id from neta_works where comedian_id=%s and title=%s",
                    (comedian_id, v["title"]),
                )
                neta_work_id = cur.fetchone()[0]

            cur.execute(
                """insert into performances (neta_work_id, video_id, start_sec, end_sec, source, review_status)
                   values (%s,%s,0,%s,'manual','approved')
                   on conflict (video_id, start_sec) do nothing""",
                (neta_work_id, v["video_id"], v["duration_sec"]),
            )
            inserted_this_channel += 1

        total_inserted += inserted_this_channel
        summary.append((name, inserted_this_channel))
        print(f"  inserted/updated {inserted_this_channel} neta videos")
        time.sleep(0.2)

    print("\n=== SUMMARY ===")
    for name, count in summary:
        print(f"{name}: {count}")
    print(f"TOTAL: {total_inserted}")

    conn.close()


if __name__ == "__main__":
    main()
