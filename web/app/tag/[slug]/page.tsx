import { getTagNetas } from '@/lib/supabase'

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
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🏷️ 「{params.slug}」のネタ</h1>

      {error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>該当するネタが見つかりません</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item: any) => {
            const nw = item.neta_works
            if (!nw) return null
            return (
              <div
                key={item.neta_work_id}
                className="p-4 border rounded-lg dark:border-slate-700"
              >
                <h3 className="font-bold text-lg mb-1">{nw.title}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                  {nw.comedians?.name} • {nw.format}
                </p>
                <a
                  href={`/neta/${nw.id}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  詳細を見る
                </a>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
