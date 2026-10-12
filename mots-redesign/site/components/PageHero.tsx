import type { ReactNode } from 'react'
import Reveal from '@/components/Reveal'

/**
 * En-tête standard des pages intérieures : surtitre, titre, introduction,
 * fond calme avec orbes dérivantes.
 */
export default function PageHero({
  surtitre,
  titre,
  intro,
  children,
}: {
  surtitre?: string
  titre: string
  intro?: string
  children?: ReactNode
}) {
  return (
    <section className="relative overflow-hidden bg-ecume">
      <div aria-hidden="true" className="orbe -top-24 -left-16 h-72 w-72 bg-sapin/20" />
      <div aria-hidden="true" className="orbe -bottom-32 right-0 h-80 w-80 bg-accent/10" style={{ animationDelay: '-8s' }} />
      <div className="conteneur relative py-16 sm:py-20">
        <Reveal>
          {surtitre && <p className="etiquette">{surtitre}</p>}
          <h1 className="titre-hero mt-4 max-w-3xl text-marine">{titre}</h1>
          {intro && <p className="mt-5 max-w-2xl text-lg text-encre/75">{intro}</p>}
          {children && <div className="mt-7">{children}</div>}
        </Reveal>
      </div>
    </section>
  )
}
