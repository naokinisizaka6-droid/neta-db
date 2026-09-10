-- ネタDB 初期スキーマ
-- Supabase (PostgreSQL) 用 DDL

-- ================= A. 自動データ =================

create table if not exists comedians (
  id           bigserial primary key,
  slug         text unique not null,
  name         text not null,
  name_kana    text,
  unit_type    text not null check (unit_type in ('combi','trio','pin','unit','other')),
  agency       text,
  formed_year  int,
  is_active    boolean not null default true,
  created_at   timestamptz not null default now()
);
comment on table comedians is '芸人マスタ';
create index on comedians (slug);
create index on comedians (name);

create table if not exists comedian_members (
  id           bigserial primary key,
  comedian_id  bigint not null references comedians(id) on delete cascade,
  name         text not null,
  role         text check (role in ('boke','tsukkomi','other')),
  created_at   timestamptz not null default now()
);
comment on table comedian_members is 'コンビ・トリオのメンバー';

create table if not exists channels (
  channel_id              text primary key,
  comedian_id             bigint references comedians(id) on delete set null,
  kind                    text not null check (kind in ('comedian','agency','contest','tv','theater','other')),
  status                  text not null default 'candidate'
                            check (status in ('candidate','approved','rejected')),
  uploads_playlist_id     text,
  last_seen_published_at  timestamptz,
  note                    text,
  created_at              timestamptz not null default now()
);
comment on table channels is 'YouTubeチャンネルホワイトリスト';
create index on channels (status);
create index on channels (comedian_id);

create table if not exists contests (
  id    bigserial primary key,
  slug  text unique not null,
  name  text not null,
  created_at timestamptz not null default now()
);
comment on table contests is '賞レース定義（M-1, KOTC等）';

create table if not exists contest_editions (
  id          bigserial primary key,
  contest_id  bigint not null references contests(id) on delete cascade,
  year        int not null,
  unique (contest_id, year),
  created_at  timestamptz not null default now()
);
comment on table contest_editions is '賞レース（年別版）';

create table if not exists contest_entries (
  id           bigserial primary key,
  edition_id   bigint not null references contest_editions(id) on delete cascade,
  comedian_id  bigint not null references comedians(id) on delete cascade,
  round        text not null,
  order_no     int,
  rank         int,
  score        numeric,
  unique (edition_id, comedian_id, round),
  created_at   timestamptz not null default now()
);
comment on table contest_entries is '賞レース参加記録';
create index on contest_entries (edition_id);
create index on contest_entries (comedian_id);

create table if not exists neta_works (
  id            bigserial primary key,
  comedian_id   bigint not null references comedians(id) on delete cascade,
  title         text,
  format        text not null check (format in ('manzai','conte','pin','other')),
  setting_note  text,
  created_at    timestamptz not null default now()
);
comment on table neta_works is 'ネタ作品定義';
create index on neta_works (comedian_id);

create table if not exists performances (
  id                bigserial primary key,
  neta_work_id      bigint references neta_works(id) on delete set null,
  video_id          text not null,
  start_sec         int not null default 0,
  end_sec           int,
  contest_entry_id  bigint references contest_entries(id) on delete set null,
  source            text not null check (source in ('llm','manual')),
  review_status     text not null default 'pending'
                      check (review_status in ('pending','approved','rejected')),
  created_at        timestamptz not null default now(),
  unique (video_id, start_sec)
);
comment on table performances is 'ネタのパフォーマンス（動画上での位置）';
create index on performances (video_id);
create index on performances (neta_work_id);
create index on performances (review_status);

create table if not exists tags (
  id        bigserial primary key,
  slug      text unique not null,
  name      text not null,
  category  text not null check (category in ('place','relation','job','theme','style')),
  created_at timestamptz not null default now()
);
comment on table tags is 'ネタの設定タグ体系';
create index on tags (category);

create table if not exists neta_work_tags (
  neta_work_id  bigint not null references neta_works(id) on delete cascade,
  tag_id        bigint not null references tags(id) on delete cascade,
  source        text not null check (source in ('llm','manual')),
  confidence    real,
  status        text not null default 'proposed'
                  check (status in ('proposed','approved','rejected')),
  created_at    timestamptz not null default now(),
  primary key (neta_work_id, tag_id)
);
comment on table neta_work_tags is 'ネタとタグの関連（LLMまたは人手）';
create index on neta_work_tags (status);

create table if not exists takedown_requests (
  id           bigserial primary key,
  target_url   text not null,
  requester    text,
  reason       text,
  status       text not null default 'open' check (status in ('open','done','rejected')),
  created_at   timestamptz not null default now()
);
comment on table takedown_requests is '削除・非公開申請';
create index on takedown_requests (status);

-- ================= B. YouTube API データ (30日ルール) =================

create table if not exists yt_channels (
  channel_id     text primary key references channels(channel_id) on delete cascade,
  title          text,
  thumbnail_url  text,
  fetched_at     timestamptz not null
);
comment on table yt_channels is 'YouTubeチャンネル情報（APIメタデータ）';
create index on yt_channels (fetched_at);

create table if not exists yt_videos (
  video_id        text primary key,
  channel_id      text not null references channels(channel_id) on delete cascade,
  title           text,
  description     text,
  published_at    timestamptz,
  duration_sec    int,
  thumbnail_url   text,
  embeddable      boolean,
  privacy_status  text,
  view_count      bigint,
  fetched_at      timestamptz not null,
  unavailable_at  timestamptz,
  created_at      timestamptz not null default now()
);
comment on table yt_videos is 'YouTube動画情報（APIメタデータ）';
create index on yt_videos (fetched_at);
create index on yt_videos (channel_id);
create index on yt_videos (published_at);

-- ================= C. LLM 派生データ =================

create table if not exists llm_classifications (
  id              bigserial primary key,
  video_id        text not null,
  model           text not null,
  prompt_version  text not null,
  output          jsonb not null,
  created_at      timestamptz not null default now()
);
comment on table llm_classifications is 'Claude APIでの分類結果（生JSON）';
create index on llm_classifications (video_id);
create index on llm_classifications (created_at);

create table if not exists api_quota_log (
  id        bigserial primary key,
  endpoint  text not null,
  units     int not null,
  called_at timestamptz not null default now()
);
comment on table api_quota_log is 'YouTube/Claude APIクォーター使用ログ';
create index on api_quota_log (called_at);

-- ================= RLS (Row Level Security) - Supabase 用 =================

-- API データは認証ユーザーのみ表示（デフォルト無効、必要に応じて有効化）
-- 申請ユーザーのみ削除申請可能
-- （詳細は Next.js/Streamlit の権限チェックで処理）

-- ================= Cleanup Policy =================

-- 30日以上のゴミ掃除（手動実行推奨、あるいはクローンジョブ）
-- DELETE FROM yt_videos WHERE fetched_at < now() - interval '30 days' AND unavailable_at IS NOT NULL;
-- DELETE FROM yt_channels WHERE fetched_at < now() - interval '30 days';
