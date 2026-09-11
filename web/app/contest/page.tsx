import Link from 'next/link'
import { getAllContests } from '@/lib/supabase'

export const metadata = {
  title: '賞レースから探す | ネタDB',
}

export default async function ContestListPage() {
  let contests: Awaited<ReturnType<typeof getAllContests>> = []
  let error = null

  try {
    contests = await getAllContests()
  } catch (e) {
    error = '一覧の取得に失敗しました。時間をおいて再度お試しください。'
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🏆 賞レースから探す</h1>

      {error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : contests.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>登録されている賞レースがまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {contests.map((c) => (
            <Link
              key={c.id}
              href={`/contest/${c.slug}`}
              className="p-6 border rounded-lg hover:shadow-lg transition-shadow hover:border-blue-600 dark:border-slate-700"
            >
              <h3 className="font-bold text-xl">{c.name}</h3>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
