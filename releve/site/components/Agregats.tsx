'use client'

import { useId, useState } from 'react'
import { AMesurer } from '@/components/ui'
import { TEL_3114_AFFICHE, TEL_3114_HREF } from '@/lib/infos'
import {
  INDICATEURS_ETABLISSEMENT,
  QUI_VOIT_QUOI,
  RECOURS_PAR_CATEGORIE,
  SEUIL_CELLULE,
  TENDANCE,
  THEMATIQUES,
  type Cellule,
} from '@/lib/demo'

/*
  Agrégats — espace direction (brief § 5.3).
  Le mur de verre : des comptages sous seuil, une tendance avec latence, et les
  indicateurs de l'établissement posés à côté — jamais reliés à un individu.
  Tout l'état vit en mémoire React : rien n'est enregistré, rien n'est transmis.
  Dataviz en CSS et SVG inline ; une seule série par graphique, aucune légende
  de couleur, les valeurs sont toujours écrites en toutes lettres.
*/

/** Espace fine insécable avant les unités, comme sur les écrans de garde. */
const NBSP = ' '

/** 14.63 → « 14,6 % ». Formatage manuel : identique au serveur et au navigateur. */
function pourcent(valeur: number, decimales = 1) {
  return `${valeur.toFixed(decimales).replace('.', ',')}${NBSP}%`
}

/** Une cellule est masquée dès que l'effectif OU le recours passe sous le seuil. */
function masquee(c: Cellule) {
  return c.effectif < SEUIL_CELLULE || c.recours < SEUIL_CELLULE
}

const TEXTE_MASQUE = `— masqué (< ${SEUIL_CELLULE})`

/** Un mois de la tendance, tel que porté par lib/demo.ts. */
type Mois = (typeof TENDANCE)[number]

/** Contrat de seuil, rappelé en tête : trois règles, pas une de plus. */
const CONTRAT_SEUIL = [
  `Toute cellule de moins de ${SEUIL_CELLULE} personnes est masquée`,
  'Aucun croisement service × métier × genre',
  'Latence d’un mois',
] as const

/** Financement et cadre (brief § 3, § 4 : garde-fous transversaux). */
const FINANCEMENT = [
  { titre: 'V1 hors dispositif médical', texte: 'Aucun agrément, aucune promesse médicale : l’outil ne dépiste pas, ne diagnostique pas, ne recommande pas.' },
  { titre: 'Appels à projets ARS QVCT / CLACT', texte: 'Sous réserve d’éligibilité de l’établissement. Rien n’est facturé par soignant suivi.' },
  { titre: 'Inscription au DUERP', texte: 'Le dispositif figure au document unique comme mesure de prévention des risques psychosociaux.' },
  { titre: 'Information-consultation du CSE', texte: 'Avant tout déploiement. Les agrégats sont restitués au CSE/CSSCT et au service de santé au travail.' },
] as const

/** Ce que la preuve devra contenir — vide tant qu'aucun chiffre n'existe. */
const PREUVE_ATTENDUE = ['Recours à 6 mois', 'Rétention du suivi', 'Retours au travail'] as const

/* ---------- Barre horizontale en CSS pur ---------- */

type BarreProps = {
  /** Part de la piste occupée, de 0 à 1. Ignorée si hachurée. */
  part: number
  /** Cellule masquée : piste hachurée, aucune largeur signifiante. */
  hachuree?: boolean
}

/** Barre fine (10 px), extrémité arrondie côté donnée, piste neutre. Purement décorative :
 *  la valeur est toujours écrite à côté, la barre n'apporte rien qu'un lecteur d'écran manquerait. */
function Barre({ part, hachuree = false }: BarreProps) {
  const largeur = `${Math.max(0, Math.min(1, part)) * 100}%`
  return (
    <div className="h-[10px] w-full overflow-hidden rounded-[2px] bg-[var(--mode-surface-2)]" aria-hidden="true">
      {hachuree ? (
        <div
          className="h-full w-full"
          style={{ backgroundImage: 'repeating-linear-gradient(135deg, var(--mode-filet) 0 3px, transparent 3px 9px)' }}
        />
      ) : (
        <div className="fondu h-full rounded-r-[4px] bg-[var(--mode-texte)]" style={{ width: largeur }} />
      )}
    </div>
  )
}

/* ---------- Tendance : ligne et points en SVG inline ---------- */

