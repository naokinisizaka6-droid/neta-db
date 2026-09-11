import { notFound } from 'next/navigation'
import { getComedianBySlug, getComedianNetas } from '@/lib/supabase'

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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{comedian.name}</h1>
        <p className="text-slate-600 dark:text-slate-400">
          {unitTypeLabel[comedian.unit_type] || comedian.unit_type}
          {comedian.agency && ` • ${comedian.agency}`}
        </p>
      </div>

      <h2 className="text-xl font-bold">ネタ一覧</h2>

      {netas.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>公開されているネタがまだありません</p>
        </div>
      ) : (
        <div className="space-y-4">
          {netas.map((nw: any) => {
            const perf = (nw.performances || [])[0]
            return (
              <div
                key={nw.id}
                className="p-4 border rounded-lg dark:border-slate-700"
              >
                <h3 className="font-bold text-lg mb-1">{nw.title}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                  {nw.format}
                  {nw.setting_note && ` • ${nw.setting_note}`}
                </p>
                {nw.neta_work_tags && nw.neta_work_tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {nw.neta_work_tags
                      .filter((t: any) => t.status === 'approved')
                      .map((t: any, i: number) => (
                        <span
                          key={i}
                          className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded"
                        >
                          {t.tags?.name}
                        </span>
                      ))}
                  </div>
                )}
                <a
                  href={`/neta/${nw.id}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  詳細を見る
                </a>
                {perf && (
                  <>
                    <span className="text-slate-400 text-sm"> • </span>
                    <a
                      href={`https://www.youtube.com/watch?v=${perf.video_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      YouTubeで見る
                    </a>
                  </>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
