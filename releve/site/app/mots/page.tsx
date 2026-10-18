import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Link from 'next/link'
import { PRODUIT, MOTS_SITE, SNB_SITE, TEL_MOTS_AFFICHE, TEL_MOTS_HREF, TEL_3114_AFFICHE, TEL_3114_HREF } from '@/lib/infos'
import { FAITS, A_MESURER } from '@/lib/faits'
import { Encadre, AMesurer } from '@/components/ui'

export const metadata: Metadata = {
  title: 'Pour MOTS',
  description:
    'Relève pour MOTS : même produit, autre porte. Le lien générique affiché par MOTS, les Transmissions comme outil des médecins effecteurs, les Agrégats comme bilan d’activité. Proposition non sollicitée, non affiliée.',
}

// ---------------------------------------------------------------------------
// Faits : uniquement lib/faits.ts. Le fait MOTS porte tout ce que cette page
// avance sur l'association (1 700+, neuf professions, 7 j/7, depuis 2010).
// ---------------------------------------------------------------------------
const fait = (valeur: string) => {
  const f = FAITS.find((x) => x.valeur === valeur)
  if (!f) throw new Error(`Fait absent de lib/faits.ts : ${valeur}`)
  return f
}
const FAIT_MOTS = fait('1 700+')

/** Démonstration de refonte du site MOTS, par SNB Consulting. */
const MOTS_DEMO_SITE = 'https://mots-redesign-demo.snb.center'

/** La transposition, élément par élément. */
type Ligne = { element: string; cliniques: string; mots: string }
const TRANSPOSITION: Ligne[] = [
  {
    element: 'La porte d’entrée',
    cliniques: 'Un lien générique affiché par l’établissement : transmissions, vestiaires, intranet, après un moment à risque.',
    mots: `Le même lien, affiché par MOTS : site refondu, ligne ${TEL_MOTS_AFFICHE}. Le soignant arrive de lui-même, d’où qu’il exerce.`,
  },
  {
    element: 'Qui répond',
    cliniques: 'Un médecin pair formé, hors établissement, choisi par profession.',
    mots: 'Un médecin effecteur de MOTS, formé au DIU « Soigner les soignants ».',
  },
  {
    element: 'Espace « Transmissions »',
    cliniques: 'L’espace de travail du binôme pair et infirmier coordinateur.',
    mots: 'L’outil de travail des médecins effecteurs : file active, dossier partagé, créneaux de 15 minutes, relais tracés.',
  },
  {
    element: 'Espace « Agrégats »',
    cliniques: 'Le tableau de la direction : recours par catégorie sous seuil de dix, à côté de ses propres indicateurs.',
    mots: 'Le bilan d’activité de MOTS, tel que l’espace Agrégats le tiendrait : appels, professions, délais, suites.',
  },
  {
    element: 'Qui voit un nom',
    cliniques: 'Jamais l’employeur.',
    mots: 'Le médecin effecteur choisi par le soignant et, avec son consentement tracé, son binôme. Jamais l’employeur.',
  },
  {
    element: 'Qui paie',
    cliniques: 'L’établissement. Le mode de tarification reste à décider ; rien n’est facturé par soignant.',
    mots: 'Le financement des établissements paie la plateforme, mise à disposition de MOTS.',
  },
]

/** Les lignes du bilan d'activité. Un seul chiffre existe ; les autres sont à mesurer. */
type LigneBilan = { indicateur: string; detail: string; valeur?: string }
const BILAN: LigneBilan[] = [
  { indicateur: 'Soignants accompagnés', detail: 'depuis 2010, chiffre déclaré par MOTS', valeur: '1 700+' },
  { indicateur: 'Professions', detail: 'professions à ordre représentées', valeur: '9' },
  { indicateur: 'Appels reçus', detail: 'par mois, par profession, par région' },
  { indicateur: 'Délai de premier contact', detail: 'entre l’appel et le premier échange avec un médecin effecteur' },
  { indicateur: 'Suites', detail: 'écoute seule, suivi engagé, orientation, arrêt, retour à l’exercice' },
]

