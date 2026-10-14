import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import BoutonAppelFlottant from '@/components/BoutonAppelFlottant'
import { ADRESSE, TEL_AFFICHE } from '@/lib/infos'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'MOTS — Prendre soin des soignants (démo de refonte)',
    template: '%s — MOTS (démo de refonte)',
  },
  description:
    'Proposition de refonte du site de l’Association MOTS : écoute et accompagnement confidentiels des professionnels de santé en difficulté, 7 j/7. Démo non officielle.',
  robots: { index: false, follow: false },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'MedicalOrganization',
  name: 'Association MOTS (Médecin-Organisation-Travail-Santé)',
  description:
    'Association d’aide et d’accompagnement des professionnels de santé en difficulté : écoute dédiée, entretien confraternel confidentiel, accompagnement global par des médecins formés.',
  telephone: '+33608282589',
  address: {
    '@type': 'PostalAddress',
    streetAddress: `${ADRESSE.ligne1}, ${ADRESSE.ligne2}`,
    addressLocality: 'Toulouse',
    postalCode: '31500',
    addressCountry: 'FR',
  },
  foundingDate: '2010',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <a
          href="#contenu"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-xl focus:bg-marine focus:px-4 focus:py-3 focus:text-white"
        >
          Aller au contenu
        </a>
        <div className="bg-marine text-center text-sm text-white">
          <p className="conteneur py-2">
            Soignant en difficulté ? Une ligne d’écoute dédiée, 7 j/7 : <strong>{TEL_AFFICHE}</strong>
          </p>
        </div>
        <Header />
        <main id="contenu">{children}</main>
        <Footer />
        <BoutonAppelFlottant />
        <script
          type="application/ld+json"
          // Échappe « < » pour empêcher toute sortie prématurée de la balise script.
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
        />
      </body>
    </html>
  )
}
