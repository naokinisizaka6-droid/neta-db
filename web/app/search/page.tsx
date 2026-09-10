import { searchNetas } from '@/lib/supabase'

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string }
}) {
  const query = searchParams.q || ''
  let results = []
  let error = null

  if (query.trim()) {
    try {
      results = await searchNetas(query, 50)
    } catch (err) {
      error = '検索エラーが発生しました。時間をおいて再度お試しください。'
    }
  }

  return (
    <div className="space-y-6">
      {/* 検索フォーム */}
      <div>
        <form action="/search" method="get" className="flex gap-2">
          <input
            type="text"
            name="q"
            defaultValue={query}
            placeholder="芸人名、設定、タグで検索..."
            className="flex-1 px-4 py-2 border rounded-lg bg-white dark:bg-slate-900 dark:border-slate-700"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            検索
          </button>
        </form>
      </div>

      {/* 検索結果 */}
      {!query.trim() ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>キーワードを入力して検索してください</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : results.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>「{query}」に該当するネタが見つかりません</p>
        </div>
      ) : (
        <div>
          <h2 className="text-2xl font-bold mb-4">
            検索結果 ({results.length} 件)
          </h2>

          <div className="space-y-4">
            {results.map((result: any, idx: number) => (
              <div
                key={idx}
                className="p-4 border rounded-lg hover:shadow-lg transition-shadow dark:border-slate-700"
              >
                <div className="flex gap-4">
                  {/* サムネイル */}
                  {result.thumbnail_url && (
                    <div className="flex-shrink-0 w-24 h-24">
                      <img
                        src={result.thumbnail_url}
                        alt={result.title}
                        className="w-full h-full object-cover rounded"
                      />
                    </div>
                  )}

                  {/* 情報 */}
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1">
                      {result.neta_title || result.title}
                    </h3>

                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                      {result.comedian_name} • {result.format} • {result.duration_sec}秒
                    </p>

                    {result.tags && result.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2">
                        {result.tags.slice(0, 3).map((tag: string, i: number) => (
                          <span
                            key={i}
                            className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-2 text-sm">
                      <a
                        href={`/neta/${result.neta_id}`}
                        className="text-blue-600 hover:underline"
                      >
                        詳細を見る
                      </a>
                      <span className="text-slate-400">•</span>
                      <a
                        href={result.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        YouTubeで見る
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
