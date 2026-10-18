import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

/**
 * Bouton d'appel toujours visible sur mobile (le public visé appelle depuis
 * un téléphone) : zéro friction entre la détresse et le premier contact.
 */
export default function BoutonAppelFlottant() {
  return (
    <a
      href={TEL_HREF}
      className="bouton-appel fixed bottom-4 right-4 z-50 !px-5 shadow-carte-haute md:hidden"
      aria-label={`Appeler la ligne d’écoute au ${TEL_AFFICHE}`}
    >
      <span aria-hidden="true" className="point-vif h-2.5 w-2.5 rounded-full bg-white" />
      Besoin d’aide ?
    </a>
  )
}
