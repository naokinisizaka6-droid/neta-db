import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getContestBySlug, getContestEditions } from '@/lib/supabase'

export default async function ContestEditionsPage({
  params,
}: {
  params: { slug: string }
}) {
  let contest
  try {
    contest = await getContestBySlug(params.slug)
  } catch (e) {
    notFound()
  }

  let editions: { id: number; year: number }[] = []
  try {
    editions = await getContestEditions(contest.id)
  } catch (e) {
    editions = []
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🏆 {contest.name}</h1>

      {editions.length === 0 ? (
        <div className="text-center text-slate-600 dark:text-slate-400 py-12">
          <p>登録されている年度がまだありません</p>
        </div>
      ) : (
        <div className="flex flex-wrap gap-3">
          {editions.map((ed) => (
            <Link
              key={ed.id}
              href={`/contest/${params.slug}/${ed.year}`}
              className="px-6 py-3 border rounded-lg hover:border-blue-600 hover:text-blue-600 dark:border-slate-700"
            >
              {ed.year}年
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
