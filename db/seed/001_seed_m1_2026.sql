-- 実データシード: M-1グランプリ公式チャンネルより取得（2026-09-11時点、YouTube Data API検証済み）
-- チャンネル: M-1グランプリ (UCCTMMUDmBo6PXc7GmVHPrkw) https://www.youtube.com/@m1grandprix
-- 「ナイスアマチュア賞」1回戦単独ネタ5本を採用（各動画1組のみ出演のため neta_works と1:1対応しやすい）

-- 芸人
insert into comedians (slug, name, unit_type, is_active) values
  ('toranisanpo', 'トラニサンポ', 'combi', true),
  ('yamadake-blues', '山田家ブルース', 'combi', true),
  ('panda-kisoku', 'パンダ規則', 'combi', true),
  ('tango-nihime', '丹後2姫', 'combi', true),
  ('kensouken', 'ケンソウ犬', 'combi', true)
on conflict (slug) do nothing;

-- チャンネル（ホワイトリスト登録・承認済み）
insert into channels (channel_id, kind, status, uploads_playlist_id, last_seen_published_at, note) values
  ('UCCTMMUDmBo6PXc7GmVHPrkw', 'contest', 'approved', 'UUCTMMUDmBo6PXc7GmVHPrkw', now(), 'M-1グランプリ公式チャンネル')
on conflict (channel_id) do nothing;

insert into yt_channels (channel_id, title, thumbnail_url, fetched_at) values
  ('UCCTMMUDmBo6PXc7GmVHPrkw', 'M-1グランプリ',
   'https://yt3.ggpht.com/eDLSHgi35tpHsIykAYJUgz25chnKn9Z0YwJM9CQfdcWsIoUhdp1I_T2cmbT_Qx7omPeG2ePaAw=s800-c-k-c0x00ffffff-no-rj',
   now())
on conflict (channel_id) do update set fetched_at = excluded.fetched_at;

-- YouTube動画メタデータ（API取得値そのまま）
insert into yt_videos (video_id, channel_id, title, description, published_at, duration_sec, thumbnail_url, embeddable, privacy_status, view_count, fetched_at) values
  ('nGUyOxMFNfg', 'UCCTMMUDmBo6PXc7GmVHPrkw', '【ナイスアマチュア賞】 トラニサンポ ＜出だしからフルスロットル！＞ 【M-1グランプリ2026】', 'M-1からニュースター誕生!? ナイスアマチュア賞2026 9/4(金) [大阪] SPACE 14', '2026-09-10T10:35:37Z', 132, 'https://i.ytimg.com/vi/nGUyOxMFNfg/hqdefault.jpg', true, 'public', 14178, now()),
  ('4Ku11ZjY1Fo', 'UCCTMMUDmBo6PXc7GmVHPrkw', '【ナイスアマチュア賞】 山田家ブルース ＜親子愛もれもれ！＞ 【M-1グランプリ2026】', 'M-1からニュースター誕生!? ナイスアマチュア賞2026 9/3(木) [大阪] SPACE 14', '2026-09-09T10:50:36Z', 128, 'https://i.ytimg.com/vi/4Ku11ZjY1Fo/hqdefault.jpg', true, 'public', 16808, now()),
  ('FzdfFh05vqk', 'UCCTMMUDmBo6PXc7GmVHPrkw', '【ナイスアマチュア賞】 パンダ規則 ＜「夢と現実」白黒つけたい！＞ 【M-1グランプリ2026】', 'M-1からニュースター誕生!? ナイスアマチュア賞2026 9/2(水) [大阪] SPACE 14', '2026-09-08T10:35:24Z', 122, 'https://i.ytimg.com/vi/FzdfFh05vqk/hqdefault.jpg', true, 'public', 19142, now()),
  ('ro3uMVGn-yA', 'UCCTMMUDmBo6PXc7GmVHPrkw', '【ナイスアマチュア賞】 丹後2姫 ＜難波に降りたった2人の姫＞ 【M-1グランプリ2026】', 'M-1からニュースター誕生!? ナイスアマチュア賞2026 9/1(火) [大阪] SPACE 14', '2026-09-07T10:45:16Z', 134, 'https://i.ytimg.com/vi/ro3uMVGn-yA/hqdefault.jpg', true, 'public', 22147, now()),
  ('QmogPZ7WfFU', 'UCCTMMUDmBo6PXc7GmVHPrkw', '【ナイスアマチュア賞】 ケンソウ犬 ＜宮城の期待の星！＞ 【M-1グランプリ2026】', 'M-1からニュースター誕生!? ナイスアマチュア賞2026 8/30(日) [宮城] ぐりりホール', '2026-09-07T10:35:36Z', 139, 'https://i.ytimg.com/vi/QmogPZ7WfFU/hqdefault.jpg', true, 'public', 10762, now())
