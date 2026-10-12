import Link from 'next/link'
import EcgLine from '@/components/EcgLine'
import { ADRESSE, NAVIGATION, SITE_OFFICIEL, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

export default function Footer() {
  return (
    <footer className="mt-24 bg-marine text-white">
      <EcgLine className="h-14 w-full text-sapin-clair/60" />
      <div className="conteneur grid gap-10 py-14 md:grid-cols-3">
        <div>
          <p className="text-xl font-bold">MOTS</p>
          <p className="mt-1 text-sm text-white/70">Médecin · Organisation · Travail · Santé</p>
          <p className="mt-4 max-w-xs text-white/80">
            Des soignants formés pour écouter et accompagner les soignants en difficulté,
            en toute confidentialité, depuis 2010.
          </p>
          <a href={TEL_HREF} className="bouton-appel mt-6">
            {TEL_AFFICHE} — 7 j/7
          </a>
        </div>

        <nav aria-label="Plan du site" className="grid grid-cols-1 content-start gap-2 sm:grid-cols-2">
          {NAVIGATION.map((item) => (
            <Link key={item.href} href={item.href} className="text-white/80 transition hover:text-white">
              {item.label}
            </Link>
          ))}
          <Link href="/mentions-legales" className="text-white/80 transition hover:text-white">
            Mentions légales
          </Link>
        </nav>

        <div className="text-white/80">
          <p className="font-semibold text-white">Siège</p>
          <p className="mt-2">
            {ADRESSE.ligne1}
            <br />
            {ADRESSE.ligne2}
            <br />
            {ADRESSE.ville}
          </p>
        </div>
      </div>

      <div className="border-t border-white/10">
        <div className="conteneur py-5 text-sm text-white/60">
          <p>
            Démonstration de refonte — proposition non officielle, non affiliée à l’Association MOTS. Site officiel :{' '}
            <a href={SITE_OFFICIEL} className="underline hover:text-white">
              association-mots.org
            </a>
          </p>
        </div>
      </div>
    </footer>
  )
}
