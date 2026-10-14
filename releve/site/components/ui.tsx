import type { ReactNode } from 'react'

/** Grand chiffre tabulaire avec sa légende et sa source. */
export function Chiffre({ valeur, texte, source, url }: { valeur: string; texte: string; source?: string; url?: string }) {
  return (
    <div className="plaque flex h-full flex-col">
      <p className="donnee text-4xl leading-none sm:text-5xl">{valeur}</p>
      <p className="mt-3 text-[0.95rem]">{texte}</p>
      {source && (
        <p className="sourd mt-auto pt-4 text-[0.75rem]">
          {url ? (
            <a href={url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
              {source} ↗
            </a>
          ) : (
            source
          )}
        </p>
      )}
    </div>
  )
}

/** Encadré sobre : un titre en étiquette et un contenu. */
export function Encadre({ etiquette, children, accent = false }: { etiquette: string; children: ReactNode; accent?: boolean }) {
  return (
    <div className={`plaque ${accent ? 'border-l-4 border-l-[var(--mode-accent)]' : ''}`}>
      <p className="etiquette">{etiquette}</p>
      <div className="mt-2">{children}</div>
    </div>
  )
}

/** Étiquette « à mesurer » : la preuve n'existe pas encore, on le dit. */
export function AMesurer({ children = 'à mesurer' }: { children?: ReactNode }) {
  return (
    <span className="mono inline-block rounded-[var(--radius-clinique)] border border-dashed border-[var(--mode-filet)] px-2 py-0.5 text-[0.7rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]">
      {children}
    </span>
  )
}

/** Pastille d'état, texte toujours présent (jamais la couleur seule). */
export function Pastille({ ton, children }: { ton: 'ambre' | 'neutre' | 'rouge'; children: ReactNode }) {
  const classes = {
    ambre: 'bg-[var(--mode-accent)] text-[var(--color-encre)]',
    neutre: 'bg-[var(--mode-surface-2)] text-[var(--mode-texte)] border border-[var(--mode-filet)]',
    rouge: 'bg-[var(--color-rouge-3114)] text-white',
  }[ton]
  return <span className={`mono inline-block rounded-[var(--radius-clinique)] px-2 py-0.5 text-[0.7rem] uppercase tracking-[0.12em] ${classes}`}>{children}</span>
}

/** Mention de mode pour les écrans de démo. */
export function BandeauDemoEcran({ espace, pour }: { espace: string; pour: string }) {
  return (
    <div className="conteneur">
      <p className="mono border-b border-filet py-3 text-[0.72rem] uppercase tracking-[0.14em] text-[var(--mode-sourd)]">
        Démonstration · espace « {espace} » · {pour} · données fictives
      </p>
    </div>
  )
}