on conflict (video_id) do update set fetched_at = excluded.fetched_at;

-- ネタ作品（M-1は漫才のみの大会のため format='manzai' で確定）
insert into neta_works (comedian_id, title, format, setting_note)
select c.id, v.neta_title, 'manzai', v.setting_note
from (values
  ('toranisanpo', '出だしからフルスロットル！', '出だしからフルスロットル！'),
  ('yamadake-blues', '親子愛もれもれ！', '親子愛もれもれ！'),
  ('panda-kisoku', '「夢と現実」白黒つけたい！', '「夢と現実」白黒つけたい！'),
  ('tango-nihime', '難波に降りたった2人の姫', '難波に降りたった2人の姫'),
  ('kensouken', '宮城の期待の星！', '宮城の期待の星！')
) as v(slug, neta_title, setting_note)
join comedians c on c.slug = v.slug
where not exists (
  select 1 from neta_works nw where nw.comedian_id = c.id and nw.title = v.neta_title
);

-- パフォーマンス（動画全体を1本のネタとして対応、公式チャンネルの確認済み内容のため承認済み扱い）
insert into performances (neta_work_id, video_id, start_sec, end_sec, source, review_status)
select nw.id, x.video_id, 0, x.dur, 'manual', 'approved'
from (values
  ('toranisanpo', 'nGUyOxMFNfg', 132),
  ('yamadake-blues', '4Ku11ZjY1Fo', 128),
  ('panda-kisoku', 'FzdfFh05vqk', 122),
  ('tango-nihime', 'ro3uMVGn-yA', 134),
  ('kensouken', 'QmogPZ7WfFU', 139)
) as x(slug, video_id, dur)
join comedians c on c.slug = x.slug
join neta_works nw on nw.comedian_id = c.id
on conflict (video_id, start_sec) do nothing;

-- タグ（公式説明文に明記された会場地・テーマから採録。推測での付与は行っていない）
insert into tags (slug, name, category) values
  ('osaka', '大阪', 'place'),
  ('miyagi', '宮城', 'place'),
  ('oyako', '親子', 'theme')
on conflict (slug) do nothing;

insert into neta_work_tags (neta_work_id, tag_id, source, confidence, status)
select nw.id, t.id, 'manual', 1.0, 'approved'
from (values
  ('toranisanpo', 'osaka'),
  ('yamadake-blues', 'osaka'),
  ('yamadake-blues', 'oyako'),
  ('panda-kisoku', 'osaka'),
  ('tango-nihime', 'osaka'),
  ('kensouken', 'miyagi')
) as x(comedian_slug, tag_slug)
join comedians c on c.slug = x.comedian_slug
join neta_works nw on nw.comedian_id = c.id
join tags t on t.slug = x.tag_slug
on conflict (neta_work_id, tag_id) do nothing;

-- 賞レース（M-1グランプリ 2026年 1回戦 ナイスアマチュア賞）
insert into contests (slug, name) values ('m1', 'M-1グランプリ')
on conflict (slug) do nothing;

insert into contest_editions (contest_id, year)
select c.id, 2026 from contests c where c.slug = 'm1'
on conflict (contest_id, year) do nothing;

insert into contest_entries (edition_id, comedian_id, round)
select ce.id, cm.id, '1回戦(ナイスアマチュア賞)'
from contest_editions ce
join contests c on c.id = ce.contest_id and c.slug = 'm1' and ce.year = 2026
join comedians cm on cm.slug in ('toranisanpo','yamadake-blues','panda-kisoku','tango-nihime','kensouken')
on conflict (edition_id, comedian_id, round) do nothing;
