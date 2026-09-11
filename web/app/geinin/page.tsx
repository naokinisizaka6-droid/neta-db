import Link from 'next/link'
import { getAllComedians } from '@/lib/supabase'

export const metadata = {
  title: '芸人から探す | ネタDB',
}

const unitTypeLabel: Record<string, string> = {
  combi: 'コンビ',
  trio: 'トリオ',
  pin: 'ピン',
  unit: 'ユニット',
  other: 'その他',
}

export default async function GeininListPage() {
  let comedians: Awaited<ReturnType<typeof getAllComedians>> = []
  let error = null

  try {
    comedians = await getAllComedians()
  } catch (e) {
    error = '一覧の取得に失敗しました。時間をおいて再度お試しください。'
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">芸人から探す</h1>

      {error ? (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          {error}
        </div>
      ) : comedians.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>登録されている芸人がまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-neutral-200">
          {comedians.map((c) => (
            <Link
              key={c.id}
              href={`/geinin/${c.slug}`}
              className="bg-white p-5 hover:bg-neutral-50 transition-colors"
            >
              <h3 className="font-bold text-sm tracking-wide">{c.name}</h3>
              <p className="text-xs text-neutral-500 mt-1">
                {unitTypeLabel[c.unit_type] || c.unit_type}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
