import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Link from 'next/link'
import { PRODUIT } from '@/lib/infos'
import { FAITS, A_MESURER } from '@/lib/faits'
import { AMesurer, Pastille } from '@/components/ui'

export const metadata: Metadata = {
  title: 'Preuves',
  description:
    'Tous les chiffres utilisés sur le site Relève, avec leur source et leur nature, mesurée ou déclarée ; ce qui reste à mesurer ; la méthode de recoupement.',
}

// ---------------------------------------------------------------------------
// Tout vient de lib/faits.ts. Cette page est la seule source de chiffres du
// site : un chiffre absent de ce tableau n'a pas le droit d'exister ailleurs.
// ---------------------------------------------------------------------------
const NB_MESURES = FAITS.filter((f) => f.nature === 'mesuré').length
const NB_DECLARES = FAITS.filter((f) => f.nature === 'déclaré').length

const NATURES = {
  mesuré: {
    ton: 'neutre',
    definition: 'Étude publiée ou statistique publique, avec une méthode consultable : méta-analyse, enquête, rapport d’une institution.',
  },
  déclaré: {
    ton: 'ambre',
    definition: 'Chiffre communiqué par une entreprise, une association ou un service, sans vérification indépendante. Il est repris tel quel, et dit comme tel.',
  },
} as const

/** Ce qui a été écarté, volontairement, et qu’on ne verra nulle part sur le site. */
const ECARTES = [
  'Un coût de remplacement d’infirmière ou un coût d’absentéisme par poste présenté comme « français » : il n’existe pas, il faudrait le modéliser et le dire.',
  'Un retour sur investissement présenté comme hospitalier, emprunté à d’autres secteurs ou d’autres pays.',
  'Un effet de la thérapie numérique sur le burnout des soignants : la preuve n’est pas là.',
  'Une prévalence récente des addictions chez les soignants français.',
  'Tout chiffre Éos présenté comme vérifié : le modèle est public, ses résultats ne le sont pas.',
] as const

// ---------------------------------------------------------------------------
// Blocs locaux de mise en page.
// ---------------------------------------------------------------------------

