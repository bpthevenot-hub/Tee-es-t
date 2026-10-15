import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Link from 'next/link'
import { PRODUIT, SIGNATURE, THESE, INNOVATIONS, INTERDITS, SNB_SITE } from '@/lib/infos'
import { FAITS, A_MESURER, EOS } from '@/lib/faits'
import { Chiffre, Encadre, AMesurer } from '@/components/ui'

export const metadata: Metadata = {
  title: 'Pourquoi',
  description:
    'Pourquoi Relève : le problème mesuré, le quadrant vide de l’offre française, ce que l’absentéisme et l’intérim coûtent aux établissements, et ce que Relève fait — et ne fait pas.',
}

// ---------------------------------------------------------------------------
// Faits utilisés sur cette page, pris par leur valeur dans lib/faits.ts.
// Aucun autre chiffre n'apparaît ici.
// ---------------------------------------------------------------------------
const fait = (valeur: string) => {
  const f = FAITS.find((x) => x.valeur === valeur)
  if (!f) throw new Error(`Fait absent de lib/faits.ts : ${valeur}`)
  return f
}
const PROBLEME = ['49 %', '+44 %', '1 sur 10', '1 sur 2'].map(fait)
const ABSENTEISME = fait('10,4 %')
const INTERIM = fait('147 M€')

/** Taux d'absentéisme déclarés, tirés du fait « 10,4 % » — tous présents dans son texte. */
type Taux = { nom: string; periode: string; valeur: string; part: number; reference?: boolean }
const TAUX_ABSENTEISME: Taux[] = [
  { nom: 'Ramsay France', periode: 'exercice 2023', valeur: '12,8 %', part: 12.8 },
  { nom: 'Clariane', periode: '2024', valeur: '10,4 %', part: 10.4 },
  { nom: 'Hôpitaux publics (FHF)', periode: '2024', valeur: '9,2 %', part: 9.2 },
  { nom: 'Santé privée', periode: 'baromètre 2026', valeur: '7,22 %', part: 7.22 },
  { nom: 'Tous secteurs', periode: 'baromètre 2026', valeur: '4,68 %', part: 4.68, reference: true },
]
const PART_MAX = Math.max(...TAUX_ABSENTEISME.map((t) => t.part))

/** Carte de positionnement : coordonnées entre 0 et 1 (x : individu → établissement ; y : écoute → parcours). */
type Point = { n: number; nom: string; x: number; y: number; texte: string; releve?: boolean }
const CARTE: Point[] = [
  { n: 1, nom: 'MOTS', x: 0.14, y: 0.34, texte: 'Ligne de médecins pairs, gratuite pour le soignant, confidentielle. Écoute et orientation, sans établissement en face.' },
  { n: 2, nom: 'SPS', x: 0.24, y: 0.14, texte: 'Ligne d’écoute nationale tenue par des psychologues, anonyme et gratuite. Un appel, rarement un parcours.' },
  { n: 3, nom: 'EAP', x: 0.74, y: 0.2, texte: 'Programmes d’aide aux employés achetés par l’établissement : coachs et écoute, sans parcours clinique ni lien avec ses indicateurs.' },
  { n: 4, nom: 'NHS Practitioner Health', x: 0.42, y: 0.8, texte: 'Service clinique britannique pour les soignants : parcours long, financé hors établissement.' },
  { n: 5, nom: PRODUIT, x: 0.84, y: 0.86, texte: 'Parcours clinique long, soigné par des pairs, vendu à l’établissement, qui ne reçoit que des agrégats. Le quadrant est vide en France.', releve: true },
]

const ESPACES = [
  { href: '/demo/soignant', etiquette: 'Espace soignant', titre: 'Journal de garde', texte: 'Un écran, une information. Le prochain rendez-vous avec votre pair, le check-in du jour, le 3114 toujours à portée. Rien n’est enregistré sans vous.' },
  { href: '/demo/equipe', etiquette: 'Espace équipe de soin', titre: 'Transmissions', texte: 'La file active du binôme pair et infirmier coordinateur. Rien ne s’allume tant que tout est normal ; seul s’allume ce que le soignant a lui-même signalé.' },
  { href: '/demo/direction', etiquette: 'Espace direction', titre: 'Agrégats', texte: 'Le seul écran lumineux. Des agrégats sous seuil de dix, posés à côté de vos propres indicateurs. Aucun nom, aucun score, aucun service identifiable.' },
] as const

