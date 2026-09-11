# -*- coding: utf-8 -*-
"""
LLM classification pass: for every currently-approved performance, ask
Claude whether the video title indicates genuine neta (manzai/conte/pin)
content, as opposed to talk segments, Q&A, radio, making-of, announcements,
live streams, interviews, vlogs, etc.

Non-neta videos are set to performances.review_status = 'rejected' so they
disappear from all public listings while remaining in the DB for audit.
Raw model output is recorded in llm_classifications per the project design.
"""
import json
import os
import time
import psycopg2
import anthropic

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
MODEL = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "classify_neta_v1"

DB_PARAMS = dict(
    host="db.jooicdngkhrdmqkpiqci.supabase.co",
    port=6543,
    dbname="postgres",
    user="postgres",
    password="***REMOVED_DB_PASSWORD***",
)

BATCH_SIZE = 25

SYSTEM_PROMPT = """あなたはお笑い動画データベースのキュレーターです。
YouTube動画のタイトル一覧が渡されます。各動画が実際の「ネタ」動画
（漫才・コント・ピン芸など、その芸人が台本のある演芸を最初から最後まで
演じている動画）かどうかを判定してください。

以下はネタではないと判定してください（タイトルが一見ネタ風でも該当すれば非ネタ）：
- トーク、雑談、Q&A、視聴者相談、悩み相談、あるあるトーク
- ラジオ、生配信、生放送のアーカイブ、ポッドキャスト形式（#数字のエピソード番号のみの企画）
- メイキング、舞台裏、密着、オフショット
- インタビュー、告知、記者会見、グッズ紹介
- 他の番組の紹介・感想・解説動画、ニュースまとめ、「〜まとめ」系
- vlog、日常、ロケ企画（ネタ実演を伴わないもの）
- トレーラー、予告編（本編の一部抜粋でないもの）
- ドッキリ企画、罰ゲーム企画
- AIとのコラボ・AI生成物を扱う企画（「AIに〜させてみた」等）
- 大富豪・選手権・診断・ランキング形式のゲームバラエティ企画
  （出演者同士で競う/採点する形式で、一人の芸人がネタを演じるものではない）
- 「あるあるドラマ」「医療ドラマ」等、エピソード仕立ての寸劇シリーズ
  （実際のコント公演とは異なる、YouTube用の連続寸劇コンテンツ）
- 複数の芸人がコラボして雑談・企画を進行するだけの動画

以下は明確にネタと判定してください：
- タイトルに「コント」「漫才」「ネタ」「ピン芸」が明記され、かつ上記の
  非ネタ要素（トーク・企画色）を含まないもの
- 「単独ライブ」「M-1」「キングオブコント」等の演芸大会・単独公演からの
  ネタ映像

回答は必ず以下のJSON配列のみで返してください。説明文は不要です。
[{"id": 1, "is_neta": true, "format": "manzai"}, {"id": 2, "is_neta": false, "format": null}, ...]

formatは is_neta が true の場合のみ "manzai" か "conte" のいずれかを推定して入れてください。
判別できない場合は "conte" としてください。"""


def classify_batch(client, items):
    """items: list of (id, title) tuples"""
    lines = [f'{i}. (id={vid}) {title}' for i, (vid, title) in enumerate(items, 1)]
    user_content = "\n".join(lines)

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    text = resp.content[0].text.strip()
    # モデルがコードブロックで返す場合に対応
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def main():
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        """
        select p.id, p.video_id, nw.id as neta_work_id, coalesce(nw.title, yv.title) as title
        from performances p
        join neta_works nw on nw.id = p.neta_work_id
        left join yt_videos yv on yv.video_id = p.video_id
        where p.review_status = 'approved'
        order by p.id
        """
    )
    rows = cur.fetchall()
    print(f"target performances: {len(rows)}")

    total_rejected = 0
    total_processed = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        items = [(r[0], r[3]) for r in batch]  # (performance_id, title)
        perf_by_id = {r[0]: r for r in batch}

        try:
            results = classify_batch(client, items)
        except Exception as e:
            print(f"  batch {i//BATCH_SIZE} FAILED: {e}")
            time.sleep(2)
            continue

        for j, res in enumerate(results):
            if j >= len(items):
                break
            perf_id, title = items[j]
            is_neta = res.get("is_neta", True)
            fmt = res.get("format")

            # 生の判定結果を記録
            perf_row = perf_by_id.get(perf_id)
            video_id = perf_row[1] if perf_row else None
            if video_id:
                cur.execute(
                    """insert into llm_classifications (video_id, model, prompt_version, output)
                       values (%s,%s,%s,%s)""",
                    (video_id, MODEL, PROMPT_VERSION, json.dumps(res, ensure_ascii=False)),
                )

            if not is_neta:
                cur.execute(
                    "update performances set review_status='rejected' where id=%s",
                    (perf_id,),
                )
                total_rejected += 1
            elif fmt in ("manzai", "conte"):
                neta_work_id = perf_row[2]
                cur.execute(
                    "update neta_works set format=%s where id=%s",
                    (fmt, neta_work_id),
                )
            total_processed += 1

        print(f"  batch {i//BATCH_SIZE + 1}/{(len(rows)+BATCH_SIZE-1)//BATCH_SIZE}: "
              f"processed {total_processed}, rejected so far {total_rejected}")
        time.sleep(0.3)

    print(f"\nTOTAL processed: {total_processed}, rejected (non-neta): {total_rejected}")
    conn.close()


if __name__ == "__main__":
    main()
