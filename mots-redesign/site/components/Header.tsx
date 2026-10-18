'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { NAVIGATION, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export default function Header() {
  const [ouvert, setOuvert] = useState(false)
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 border-b border-encre/8 bg-ivoire/85 backdrop-blur-md">
      <div className="conteneur flex items-center justify-between gap-4 py-3">
        <Link href="/" className="flex items-center gap-2.5 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-sapin" onClick={() => setOuvert(false)}>
          <span aria-hidden="true" className="flex h-10 w-10 items-center justify-center rounded-xl bg-sapin font-bold text-white">
            M
          </span>
          <span className="leading-tight">
            <span className="block font-bold tracking-tight text-marine">MOTS</span>
            <span className="block text-[11px] text-brume">Médecin · Organisation · Travail · Santé</span>
          </span>
        </Link>

        <nav aria-label="Navigation principale" className="hidden items-center gap-1 xl:flex">
          {NAVIGATION.map((item) => {
            const actif = pathname === item.href || pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={actif ? 'page' : undefined}
                className={`rounded-full px-3 py-2 text-[15px] font-medium transition hover:bg-ecume hover:text-sapin focus-visible:outline-2 focus-visible:outline-sapin ${
                  actif ? 'bg-ecume text-sapin' : 'text-encre/80'
                }`}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-2">
          <a href={TEL_HREF} className="bouton-appel hidden !py-2.5 text-sm md:inline-flex">
            <IconeTelephone />
            {TEL_AFFICHE}
          </a>
          <button
            type="button"
            className="rounded-xl border border-encre/12 p-2.5 xl:hidden"
            aria-expanded={ouvert}
            aria-controls="menu-mobile"
            onClick={() => setOuvert(!ouvert)}
          >
            <span className="sr-only">{ouvert ? 'Fermer le menu' : 'Ouvrir le menu'}</span>
            <svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              {ouvert ? <path d="M4 4 L16 16 M16 4 L4 16" /> : <path d="M3 5 H17 M3 10 H17 M3 15 H17" />}
            </svg>
          </button>
        </div>
      </div>

      {ouvert && (
        <nav id="menu-mobile" aria-label="Navigation mobile" className="border-t border-encre/8 bg-ivoire xl:hidden">
          <div className="conteneur flex flex-col gap-1 py-4">
            {NAVIGATION.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOuvert(false)}
                className="rounded-xl px-4 py-3 font-medium text-encre/85 transition hover:bg-ecume hover:text-sapin"
              >
                {item.label}
              </Link>
            ))}
            <a href={TEL_HREF} className="bouton-appel mt-2 justify-center">
              <IconeTelephone />
              Besoin d’aide ? {TEL_AFFICHE}
            </a>
          </div>
        </nav>
      )}
    </header>
  )
}

function IconeTelephone() {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M6.6 10.8a15.6 15.6 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.4c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1l-2.2 2.2Z" />
    </svg>
  )
}
