import Link from 'next/link'
import { getAllTags } from '@/lib/supabase'

export const metadata = {
  title: '設定から探す | ネタDB',
}

const categoryLabel: Record<string, string> = {
  place: '場所',
  relation: '関係',
  job: '職業',
  theme: 'テーマ',
  style: 'スタイル',
}

export default async function TagListPage() {
  let tags: Awaited<ReturnType<typeof getAllTags>> = []
  let error = null

  try {
    tags = await getAllTags()
  } catch (e) {
    error = '一覧の取得に失敗しました。時間をおいて再度お試しください。'
  }

  const grouped = tags.reduce((acc: Record<string, typeof tags>, tag) => {
    acc[tag.category] = acc[tag.category] || []
    acc[tag.category].push(tag)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🏷️ 設定から探す</h1>

      {error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : tags.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>登録されているタグがまだありません</p>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([category, list]) => (
            <div key={category}>
              <h2 className="text-lg font-bold mb-3">
                {categoryLabel[category] || category}
              </h2>
              <div className="flex flex-wrap gap-2">
                {list.map((tag) => (
                  <Link
                    key={tag.id}
                    href={`/tag/${tag.slug}`}
                    className="px-4 py-2 border rounded-lg hover:border-blue-600 hover:text-blue-600 dark:border-slate-700"
                  >
                    {tag.name}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
