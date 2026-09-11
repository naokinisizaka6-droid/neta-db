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
    <div className="space-y-8">
      <h1 className="text-2xl font-bold tracking-wide">{contest.name}</h1>

      {editions.length === 0 ? (
        <div className="text-center text-neutral-500 py-20 text-sm">
          <p>登録されている年度がまだありません</p>
        </div>
      ) : (
        <div className="flex flex-wrap gap-3">
          {editions.map((ed) => (
            <Link
              key={ed.id}
              href={`/contest/${params.slug}/${ed.year}`}
              className="px-6 py-3 border border-neutral-300 text-sm hover:border-black hover:bg-black hover:text-white transition-colors"
            >
              {ed.year}年
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
