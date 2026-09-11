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
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">設定から探す</h1>

      {error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : tags.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>登録されているタグがまだありません</p>
        </div>
      ) : (
        <div className="space-y-10">
          {Object.entries(grouped).map(([category, list]) => (
            <div key={category}>
              <h2 className="text-xs font-bold tracking-widest text-neutral-500 mb-4 uppercase">
                {categoryLabel[category] || category}
              </h2>
              <div className="flex flex-wrap gap-2">
                {list.map((tag) => (
                  <Link
                    key={tag.id}
                    href={`/tag/${tag.slug}`}
                    className="px-4 py-2 border border-neutral-300 text-sm hover:border-black hover:bg-black hover:text-white transition-colors"
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
