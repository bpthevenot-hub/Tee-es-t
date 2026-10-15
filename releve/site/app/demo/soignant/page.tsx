import type { Metadata } from 'next'
import { BandeauDemoEcran } from '@/components/ui'
import JournalDeGarde from '@/components/JournalDeGarde'

export const metadata: Metadata = {
  title: 'Journal de garde',
  description:
    'Espace soignant de Relève : le prochain micro-rendez-vous avec un pair, le check-in du jour en une couleur et une phrase, le chiffre brut accessible en un tap, le mode nuit et le mode couloir. Démonstration, données fictives.',
}

/** Écran soignant — « Journal de garde » (brief § 5.1). Un écran, une information. */
export default function PageSoignant() {
  return (
    <>
      <BandeauDemoEcran espace="Journal de garde" pour="le soignant" />
      <div className="conteneur pt-8">
        <p className="etiquette">Espace soignant</p>
        <h1 className="titre titre-section mt-2">Journal de garde</h1>
        <p className="sourd texte mt-3 text-[0.95rem]">
          Un écran, une information. Rien n’est enregistré au-delà de cet écran, rien n’est transmis à l’établissement.
        </p>
      </div>
      <JournalDeGarde />
    </>
  )
}
