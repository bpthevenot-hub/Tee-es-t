'use client'

import { useEffect, useId, useRef, useState } from 'react'
import { PRODUIT, TEL_3114_AFFICHE, TEL_3114_HREF } from '@/lib/infos'
import { QUADRANTS, SOIGNANT_DEMO, type Quadrant } from '@/lib/demo'

/*
  Journal de garde — espace soignant (brief § 5.1).
  Tout l'état vit en mémoire React : rien n'est enregistré, rien n'est transmis.
  La couleur pleine page du check-in est le seul moment chromatique de l'app.
  La barre « 3114 / Joindre mon pair » est fixée en bas de l'écran, hors du flux :
  sa hauteur réelle est réservée sur le corps de page (padding-bottom) et déclarée
  en scroll-padding-bottom, pour qu'aucun contenu ni contrôle focalisé ne passe dessous.
*/

/** Ordre de lecture de la grille énergie × agréabilité : haute en haut, agréable à droite. */
const ORDRE_GRILLE: Quadrant[] = ['brique', 'ambre', 'prune', 'sauge']

const COULEUR: Record<Quadrant, string> = {
  ambre: 'var(--color-q-ambre)',
  brique: 'var(--color-q-brique)',
  prune: 'var(--color-q-prune)',
  sauge: 'var(--color-q-sauge)',
}

/** Couleur de texte lisible sur chaque aplat : encre sur l'ambre, blanc sur la brique
 *  et la sauge (meilleur contraste que l'ivoire), ivoire sur la prune. Réservée aux
 *  grands corps (.titre, .phrase) ; le reste du texte vit dans des plaques. */
const TEXTE_SUR: Record<Quadrant, string> = {
  ambre: 'var(--color-encre)',
  brique: '#ffffff',
  prune: 'var(--color-ivoire)',
  sauge: '#ffffff',
}

