import Link from 'next/link'
import { PRODUIT, SIGNATURE, THESE } from '@/lib/infos'

// Page provisoire : la page « Pourquoi » complète est construite par l'équipe
// de construction à partir du brief. Elle garantit un build vert entre-temps.
export default function Accueil() {
  return (
    <section className="conteneur py-20">
      <p className="etiquette">{SIGNATURE}</p>
      <h1 className="titre titre-hero mt-4">{PRODUIT}</h1>
      <p className="phrase mt-8 max-w-3xl">{THESE}</p>
      <p className="mt-10">
        <Link href="/demo/soignant" className="bouton">Voir le journal de garde</Link>
      </p>
    </section>
  )
}
