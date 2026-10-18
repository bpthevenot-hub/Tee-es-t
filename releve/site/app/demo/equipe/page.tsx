import type { Metadata } from 'next'
import { BandeauDemoEcran } from '@/components/ui'
import Transmissions from '@/components/Transmissions'

export const metadata: Metadata = {
  title: 'Transmissions',
  description:
    'Espace équipe de soin de Relève : la file active du binôme pair + infirmier coordinateur, le dossier partagé, le protocole en cinq étapes, la planification des quinze minutes, le relais psychologue avec consentement tracé, le temps d’équipe. Démonstration, données fictives.',
}

/** Écran équipe de soin — « Transmissions » (brief § 5.2). Rien ne s’allume tant que tout est normal. */
export default function PageEquipe() {
  return (
    <>
      <BandeauDemoEcran espace="Transmissions" pour="le binôme pair + infirmier coordinateur" />
      <div className="conteneur pt-8">
        <p className="etiquette">Espace équipe de soin</p>
        <h1 className="titre titre-section mt-2">Transmissions</h1>
        <p className="sourd texte mt-3 text-[0.95rem]">
          La relève du binôme : une file active, un dossier partagé, un protocole court. Rien ne s’allume tant que tout est normal.
          Rien n’est enregistré au-delà de cet écran.
        </p>
      </div>
      <Transmissions />
    </>
  )
}
