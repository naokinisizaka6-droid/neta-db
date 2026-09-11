import type { Metadata } from 'next'
import { Jost } from 'next/font/google'
import './globals.css'

const jost = Jost({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-jost',
})

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
    <html lang="ja" className={jost.variable}>
      <body className="bg-white text-neutral-900 font-sans">
        <header className="border-b border-neutral-200 bg-white sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 flex justify-between items-center">
            <a href="/" className="text-xl font-bold tracking-widest">
              NETA DB
            </a>
            <nav className="flex gap-6 sm:gap-8 text-xs sm:text-sm tracking-wider uppercase">
              <a href="/geinin" className="hover:text-neutral-500">
                芸人
              </a>
              <a href="/tag" className="hover:text-neutral-500">
                設定
              </a>
              <a href="/contest" className="hover:text-neutral-500">
                賞レース
              </a>
              <a href="/search" className="hover:text-neutral-500">
                検索
              </a>
            </nav>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
          {children}
        </main>

        <footer className="border-t border-neutral-200 mt-16 py-8 text-center text-xs text-neutral-500 tracking-wide">
          <p>© 2024 ネタDB. All rights reserved.</p>
          <p className="mt-2">
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