function majuscule(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/** « Lun 20 h – 8 h » → « Lun 20 h » : le début de la prochaine garde déclarée. */
const PROCHAINE_GARDE = SOIGNANT_DEMO.gardesDeclarees[0].split(' – ')[0]

/** « Lun, Mar, Ven » et « 20 h – 8 h », à partir des gardes déclarées. */
const JOURS_GARDE = SOIGNANT_DEMO.gardesDeclarees.map((g) => g.split(' ')[0]).join(', ')
const PLAGE_GARDE = SOIGNANT_DEMO.gardesDeclarees[0].split(' ').slice(1).join(' ')

type Entree = { jour: string; quadrant: Quadrant; phrase: string }

export default function JournalDeGarde() {
  const id = useId()
  const idPhrase = `${id}-phrase`
  const idDictee = `${id}-dictee`
  const idScores = `${id}-scores`
  const idPair = `${id}-pair`
  const idEnregistre = `${id}-enregistre`

  // Check-in du jour
  const [quadrant, setQuadrant] = useState<Quadrant | null>(null)
  const [phrase, setPhrase] = useState('')
  const [dictee, setDictee] = useState(false)
  const [enregistre, setEnregistre] = useState<Entree | null>(null)
  const [tentative, setTentative] = useState(false)
  // Chiffre brut
  const [scoresOuverts, setScoresOuverts] = useState(false)
  // Gestes de sortie et modes
  const [ferme, setFerme] = useState(false)
  const [couloir, setCouloir] = useState(false)
  const [nuit, setNuit] = useState(false)
  const [panneauPair, setPanneauPair] = useState(false)

  /* Réserve, sous la page, la hauteur réelle de la barre fixe (elle grandit quand le
     panneau du pair s'ouvre). Posé sur body pour que le pied de page reste atteignable,
     et sur html en scroll-padding pour que le focus clavier ne tombe jamais sous la barre. */
  const refBarre = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const barre = refBarre.current
    if (!barre) return
    const reserver = () => {
      const h = Math.ceil(barre.getBoundingClientRect().height)
      document.body.style.paddingBottom = `${h}px`
      document.documentElement.style.scrollPaddingBottom = `${h + 16}px`
    }
    reserver()
    const observateur = new ResizeObserver(reserver)
    observateur.observe(barre)
    return () => {
      observateur.disconnect()
      document.body.style.paddingBottom = ''
      document.documentElement.style.scrollPaddingBottom = ''
    }
  }, [couloir, ferme])

  const { prenom, profession, pair, prochainRdv, semaineProtocole, semainesProtocole, journal } = SOIGNANT_DEMO

  const fond = quadrant && !couloir && !ferme ? COULEUR[quadrant] : 'var(--mode-fond)'
  const texteSurFond = quadrant && !couloir && !ferme ? TEXTE_SUR[quadrant] : 'var(--mode-texte)'
  const journalComplet: Entree[] = enregistre ? [...journal, enregistre] : journal

  function choisir(q: Quadrant) {
    setQuadrant(q)
    setEnregistre(null)
    setTentative(false)
  }

  function enregistrer() {
    if (!quadrant) {
      setTentative(true)
      return
    }
    setTentative(false)
    setEnregistre({ jour: 'Auj.', quadrant, phrase: phrase.trim() })
  }

  /* ---------- Barre fixe : 3114 et pair, toujours en bas d'écran, hors du flux ---------- */
  const barre = (
    <div
      ref={refBarre}
      data-barre-fixe
      className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--mode-filet)] bg-[var(--mode-surface)] text-[var(--mode-texte)]"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {!couloir && (
        <div
          id={idPair}
          hidden={!panneauPair}
          className="border-b border-[var(--mode-filet)] bg-[var(--mode-surface-2)]"
        >
          <div className="conteneur flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[1.05rem]">
                Votre pair vous rappelle au prochain créneau : <span className="donnee">{prochainRdv.jour} {prochainRdv.heure}</span>, {prochainRdv.mode}.
              </p>
              <p className="sourd mt-1 text-sm">Démonstration : aucun message n’est envoyé.</p>
            </div>
            <button type="button" className="bouton bouton-second" onClick={() => setPanneauPair(false)}>
              Fermer ce message
            </button>
          </div>
        </div>
      )}
      <div className="conteneur flex gap-3 py-3">
        <a href={TEL_3114_HREF} className="bouton bouton-3114 flex-1 !px-3">
          {TEL_3114_AFFICHE}
          <span className="sr-only">, prévention du suicide, 24 h/24</span>
        </a>
        {!couloir && (
          <button
            type="button"
            className="bouton bouton-second flex-1 !px-3 max-[400px]:!tracking-[0.02em]"
            aria-expanded={panneauPair}
            aria-controls={idPair}
            onClick={() => setPanneauPair((v) => !v)}
          >
            Joindre mon pair
          </button>
        )}
      </div>
    </div>
  )

  /* ---------- Mode couloir : ni nom, ni pair, ni état, ni couleur ---------- */
  if (couloir) {
    return (
      <section
        data-mode={nuit ? 'nuit' : undefined}
        aria-label="Écran verrouillé"
        className="fondu mt-6 bg-[var(--mode-fond)] text-[var(--mode-texte)]"
      >
        <div className="conteneur flex min-h-[60vh] flex-col items-center justify-center gap-10 py-16 text-center">
          <p className="titre titre-hero">{PRODUIT}</p>
          <button type="button" className="bouton bouton-second min-w-[12rem]" onClick={() => setCouloir(false)}>
            Déverrouiller
          </button>
        </div>
        {barre}
      </section>
    )
  }

  /* ---------- Fermé jusqu'à la prochaine garde : aucune notification ---------- */
  if (ferme) {
    return (
      <section
        data-mode={nuit ? 'nuit' : undefined}
        className="fondu mt-6 bg-[var(--mode-fond)] text-[var(--mode-texte)]"
      >
        <div className="conteneur py-12">
          <div className="plaque max-w-2xl">
            <h2 className="etiquette">État</h2>
            <p className="phrase mt-3">Fermé jusqu’à {PROCHAINE_GARDE}.</p>
            <p className="mt-4 text-[1.05rem]">Aucune notification d’ici là. Le 3114 et votre pair restent joignables en bas d’écran.</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" className="bouton" onClick={() => setFerme(false)}>
                Rouvrir maintenant
              </button>
              <button type="button" data-mode-couloir className="bouton bouton-second" onClick={() => setCouloir(true)}>
                Mode couloir
              </button>
            </div>
          </div>
        </div>
        {barre}
      </section>
    )
  }

  /* ---------- Écran principal ---------- */
  return (
    <section
      data-mode={nuit ? 'nuit' : undefined}
      data-checkin-fond={quadrant ?? undefined}
      className="fondu mt-6 text-[var(--mode-texte)]"
      style={{ background: fond }}
    >
      <div className="conteneur grid gap-5 py-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)] lg:gap-8">
        {/* Colonne gauche : la personne, le prochain créneau, les réglages */}
        <div className="grid content-start gap-5">
          <div className="plaque">
            <p className="mono text-[0.78rem] uppercase tracking-[0.12em]">
              {prenom} <span className="sourd">· {profession}</span>
            </p>
            <h2 className="etiquette mt-5">Prochain micro-RDV</h2>
            <p className="donnee mt-2 text-3xl leading-none sm:text-4xl">
              {prochainRdv.jour} {prochainRdv.heure}
            </p>
            <p className="mt-2 text-[1.05rem]">
              {majuscule(prochainRdv.mode)} · {prochainRdv.duree}
            </p>
            <div className="filet mt-5 pt-5">
              <h2 className="etiquette">Votre pair</h2>
              <p className="titre mt-1 text-2xl">{pair.prenom}</p>
              <p className="sourd mt-1 text-sm">{majuscule(pair.profession)}</p>
            </div>
          </div>

          <div className="plaque">
            <h2 className="etiquette">Écran</h2>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button
                type="button"
                aria-pressed={nuit}
                className="bouton bouton-second scroll-mb-28"
                onClick={() => setNuit((v) => !v)}
              >
                Nuit
                <span className="mono text-[0.72rem] tracking-[0.12em]">{nuit ? 'activée' : 'désactivée'}</span>
              </button>
            </div>
            <p className="sourd mt-3 text-sm">
              Nuit automatique sur vos gardes déclarées : {JOURS_GARDE} {PLAGE_GARDE}. Ambre, sans bleu.
            </p>
          </div>
        </div>

        {/* Colonne droite : le check-in du jour */}
        <div className="grid content-start gap-5">
          <div>
            <h2 className="titre titre-bloc" style={{ color: texteSurFond }}>
              Le check-in du jour
            </h2>
            <p className="phrase mt-4 max-w-2xl" style={{ color: texteSurFond }}>
              {quadrant ? `${QUADRANTS[quadrant].nom}. ${majuscule(QUADRANTS[quadrant].mots.join(', '))}.` : 'Une couleur pour aujourd’hui. Rien d’autre.'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3" role="group" aria-label="Énergie et agréabilité : quatre zones">
            {ORDRE_GRILLE.map((q) => {
              const def = QUADRANTS[q]
              const choisi = quadrant === q
              return (
                <button
                  key={q}
                  type="button"
                  data-quadrant={q}
                  aria-pressed={choisi}
                  onClick={() => choisir(q)}
                  className={`fondu flex min-h-[8rem] flex-col items-stretch gap-2 rounded-[var(--radius-clinique)] border bg-[var(--mode-surface)] p-3 text-left ${
                    choisi ? 'border-[var(--mode-texte)]' : 'border-[var(--mode-filet)] hover:bg-[var(--mode-surface-2)]'
                  }`}
                >
                  <span aria-hidden="true" className="block h-4 w-full rounded-[2px]" style={{ background: COULEUR[q] }} />
                  <span className="titre text-2xl leading-none">{def.nom}</span>
                  <span className="sourd mono text-[0.7rem] uppercase tracking-[0.12em]">
                    Énergie {def.energie} · {def.agreabilite}
                  </span>
                  <span className="text-sm leading-snug">{majuscule(def.mots.join(', '))}</span>
                  <span className="mono mt-auto text-[0.7rem] uppercase tracking-[0.12em]">{choisi ? 'Choisi' : ' '}</span>
                </button>
              )
            })}
          </div>

          <div className="plaque">
            <label htmlFor={idPhrase} className="etiquette block">
              Une phrase, si vous voulez
            </label>
            <textarea
              id={idPhrase}
              rows={2}
              value={phrase}
              onChange={(e) => {
                setPhrase(e.target.value)
                setEnregistre(null)
              }}
              aria-describedby={idDictee}
              className="mt-3 w-full scroll-mb-28 resize-y rounded-[var(--radius-clinique)] border border-[var(--mode-filet)] bg-[var(--mode-fond)] px-3 py-2 text-[1.05rem] text-[var(--mode-texte)] placeholder:text-[var(--mode-sourd)]"
              placeholder="Ce qui s’est passé, en une phrase."
            />
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button type="button" className="bouton bouton-second" onClick={() => setDictee(true)}>
                Dicter
              </button>
              <button type="button" className="bouton" onClick={enregistrer} aria-describedby={idEnregistre}>
                Enregistrer pour moi
              </button>
            </div>
            <p id={idDictee} role="status" className="sourd mt-3 min-h-[1.5rem] text-sm">
              {dictee ? 'Dictée : démonstration. La voix capterait, l’écran confirmerait.' : ''}
            </p>
            <p id={idEnregistre} role="status" className="mt-1 text-sm">
              {enregistre
                ? 'Enregistré pour vous, sur cet écran seulement. Rien n’est transmis : ni à votre pair, ni à l’établissement.'
                : tentative
                  ? 'Choisissez d’abord une zone de la grille. Rien n’est transmis.'
                  : 'Rien n’est transmis. Ce que vous enregistrez reste pour vous.'}
            </p>
          </div>

          {/* Chiffre brut : accessible en un tap, jamais affiché d'office */}
          <div className="plaque">
            <h2 className="etiquette">Chiffre brut</h2>
            <button
              type="button"
              className="bouton bouton-second mt-3"
              aria-expanded={scoresOuverts}
              aria-controls={idScores}
              onClick={() => setScoresOuverts((v) => !v)}
            >
              {scoresOuverts ? 'Masquer mes scores' : 'Voir mes scores saisis'}
            </button>
            <div id={idScores} hidden={!scoresOuverts} className="mt-4">
              <p className="text-[1.05rem]">Saisis par vous, lus par votre pair, jamais interprétés par la machine.</p>
              <div className="defilable mt-3">
                <table className="tableau">
                  <caption className="sr-only">Échelles saisies par le soignant et qui les lit</caption>
                  <thead>
                    <tr>
                      <th scope="col">Échelle</th>
                      <th scope="col">Saisi par</th>
                      <th scope="col">Lu par</th>
                      <th scope="col">Interprété par la machine</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="row" className="donnee !normal-case !tracking-normal !text-[0.95rem] !text-[var(--mode-texte)]">MBI</th>
                      <td>Vous, à l’entrée</td>
                      <td>Votre pair</td>
                      <td>Jamais</td>
                    </tr>
                    <tr>
                      <th scope="row" className="donnee !normal-case !tracking-normal !text-[0.95rem] !text-[var(--mode-texte)]">PHQ-9</th>
                      <td>Vous, à l’entrée</td>
                      <td>Votre pair</td>
                      <td>Jamais</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="sourd mt-3 text-sm">
                Dans cette démonstration, aucun score n’est renseigné : le vôtre s’afficherait ici tel que vous l’avez saisi, sans seuil, sans courbe, sans couleur.
              </p>
            </div>
          </div>
        </div>

        {/* Pleine largeur : la semaine, puis les gestes de sortie */}
        <div className="plaque lg:col-span-2">
          <div className="flex flex-wrap items-baseline justify-between gap-3">
            <h2 className="etiquette">Cette semaine</h2>
            <p className="mono text-sm">
              semaine {semaineProtocole} / {semainesProtocole}
            </p>
          </div>
          <div className="mt-3 h-[3px] w-full bg-[var(--mode-filet)]" aria-hidden="true">
            <div className="h-full bg-[var(--mode-texte)]" style={{ width: `${(semaineProtocole / semainesProtocole) * 100}%` }} />
          </div>
          <ol className="mt-4 grid gap-2">
            {journalComplet.map((e, i) => (
              <li key={`${e.jour}-${i}`} className={`grid grid-cols-[3rem_auto_minmax(0,1fr)] items-baseline gap-3 py-2 ${i > 0 ? 'filet' : ''}`}>
                <span className="mono text-sm">{e.jour}</span>
                <span className="flex items-center gap-2">
                  <span aria-hidden="true" className="inline-block h-3 w-3 rounded-full" style={{ background: COULEUR[e.quadrant] }} />
                  <span className="mono text-[0.72rem] uppercase tracking-[0.12em]">{QUADRANTS[e.quadrant].nom}</span>
                </span>
                <span className="text-[0.95rem]">{e.phrase || <span className="sourd">Sans phrase.</span>}</span>
              </li>
            ))}
          </ol>
        </div>

        <div className="plaque lg:col-span-2">
          <h2 className="etiquette">Sortir</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="bouton bouton-second" onClick={() => setFerme(true)}>
              Fermer jusqu’à la prochaine garde
            </button>
            <button type="button" data-mode-couloir className="bouton bouton-second" onClick={() => setCouloir(true)}>
              Mode couloir
            </button>
          </div>
          <p className="sourd mt-3 max-w-2xl text-sm">
            Fermer coupe toute notification jusqu’à {PROCHAINE_GARDE}. Le mode couloir efface le prénom, le pair, l’état et la couleur de l’écran ; seul « {PRODUIT} » reste.
          </p>
        </div>
      </div>

      {barre}
    </section>
  )
}
