export const metadata = {
  title: '削除申請 | ネタDB',
}

export default function TakedownPage({
  searchParams,
}: {
  searchParams: { sent?: string; error?: string }
}) {
  return (
    <div className="space-y-8 max-w-xl">
      <h1 className="text-2xl font-bold tracking-wide">削除・非公開申請</h1>
      <p className="text-sm text-neutral-600 leading-relaxed">
        掲載内容の削除・非公開をご希望の場合は、以下のフォームからご申請ください。
        内容を確認のうえ、対応いたします。
      </p>

      {searchParams.sent && (
        <div className="border border-green-200 bg-green-50 text-green-700 p-4 text-sm">
          申請を受け付けました。ご連絡ありがとうございます。
        </div>
      )}
      {searchParams.error && (
        <div className="border border-red-200 bg-red-50 text-red-600 p-4 text-sm">
          送信に失敗しました。時間をおいて再度お試しください。
        </div>
      )}

      <form action="/api/takedown" method="post" className="space-y-5">
        <div>
          <label className="block text-xs tracking-wide text-neutral-500 mb-1.5">対象ページ・動画URL *</label>
          <input
            type="text"
            name="target_url"
            required
            placeholder="https://..."
            className="w-full px-4 py-2.5 border border-neutral-300 focus:outline-none focus:border-black text-sm"
          />
        </div>
        <div>
          <label className="block text-xs tracking-wide text-neutral-500 mb-1.5">申請者（任意）</label>
          <input
            type="text"
            name="requester"
            placeholder="お名前・チャンネル名など"
            className="w-full px-4 py-2.5 border border-neutral-300 focus:outline-none focus:border-black text-sm"
          />
        </div>
        <div>
          <label className="block text-xs tracking-wide text-neutral-500 mb-1.5">理由（任意）</label>
          <textarea
            name="reason"
            rows={4}
            placeholder="削除・非公開を希望する理由をご記入ください"
            className="w-full px-4 py-2.5 border border-neutral-300 focus:outline-none focus:border-black text-sm"
          />
        </div>
        <button
          type="submit"
          className="px-8 py-3 bg-black text-white text-sm tracking-wide hover:bg-neutral-800"
        >
          申請を送信
        </button>
      </form>
    </div>
  )
}
