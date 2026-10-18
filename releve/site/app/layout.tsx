import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import Bandeau from '@/components/Bandeau'
import { PRODUIT, SIGNATURE } from '@/lib/infos'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: `${PRODUIT} — ${SIGNATURE} (démonstration)`,
    template: `%s — ${PRODUIT}`,
  },
  description:
    'Relève : une clinique digitale vendue à l’établissement, soignée par des pairs, conçue pour la garde, qui ne remonte à la direction que des agrégats. Démonstration, aucune donnée réelle.',
  robots: { index: false, follow: false },
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body className="min-h-dvh flex flex-col">
        <a href="#contenu" className="evitement">Aller au contenu</a>
        <Bandeau />
        <Header />
        <main id="contenu" tabIndex={-1} className="flex-1 outline-none">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  )
}
