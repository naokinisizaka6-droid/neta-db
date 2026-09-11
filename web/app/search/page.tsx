import { searchNetas } from '@/lib/supabase'
import NetaCard from '@/components/NetaCard'

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string }
}) {
  const query = searchParams.q || ''
  let results: any[] = []
  let error = null

  if (query.trim()) {
    try {
      results = await searchNetas(query, 50)
    } catch (err) {
      error = '検索エラーが発生しました。時間をおいて再度お試しください。'
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <form action="/search" method="get" className="flex gap-2 max-w-xl">
          <input
            type="text"
            name="q"
            defaultValue={query}
            placeholder="芸人名、設定、タグで検索..."
            className="flex-1 px-4 py-2.5 border border-neutral-300 focus:outline-none focus:border-black text-sm"
          />
          <button
            type="submit"
            className="px-6 py-2.5 bg-black text-white text-sm tracking-wide hover:bg-neutral-800"
          >
            検索
          </button>
        </form>
      </div>

      {!query.trim() ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>キーワードを入力して検索してください</p>
        </div>
      ) : error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : results.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>「{query}」に該当するネタが見つかりません</p>
        </div>
      ) : (
        <div>
          <h2 className="text-sm text-neutral-500 mb-6 tracking-wide">
            検索結果 {results.length} 件
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-10">
            {results.map((r: any) => (
              <NetaCard
                key={r.neta_id}
                href={`/neta/${r.neta_id}`}
                thumbnailUrl={r.thumbnail_url}
                title={r.neta_title || r.title}
                comedianName={r.comedian_name}
                format={r.format}
                durationSec={r.duration_sec}
                tags={r.tags}
                youtubeUrl={r.youtube_url}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
