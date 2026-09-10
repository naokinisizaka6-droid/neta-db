import Link from 'next/link'

export default function Home() {
  return (
    <div className="space-y-12">
      {/* ヒーロー */}
      <section className="py-12 text-center space-y-4">
        <h1 className="text-4xl font-bold">
          🎭 ネタDB
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-400">
          YouTubeの公式漫才・コント動画から
          <br />
          芸人・形式・設定・賞レースで検索できるデータベース
        </p>

        {/* 検索ボックス */}
        <div className="mt-8">
          <form action="/search" method="get" className="flex gap-2 max-w-2xl mx-auto">
            <input
              type="text"
              name="q"
              placeholder="芸人名、設定、タグで検索..."
              className="flex-1 px-4 py-3 border rounded-lg bg-white dark:bg-slate-900 dark:border-slate-700"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              検索
            </button>
          </form>
        </div>
      </section>

      {/* ナビゲーション */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/geinin"
          className="p-6 border rounded-lg hover:shadow-lg transition-shadow hover:border-blue-600 dark:border-slate-700"
        >
          <h3 className="text-xl font-bold mb-2">👥 芸人から探す</h3>
          <p className="text-slate-600 dark:text-slate-400">
            漫才師、コンビ、ユニット等のネタを一覧から検索
          </p>
        </Link>

        <Link
          href="/tag"
          className="p-6 border rounded-lg hover:shadow-lg transition-shadow hover:border-blue-600 dark:border-slate-700"
        >
          <h3 className="text-xl font-bold mb-2">🏷️ 設定から探す</h3>
          <p className="text-slate-600 dark:text-slate-400">
            コンビニ、デパート、学校など設定のキーワードで検索
          </p>
        </Link>

        <Link
          href="/contest"
          className="p-6 border rounded-lg hover:shadow-lg transition-shadow hover:border-blue-600 dark:border-slate-700"
        >
          <h3 className="text-xl font-bold mb-2">🏆 賞レースから探す</h3>
          <p className="text-slate-600 dark:text-slate-400">
            M-1グランプリ、キング・オブ・コント等の作品を検索
          </p>
        </Link>
      </section>

      {/* 情報セクション */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">📋 ネタDBについて</h2>

        <div className="space-y-4 text-slate-700 dark:text-slate-300">
          <div>
            <h3 className="font-bold mb-2">✨ 特徴</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>公式チャンネルの認可済みネタのみを掲載</li>
              <li>漫才・コント・ピン芸を形式で分類</li>
              <li>コンビニ店員、デパート、インタビューなど設定でタグ付け</li>
              <li>M-1グランプリなど主要賞レースの映像と順位を対応</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold mb-2">🔍 検索方法</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>検索ボックスから芸人名、設定、タグで横断検索</li>
              <li>芸人ページから全ネタを一覧表示</li>
              <li>タグページから設定の種類別に一覧</li>
              <li>賞レースページから年度別・ラウンド別に表示</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold mb-2">⚖️ 利用規約</h3>
            <p className="text-sm">
              当サイトはYouTubeの公開APIを利用してメタデータのみを保存しています。
              映像・音声のダウンロードは禁止しており、公式の埋め込みプレイヤーでの視聴のみです。
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-50 dark:bg-blue-950/20 p-6 rounded-lg text-center">
        <h3 className="font-bold mb-2">🚀 ネタを提案する</h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
          見落としているネタがあればお知らせください。
          （フィードバックは X / メール経由）
        </p>
        <a href="/about" className="text-blue-600 hover:underline">
          詳細はこちら →
        </a>
      </section>
    </div>
  )
}