/** Un mois est masqué dès que son agrégat passe sous le seuil : même contrat que les cellules. */
function moisMasque(t: Mois) {
  return t.recours < SEUIL_CELLULE
}

/** Points de la tendance, indexés et qualifiés : un mois masqué n'a ni point, ni valeur. */
const POINTS = TENDANCE.map((t, i) => ({ ...t, i, cache: moisMasque(t) }))
const POINTS_VISIBLES = POINTS.filter((p) => !p.cache)
const NB_MOIS_MASQUES = POINTS.length - POINTS_VISIBLES.length

/** Graphe en ligne : un seul tracé, axes légendés, premier et dernier points visibles étiquetés.
 *  Un mois sous le seuil n'a pas de point : la ligne s'interrompt et une bande hachurée tient sa
 *  place, avec le texte « masqué ». Le texte alternatif complet est porté par <title> et <desc>,
 *  et une table suit le graphe. */
function GrapheTendance({ idTitre, idDesc, idMotif }: { idTitre: string; idDesc: string; idMotif: string }) {
  const L = 640
  const H = 248
  // Marge haute : la place du texte « masqué », au-dessus de la graduation la plus haute.
  // Marge gauche : la colonne des graduations, que rien ne recouvre.
  const marge = { haut: 28, droite: 28, bas: 36, gauche: 44 }
  const largeurUtile = L - marge.gauche - marge.droite
  const hauteurUtile = H - marge.haut - marge.bas
  // Retrait interne : le premier et le dernier mois ne sont pas posés sur les bords de la zone
  // tracée, afin qu'une bande « masqué » (36 px au plus) reste à droite de la colonne des
  // graduations et à gauche du bord droit, sans rien recouvrir.
  const retrait = 24
  const largeurTracee = largeurUtile - 2 * retrait

  const maxBrut = Math.max(0, ...POINTS_VISIBLES.map((p) => p.recours))
  const pas = 10
  const maxAxe = Math.max(pas, Math.ceil(maxBrut / pas) * pas)
  const graduations = Array.from({ length: maxAxe / pas + 1 }, (_, i) => i * pas)

  const x = (i: number) =>
    marge.gauche + retrait + (POINTS.length === 1 ? largeurTracee / 2 : (i / (POINTS.length - 1)) * largeurTracee)
  const y = (v: number) => marge.haut + hauteurUtile - (v / maxAxe) * hauteurUtile
  // Le texte « masqué » est centré sur sa bande, mais jamais au-delà de la zone tracée :
  // sa demi-largeur (≈ 45 px en monospace 11 px) le garde à droite des graduations.
  const demiLargeurTexteMasque = 45
  const xTexteMasque = (i: number) =>
    Math.min(Math.max(x(i), marge.gauche + demiLargeurTexteMasque), L - marge.droite - demiLargeurTexteMasque)
  // Tracé : la ligne ne relie que des mois visibles consécutifs ; un mois masqué la coupe
  // (nouveau « M » après le trou), sans jamais interpoler la valeur absente.
  const chemin = POINTS.map((p, k) => {
    if (p.cache) return null
    const relieAuPrecedent = k > 0 && !POINTS[k - 1].cache
    return `${relieAuPrecedent ? 'L' : 'M'}${x(p.i).toFixed(1)} ${y(p.recours).toFixed(1)}`
  })
    .filter((s): s is string => s !== null)
    .join(' ')
  const largeurBande = Math.min(36, largeurTracee / Math.max(1, POINTS.length - 1) - 12)

  const premierMois = POINTS[0]
  const dernierMois = POINTS[POINTS.length - 1]
  const premierVisible = POINTS_VISIBLES[0]
  const dernierVisible = POINTS_VISIBLES[POINTS_VISIBLES.length - 1]
  const resume = POINTS.map((p) => `${p.mois} ${p.cache ? `masqué (moins de ${SEUIL_CELLULE})` : p.recours}`).join(', ')

  // Les <title> SVG reçoivent une chaîne unique : le rendu serveur de React ne sérialise
  // qu'un enfant, et un tableau d'enfants donnerait un <title> vide côté serveur, donc une
  // hydratation en échec. Même régime pour <desc>, par cohérence.
  const titreGraphe = `Recours mensuels au dispositif sur six mois, de ${premierMois.mois} à ${dernierMois.mois}`
  const descGraphe = premierVisible
    ? `Ligne de ${premierVisible.recours} (${premierVisible.mois}) à ${dernierVisible.recours} (${dernierVisible.mois}) recours par mois. ${
        NB_MOIS_MASQUES === 0
          ? 'Aucun mois masqué.'
          : `${NB_MOIS_MASQUES} mois sous le seuil de ${SEUIL_CELLULE}, sans point ni valeur.`
      } Valeurs : ${resume}. Le mois en cours n’est pas affiché.`
    : `Aucun mois n’atteint le seuil de ${SEUIL_CELLULE} : aucune valeur n’est affichée. Le mois en cours n’est pas affiché.`

  return (
    <svg
      viewBox={`0 0 ${L} ${H}`}
      role="img"
      aria-labelledby={`${idTitre} ${idDesc}`}
      className="mono block h-auto w-full"
      style={{ fontSize: 12 }}
    >
      <title id={idTitre}>{titreGraphe}</title>
      <desc id={idDesc}>{descGraphe}</desc>
      <defs>
        {/* Même hachure que les barres masquées : un mois masqué se lit comme une cellule masquée */}
        <pattern id={idMotif} width={8} height={8} patternUnits="userSpaceOnUse" patternTransform="rotate(135)">
          <rect width={3} height={8} fill="var(--mode-filet)" />
        </pattern>
      </defs>

      {/* Grille horizontale et axe des ordonnées, en retrait */}
      {graduations.map((g) => (
        <g key={g}>
          <line x1={marge.gauche} x2={L - marge.droite} y1={y(g)} y2={y(g)} stroke="var(--mode-filet)" strokeWidth={1} />
          <text x={marge.gauche - 10} y={y(g) + 4} textAnchor="end" fill="var(--mode-sourd)">
            {g}
          </text>
        </g>
      ))}

      {/* Axe des abscisses : les mois */}
      {POINTS.map((p) => (
        <text key={p.mois} x={x(p.i)} y={H - 12} textAnchor="middle" fill="var(--mode-sourd)">
          {p.mois}
        </text>
      ))}

      {/* Mois masqués : une bande hachurée sur toute la hauteur, le mot « masqué » écrit dessus */}
      {POINTS.filter((p) => p.cache).map((p) => (
        <g key={p.mois}>
          <rect
            x={x(p.i) - largeurBande / 2}
            y={marge.haut}
            width={largeurBande}
            height={hauteurUtile}
            fill={`url(#${idMotif})`}
            stroke="var(--mode-filet)"
            strokeWidth={1}
          />
          <text x={xTexteMasque(p.i)} y={marge.haut - 10} textAnchor="middle" fill="var(--mode-sourd)" fontSize={11}>
            {`masqué (< ${SEUIL_CELLULE})`}
          </text>
        </g>
      ))}

      {/* La série : un trait de 2 px, des points de 8 px cerclés de surface — mois visibles seulement */}
      {chemin && <path d={chemin} fill="none" stroke="var(--mode-texte)" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />}
      {POINTS_VISIBLES.map((p) => (
        <g key={p.mois}>
          <circle cx={x(p.i)} cy={y(p.recours)} r={6} fill="var(--mode-surface)" />
          <circle cx={x(p.i)} cy={y(p.recours)} r={4} fill="var(--mode-texte)">
            <title>{`${p.mois} : ${p.recours} recours`}</title>
          </circle>
        </g>
      ))}

      {/* Étiquettes directes : premier et dernier point visibles seulement */}
      {premierVisible && (
        <text x={x(premierVisible.i)} y={y(premierVisible.recours) - 12} textAnchor="start" fill="var(--mode-texte)" fontWeight={500}>
          {premierVisible.recours}
        </text>
      )}
      {dernierVisible && dernierVisible !== premierVisible && (
        <text x={x(dernierVisible.i)} y={y(dernierVisible.recours) - 12} textAnchor="end" fill="var(--mode-texte)" fontWeight={500}>
          {dernierVisible.recours}
        </text>
      )}
    </svg>
  )
}

