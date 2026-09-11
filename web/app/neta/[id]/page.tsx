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
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">{neta.title}</h1>
        <p className="text-slate-600 dark:text-slate-400">
          <a href={`/geinin/${neta.comedians?.slug}`} className="hover:underline">
            {neta.comedians?.name}
          </a>
          {' • '}
          {neta.format}
        </p>
      </div>

      {perf && (
        <div className="aspect-video w-full">
          <iframe
            className="w-full h-full rounded-lg"
            src={`https://www.youtube.com/embed/${perf.video_id}${perf.start_sec ? `?start=${perf.start_sec}` : ''}`}
            title={neta.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {neta.setting_note && (
        <p className="text-slate-700 dark:text-slate-300">{neta.setting_note}</p>
      )}

      {neta.neta_work_tags && neta.neta_work_tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {neta.neta_work_tags
            .filter((t: any) => t.status === 'approved')
            .map((t: any, i: number) => (
              <a
                key={i}
                href={`/tag/${t.tags?.slug}`}
                className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded hover:underline"
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
          className="inline-block text-blue-600 hover:underline"
        >
          YouTubeで見る →
        </a>
      )}
    </div>
  )
}