const ROMAINS = ['I', 'II', 'III', 'IV', 'V'] as const

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

/** Carte de positionnement en SVG inline. La légende textuelle, en dessous, porte toute l'information. */
function QuadrantVide() {
  const L = 400
  const H = 300
  const marge = 14
  const px = (x: number) => marge + x * (L - 2 * marge)
  const py = (y: number) => H - marge - y * (H - 2 * marge)
  const mx = L / 2
  const my = H / 2
  const releve = CARTE.find((c) => c.releve)

  return (
    <div className="grid gap-6 lg:grid-cols-[1.15fr_1fr] lg:gap-12">
      <figure className="plaque p-4 sm:p-6">
        <div className="grid grid-cols-1 gap-x-3 gap-y-2 sm:grid-cols-[auto_1fr]">
          {/* Axe vertical, en mobile : une ligne au-dessus de la carte. Les libellés
              verticaux se télescopent à 390 px, la colonne suivant la hauteur du SVG. */}
          <p className="etiquette text-[0.62rem] sm:hidden" aria-hidden="true">
            ↑ Parcours clinique long · ↓ Écoute
          </p>
          {/* Axe vertical, à partir de sm : écoute (bas) → parcours clinique long (haut). */}
          <div className="hidden flex-col justify-between py-1 sm:flex" aria-hidden="true">
            <span className="etiquette [writing-mode:vertical-rl] rotate-180 text-[0.62rem] sm:text-[0.68rem]">Parcours clinique long</span>
            <span className="etiquette [writing-mode:vertical-rl] rotate-180 text-[0.62rem] sm:text-[0.68rem]">Écoute</span>
          </div>

          <svg
            viewBox={`0 0 ${L} ${H}`}
            role="img"
            aria-labelledby="carte-titre carte-desc"
            className="block h-auto w-full"
          >
            <title id="carte-titre">Carte de positionnement de l’offre de soutien aux soignants</title>
            <desc id="carte-desc">
              Quatre quadrants. En bas à gauche, écoute pour l’individu, gratuite et anonyme : MOTS et SPS. En bas à droite, écoute payée par l’établissement : les EAP. En haut à gauche, parcours clinique long financé hors établissement : NHS Practitioner Health. En haut à droite, parcours clinique long vendu à l’établissement : Relève, seul dans ce quadrant.
            </desc>
            {/* Quadrant haut-droit : surface à peine marquée, hachures pour ne pas reposer sur la couleur seule. */}
            <defs>
              <pattern id="hachures" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="8" stroke="var(--mode-filet)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect x={mx} y={marge} width={L - marge - mx} height={my - marge} fill="url(#hachures)" opacity="0.6" />
            <rect x={mx} y={marge} width={L - marge - mx} height={my - marge} fill="none" stroke="var(--mode-accent)" strokeWidth="1" strokeDasharray="3 4" />

            {/* Cadre et axes médians */}
            <rect x={marge} y={marge} width={L - 2 * marge} height={H - 2 * marge} fill="none" stroke="var(--mode-filet)" strokeWidth="1" />
            <line x1={mx} y1={marge} x2={mx} y2={H - marge} stroke="var(--mode-filet)" strokeWidth="1" />
            <line x1={marge} y1={my} x2={L - marge} y2={my} stroke="var(--mode-filet)" strokeWidth="1" />

            {/* Mention du quadrant vide */}
            <text x={L - marge - 8} y={marge + 18} textAnchor="end" fontFamily="var(--font-mono)" fontSize="10" letterSpacing="1.4" fill="var(--mode-sourd)">
              QUADRANT VIDE EN FRANCE
            </text>

            {/* Points numérotés */}
            {CARTE.map((c) => (
              <g key={c.n}>
                <circle
                  cx={px(c.x)}
                  cy={py(c.y)}
                  r={c.releve ? 15 : 12}
                  fill={c.releve ? 'var(--mode-accent)' : 'var(--mode-surface-2)'}
                  stroke={c.releve ? 'var(--mode-accent)' : 'var(--mode-texte)'}
                  strokeWidth={c.releve ? 0 : 1.25}
                />
                <text
                  x={px(c.x)}
                  y={py(c.y)}
                  dy="0.36em"
                  textAnchor="middle"
                  fontFamily="var(--font-mono)"
                  fontSize={c.releve ? 15 : 13}
                  fontWeight="600"
                  fill={c.releve ? 'var(--color-encre)' : 'var(--mode-texte)'}
                >
                  {c.n}
                </text>
              </g>
            ))}
            {/* Nom de Relève, seul libellé dans la carte : les autres sont dans la légende. */}
            {releve && (
              <text
                x={px(releve.x)}
                y={py(releve.y) + 32}
                textAnchor="middle"
                fontFamily="var(--font-titre)"
                fontSize="16"
                fontWeight="600"
                letterSpacing="0.8"
                fill="var(--mode-texte)"
              >
                {PRODUIT.toUpperCase()}
              </text>
            )}
          </svg>

          {/* Axe horizontal : individu (gauche) → établissement (droite). */}
          <div className="hidden sm:block" aria-hidden="true" />
          <div className="flex justify-between gap-4">
            <span className="etiquette">
              Individu · gratuit<span className="hidden sm:inline"> · anonyme</span>
            </span>
            <span className="etiquette text-right">
              Établissement · payant<span className="hidden sm:inline"> · piloté</span>
            </span>
          </div>
        </div>
        <figcaption className="sourd mt-4 text-[0.78rem]">
          Positionnement qualitatif, pas une mesure. Axe horizontal : qui paie et qui pilote. Axe vertical : de l’écoute ponctuelle au parcours clinique long.
        </figcaption>
      </figure>

      <ol className="flex flex-col gap-4" aria-label="Légende de la carte">
        {CARTE.map((c) => (
          <li key={c.n} className="grid grid-cols-[2.2rem_1fr] gap-3">
            <span
              className={`donnee flex h-9 w-9 items-center justify-center rounded-[var(--radius-clinique)] text-[0.95rem] ${c.releve ? 'bg-[var(--mode-accent)] text-[var(--color-encre)]' : 'border border-[var(--mode-texte)] text-[var(--mode-texte)]'}`}
              aria-hidden="true"
            >
              {c.n}
            </span>
            <div>
              <p className="titre text-[1.15rem] tracking-[0.03em]">
                {c.nom}
                {c.releve && <span className="etiquette ml-3 normal-case tracking-[0.1em]">quadrant haut-droit</span>}
              </p>
              <p className="sourd mt-1 text-[0.92rem]">{c.texte}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function Pourquoi() {
  return (
    <>
      {/* 1. Héro */}
      <section className="conteneur py-20 sm:py-28 lg:py-36" aria-labelledby="hero-titre">
        <p className="etiquette">{SIGNATURE}</p>
        <h1 id="hero-titre" className="titre titre-hero mt-4">
          {PRODUIT}
        </h1>
        <p className="phrase mt-10 max-w-4xl">{THESE}</p>
        <p className="sourd texte mt-6 text-[1.05rem]">
          Une clinique digitale vendue à l’établissement, soignée par des pairs, conçue pour la garde, qui ne remonte à la direction que des agrégats.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <Link href="/demo/soignant" className="bouton">
            Voir le journal de garde
          </Link>
          <Link href="/methode" className="bouton bouton-second">
            La méthode
          </Link>
        </div>
      </section>

      {/* 2. Le problème, mesuré */}
      <Section numero="01" titre="Le problème, mesuré" id="probleme">
        <p className="texte text-[1.05rem]">
          Quatre chiffres, quatre sources. Aucun n’est à nous. Ils disent pourquoi un dispositif pour les soignants ne peut pas être une ligne de plus.
        </p>
        <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Quatre chiffres sourcés">
          {PROBLEME.map((f) => (
            <li key={f.valeur} className="h-full">
              <Chiffre valeur={f.valeur} texte={f.texte} source={f.source} url={f.url} />
            </li>
          ))}
        </ul>
      </Section>

      {/* 3. Le quadrant vide */}
      <Section numero="02" titre="Le quadrant vide" id="quadrant">
        <p className="phrase max-w-4xl">
          En France, personne ne vend à l’établissement un parcours clinique long pour ses soignants. Les lignes gratuites écoutent. Les EAP coachent. Le quadrant haut-droit est vide.
        </p>
        <div className="mt-12">
          <QuadrantVide />
        </div>
      </Section>

      {/* 4. Ce que ça coûte aux établissements */}
      <Section numero="03" titre="Ce que ça coûte aux établissements" id="cout">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr] lg:gap-16">
          <div>
            <h3 className="titre titre-bloc">Absentéisme</h3>
            <p className="sourd mt-2 text-[0.92rem]">Taux déclarés par les établissements et les baromètres. Chaque barre porte sa valeur.</p>
            <ul className="mt-6 flex flex-col gap-3" aria-label="Taux d’absentéisme déclarés">
              {TAUX_ABSENTEISME.map((t) => (
                <li key={t.nom} className="grid grid-cols-[1fr_auto] items-end gap-x-4 gap-y-1 sm:grid-cols-[11rem_1fr_auto] sm:items-center">
                  <span className="text-[0.95rem]">
                    {t.nom} <span className="sourd text-[0.8rem]">· {t.periode}</span>
                  </span>
                  <span className="donnee text-[1.05rem] sm:order-3">{t.valeur}</span>
                  <span className="col-span-2 h-3 w-full rounded-[2px] bg-[var(--mode-surface-2)] sm:order-2 sm:col-span-1" aria-hidden="true">
                    <span
                      className={`block h-3 rounded-[2px] ${t.reference ? 'bg-[var(--mode-sourd)]' : 'bg-[var(--mode-texte)]'}`}
                      style={{ width: `${(t.part / PART_MAX) * 100}%` }}
                    />
                  </span>
                </li>
              ))}
            </ul>
            <p className="sourd mt-4 text-[0.75rem]">
              <a href={ABSENTEISME.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
                {ABSENTEISME.source} ↗
              </a>
              {' · '}Rapports d’entreprise et baromètres : chiffres déclarés, périmètres non homogènes.
            </p>
          </div>

          <div>
            <h3 className="titre titre-bloc">Intérim médical</h3>
            <p className="sourd mt-2 text-[0.92rem]">Dépense nationale, 2022.</p>
            <div className="plaque mt-6">
              <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2">
                <p className="donnee text-4xl leading-none sm:text-5xl">{INTERIM.valeur}</p>
                <p className="sourd text-[0.85rem]">en 2022, intérim strict</p>
              </div>
              <p className="etiquette mt-6" aria-hidden="true">
                → avec les contrats courts
              </p>
              <p className="donnee mt-2 text-4xl leading-none sm:text-5xl">559 – 662 M€</p>
              <p className="mt-3 text-[0.95rem]">{INTERIM.texte}</p>
              <p className="sourd mt-4 text-[0.75rem]">
                <a href={INTERIM.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
                  {INTERIM.source} ↗
                </a>
              </p>
            </div>
          </div>
        </div>

        <div className="mt-12 border-l-4 border-[var(--mode-accent)] pl-5 sm:pl-6">
          <p className="etiquette">Pour un directeur d’établissement</p>
          <p className="phrase mt-3 max-w-4xl">
            Vous connaissez déjà votre absentéisme et votre facture d’intérim. Relève pose ses agrégats à côté, sans jamais un nom, et s’engage à mesurer avec vous ce qui bouge.
          </p>
        </div>
      </Section>

      {/* 5. Trois espaces */}
      <Section numero="04" titre="Trois espaces" id="espaces">
        <p className="texte text-[1.05rem]">
          Un produit, trois écrans, trois publics. Le soignant, le binôme qui le suit, la direction qui finance. Chacun voit ce qui le concerne, et rien d’autre.
        </p>
        <ul className="mt-8 grid gap-4 md:grid-cols-3" aria-label="Les trois espaces de la démonstration">
          {ESPACES.map((e) => (
            <li key={e.href} className="h-full">
              <Link
                href={e.href}
                className="plaque fondu group flex h-full flex-col hover:border-[var(--mode-accent)] focus-visible:border-[var(--mode-accent)]"
              >
                <span className="etiquette">{e.etiquette}</span>
                <span className="titre titre-bloc mt-3 block">{e.titre}</span>
                <span className="mt-3 block text-[0.95rem]">{e.texte}</span>
                <span className="mono mt-auto block pt-6 text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-accent)]">
                  Ouvrir l’écran →
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </Section>

      {/* 6. Cinq innovations */}
      <Section numero="05" titre="Cinq innovations" id="innovations">
        <ol className="grid gap-x-12 gap-y-8 md:grid-cols-2" aria-label="Les cinq innovations de Relève">
          {INNOVATIONS.map((inno, i) => (
            <li key={inno.titre} className={`grid grid-cols-[3.2rem_1fr] gap-4 ${i === INNOVATIONS.length - 1 && INNOVATIONS.length % 2 === 1 ? 'md:col-span-2 md:max-w-[calc(50%-1.5rem)] md:justify-self-center md:w-full' : ''}`}>
              <span className="donnee pt-1 text-2xl text-[var(--mode-accent)]" aria-hidden="true">
                {ROMAINS[i]}
              </span>
              <div>
                <h3 className="titre titre-bloc">
                  <span className="sr-only">{ROMAINS[i]}. </span>
                  {inno.titre}
                </h3>
                <p className="mt-2 text-[0.95rem]">{inno.texte}</p>
              </div>
            </li>
          ))}
        </ol>
      </Section>

      {/* 7. Éos */}
      <Section numero="06" titre="Ce qu’Éos a réussi — et laissé ouvert" id="eos">
        <p className="texte text-[1.05rem]">
          Éos est une clinique digitale d’addictologie. Elle a ouvert en France un parcours court, en binôme, branché sur le flux amont d’un groupe de cliniques. Relève transpose le modèle aux soignants et reprend ce qu’Éos a laissé ouvert.
        </p>
        <div className="mt-10 grid gap-8 md:grid-cols-2 md:gap-12">
          <div>
            <h3 className="titre titre-bloc">Réussi</h3>
            <ul className="mt-5 flex flex-col">
              {EOS.reussites.map((r) => (
                <li key={r} className="filet py-4 text-[0.95rem] first:border-t-0 first:pt-0">
                  {r}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="titre titre-bloc">Laissé ouvert</h3>
            <ul className="mt-5 flex flex-col">
              {EOS.ouvert.map((o) => (
                <li key={o} className="filet py-4 text-[0.95rem] first:border-t-0 first:pt-0">
                  {o}
                </li>
              ))}
            </ul>
            <p className="sourd mt-5 text-[0.8rem]">Dossier Éos : éléments publics et déclarés, aucun chiffre vérifié de façon indépendante.</p>
          </div>
        </div>
      </Section>

      {/* 8. Ce que Relève ne fait pas, à mesurer, financement */}
      <Section numero="07" titre="Ce que Relève ne fait pas" id="limites">
        <div className="grid gap-8 lg:grid-cols-[1.2fr_1fr] lg:gap-12">
          <ul className="flex flex-col" aria-label="Ce que Relève ne fait pas">
            {INTERDITS.map((x) => (
              <li key={x} className="filet grid grid-cols-[2rem_1fr] gap-3 py-4 text-[1.02rem] first:border-t-0 first:pt-0">
                <span className="donnee text-[var(--mode-sourd)]" aria-hidden="true">
                  —
                </span>
                <span>{x}</span>
              </li>
            ))}
          </ul>

          <div className="flex flex-col gap-4">
            <Encadre etiquette="Avant de parler chiffres" accent>
              <ul className="flex flex-col gap-3">
                {A_MESURER.slice(0, 3).map((m) => (
                  <li key={m} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-[0.95rem]">
                    <span>{m}</span>
                    <AMesurer />
                  </li>
                ))}
              </ul>
              <p className="sourd mt-4 text-[0.8rem]">Aucun de ces chiffres n’existe encore. La preuve vendue sera un chiffre signé par un établissement nommé, pas une capture d’écran.</p>
            </Encadre>

            <Encadre etiquette="Financement">
              <p className="text-[0.95rem]">
                La V1 est hors dispositif médical et financée par l’établissement — appels à projets ARS QVCT et CLACT lorsque l’établissement y est éligible — tandis que le soin lui-même est facturé par les professionnels en leur nom, dans le droit commun du remboursement.
              </p>
            </Encadre>
          </div>
        </div>
      </Section>

      {/* 9. Appel final */}
      <section className="filet" aria-labelledby="appel-titre">
        <div className="conteneur py-20 sm:py-28">
          <p className="etiquette">Et maintenant</p>
          <h2 id="appel-titre" className="titre titre-section mt-3">
            Voir avant de croire
          </h2>
          <p className="phrase mt-8 max-w-4xl">
            Rien ici n’est une preuve. Les trois écrans montrent ce que nous proposons de mesurer, avec vous, dans votre établissement.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <a href={SNB_SITE} rel="noopener noreferrer" className="bouton">
              Demander une démonstration
            </a>
            <Link href="/mots" className="bouton bouton-second">
              Pour MOTS
            </Link>
          </div>
          <p className="sourd mt-6 text-[0.8rem]">Démonstration : rien n’est enregistré sur ce site, aucune donnée n’est collectée.</p>
        </div>
      </section>
    </>
  )
}
