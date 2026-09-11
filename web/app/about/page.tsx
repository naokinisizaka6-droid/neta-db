export const metadata = {
  title: 'について | ネタDB',
}

export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-3xl">
      <h1 className="text-3xl font-bold">📋 ネタDBについて</h1>

      <section className="space-y-2">
        <h2 className="text-xl font-bold">サイトの目的</h2>
        <p className="text-slate-700 dark:text-slate-300">
          ネタDBは、YouTubeの公式チャンネルで公開されている漫才・コント動画を、
          芸人・形式・設定・賞レースなどの切り口から検索できるデータベースサイトです。
        </p>
      </section>

      <section className="space-y-2">
        <h2 className="text-xl font-bold">データの取り扱い</h2>
        <ul className="list-disc list-inside space-y-1 text-sm text-slate-700 dark:text-slate-300">
          <li>掲載対象は、事前に確認・承認したホワイトリスト内の公式チャンネルの動画のみです。</li>
          <li>動画・音声のダウンロードは行わず、YouTube公式の埋め込みプレイヤー経由でのみ視聴できます。</li>
          <li>YouTube Data APIで取得したメタデータ（タイトル・再生数等）は、API利用規約に基づき定期的に更新・削除します。</li>
          <li>タグや分類の一部はLLM（Claude API）による推定を含みますが、公開前に人手でレビューしています。</li>
        </ul>
      </section>

      <section className="space-y-2">
        <h2 className="text-xl font-bold">ネタを提案する</h2>
        <p className="text-sm text-slate-700 dark:text-slate-300">
          掲載すべき公式チャンネルの見落としや、内容の誤りに気づいた場合は、
          お手数ですが <a href="/takedown" className="text-blue-600 hover:underline">削除申請フォーム</a> または
          運営のX/メールまでご連絡ください。
        </p>
      </section>
    </div>
  )
}
