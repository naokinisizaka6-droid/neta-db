import Link from 'next/link'

export default function Home() {
  return (
    <div className="space-y-20">
      {/* ヒーロー */}
      <section className="py-16 text-center space-y-6">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-widest">
          NETA DB
        </h1>
        <p className="text-sm sm:text-base text-neutral-500 leading-relaxed">
          YouTubeの公式漫才・コント動画から
          <br />
          芸人・形式・設定・賞レースで検索できるデータベース
        </p>

        {/* 検索ボックス */}
        <div className="mt-10">
          <form action="/search" method="get" className="flex gap-2 max-w-xl mx-auto">
            <input
              type="text"
              name="q"
              placeholder="芸人名、設定、タグで検索..."
              className="flex-1 px-4 py-3 border border-neutral-300 focus:outline-none focus:border-black text-sm"
            />
            <button
              type="submit"
              className="px-8 py-3 bg-black text-white text-sm tracking-wide hover:bg-neutral-800"
            >
              検索
            </button>
          </form>
        </div>
      </section>

      {/* ナビゲーション */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-px bg-neutral-200">
        <Link
          href="/geinin"
          className="bg-white p-10 text-center hover:bg-neutral-50 transition-colors"
        >
          <h3 className="text-sm font-bold tracking-widest mb-2">芸人から探す</h3>
          <p className="text-xs text-neutral-500">
            漫才師、コンビ、ユニット等のネタを一覧から検索
          </p>
        </Link>

        <Link
          href="/tag"
          className="bg-white p-10 text-center hover:bg-neutral-50 transition-colors"
        >
          <h3 className="text-sm font-bold tracking-widest mb-2">設定から探す</h3>
          <p className="text-xs text-neutral-500">
            コンビニ、デパート、学校など設定のキーワードで検索
          </p>
        </Link>

        <Link
          href="/contest"
          className="bg-white p-10 text-center hover:bg-neutral-50 transition-colors"
        >
          <h3 className="text-sm font-bold tracking-widest mb-2">賞レースから探す</h3>
          <p className="text-xs text-neutral-500">
            M-1グランプリ、キング・オブ・コント等の作品を検索
          </p>
        </Link>
      </section>

      {/* 情報セクション */}
      <section className="space-y-6 max-w-2xl mx-auto">
        <h2 className="text-lg font-bold tracking-wide text-center">ネタDBについて</h2>

        <div className="space-y-6 text-sm text-neutral-600">
          <div>
            <h3 className="font-bold text-black mb-2 tracking-wide">特徴</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>公式チャンネルの認可済みネタのみを掲載</li>
              <li>漫才・コント・ピン芸を形式で分類</li>
              <li>コンビニ店員、デパート、インタビューなど設定でタグ付け</li>
              <li>M-1グランプリなど主要賞レースの映像と順位を対応</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-black mb-2 tracking-wide">検索方法</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>検索ボックスから芸人名、設定、タグで横断検索</li>
              <li>芸人ページから全ネタを一覧表示</li>
              <li>タグページから設定の種類別に一覧</li>
              <li>賞レースページから年度別・ラウンド別に表示</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-black mb-2 tracking-wide">利用規約</h3>
            <p>
              当サイトはYouTubeの公開APIを利用してメタデータのみを保存しています。
              映像・音声のダウンロードは禁止しており、公式の埋め込みプレイヤーでの視聴のみです。
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border border-neutral-200 p-10 text-center">
        <h3 className="font-bold tracking-wide mb-2">ネタを提案する</h3>
        <p className="text-sm text-neutral-500 mb-4">
          見落としているネタがあればお知らせください。
          （フィードバックは X / メール経由）
        </p>
        <a href="/about" className="text-sm underline hover:text-neutral-500">
          詳細はこちら →
        </a>
      </section>
    </div>
  )
}