/** Les trois plaques. */
const APPORT_MOTS = [
  `${FAIT_MOTS.valeur} soignants accompagnés depuis 2010`,
  'Neuf professions à ordre',
  'Des médecins pairs formés au DIU « Soigner les soignants »',
  `Une ligne ouverte 7 j/7 : ${TEL_MOTS_AFFICHE}`,
] as const

const APPORT_RELEVE = [
  'Un dossier partagé entre effecteurs, avec le consentement tracé du soignant',
  'La planification des créneaux de 15 minutes et le rappel du créneau',
  'La facturation conventionnelle et Mon soutien psy portées par la plateforme',
  'Le bilan d’activité, produit sans tableur, prêt pour un financeur',
  'Le mode nuit, le mode couloir, le droit de fermer l’application',
] as const

const DECIDE_ENSEMBLE = [
  'La part du financement des établissements reversée au réseau de pairs',
  'La rémunération et le recrutement des médecins effecteurs',
  'La gouvernance du réseau partagé entre les deux portes',
  'Le registre d’outcomes rendu chaque année à MOTS et aux établissements',
] as const

// ---------------------------------------------------------------------------
// Blocs locaux de mise en page.
// ---------------------------------------------------------------------------

/** Section de page : filet, grand espace, numéro et titre de niveau 2. */
function Section({ numero, titre, id, children }: { numero: string; titre: string; id: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-titre`} className="filet">
      <div className="conteneur py-16 sm:py-24">
        <p className="etiquette">{numero}</p>
        <h2 id={`${id}-titre`} className="titre titre-section mt-3">
          {titre}
        </h2>
        <div className="mt-10 sm:mt-12">{children}</div>
      </div>
    </section>
  )
}

/** Liste sobre à filets, pour les trois plaques. */
function Liste({ items, label }: { items: readonly string[]; label: string }) {
  return (
    <ul className="mt-4 flex flex-col" aria-label={label}>
      {items.map((x) => (
        <li key={x} className="filet py-3 text-[0.95rem] first:border-t-0 first:pt-0">
          {x}
        </li>
      ))}
    </ul>
  )
}

/**
 * Le bilan d'activité, en mode jour : comme l'espace Agrégats, il parle à
 * quelqu'un qui finance. C'est le seul bloc clair de la page.
 */
function BilanActivite() {
  return (
    <figure
      data-mode="jour"
      className="rounded-[var(--radius-clinique)] border border-[var(--mode-filet)] bg-[var(--mode-fond)] p-5 text-[var(--mode-texte)] sm:p-7"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-2">
        <h3 className="titre titre-bloc">Bilan d’activité</h3>
        <p className="etiquette">Association MOTS · exercice à venir · maquette</p>
      </div>
      <dl className="mt-6">
        {BILAN.map((b) => (
          <div key={b.indicateur} className="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1 border-t border-[var(--mode-filet)] py-4 first:border-t-0 first:pt-0">
            <dt>
              <span className="block text-[0.98rem]">{b.indicateur}</span>
              <span className="sourd block text-[0.8rem]">{b.detail}</span>
            </dt>
            <dd className="text-right">
              {b.valeur ? <span className="donnee text-2xl sm:text-3xl">{b.valeur}</span> : <AMesurer />}
            </dd>
          </div>
        ))}
      </dl>
      <figcaption className="sourd mt-5 text-[0.78rem]">
        Les lignes vides ne sont pas un oubli. C’est ce que la plateforme remplit, mois après mois, sans qu’un médecin ait à tenir un tableur. Les deux chiffres présents sont déclarés par MOTS (
        <a href={FAIT_MOTS.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
          {FAIT_MOTS.source} ↗
        </a>
        ).
      </figcaption>
    </figure>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function PourMots() {
  return (
    <>
      {/* 1. Héro */}
      <section className="conteneur py-20 sm:py-28 lg:py-36" aria-labelledby="hero-titre">
        <p className="etiquette">Transposition</p>
        <h1 id="hero-titre" className="titre titre-hero mt-4">
          {PRODUIT} pour MOTS
        </h1>
        <p className="phrase mt-10 max-w-4xl">Même produit, autre porte.</p>
        <p className="sourd texte mt-6 text-[1.05rem]">
          Relève est conçu pour être vendu aux établissements. Le même logiciel, sans rien y changer, peut être tenu par l’association MOTS, qui soigne les soignants depuis 2010 avec des médecins pairs. Cette page montre ce qui se transpose, ce que chacun apporte, et ce qui reste à décider ensemble.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <a href={MOTS_SITE} target="_blank" rel="noopener noreferrer" className="bouton bouton-second">
            Le site de MOTS ↗
          </a>
          <a href={MOTS_DEMO_SITE} target="_blank" rel="noopener noreferrer" className="bouton bouton-second">
            Démo de refonte du site ↗
          </a>
        </div>
        <p className="sourd mt-6 text-[0.8rem]">
          Proposition non sollicitée, non affiliée à l’association MOTS. Aucun de ces écrans n’a été validé par elle.
        </p>
      </section>

      {/* 2. Ce qui se transpose */}
      <Section numero="01" titre="Ce qui se transpose" id="transposition">
        <p className="texte text-[1.05rem]">
          Chez un établissement, le lien générique est affiché dans les transmissions et les vestiaires. Chez MOTS, il est affiché par le site refondu et par la ligne. Tout le reste est identique.
        </p>
        <div className="defilable mt-8 rounded-[var(--radius-clinique)] border border-[var(--mode-filet)]">
          <table className="tableau min-w-[42rem]">
            <caption className="sr-only">La transposition de Relève, élément par élément, entre les cliniques et MOTS</caption>
            <thead>
              <tr>
                <th scope="col" className="border-t-0 w-[11rem]">
                  Élément
                </th>
                <th scope="col" className="border-t-0">
                  Relève pour cliniques
                </th>
                <th scope="col" className="border-t-0 text-[var(--mode-accent)]">
                  Relève pour MOTS
                </th>
              </tr>
            </thead>
            <tbody>
              {TRANSPOSITION.map((l) => (
                <tr key={l.element}>
                  <th scope="row" className="titre text-[1rem] normal-case tracking-[0.02em] text-[var(--mode-texte)]">
                    {l.element}
                  </th>
                  <td className="sourd">{l.cliniques}</td>
                  <td className="border-l border-[var(--mode-filet)]">{l.mots}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="mt-8 grid gap-4 md:grid-cols-2" aria-label="Les deux espaces transposés">
          <li>
            <Link href="/demo/equipe" className="plaque fondu flex h-full flex-col hover:border-[var(--mode-accent)] focus-visible:border-[var(--mode-accent)]">
              <span className="etiquette">Espace « Transmissions »</span>
              <span className="titre titre-bloc mt-3 block">L’outil de travail des médecins effecteurs</span>
              <span className="mt-3 block text-[0.95rem]">
                File active, dossier partagé, protocole en étapes, notes rédigées par un humain. Rien ne s’allume tant que tout est normal ; seul s’allume ce que le soignant a lui-même signalé.
              </span>
              <span className="mono mt-auto block pt-6 text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-accent)]">Ouvrir l’écran →</span>
            </Link>
          </li>
          <li>
            <Link href="/demo/direction" className="plaque fondu flex h-full flex-col hover:border-[var(--mode-accent)] focus-visible:border-[var(--mode-accent)]">
              <span className="etiquette">Espace « Agrégats »</span>
              <span className="titre titre-bloc mt-3 block">Le bilan d’activité de MOTS</span>
              <span className="mt-3 block text-[0.95rem]">
                Le même écran qu’une direction de clinique, tenu par l’association : appels, professions, délais, suites. Sous seuil de dix, avec latence, sans jamais un nom.
              </span>
              <span className="mono mt-auto block pt-6 text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-accent)]">Ouvrir l’écran →</span>
            </Link>
          </li>
        </ul>
      </Section>

      {/* 3. Un bilan à publier */}
      <Section numero="02" titre="Un bilan à publier" id="bilan">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.2fr] lg:gap-16">
          <div>
            <p className="phrase max-w-xl">Quatre colonnes suffisent à un financeur.</p>
            <p className="texte mt-6 text-[1.02rem]">
              Appels, professions, délais, suites. Ce sont les quatre questions qu’un financeur institutionnel ou un groupe de cliniques pose à une association avant de signer. L’espace Agrégats le tiendrait, à partir de ce que les médecins effecteurs saisissent déjà dans les Transmissions.
            </p>
            <ul className="mt-8 flex flex-col gap-4" aria-label="À qui sert le bilan">
              <li className="grid grid-cols-[3.2rem_1fr] gap-4">
                <span className="donnee pt-1 text-2xl text-[var(--mode-accent)]" aria-hidden="true">
                  I
                </span>
                <div>
                  <h3 className="titre titre-bloc">
                    <span className="sr-only">I. </span>
                    Pour ses financeurs
                  </h3>
                  <p className="mt-2 text-[0.95rem]">Un bilan annuel qui montre l’activité de l’année, par profession et par région, à côté du total cumulé depuis 2010.</p>
                </div>
              </li>
              <li className="grid grid-cols-[3.2rem_1fr] gap-4">
                <span className="donnee pt-1 text-2xl text-[var(--mode-accent)]" aria-hidden="true">
                  II
                </span>
                <div>
                  <h3 className="titre titre-bloc">
                    <span className="sr-only">II. </span>
                    Pour les groupes qu’il sollicite
                  </h3>
                  <p className="mt-2 text-[0.95rem]">Le délai de premier contact et les suites données : ce qu’un directeur de clinique veut lire avant de recommander la ligne à ses équipes.</p>
                </div>
              </li>
            </ul>
          </div>
          <BilanActivite />
        </div>
      </Section>

      {/* 4. Trois plaques */}
      <Section numero="03" titre="Un réseau, deux portes" id="reseau">
        <p className="texte text-[1.05rem]">
          Relève pour cliniques et Relève pour MOTS partagent le même réseau de pairs. Les médecins formés qui répondent à la ligne sont ceux vers qui Relève oriente les soignants des établissements. L’un finance l’autre.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="plaque flex flex-col">
            <p className="etiquette">Ce que MOTS apporte</p>
            <Liste items={APPORT_MOTS} label="Ce que MOTS apporte" />
            <p className="sourd mt-auto pt-5 text-[0.75rem]">
              <a href={FAIT_MOTS.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
                {FAIT_MOTS.source} ↗
              </a>{' '}
              · chiffres déclarés
            </p>
          </div>
          <div className="plaque flex flex-col border-l-4 border-l-[var(--mode-accent)]">
            <p className="etiquette">Ce que Relève apporte</p>
            <Liste items={APPORT_RELEVE} label="Ce que Relève apporte" />
            <p className="sourd mt-auto pt-5 text-[0.75rem]">Le logiciel, sa maintenance, l’hébergement de santé et le DPO. Aucun acte médical.</p>
          </div>
          <div className="plaque flex flex-col">
            <p className="etiquette">Ce qu’on décide ensemble</p>
            <ul className="mt-4 flex flex-col" aria-label="Ce qu’on décide ensemble">
              {DECIDE_ENSEMBLE.map((x) => (
                <li key={x} className="filet flex flex-wrap items-center justify-between gap-x-4 gap-y-1 py-3 text-[0.95rem] first:border-t-0 first:pt-0">
                  <span>{x}</span>
                  <AMesurer>à décider</AMesurer>
                </li>
              ))}
            </ul>
            <p className="sourd mt-auto pt-5 text-[0.75rem]">Rien de ceci n’est arrêté. Ce sont les termes d’une discussion qui n’a pas eu lieu.</p>
          </div>
        </div>

        <div className="mt-12 border-l-4 border-[var(--mode-accent)] pl-5 sm:pl-6">
          <p className="etiquette">Comment l’un finance l’autre</p>
          <p className="phrase mt-3 max-w-4xl">
            Les établissements financent la plateforme. La plateforme équipe MOTS. MOTS fournit les pairs. Le soin est facturé par les professionnels et remboursé dans le droit commun ; le dispositif, lui, n’est jamais facturé au soignant.
          </p>
        </div>
      </Section>

      {/* 5. Avant de parler chiffres */}
      <Section numero="04" titre="Avant de parler chiffres" id="mesurer">
        <div className="grid gap-8 lg:grid-cols-[1.2fr_1fr] lg:gap-12">
          <div>
            <p className="texte text-[1.05rem]">
              Les mêmes engagements que pour les cliniques. Le bilan d’activité de MOTS commence vide et se remplit avec l’usage. Aucun chiffre n’est promis avant d’être mesuré.
            </p>
            <ul className="mt-8 flex flex-col" aria-label="Ce que Relève s’engage à mesurer">
              {A_MESURER.map((m) => (
                <li key={m} className="filet flex flex-wrap items-center justify-between gap-x-4 gap-y-1 py-3 text-[0.98rem] first:border-t-0 first:pt-0">
                  <span>{m}</span>
                  <AMesurer />
                </li>
              ))}
            </ul>
          </div>
          <div className="flex flex-col gap-4">
            <Encadre etiquette="Proposition non sollicitée" accent>
              <p className="text-[0.95rem]">
                Cette page est une proposition de SNB Consulting. L’association MOTS ne l’a pas demandée, n’y est pas affiliée et n’a validé aucun de ces écrans. Les seuls chiffres cités sur MOTS sont ceux qu’elle publie elle-même.
              </p>
              <p className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[0.85rem]">
                <a href={MOTS_SITE} target="_blank" rel="noopener noreferrer" className="mono underline underline-offset-4">
                  association-mots.org ↗
                </a>
                <a href={MOTS_DEMO_SITE} target="_blank" rel="noopener noreferrer" className="mono underline underline-offset-4">
                  mots-redesign-demo.snb.center ↗
                </a>
              </p>
            </Encadre>
            <Encadre etiquette="Si ça ne va pas, maintenant">
              <p className="text-[0.95rem]">
                Un médecin pair de MOTS, 7 j/7 :{' '}
                <a href={TEL_MOTS_HREF} className="donnee underline underline-offset-4">
                  {TEL_MOTS_AFFICHE}
                </a>
              </p>
              <p className="mt-3">
                <a href={TEL_3114_HREF} className="bouton bouton-3114">
                  {TEL_3114_AFFICHE} — prévention du suicide, 24 h/24
                </a>
              </p>
            </Encadre>
          </div>
        </div>
      </Section>

      {/* 6. Appel final */}
      <section className="filet" aria-labelledby="appel-titre">
        <div className="conteneur py-20 sm:py-28">
          <p className="etiquette">Et maintenant</p>
          <h2 id="appel-titre" className="titre titre-section mt-3">
            Une porte, puis l’autre
          </h2>
          <p className="phrase mt-8 max-w-4xl">
            Relève se construit avec un premier établissement. MOTS en reçoit le logiciel dès que le réseau de pairs est partagé. L’ordre peut s’inverser.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <a href={SNB_SITE} rel="noopener noreferrer" className="bouton">
              Écrire à SNB Consulting
            </a>
            <Link href="/methode" className="bouton bouton-second">
              La méthode
            </Link>
            <Link href="/preuves" className="bouton bouton-second">
              Les sources
            </Link>
          </div>
          <p className="sourd mt-6 text-[0.8rem]">Démonstration : rien n’est enregistré sur ce site, aucune donnée n’est collectée.</p>
        </div>
      </section>
    </>
  )
}
