import { BANDEAU_DEMO } from '@/lib/infos'

/** Bandeau permanent : démonstration, aucune donnée réelle, aucune affiliation. */
export default function Bandeau() {
  return (
    <div className="bg-black/40 border-b border-filet text-ivoire/80">
      <p className="conteneur mono py-2 text-[0.72rem] leading-snug tracking-wide">
        {BANDEAU_DEMO}
      </p>
    </div>
  )
}
