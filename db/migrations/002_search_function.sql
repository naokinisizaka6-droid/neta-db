-- ネタ検索用 RPC 関数
-- web/lib/supabase.ts の searchNetas() から呼び出される
-- 承認済み(performances.review_status='approved')のネタのみを対象に、
-- 芸人名・ネタタイトル・設定・タグを横断検索する

create or replace function search_netas(search_query text, result_limit int default 20)
returns table (
  neta_id        bigint,
  neta_title     text,
  comedian_name  text,
  format         text,
  duration_sec   int,
  thumbnail_url  text,
  youtube_url    text,
  tags           text[]
)
language sql
stable
as $$
  select
    nw.id as neta_id,
    nw.title as neta_title,
    c.name as comedian_name,
    nw.format,
    v.duration_sec,
    v.thumbnail_url,
    'https://www.youtube.com/watch?v=' || p.video_id as youtube_url,
    coalesce(tag_agg.tags, array[]::text[]) as tags
  from neta_works nw
  join comedians c on c.id = nw.comedian_id
  join performances p on p.neta_work_id = nw.id and p.review_status = 'approved'
  left join yt_videos v on v.video_id = p.video_id
  left join lateral (
    select array_agg(t.name) as tags
    from neta_work_tags nwt
    join tags t on t.id = nwt.tag_id
    where nwt.neta_work_id = nw.id and nwt.status = 'approved'
  ) tag_agg on true
  where
    nw.title ilike '%' || search_query || '%'
    or c.name ilike '%' || search_query || '%'
    or nw.setting_note ilike '%' || search_query || '%'
    or exists (
      select 1 from neta_work_tags nwt2
      join tags t2 on t2.id = nwt2.tag_id
      where nwt2.neta_work_id = nw.id
        and nwt2.status = 'approved'
        and t2.name ilike '%' || search_query || '%'
    )
  order by nw.id desc
  limit result_limit;
$$;

comment on function search_netas is 'ネタ横断検索（芸人名・タイトル・設定・タグ）承認済みのみ対象';