/** Section de page : filet, étiquette, titre de niveau 2. */
function Section({ etiquette, titre, id, children }: { etiquette: string; titre: string; id: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-titre`} className="filet">
      <div className="conteneur py-16 sm:py-24">
        <p className="etiquette">{etiquette}</p>
        <h2 id={`${id}-titre`} className="titre titre-section mt-3">
          {titre}
        </h2>
        <div className="mt-10 sm:mt-12">{children}</div>
      </div>
    </section>
  )
}

/** Lien de source, ouvert dans un nouvel onglet, flèche en clair. */
function Source({ texte, url }: { texte: string; url: string }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
      {texte} <span aria-hidden="true">↗</span>
      <span className="sr-only"> (nouvel onglet)</span>
    </a>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function Preuves() {
  return (
    <>
      {/* Héro */}
      <section className="conteneur py-20 sm:py-28" aria-labelledby="preuves-titre">
        <p className="etiquette">Preuves</p>
        <h1 id="preuves-titre" className="titre titre-hero mt-4">
          Chaque chiffre, sa source
        </h1>
        <p className="phrase mt-10 max-w-4xl">Rien ici qui n’ait sa source. Ce qui manque est marqué à mesurer.</p>
        <p className="sourd texte mt-6 text-[1.05rem]">
          Ce tableau est la seule origine des chiffres du site {PRODUIT}. Un chiffre qui n’y figure pas n’a pas le droit d’apparaître ailleurs. Aucun n’est à nous.
        </p>

        <dl className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-4" aria-label="Décompte du tableau">
          <div className="plaque">
            <dt className="etiquette">Faits sourcés</dt>
            <dd className="donnee mt-2 text-3xl leading-none">{FAITS.length}</dd>
          </div>
          <div className="plaque">
            <dt className="etiquette">Mesurés</dt>
            <dd className="donnee mt-2 text-3xl leading-none">{NB_MESURES}</dd>
          </div>
          <div className="plaque">
            <dt className="etiquette">Déclarés</dt>
            <dd className="donnee mt-2 text-3xl leading-none">{NB_DECLARES}</dd>
          </div>
          <div className="plaque border-dashed">
            <dt className="etiquette">À mesurer</dt>
            <dd className="donnee mt-2 text-3xl leading-none">{A_MESURER.length}</dd>
          </div>
        </dl>
      </section>

      {/* Le tableau */}
      <Section etiquette="01" titre="Les faits" id="faits">
        <div className="grid gap-4 md:grid-cols-2" aria-label="Lecture de la colonne nature">
          {(Object.keys(NATURES) as Array<keyof typeof NATURES>).map((n) => (
            <div key={n} className="flex items-start gap-3">
              <Pastille ton={NATURES[n].ton}>{n}</Pastille>
              <p className="sourd text-[0.88rem]">{NATURES[n].definition}</p>
            </div>
          ))}
        </div>

        {/* « relative » : les éléments sr-only du tableau (caption, mentions de lien) sont en
            position absolue ; sans ancre, leur bloc conteneur est le document et ils
            débordent la page à 390 px malgré le défilement interne. */}
        <div className="defilable relative mt-8 border-b border-[var(--mode-filet)]">
          <table className="tableau min-w-[56rem]">
            <caption className="sr-only">Les faits utilisés sur le site, avec leur valeur, leur source et leur nature</caption>
            <thead>
              <tr>
                <th scope="col" className="w-10">
                  N°
                </th>
                <th scope="col" className="w-36">
                  Valeur
                </th>
                <th scope="col">Fait</th>
                <th scope="col" className="w-72">
                  Source
                </th>
                <th scope="col" className="w-28">
                  Nature
                </th>
              </tr>
            </thead>
            <tbody>
              {FAITS.map((f, i) => (
                <tr key={f.valeur} id={`fait-${i + 1}`} className="align-top">
                  <td className="donnee text-[var(--mode-sourd)]">{String(i + 1).padStart(2, '0')}</td>
                  <th scope="row" className="donnee !normal-case !tracking-normal !text-[1.3rem] !font-medium !text-[var(--mode-texte)] whitespace-nowrap">
                    {f.valeur}
                  </th>
                  <td>{f.texte}</td>
                  <td className="sourd text-[0.85rem]">
                    <Source texte={f.source} url={f.url} />
                  </td>
                  <td>
                    <Pastille ton={NATURES[f.nature].ton}>{f.nature}</Pastille>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="sourd mt-4 text-[0.78rem]">
          Sur un écran étroit, le tableau se fait glisser horizontalement. Les liens ouvrent la source dans un nouvel onglet ; certains pointent vers l’éditeur ou l’institution, pas vers le document exact.
        </p>
      </Section>

      {/* À mesurer */}
      <Section etiquette="02" titre="À mesurer" id="a-mesurer">
        <p className="phrase max-w-4xl">Aucun de ces chiffres n’existe. {PRODUIT} ne les avancera pas tant qu’un établissement nommé ne les aura pas signés.</p>
        <ol className="mt-12 grid gap-x-10 md:grid-cols-2" aria-label="Ce qui reste à mesurer">
          {A_MESURER.map((m, i) => (
            <li key={m} className="filet grid grid-cols-[2.6rem_1fr_auto] items-center gap-3 py-4 first:border-t-0 md:[&:nth-child(2)]:border-t-0">
              <span className="donnee text-[var(--mode-sourd)]" aria-hidden="true">
                {String(i + 1).padStart(2, '0')}
              </span>
              <span className="text-[1.02rem]">{m}</span>
              <AMesurer />
            </li>
          ))}
        </ol>
        <p className="sourd texte mt-8 text-[0.95rem]">
          La preuve vendue sera un chiffre signé par un établissement nommé, rendu chaque année aux établissements et à MOTS, jamais une capture d’écran.
        </p>
      </Section>

      {/* Méthode */}
      <Section etiquette="03" titre="Méthode" id="methode-preuves">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr] lg:gap-16">
          <div>
            <h3 className="titre titre-bloc">Comment ce tableau a été construit</h3>
            <ul className="mt-5 flex flex-col" aria-label="Règles de construction du tableau">
              {[
                'Les sources ont été rapprochées en octobre 2026 ; certaines restent à relire dans le document d’origine.',
                'Chaque fait porte une nature. « Mesuré » renvoie à une étude ou une statistique publique ; « déclaré » à un chiffre d’entreprise, d’association ou de service, repris sans vérification indépendante.',
                'Plusieurs chiffres d’entreprise restent déclaratifs : absentéisme des groupes de cliniques, inscriptions au NHS Practitioner Health, file de l’association MOTS. Ils sont utiles, pas prouvés.',
                'Aucun chiffre n’est utilisé ailleurs sur le site s’il n’est pas dans ce tableau. Les pages prennent leurs faits par leur valeur dans la même liste ; un chiffre absent fait échouer la page.',
                'Quand deux sources divergent, la plus prudente est retenue et la divergence est écrite dans le fait lui-même.',
              ].map((r) => (
                <li key={r} className="filet grid grid-cols-[1.2rem_1fr] gap-3 py-4 text-[0.95rem] first:border-t-0 first:pt-0">
                  <span className="donnee text-[var(--mode-sourd)]" aria-hidden="true">
                    —
                  </span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="titre titre-bloc">Ce qui a été écarté</h3>
            <p className="sourd mt-2 text-[0.92rem]">Des chiffres qui circulent et qu’on ne verra nulle part ici.</p>
            <ul className="mt-5 flex flex-col" aria-label="Chiffres écartés">
              {ECARTES.map((e) => (
                <li key={e} className="filet grid grid-cols-[1.2rem_1fr] gap-3 py-4 text-[0.92rem] first:border-t-0 first:pt-0">
                  <span className="donnee text-[var(--mode-sourd)]" aria-hidden="true">
                    —
                  </span>
                  <span>{e}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-12 border-l-4 border-[var(--mode-accent)] pl-5 sm:pl-6">
          <p className="etiquette">Si vous trouvez une erreur</p>
          <p className="texte mt-3 text-[1.02rem]">
            Un chiffre faux dans ce tableau est une faute, pas un détail. Signalez-le : il sera corrigé ou retiré, et la correction sera visible.
          </p>
        </div>
      </Section>

      {/* Suite */}
      <section className="filet" aria-labelledby="preuves-suite-titre">
        <div className="conteneur py-20 sm:py-28">
          <p className="etiquette">Et maintenant</p>
          <h2 id="preuves-suite-titre" className="titre titre-section mt-3">
            Lire la méthode
          </h2>
          <p className="phrase mt-8 max-w-4xl">Les faits disent pourquoi. La méthode dit comment, et ce qui ne se fera pas.</p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/methode" className="bouton">
              La méthode
            </Link>
            <Link href="/demo/direction" className="bouton bouton-second">
              L’écran direction
            </Link>
          </div>
          <p className="sourd mt-6 text-[0.8rem]">Démonstration : rien n’est enregistré sur ce site, aucune donnée n’est collectée.</p>
        </div>
      </section>
    </>
  )
}
