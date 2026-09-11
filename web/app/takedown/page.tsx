export const metadata = {
  title: '削除申請 | ネタDB',
}

export default function TakedownPage({
  searchParams,
}: {
  searchParams: { sent?: string; error?: string }
}) {
  return (
    <div className="space-y-6 max-w-xl">
      <h1 className="text-3xl font-bold">🚫 削除・非公開申請</h1>
      <p className="text-sm text-slate-700 dark:text-slate-300">
        掲載内容の削除・非公開をご希望の場合は、以下のフォームからご申請ください。
        内容を確認のうえ、対応いたします。
      </p>

      {searchParams.sent && (
        <div className="bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-400 p-4 rounded-lg">
          申請を受け付けました。ご連絡ありがとうございます。
        </div>
      )}
      {searchParams.error && (
        <div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
          送信に失敗しました。時間をおいて再度お試しください。
        </div>
      )}

      <form action="/api/takedown" method="post" className="space-y-4">
        <div>
          <label className="block text-sm font-bold mb-1">対象ページ・動画URL *</label>
          <input
            type="text"
            name="target_url"
            required
            placeholder="https://..."
            className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-slate-900 dark:border-slate-700"
          />
        </div>
        <div>
          <label className="block text-sm font-bold mb-1">申請者（任意）</label>
          <input
            type="text"
            name="requester"
            placeholder="お名前・チャンネル名など"
            className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-slate-900 dark:border-slate-700"
          />
        </div>
        <div>
          <label className="block text-sm font-bold mb-1">理由（任意）</label>
          <textarea
            name="reason"
            rows={4}
            placeholder="削除・非公開を希望する理由をご記入ください"
            className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-slate-900 dark:border-slate-700"
          />
        </div>
        <button
          type="submit"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          申請を送信
        </button>
      </form>
    </div>
  )
}
