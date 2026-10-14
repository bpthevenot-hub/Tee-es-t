import Link from 'next/link'
import { MOTS_SITE, NAVIGATION, PRODUIT, SNB_SITE, TEL_3114_AFFICHE, TEL_3114_HREF, TEL_MOTS_AFFICHE, TEL_MOTS_HREF } from '@/lib/infos'

/** Pied de page : le 3114 et la ligne MOTS sur chaque écran, sans exception. */
export default function Footer() {
  return (
    <footer className="mt-16 border-t border-filet">
      <div className="conteneur grid gap-8 py-10 md:grid-cols-3">
        <div>
          <p className="titre text-xl tracking-[0.06em]">{PRODUIT}</p>
          <p className="sourd mt-2 max-w-xs text-sm">
            La clinique digitale du soignant. Une proposition de SNB Consulting, à l’image de ce que l’association MOTS fait depuis 2010.
          </p>
          <p className="mt-4">
            <a href={SNB_SITE} rel="noopener noreferrer" className="mono text-[0.78rem] uppercase tracking-[0.12em] underline underline-offset-4">
              snb.center
            </a>
          </p>
        </div>

        <div>
          <p className="etiquette">Si ça ne va pas, maintenant</p>
          <p className="mt-3">
            <a href={TEL_3114_HREF} className="bouton bouton-3114">
              {TEL_3114_AFFICHE} — prévention du suicide, 24 h/24
            </a>
          </p>
          <p className="mt-3 text-sm">
            Un pair, 7 j/7 :{' '}
            <a href={TEL_MOTS_HREF} className="donnee underline underline-offset-4">
              {TEL_MOTS_AFFICHE}
            </a>{' '}
            <span className="sourd">(association MOTS)</span>
          </p>
        </div>

        <nav aria-label="Plan du site">
          <p className="etiquette">Plan</p>
          <ul className="mt-3 grid grid-cols-2 gap-1 text-sm">
            {NAVIGATION.map((n) => (
              <li key={n.href}>
                <Link href={n.href} className="hover:underline underline-offset-4">
                  {n.label}
                </Link>
              </li>
            ))}
            <li>
              <Link href="/mentions" className="hover:underline underline-offset-4">
                Mentions
              </Link>
            </li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-filet">
        <p className="conteneur sourd py-4 text-[0.78rem]">
          Démonstration non officielle, aucune donnée réelle, aucune collecte. Non affiliée à l’association MOTS (
          <a href={MOTS_SITE} rel="noopener noreferrer" className="underline underline-offset-2">association-mots.org</a>) ni à Eos Care.
        </p>
      </div>
    </footer>
  )
}
