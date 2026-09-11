import { notFound } from 'next/navigation'
import { getNetaById } from '@/lib/supabase'

export default async function NetaDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const id = parseInt(params.id, 10)
  if (Number.isNaN(id)) notFound()

  let neta
  try {
    neta = await getNetaById(id)
  } catch (e) {
    notFound()
  }

  const perf = (neta.performances || [])[0]
  const video = perf?.yt_videos

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-wide">{neta.title}</h1>
        <p className="text-sm text-neutral-500 mt-1">
          <a href={`/geinin/${neta.comedians?.slug}`} className="hover:underline">
            {neta.comedians?.name}
          </a>
          {' • '}
          {neta.format}
        </p>
      </div>

      {perf && (
        <div className="aspect-video w-full bg-neutral-100">
          <iframe
            className="w-full h-full"
            src={`https://www.youtube.com/embed/${perf.video_id}${perf.start_sec ? `?start=${perf.start_sec}` : ''}`}
            title={neta.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {neta.setting_note && (
        <p className="text-sm text-neutral-600">{neta.setting_note}</p>
      )}

      {neta.neta_work_tags && neta.neta_work_tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {neta.neta_work_tags
            .filter((t: any) => t.status === 'approved')
            .map((t: any, i: number) => (
              <a
                key={i}
                href={`/tag/${t.tags?.slug}`}
                className="text-xs border border-neutral-300 text-neutral-600 px-2 py-1 hover:border-black hover:text-black"
              >
                {t.tags?.name}
              </a>
            ))}
        </div>
      )}

      {video && (
        <a
          href={`https://www.youtube.com/watch?v=${perf.video_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-sm underline hover:text-neutral-500"
        >
          YouTubeで見る →
        </a>
      )}
    </div>
  )
}
