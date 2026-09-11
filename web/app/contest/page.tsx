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
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">賞レースから探す</h1>

      {error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : contests.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>登録されている賞レースがまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-neutral-200">
          {contests.map((c) => (
            <Link
              key={c.id}
              href={`/contest/${c.slug}`}
              className="bg-white p-10 hover:bg-neutral-50 transition-colors"
            >
              <h3 className="font-bold tracking-wide">{c.name}</h3>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
