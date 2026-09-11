import Link from 'next/link'

export interface NetaCardProps {
  href: string
  thumbnailUrl?: string | null
  title: string
  comedianName?: string | null
  format?: string | null
  durationSec?: number | null
  tags?: string[]
  youtubeUrl?: string | null
}

function formatDuration(sec?: number | null) {
  if (!sec) return null
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

export default function NetaCard({
  href,
  thumbnailUrl,
  title,
  comedianName,
  format,
  durationSec,
  tags,
  youtubeUrl,
}: NetaCardProps) {
  const duration = formatDuration(durationSec)

  return (
    <div className="group">
      <Link href={href} className="block">
        <div className="relative aspect-square w-full overflow-hidden bg-neutral-100">
          {thumbnailUrl ? (
            <img
              src={thumbnailUrl}
              alt={title}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-neutral-300 text-4xl">
              🎬
            </div>
          )}
          {duration && (
            <span className="absolute bottom-2 right-2 bg-black/75 text-white text-[11px] px-1.5 py-0.5 rounded">
              {duration}
            </span>
          )}
        </div>

        <div className="mt-3 space-y-0.5">
          {comedianName && (
            <p className="text-[11px] text-neutral-500 tracking-wide">{comedianName}</p>
          )}
          <h3 className="text-sm font-bold leading-snug text-black group-hover:underline">
            {title}
          </h3>
          {format && <p className="text-xs text-neutral-500">{format}</p>}
        </div>
      </Link>

      {(tags && tags.length > 0) || youtubeUrl ? (
        <div className="mt-1.5 flex items-center justify-between gap-2">
          {tags && tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {tags.slice(0, 3).map((tag, i) => (
                <span
                  key={i}
                  className="text-[10px] border border-neutral-300 text-neutral-600 px-1.5 py-0.5"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          {youtubeUrl && (
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-neutral-500 hover:text-black hover:underline whitespace-nowrap"
            >
              YouTube ↗
            </a>
          )}
        </div>
      ) : null}
    </div>
  )
}
