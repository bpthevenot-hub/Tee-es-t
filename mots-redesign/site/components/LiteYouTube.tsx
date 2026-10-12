'use client'

import { useState } from 'react'

/**
 * Façade YouTube légère : rien n'est chargé depuis YouTube tant que le
 * visiteur n'a pas cliqué (performance + sobriété + confidentialité).
 */
export default function LiteYouTube({ videoId, title }: { videoId: string; title: string }) {
  const [active, setActive] = useState(false)

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-2xl bg-marine shadow-carte-haute">
      {active ? (
        <iframe
          className="absolute inset-0 h-full w-full"
          src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      ) : (
        <button
          type="button"
          onClick={() => setActive(true)}
          className="group absolute inset-0 flex h-full w-full flex-col items-center justify-center gap-4 text-white focus-visible:outline-2 focus-visible:-outline-offset-4 focus-visible:outline-white"
          aria-label={`Lire la vidéo : ${title}`}
        >
          <span
            aria-hidden="true"
            className="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_20%,rgba(20,114,124,0.75),transparent_60%),radial-gradient(ellipse_at_75%_80%,rgba(228,87,46,0.35),transparent_55%)]"
          />
          <span className="relative flex h-16 w-16 items-center justify-center rounded-full bg-accent transition group-hover:scale-110">
            <svg aria-hidden="true" width="22" height="26" viewBox="0 0 22 26" fill="white">
              <path d="M0 0 L22 13 L0 26 Z" />
            </svg>
          </span>
          <span className="relative max-w-md px-6 text-center font-semibold">{title}</span>
          <span className="relative text-sm text-white/70">Vidéo officielle — chargée depuis YouTube au clic</span>
        </button>
      )}
    </div>
  )
}
