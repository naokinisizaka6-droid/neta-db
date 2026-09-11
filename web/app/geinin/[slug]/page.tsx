import { notFound } from 'next/navigation'
import { getComedianBySlug, getComedianNetas } from '@/lib/supabase'
import NetaCard from '@/components/NetaCard'

const unitTypeLabel: Record<string, string> = {
  combi: 'コンビ',
  trio: 'トリオ',
  pin: 'ピン',
  unit: 'ユニット',
  other: 'その他',
}

export default async function GeininDetailPage({
  params,
}: {
  params: { slug: string }
}) {
  let comedian
  try {
    comedian = await getComedianBySlug(params.slug)
  } catch (e) {
    notFound()
  }

  let netas: any[] = []
  try {
    netas = await getComedianNetas(comedian.id)
  } catch (e) {
    netas = []
  }

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold tracking-wide">{comedian.name}</h1>
        <p className="text-sm text-neutral-500 mt-1">
          {unitTypeLabel[comedian.unit_type] || comedian.unit_type}
          {comedian.agency && ` • ${comedian.agency}`}
        </p>
      </div>

      {netas.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>公開されているネタがまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-10">
          {netas.map((nw: any) => {
            const perf = (nw.performances || [])[0]
            const tags = (nw.neta_work_tags || [])
              .filter((t: any) => t.status === 'approved')
              .map((t: any) => t.tags?.name)
              .filter(Boolean)

            return (
              <NetaCard
                key={nw.id}
                href={`/neta/${nw.id}`}
                thumbnailUrl={perf?.yt_videos?.thumbnail_url}
                title={nw.title}
                format={nw.format}
                durationSec={perf?.yt_videos?.duration_sec}
                tags={tags}
                youtubeUrl={perf ? `https://www.youtube.com/watch?v=${perf.video_id}` : undefined}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
