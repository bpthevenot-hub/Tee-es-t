import Reveal from '@/components/Reveal'
import { ETUDES, ETUDE_ESPOIR, TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

/**
 * « Ce que dit la science » — les chiffres publiés sur la santé des soignants
 * (méta-analyses, enquête nationale), chacun relié à sa publication, puis la
 * contre-preuve d'espoir : l'accompagnement fonctionne (The Lancet, 2016).
 */
export default function EtudesScientifiques() {
  return (
    <section aria-labelledby="titre-science" className="bg-ecume/60 py-16">
      <div className="conteneur">
        <Reveal>
          <p className="etiquette">Ce que dit la science</p>
          <h2 id="titre-science" className="titre-section mt-3 max-w-2xl text-marine">
            L’épuisement des soignants n’est pas un ressenti. Il est mesuré.
          </h2>
        </Reveal>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {ETUDES.map((e, i) => (
            <Reveal key={e.url} delay={i * 110}>
              <article className="carte flex h-full flex-col">
                <p className="text-4xl font-bold tracking-tight text-sapin">{e.valeur}</p>
                <p className="mt-2 text-encre/80">{e.texte}</p>
                <p className="mt-auto pt-4 text-xs text-brume">
                  <a
                    href={e.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline decoration-brume/40 underline-offset-2 transition hover:text-sapin"
                  >
                    {e.source} ↗
                  </a>
                </p>
              </article>
            </Reveal>
          ))}
        </div>

        <Reveal delay={200} className="mt-6">
          <aside className="carte border-l-4 !border-l-accent sm:flex sm:items-center sm:justify-between sm:gap-8">
            <div>
              <h3 className="font-bold text-marine">La bonne nouvelle : l’accompagnement fonctionne.</h3>
              <p className="mt-1 text-encre/75">{ETUDE_ESPOIR.texte}</p>
              <p className="mt-2 text-xs text-brume">
                <a
                  href={ETUDE_ESPOIR.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline decoration-brume/40 underline-offset-2 transition hover:text-sapin"
                >
                  {ETUDE_ESPOIR.source} ↗
                </a>
              </p>
            </div>
            <a href={TEL_HREF} className="bouton-appel mt-5 shrink-0 sm:mt-0">
              {TEL_AFFICHE}
            </a>
          </aside>
        </Reveal>
      </div>
    </section>
  )
}
