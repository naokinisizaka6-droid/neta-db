"""
ネタDB 管理画面 (Streamlit)
pending ステータスのネタを確認・承認
"""

import os
import json
import streamlit as st
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ページ設定
st.set_page_config(
    page_title="ネタDB 管理画面",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 ネタDB 管理画面")

# DB 接続
@st.cache_resource
def get_db_connection():
    """DB接続をキャッシュ"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        st.error("DATABASE_URL is not set in .env")
        st.stop()
    return psycopg2.connect(db_url)

db_conn = get_db_connection()

# ===== ユーティリティ関数 =====

def get_pending_performances(limit: int = 100) -> List[Dict[str, Any]]:
    """pending ステータスの performances を取得"""
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            """
            SELECT
                p.id,
                p.video_id,
                p.start_sec,
                p.end_sec,
                p.source,
                p.review_status,
                p.created_at,
                yv.title,
                yv.description,
                yv.duration_sec,
                yv.channel_id,
                lc.output
            FROM performances p
            LEFT JOIN yt_videos yv ON p.video_id = yv.video_id
            LEFT JOIN llm_classifications lc ON yv.video_id = lc.video_id
            WHERE p.review_status = 'pending'
            ORDER BY
                CASE WHEN lc.output IS NOT NULL
                    THEN (lc.output->>'confidence')::float
                    ELSE 1.0
                END ASC,
                p.created_at ASC
            LIMIT %s
            """,
            (limit,)
        )
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    except Exception as e:
        st.error(f"Failed to get pending performances: {e}")
        return []

def get_stats() -> Dict[str, Any]:
    """統計情報を取得"""
    try:
        cursor = db_conn.cursor()

        # pending 件数
        cursor.execute("SELECT COUNT(*) FROM performances WHERE review_status = 'pending'")
        pending_count = cursor.fetchone()[0]

        # 承認済み件数
        cursor.execute("SELECT COUNT(*) FROM performances WHERE review_status = 'approved'")
        approved_count = cursor.fetchone()[0]

        # ネタ作品数
        cursor.execute("SELECT COUNT(*) FROM neta_works")
        neta_count = cursor.fetchone()[0]

        # 芸人数
        cursor.execute("SELECT COUNT(*) FROM comedians WHERE is_active = true")
        comedian_count = cursor.fetchone()[0]

        # 今日のAPIクォーター
        cursor.execute(
            """
            SELECT COALESCE(SUM(units), 0) FROM api_quota_log
            WHERE DATE(called_at) = CURRENT_DATE
            """
        )
        quota_today = cursor.fetchone()[0]

        cursor.close()

        return {
            "pending": pending_count,
            "approved": approved_count,
            "netas": neta_count,
            "comedians": comedian_count,
            "quota_today": quota_today
        }

    except Exception as e:
        st.error(f"Failed to get stats: {e}")
        return {}

def approve_performance(perf_id: int):
    """performance を承認"""
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            "UPDATE performances SET review_status = %s WHERE id = %s",
            ("approved", perf_id)
        )
        db_conn.commit()
        cursor.close()
        st.success("✅ Approved!")
    except Exception as e:
        st.error(f"Failed to approve: {e}")

def reject_performance(perf_id: int):
    """performance を却下"""
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            "UPDATE performances SET review_status = %s WHERE id = %s",
            ("rejected", perf_id)
        )
        db_conn.commit()
        cursor.close()
        st.success("❌ Rejected!")
    except Exception as e:
        st.error(f"Failed to reject: {e}")

# ===== UI =====

# サイドバー
with st.sidebar:
    st.header("📊 ダッシュボード")
    stats = get_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pending", stats.get("pending", 0), delta="need review")
    with col2:
        st.metric("Approved", stats.get("approved", 0), delta="✅")

    col3, col4 = st.columns(2)
    with col3:
        st.metric("Netas", stats.get("netas", 0))
    with col4:
        st.metric("Comedians", stats.get("comedians", 0))

    st.divider()

    col5, col6 = st.columns(2)
    with col5:
        st.metric("API Quota (Today)", stats.get("quota_today", 0))

    st.divider()

    # フィルター
    limit = st.slider("表示件数", 10, 500, 100, step=10)

# メインコンテンツ
st.header("📝 Pending レビュー")

performances = get_pending_performances(limit)

if not performances:
    st.info("✅ All performances are reviewed!")
else:
    st.subheader(f"{len(performances)} 件のレビュー待ち")

    for idx, perf in enumerate(performances, 1):
        with st.expander(f"#{idx} {perf.get('title', 'Unknown')[:50]}...", expanded=(idx == 1)):
            col1, col2 = st.columns([2, 1])

            with col1:
                # 動画情報
                st.subheader(perf.get("title", "Unknown"))
                st.caption(f"Channel: {perf.get('channel_id')}")
                st.caption(f"Duration: {perf.get('duration_sec', 0)} sec | Segment: {perf.get('start_sec', 0)}～{perf.get('end_sec', 'END')}")

                # 説明文
                if perf.get("description"):
                    st.text_area("Description", value=perf["description"][:300], height=60, disabled=True)

                # LLM 分類結果
                if perf.get("output"):
                    try:
                        classification = json.loads(perf["output"])
                        st.subheader("🤖 LLM Classification")

                        col_conf, col_format = st.columns(2)
                        with col_conf:
                            confidence = classification.get("confidence", 0)
                            st.metric("Confidence", f"{confidence:.2%}")

                        with col_format:
                            st.metric("Format", classification.get("format", "unknown"))

                        if classification.get("performers"):
                            st.write(f"**Performers:** {', '.join(classification['performers'])}")

                        if classification.get("setting_tags"):
                            tags = ", ".join([f"`{tag}`" for tag in classification["setting_tags"]])
                            st.write(f"**Tags:** {tags}")

                        if classification.get("new_tag_proposals"):
                            st.write("**New Tag Proposals:**")
                            for proposal in classification["new_tag_proposals"]:
                                st.write(f"- {proposal.get('name')} (`{proposal.get('slug')}`)")

                    except json.JSONDecodeError:
                        st.warning("Invalid JSON in classification output")

            with col2:
                # YouTube 埋め込み
                st.subheader("📺 Preview")

                video_id = perf.get("video_id")
                start_sec = perf.get("start_sec", 0)
                end_sec = perf.get("end_sec")

                if video_id:
                    # YouTube 埋め込みプレイヤー
                    if end_sec:
                        st.video(f"https://www.youtube.com/embed/{video_id}?start={start_sec}&end={end_sec}")
                    else:
                        st.video(f"https://www.youtube.com/embed/{video_id}?start={start_sec}")

            # アクション
            st.divider()
            col_action1, col_action2, col_action3 = st.columns(3)

            perf_id = perf.get("id")
            if perf_id:
                with col_action1:
                    if st.button("✅ Approve", key=f"approve_{perf_id}"):
                        approve_performance(perf_id)
                        st.rerun()

                with col_action2:
                    if st.button("❌ Reject", key=f"reject_{perf_id}"):
                        reject_performance(perf_id)
                        st.rerun()

                with col_action3:
                    if st.button("📝 Edit", key=f"edit_{perf_id}"):
                        st.info("Edit feature will be implemented soon")

# フッター
st.divider()
st.caption("🎭 ネタDB Admin Dashboard | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
