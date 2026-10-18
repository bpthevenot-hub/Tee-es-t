import type { Metadata } from 'next'
import { BandeauDemoEcran } from '@/components/ui'
import Agregats from '@/components/Agregats'
import { SEUIL_CELLULE } from '@/lib/demo'

export const metadata: Metadata = {
  title: 'Agrégats',
  description:
    'Espace direction de Relève : taux de recours par grande catégorie sous seuil de dix, thématiques dominantes, tendance mensuelle avec latence, posés à côté des indicateurs saisis par l’établissement. Jamais un nom, jamais un score. Démonstration, données fictives.',
}

/** Écran direction — « Agrégats » (brief § 5.3). Le seul écran lumineux : il parle à un acheteur. */
export default function PageDirection() {
  return (
    // Mode jour : papier sur les mêmes accents. Il s'applique à tout l'écran — bandeau de démonstration,
    // en-tête et agrégats — mais pas au site : la navigation et le pied de page restent sur anthracite.
    // Le filet du bandeau (couleur fixe « filet ») est ramené au filet du mode pour ne pas rayer le papier.
    <div
      data-mode="jour"
      className="fondu border-y border-[var(--mode-filet)] bg-[var(--mode-fond)] text-[var(--mode-texte)] [&_.border-filet]:border-[var(--mode-filet)]"
    >
      <BandeauDemoEcran espace="Agrégats" pour="la direction de l’établissement" />
      <div className="conteneur pt-8">
        <p className="etiquette">Espace direction</p>
        <h1 className="titre titre-section mt-2">Agrégats</h1>
        <p className="sourd texte mt-3 text-[0.95rem]">
          Ce que l’établissement reçoit : des comptages sous seuil de {SEUIL_CELLULE}, une tendance avec un mois de latence, ses propres
          indicateurs à côté. Aucun nom, aucun score, aucun service identifiable. Le mode jour s’applique à cet écran seulement.
        </p>
      </div>
      <Agregats />
    </div>
  )
}
