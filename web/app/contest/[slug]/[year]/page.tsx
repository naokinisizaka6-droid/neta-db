import { getContestNetas } from '@/lib/supabase'

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
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">
        {params.slug.toUpperCase()} {year}年
      </h1>

      {error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>登録されているエントリーがまだありません</p>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry: any) => {
            const perf = (entry.performances || [])[0]
            return (
              <div
                key={entry.id}
                className="p-4 border rounded-lg dark:border-slate-700 flex justify-between items-center"
              >
                <div>
                  <h3 className="font-bold text-lg">{entry.comedians?.name}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {entry.round}
                    {entry.rank && ` • ${entry.rank}位`}
                  </p>
                </div>
                {perf && (
                  <a
                    href={`https://www.youtube.com/watch?v=${perf.video_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    YouTubeで見る
                  </a>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
