import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ネタDB - YouTube 漫才・コント検索',
  description: '公式チャンネルの漫才・コント動画から芸人・形式・設定・賞レースで検索できるデータベース',
  openGraph: {
    title: 'ネタDB',
    description: 'YouTube 漫才・コント動画検索',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50">
        <header className="border-b bg-white dark:bg-slate-900">
          <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
            <a href="/" className="text-2xl font-bold">
              🎭 ネタDB
            </a>
            <nav className="flex gap-6">
              <a href="/search" className="hover:text-blue-600">
                検索
              </a>
              <a href="/about" className="hover:text-blue-600">
                について
              </a>
            </nav>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 py-8">
          {children}
        </main>

        <footer className="border-t mt-12 py-6 text-center text-sm text-slate-600 dark:text-slate-400">
          <p>© 2024 ネタDB. All rights reserved.</p>
          <p>
            <a href="/about" className="hover:underline">
              について
            </a>
            {' • '}
            <a href="/takedown" className="hover:underline">
              削除申請
            </a>
          </p>
        </footer>
      </body>
    </html>
  )
}
