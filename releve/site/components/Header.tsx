'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { NAVIGATION, PRODUIT, TEL_3114_HREF } from '@/lib/infos'

export default function Header() {
  const [ouvert, setOuvert] = useState(false)
  const chemin = usePathname()

  return (
    <header className="sticky top-0 z-40 border-b border-filet bg-[var(--mode-fond)]/95 backdrop-blur-sm">
      <div className="conteneur flex items-center justify-between gap-4 py-3">
        <Link href="/" className="titre text-2xl tracking-[0.06em] text-[var(--mode-texte)]" aria-label={`${PRODUIT}, accueil`}>
          {PRODUIT}
        </Link>

        <nav aria-label="Navigation principale" className="hidden lg:block">
          <ul className="flex items-center gap-1">
            {NAVIGATION.map((n) => {
              const actif = n.href === '/' ? chemin === '/' : chemin.startsWith(n.href)
              return (
                <li key={n.href}>
                  <Link
                    href={n.href}
                    aria-current={actif ? 'page' : undefined}
                    className={`mono fondu inline-block rounded-[var(--radius-clinique)] px-3 py-2 text-[0.78rem] uppercase tracking-[0.12em] ${actif ? 'bg-[var(--mode-surface-2)] text-[var(--mode-texte)]' : 'text-[var(--mode-sourd)] hover:text-[var(--mode-texte)]'}`}
                  >
                    {n.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="flex items-center gap-2">
          <a href={TEL_3114_HREF} className="bouton bouton-3114 !min-h-[2.4rem] !px-3 !text-sm">
            3114
          </a>
          <button
            type="button"
            className="bouton bouton-second !min-h-[2.4rem] !px-3 !text-sm lg:hidden"
            aria-expanded={ouvert}
            aria-controls="menu-mobile"
            onClick={() => setOuvert((v) => !v)}
          >
            {ouvert ? 'Fermer' : 'Menu'}
          </button>
        </div>
      </div>

      {ouvert && (
        <nav id="menu-mobile" aria-label="Navigation mobile" className="border-t border-filet bg-[var(--mode-surface)] lg:hidden">
          <ul className="conteneur flex flex-col py-2">
            {NAVIGATION.map((n) => (
              <li key={n.href}>
                <Link
                  href={n.href}
                  onClick={() => setOuvert(false)}
                  className="mono block rounded-[var(--radius-clinique)] px-3 py-3 text-[0.85rem] uppercase tracking-[0.12em] text-[var(--mode-texte)] hover:bg-[var(--mode-surface-2)]"
                >
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  )
}
