-- 実データシード: キングオブコント公式チャンネルより取得（2026-09-11時点、YouTube Data API検証済み）
-- チャンネル: キングオブコント (UCvHjqot4S5xj5J8RlQE-MYw) https://www.youtube.com/@kingofconte
-- 「ファイナリスト10組」紹介動画6本を採用（各動画1組のみ出演）

insert into comedians (slug, name, unit_type, is_active) values
  ('longcoat-daddy', 'ロングコートダディ', 'combi', true),
  ('rainbow', 'レインボー', 'combi', true),
  ('yadan', 'や団', 'combi', true),
  ('bernardo', 'ベルナルド', 'combi', true),
  ('fire-thunder', 'ファイヤーサンダー', 'combi', true),
  ('tom-brown', 'トム・ブラウン', 'combi', true)
on conflict (slug) do nothing;

insert into channels (channel_id, kind, status, uploads_playlist_id, last_seen_published_at, note) values
  ('UCvHjqot4S5xj5J8RlQE-MYw', 'contest', 'approved', 'UUvHjqot4S5xj5J8RlQE-MYw', now(), 'キングオブコント公式チャンネル')
on conflict (channel_id) do nothing;

insert into yt_channels (channel_id, title, thumbnail_url, fetched_at) values
  ('UCvHjqot4S5xj5J8RlQE-MYw', 'キングオブコント',
   'https://yt3.ggpht.com/fZsD1vbL0UwEH7YCm8z0gyqAzY8D6ivvuUeZ7hmCJvcBj8gjxnVyidMpCYf1ElmJI1cEogGQ=s800-c-k-c0x00ffffff-no-rj',
   now())
on conflict (channel_id) do update set fetched_at = excluded.fetched_at;

insert into yt_videos (video_id, channel_id, title, description, published_at, duration_sec, thumbnail_url, embeddable, privacy_status, view_count, fetched_at) values
  ('cH4TJif1EIQ', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】ロングコートダディ＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-05T09:15:03Z', 574, 'https://i.ytimg.com/vi/cH4TJif1EIQ/hqdefault.jpg', true, 'public', 271731, now()),
  ('TXkDI2ropAs', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】レインボー＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-05T09:00:29Z', 629, 'https://i.ytimg.com/vi/TXkDI2ropAs/hqdefault.jpg', true, 'public', 136394, now()),
  ('9GG2xjqIYA4', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】や団＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-04T09:45:01Z', 619, 'https://i.ytimg.com/vi/9GG2xjqIYA4/hqdefault.jpg', true, 'public', 37019, now()),
  ('YgCxd2qDR18', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】ベルナルド＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-04T09:30:18Z', 670, 'https://i.ytimg.com/vi/YgCxd2qDR18/hqdefault.jpg', true, 'public', 17430, now()),
  ('BuGvSeli8gE', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】ファイヤーサンダー＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-04T09:15:00Z', 682, 'https://i.ytimg.com/vi/BuGvSeli8gE/hqdefault.jpg', true, 'public', 31718, now()),
  ('o6W3caLNtpM', 'UCvHjqot4S5xj5J8RlQE-MYw', '【ファイナリスト10組】トム・ブラウン＜キングオブコント2025＞', 'キングオブコント2025 ファイナリスト紹介', '2025-10-03T09:15:05Z', 701, 'https://i.ytimg.com/vi/o6W3caLNtpM/hqdefault.jpg', true, 'public', 73834, now())
on conflict (video_id) do update set fetched_at = excluded.fetched_at;

-- ネタ作品（キングオブコントはコントのみの大会のため format='conte' で確定）
insert into neta_works (comedian_id, title, format, setting_note)
select c.id, v.neta_title, 'conte', null
from (values
  ('longcoat-daddy', 'ファイナリスト紹介 <キングオブコント2025>'),
  ('rainbow', 'ファイナリスト紹介 <キングオブコント2025>'),
  ('yadan', 'ファイナリスト紹介 <キングオブコント2025>'),
  ('bernardo', 'ファイナリスト紹介 <キングオブコント2025>'),
  ('fire-thunder', 'ファイナリスト紹介 <キングオブコント2025>'),
  ('tom-brown', 'ファイナリスト紹介 <キングオブコント2025>')
) as v(slug, neta_title)
join comedians c on c.slug = v.slug
where not exists (
  select 1 from neta_works nw where nw.comedian_id = c.id and nw.title = v.neta_title
);

insert into performances (neta_work_id, video_id, start_sec, end_sec, source, review_status)
select nw.id, x.video_id, 0, x.dur, 'manual', 'approved'
from (values
  ('longcoat-daddy', 'cH4TJif1EIQ', 574),
  ('rainbow', 'TXkDI2ropAs', 629),
  ('yadan', '9GG2xjqIYA4', 619),
  ('bernardo', 'YgCxd2qDR18', 670),
  ('fire-thunder', 'BuGvSeli8gE', 682),
  ('tom-brown', 'o6W3caLNtpM', 701)
) as x(slug, video_id, dur)
join comedians c on c.slug = x.slug
join neta_works nw on nw.comedian_id = c.id
on conflict (video_id, start_sec) do nothing;

-- 賞レース（キングオブコント 2025年 ファイナリスト）
insert into contests (slug, name) values ('koc', 'キングオブコント')
on conflict (slug) do nothing;

insert into contest_editions (contest_id, year)
select c.id, 2025 from contests c where c.slug = 'koc'
on conflict (contest_id, year) do nothing;

insert into contest_entries (edition_id, comedian_id, round)
select ce.id, cm.id, 'ファイナリスト'
from contest_editions ce
join contests c on c.id = ce.contest_id and c.slug = 'koc' and ce.year = 2025
join comedians cm on cm.slug in ('longcoat-daddy','rainbow','yadan','bernardo','fire-thunder','tom-brown')
on conflict (edition_id, comedian_id, round) do nothing;

-- performances.contest_entry_id をバックフィル（今回投入した6組・KOC2025のみ対象）
update performances p
set contest_entry_id = ce.id
from contest_entries ce
join contest_editions ced on ced.id = ce.edition_id
join contests c on c.id = ced.contest_id and c.slug = 'koc' and ced.year = 2025
join neta_works nw on nw.comedian_id = ce.comedian_id
where p.neta_work_id = nw.id
  and p.contest_entry_id is null
  and ce.comedian_id in (
    select id from comedians where slug in ('longcoat-daddy','rainbow','yadan','bernardo','fire-thunder','tom-brown')
  );