/* ---------- Composant principal ---------- */

export default function Agregats() {
  const id = useId()
  const idTitreGraphe = `${id}-tendance-titre`
  const idDescGraphe = `${id}-tendance-desc`
  // Référencé dans un url(#…) : on retire les délimiteurs de useId (« : », « « », « » ») que
  // certains navigateurs refusent dans une référence de motif SVG.
  const idMotifGraphe = `${id.replace(/[^a-zA-Z0-9_-]/g, '')}-tendance-hachure`
  const idExport = `${id}-export`

  // Indicateurs saisis par l'établissement — en mémoire seulement, rien n'est enregistré.
  const [indicateurs, setIndicateurs] = useState(() => INDICATEURS_ETABLISSEMENT.map((i) => i.valeur))
  const [messageExport, setMessageExport] = useState<string | null>(null)

  function saisir(index: number, valeur: string) {
    setIndicateurs((courants) => courants.map((v, i) => (i === index ? valeur : v)))
  }

  // Recours par catégorie : totaux et taux global, cellules masquées incluses dans le total.
  const totalEffectif = RECOURS_PAR_CATEGORIE.reduce((s, c) => s + c.effectif, 0)
  const totalRecours = RECOURS_PAR_CATEGORIE.reduce((s, c) => s + c.recours, 0)
  const tauxGlobal = totalEffectif > 0 ? (totalRecours / totalEffectif) * 100 : 0
  const cellulesMasquees = RECOURS_PAR_CATEGORIE.filter(masquee)
  const nbMasquees = cellulesMasquees.length
  const recoursMasques = cellulesMasquees.reduce((s, c) => s + c.recours, 0)
  // Les cellules masquées n'entrent dans le total que si, regroupées, elles atteignent le seuil :
  // sinon le total permettrait de les recalculer par différence, et il est masqué à son tour.
  const totalPubliable = nbMasquees === 0 || recoursMasques >= SEUIL_CELLULE
  const tauxVisibles = RECOURS_PAR_CATEGORIE.filter((c) => !masquee(c)).map((c) => (c.recours / c.effectif) * 100)
  // Échelle des barres : multiple de 5 au-dessus du taux visible le plus élevé, jamais sous 20 %.
  const echelle = Math.max(20, Math.ceil(Math.max(0, ...tauxVisibles) / 5) * 5)

  const partMax = Math.max(...THEMATIQUES.map((t) => t.part))
  const dernierMois = TENDANCE[TENDANCE.length - 1].mois

  return (
    <div className="conteneur py-10 sm:py-12">
      {/* ---------- Une phrase, puis qui voit quoi ---------- */}
      <p className="phrase max-w-[22ch]">Des agrégats. Jamais un nom.</p>

      <section aria-labelledby={`${id}-qui`} className="plaque mt-8 border-l-4 border-l-[var(--mode-accent)]">
        <h2 id={`${id}-qui`} className="etiquette">
          Qui voit quoi
        </h2>
        <dl className="mt-3 grid gap-x-6 gap-y-2 sm:grid-cols-[max-content_1fr]">
          {QUI_VOIT_QUOI.map((ligne) => (
            <div key={ligne.qui} className="contents">
              <dt className="mono text-[0.85rem] font-medium sm:py-1">{ligne.qui}</dt>
              <dd className="border-b border-[var(--mode-filet)] pb-2 text-[0.95rem] sm:border-b-0 sm:py-1">{ligne.voit}</dd>
            </div>
          ))}
        </dl>
        <div className="filet mt-4 pt-4">
          <p className="etiquette">Contrat de seuil</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {CONTRAT_SEUIL.map((regle) => (
              <li
                key={regle}
                className="mono rounded-[var(--radius-clinique)] border border-[var(--mode-filet)] bg-[var(--mode-surface-2)] px-2.5 py-1 text-[0.8rem]"
              >
                {regle}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* ---------- Agrégats à gauche, indicateurs de l'établissement à droite ---------- */}
      <div className="mt-10 grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:gap-10">
        <div className="min-w-0 space-y-10">
          {/* Recours par catégorie */}
          <section aria-labelledby={`${id}-recours`}>
            <p className="etiquette">Agrégat 1</p>
            <h2 id={`${id}-recours`} className="titre titre-bloc mt-1">
              Recours par catégorie
            </h2>
            <p className="sourd mt-2 text-[0.9rem]">
              Soignants ayant pris contact avec un pair, rapportés à l’effectif déclaré. Échelle des barres : 0 à {echelle}
              {NBSP}%.
            </p>
            <ol className="mt-5 space-y-4">
              {RECOURS_PAR_CATEGORIE.map((c) => {
                const cache = masquee(c)
                const taux = cache ? 0 : (c.recours / c.effectif) * 100
                return (
                  <li key={c.categorie} className="grid grid-cols-[1fr_auto] items-baseline gap-x-4 gap-y-1.5">
                    <span className="text-[0.95rem]">{c.categorie}</span>
                    <span className={`donnee text-right text-[0.95rem] ${cache ? 'sourd' : ''}`}>
                      {cache ? (
                        TEXTE_MASQUE
                      ) : (
                        <>
                          {pourcent(taux)}
                          <span className="sourd ml-2 text-[0.8rem] font-normal">
                            {c.recours}
                            {NBSP}/{NBSP}
                            {c.effectif}
                          </span>
                        </>
                      )}
                    </span>
                    <div className="col-span-2">
                      <Barre part={taux / echelle} hachuree={cache} />
                    </div>
                  </li>
                )
              })}
            </ol>
            <div className="filet mt-5 grid grid-cols-2 gap-4 pt-4 sm:grid-cols-3">
              <div>
                <p className="etiquette">Recours</p>
                <p className={`donnee mt-1 leading-none ${totalPubliable ? 'text-2xl' : 'sourd text-[0.95rem]'}`}>
                  {totalPubliable ? totalRecours : TEXTE_MASQUE}
                </p>
              </div>
              <div>
                <p className="etiquette">Effectif</p>
                <p className="donnee mt-1 text-2xl leading-none">{totalEffectif}</p>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <p className="etiquette">Taux global</p>
                <p className={`donnee mt-1 leading-none ${totalPubliable ? 'text-2xl' : 'sourd text-[0.95rem]'}`}>
                  {totalPubliable ? pourcent(tauxGlobal) : TEXTE_MASQUE}
                </p>
              </div>
            </div>
            <p className="sourd mt-3 text-[0.8rem]">
              {nbMasquees === 0
                ? 'Aucune cellule masquée ce mois-ci.'
                : totalPubliable
                  ? `Le total inclut les ${nbMasquees} cellules masquées, regroupées : aucune n’est recalculable par différence.`
                  : `Les ${nbMasquees} cellules masquées n’atteignent pas le seuil une fois regroupées : le total est masqué à son tour.`}
            </p>
          </section>

          {/* Thématiques dominantes */}
          <section aria-labelledby={`${id}-themes`}>
            <p className="etiquette">Agrégat 2</p>
            <h2 id={`${id}-themes`} className="titre titre-bloc mt-1">
              Thématiques dominantes
            </h2>
            <p className="sourd mt-2 text-[0.9rem]">
              Part des premiers échanges, classés par le pair, jamais par la machine. Aucune thématique n’est reliée à un service.
            </p>
            <ol className="mt-5 space-y-4">
              {THEMATIQUES.map((t) => (
                <li key={t.nom} className="grid grid-cols-[1fr_auto] items-baseline gap-x-4 gap-y-1.5">
                  <span className="text-[0.95rem]">{t.nom}</span>
                  <span className="donnee text-right text-[0.95rem]">{pourcent(t.part, 0)}</span>
                  <div className="col-span-2">
                    <Barre part={partMax > 0 ? t.part / partMax : 0} />
                  </div>
                </li>
              ))}
            </ol>
          </section>

          {/* Tendance */}
          <section aria-labelledby={`${id}-tendance`}>
            <p className="etiquette">Agrégat 3</p>
            <h2 id={`${id}-tendance`} className="titre titre-bloc mt-1">
              Tendance
            </h2>
            <p className="sourd mt-2 text-[0.9rem]">
              Recours par mois, toutes catégories confondues. Le mois en cours n’est pas affiché (latence d’un mois) ; dernier mois
              restitué : {dernierMois}. Un mois sous le seuil de {SEUIL_CELLULE} est masqué, comme toute cellule
              {NB_MOIS_MASQUES === 0 ? '.' : ` ; ici, ${NB_MOIS_MASQUES} mois sur ${TENDANCE.length}.`}
            </p>
            <div className="plaque mt-5 !p-3 sm:!p-5">
              <GrapheTendance idTitre={idTitreGraphe} idDesc={idDescGraphe} idMotif={idMotifGraphe} />
            </div>
            <div className="defilable mt-4">
              <table className="tableau">
                <caption className="sr-only">Valeurs de la tendance, recours par mois</caption>
                <thead>
                  <tr>
                    <th scope="col">Mois</th>
                    {TENDANCE.map((t) => (
                      <th key={t.mois} scope="col" className="text-right">
                        {t.mois}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row">Recours</th>
                    {TENDANCE.map((t) => (
                      <td key={t.mois} className={`donnee whitespace-nowrap text-right ${moisMasque(t) ? 'sourd' : ''}`}>
                        {moisMasque(t) ? TEXTE_MASQUE : t.recours}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        {/* ---------- Colonne de l'établissement ---------- */}
        <aside className="min-w-0 space-y-6 lg:border-l lg:border-[var(--mode-filet)] lg:pl-8" aria-label="Indicateurs et cadre de l’établissement">
          <section aria-labelledby={`${id}-indic`} className="plaque">
            <p className="etiquette">Saisi par l’établissement</p>
            <h2 id={`${id}-indic`} className="titre titre-bloc mt-1">
              Vos indicateurs
            </h2>
            <p className="sourd mt-2 text-[0.9rem]">
              Saisi par la DRH ou la DAF, jamais calculé par Relève. Posés à côté des agrégats, jamais reliés à un individu. Valeurs en
              mémoire seulement : rien n’est enregistré.
            </p>
            <div className="mt-5 space-y-4">
              {INDICATEURS_ETABLISSEMENT.map((ind, i) => {
                const idChamp = `${id}-indic-${i}`
                return (
                  <div key={ind.nom}>
                    <label htmlFor={idChamp} className="block text-[0.95rem] font-medium">
                      {ind.nom}
                    </label>
                    <p id={`${idChamp}-aide`} className="sourd mono mt-0.5 text-[0.75rem]">
                      {ind.periode} · saisi par {ind.saisiPar}
                    </p>
                    <input
                      id={idChamp}
                      type="text"
                      value={indicateurs[i]}
                      onChange={(e) => saisir(i, e.target.value)}
                      aria-describedby={`${idChamp}-aide`}
                      className="donnee mt-2 block min-h-[44px] w-full rounded-[var(--radius-clinique)] border border-[var(--mode-filet)] bg-[var(--mode-surface)] px-3 text-[1.05rem]"
                    />
                  </div>
                )
              })}
            </div>
          </section>

          <section aria-labelledby={`${id}-preuve`} className="plaque border-dashed">
            <p className="etiquette">Preuve</p>
            <h2 id={`${id}-preuve`} className="titre titre-bloc mt-1">
              Encadré vide, volontairement
            </h2>
            <ul className="mt-4 space-y-2.5">
              {PREUVE_ATTENDUE.map((p) => (
                <li key={p} className="flex items-center justify-between gap-3 text-[0.95rem]">
                  <span>{p}</span>
                  <AMesurer />
                </li>
              ))}
            </ul>
            <p className="filet mt-4 pt-4 text-[0.9rem]">
              La preuve vendue sera un chiffre signé par un établissement nommé, pas une capture d’écran. Cet encadré reste vide tant
              qu’aucun chiffre n’existe.
            </p>
          </section>

          <section aria-labelledby={`${id}-finance`} className="plaque">
            <p className="etiquette">Financement et cadre</p>
            <h2 id={`${id}-finance`} className="titre titre-bloc mt-1">
              Ce que l’établissement signe
            </h2>
            <dl className="mt-4 space-y-3">
              {FINANCEMENT.map((f) => (
                <div key={f.titre} className="filet pt-3 first:border-t-0 first:pt-0">
                  <dt className="mono text-[0.85rem] font-medium">{f.titre}</dt>
                  <dd className="sourd mt-0.5 text-[0.9rem]">{f.texte}</dd>
                </div>
              ))}
            </dl>
          </section>
        </aside>
      </div>

      {/* ---------- Export et rappel ---------- */}
      <div className="filet mt-10 flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" className="bouton" aria-describedby={idExport} onClick={() => setMessageExport('Export : démonstration')}>
            Exporter pour le CSE
          </button>
          <p id={idExport} className="mono text-[0.85rem]" aria-live="polite">
            {messageExport ?? 'Restitution trimestrielle, mêmes agrégats, même seuil.'}
          </p>
        </div>
        <p className="sourd text-[0.85rem]">
          Un soignant en détresse ne passe jamais par cet écran.{' '}
          <a href={TEL_3114_HREF} className="font-medium text-[var(--color-rouge-3114)] underline underline-offset-2">
            {TEL_3114_AFFICHE}
          </a>
          , 24 h/24.
        </p>
      </div>
    </div>
  )
}
