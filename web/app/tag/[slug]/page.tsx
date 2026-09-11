import { getTagNetas } from '@/lib/supabase'
import NetaCard from '@/components/NetaCard'

export default async function TagDetailPage({
  params,
}: {
  params: { slug: string }
}) {
  let items: any[] = []
  let error = null

  try {
    items = await getTagNetas(params.slug)
  } catch (e) {
    error = 'ネタ一覧の取得に失敗しました。時間をおいて再度お試しください。'
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">🏷️ 「{params.slug}」のネタ</h1>

      {error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>該当するネタが見つかりません</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-10">
          {items.map((item: any) => {
            const nw = item.neta_works
            if (!nw) return null
            const perf = (nw.performances || [])[0]
            return (
              <NetaCard
                key={item.neta_work_id}
                href={`/neta/${nw.id}`}
                thumbnailUrl={perf?.yt_videos?.thumbnail_url}
                title={nw.title}
                comedianName={nw.comedians?.name}
                format={nw.format}
                durationSec={perf?.yt_videos?.duration_sec}
                youtubeUrl={perf ? `https://www.youtube.com/watch?v=${perf.video_id}` : undefined}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
