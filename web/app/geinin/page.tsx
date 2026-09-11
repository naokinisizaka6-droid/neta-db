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
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">👥 芸人から探す</h1>

      {error ? (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      ) : comedians.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>登録されている芸人がまだありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {comedians.map((c) => (
            <Link
              key={c.id}
              href={`/geinin/${c.slug}`}
              className="p-4 border rounded-lg hover:shadow-lg transition-shadow hover:border-blue-600 dark:border-slate-700"
            >
              <h3 className="font-bold text-lg">{c.name}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {unitTypeLabel[c.unit_type] || c.unit_type}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
