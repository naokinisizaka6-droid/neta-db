-- performances.video_id -> yt_videos.video_id の外部キーが未定義だったため追加
-- (PostgRESTのネストしたリレーション解決 performances(...,yt_videos(...)) に必要)
-- 既存データに不整合(yt_videosに存在しないvideo_id)があれば先にNULL/削除する必要があるため
-- 実行前にvalidateする

alter table performances
  add constraint performances_video_id_fkey
  foreign key (video_id) references yt_videos(video_id) on delete cascade;
