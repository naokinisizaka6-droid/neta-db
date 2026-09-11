import { getContestNetas } from '@/lib/supabase'
import NetaCard from '@/components/NetaCard'

export default async function ContestYearPage({
  params,
}: {
  params: { slug: string; year: string }
}) {
  const year = parseInt(params.year, 10)
  let entries: any[] = []
  let error = null

  try {
    entries = await getContestNetas(params.slug, year)
  } catch (e) {
    error = 'エントリー一覧の取得に失敗しました。時間をおいて再度お試しください。'
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">
        {params.slug.toUpperCase()} {year}年
      </h1>

      {error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>登録されているエントリーがまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-10">
          {entries.map((entry: any) => {
            const perf = (entry.performances || [])[0]
            return (
              <NetaCard
                key={entry.id}
                href={`/geinin/${entry.comedians?.slug}`}
                thumbnailUrl={perf?.yt_videos?.thumbnail_url}
                title={entry.comedians?.name}
                comedianName={entry.rank ? `${entry.rank}位` : entry.round}
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
