'use client'

import { useEffect, useRef, useState, type ReactNode } from 'react'
import { ETAPES_PROTOCOLE, FILE_ACTIVE, TEMPS_EQUIPE, type Dossier } from '@/lib/demo'
import { FAITS } from '@/lib/faits'
import { TEL_3114_AFFICHE, TEL_3114_HREF } from '@/lib/infos'
import { AMesurer, Encadre } from '@/components/ui'

/*
  Transmissions — l’outil de travail du binôme (pair + infirmier coordinateur).
  Principe quiet dark : la file active est un tableau sobre ; seule la ligne que
  le soignant a lui-même signalée (« Je veux être rappelée ») porte une pastille
  ambre qui pulse à 1 Hz, toujours accompagnée d’un texte.
  Tout l’état vit en mémoire React : rien n’est enregistré, rien n’est transmis.
*/

const ROMAINS = ['I', 'II', 'III', 'IV', 'V'] as const

/** Trois propositions de 15 min, hors des gardes déclarées par le soignant. Fictif. */
const CRENEAUX: Record<string, readonly [string, string, string]> = {
  'R-0417': ['Jeu 14 h 15', 'Jeu 14 h 45', 'Ven 11 h 30'],
  'R-0402': ['Mar 7 h 30', 'Mar 13 h', 'Jeu 7 h 30'],
  'R-0388': ['Lun 12 h', 'Lun 12 h 30', 'Mer 12 h'],
  'R-0421': ['Mer 9 h', 'Mer 17 h 30', 'Sam 10 h'],
  'R-0395': ['Mer 16 h', 'Mer 16 h 30', 'Ven 16 h'],
}
const CRENEAUX_DEFAUT: readonly [string, string, string] = ['Lun 12 h', 'Mer 9 h', 'Ven 14 h']

/** Dernière note du dossier. Le délai de premier contact reste « à mesurer » : aucune note ne le présente comme tenu. */
function derniereNote(d: Dossier): string {
  return d.derniereNote
}

/** Consentement au relais psychologue, tel que tracé dans le dossier (cohérent avec la dernière note). */
type Consentement = { etat: 'oui' | 'non' | 'non demandé'; precision: string }
function consentementRelais(d: Dossier): Consentement {
  if (d.code === 'R-0395') return { etat: 'oui', precision: 'tracé le 2 octobre, Mon soutien psy' }
  if (d.code === 'R-0417') return { etat: 'non', precision: 'pour l’instant — refus noté par le pair, révocable' }
  return { etat: 'non demandé', precision: 'aucun relais proposé à ce stade' }
}

/** Repère d’étape : cinq traits, remplis jusqu’à l’étape courante. Le texte porte toujours l’information. */
function RepereEtape({ etape }: { etape: Dossier['etape'] }) {
  return (
    <span className="inline-flex items-center gap-[3px]" aria-hidden="true">
      {ETAPES_PROTOCOLE.map((_, i) => (
        <span
          key={i}
          className={`inline-block h-[4px] w-[10px] rounded-[1px] ${i < etape ? 'bg-[var(--mode-texte)]' : 'bg-[var(--mode-filet)]'}`}
        />
      ))}
    </span>
  )
}

/** Ligne de la file active. Le bouton est le contrôle ; la ligne entière répond aussi au clic. */
function LigneDossier({ d, ouvert, onOuvrir }: { d: Dossier; ouvert: boolean; onOuvrir: () => void }) {
  const nomEtape = ETAPES_PROTOCOLE[d.etape - 1]
  return (
    <tr
      onClick={onOuvrir}
      className={`fondu cursor-pointer ${ouvert ? 'bg-[var(--mode-surface-2)]' : 'hover:bg-[var(--mode-surface-2)]/60'}`}
    >
      <td className="!py-1.5">
        <button
          type="button"
          aria-pressed={ouvert}
          aria-label={`${ouvert ? 'Dossier ouvert' : 'Ouvrir le dossier'} ${d.code}`}
          onClick={(e) => {
            e.stopPropagation()
            onOuvrir()
          }}
          className={`fondu inline-flex min-h-[2.75rem] min-w-[2.75rem] items-center rounded-[var(--radius-clinique)] border px-2.5 ${
            ouvert ? 'border-[var(--mode-texte)]' : 'border-[var(--mode-filet)] hover:border-[var(--mode-sourd)]'
          }`}
        >
          <span className="donnee whitespace-nowrap text-[0.95rem]">{d.code}</span>
        </button>
      </td>
      {/* La profession peut se replier sur deux lignes : la colonne « État » doit rester dans le champ. */}
      <td className="min-w-[9rem]">{d.profession}</td>
      <td className="whitespace-nowrap">
        {/* Chiffre romain seul à l’écran ; le nom de l’étape reste lu par les lecteurs d’écran et en infobulle. */}
        <span className="inline-flex items-center gap-2" title={`Étape ${ROMAINS[d.etape - 1]} — ${nomEtape}`}>
          <RepereEtape etape={d.etape} />
          <span className="donnee">{ROMAINS[d.etape - 1]}</span>
          <span className="sr-only">{nomEtape}</span>
        </span>
      </td>
      <td className="donnee">{d.semaine}</td>
      <td className={`whitespace-nowrap ${d.prochainRdv === 'À planifier' ? 'sourd' : 'donnee'}`}>{d.prochainRdv}</td>
      <td className="whitespace-nowrap">
        {d.signale ? (
          <span className="inline-flex items-center gap-2">
            <span className="signale inline-block h-2.5 w-2.5 rounded-full bg-[var(--mode-accent)]" aria-hidden="true" />
            <span className="mono text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-accent)]">Rappel demandé</span>
          </span>
        ) : (
          <span className="sourd">Normal</span>
        )}
      </td>
    </tr>
  )
}

/** Protocole en cinq étapes, avec l’étape courante. */
function Protocole({ etape }: { etape: Dossier['etape'] }) {
  return (
    <ol className="mt-3 grid gap-1">
      {ETAPES_PROTOCOLE.map((nom, i) => {
        const n = i + 1
        const statut = n < etape ? 'fait' : n === etape ? 'en cours' : 'à venir'
        return (
          <li
            key={nom}
            aria-current={n === etape ? 'step' : undefined}
            className={`flex items-center gap-3 rounded-[var(--radius-clinique)] px-2 py-1.5 ${n === etape ? 'bg-[var(--mode-surface-2)]' : ''}`}
          >
            <span
              aria-hidden="true"
              className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full border ${
                n < etape
                  ? 'border-[var(--mode-texte)] bg-[var(--mode-texte)]'
                  : n === etape
                    ? 'border-[var(--mode-texte)] bg-transparent'
                    : 'border-[var(--mode-filet)] bg-transparent'
              }`}
            />
            <span className="donnee w-6 text-[0.85rem]">{ROMAINS[i]}</span>
            <span className={n > etape ? 'sourd' : ''}>{nom}</span>
            <span className="mono ml-auto text-[0.7rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]">{statut}</span>
          </li>
        )
      })}
    </ol>
  )
}

/** Panneau « Dossier » : protocole, dernière note, consentements, actions. */
function PanneauDossier({
  d,
  creneauRetenu,
  onRetenirCreneau,
  relaisDemande,
  onDemanderRelais,
}: {
  d: Dossier
  creneauRetenu: string | null
  onRetenirCreneau: (c: string) => void
  relaisDemande: boolean
  onDemanderRelais: () => void
}) {
  const [selecteurOuvert, setSelecteurOuvert] = useState(false)
  const [choix, setChoix] = useState<string>('')
  const creneaux = CRENEAUX[d.code] ?? CRENEAUX_DEFAUT
  const consentement = consentementRelais(d)
  const idGroupe = `creneaux-${d.code}`

  return (
    <section aria-labelledby="titre-dossier" className="plaque flex h-full min-w-0 flex-col">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <div>
          <p className="etiquette">Dossier</p>
          <h2 id="titre-dossier" className="donnee mt-1 text-3xl leading-none">
            {d.code}
          </h2>
        </div>
        <p className="mono text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]">
          Semaine {d.semaine} · étape {ROMAINS[d.etape - 1]}
        </p>
      </div>
      <p className="mt-2 text-[0.95rem]">{d.profession}</p>

      {d.signale && d.demande && (
        <p className="mt-4 flex items-start gap-2 rounded-[var(--radius-clinique)] border border-[var(--mode-accent)] px-3 py-2 text-[0.95rem]">
          <span className="signale mt-[0.45rem] inline-block h-2.5 w-2.5 shrink-0 rounded-full bg-[var(--mode-accent)]" aria-hidden="true" />
          <span>
            <span className="mono text-[0.72rem] uppercase tracking-[0.12em] text-[var(--mode-accent)]">Rappel demandé par le soignant</span>
            <br />« {d.demande} »
          </span>
        </p>
      )}

      <div className="filet mt-5 pt-4">
        <h3 className="etiquette">Protocole</h3>
        <Protocole etape={d.etape} />
      </div>

      <div className="filet mt-5 pt-4">
        <h3 className="etiquette">Dernière note</h3>
        <blockquote className="mt-2 border-l-2 border-[var(--mode-filet)] pl-3 text-[0.95rem]">{derniereNote(d)}</blockquote>
        <p className="sourd mt-2 text-[0.78rem]">Notes rédigées par le pair — aucune note automatique en V1.</p>
      </div>

      <div className="filet mt-5 pt-4">
        <h3 className="etiquette">Consentements tracés</h3>
        <dl className="mt-2 grid gap-1 text-[0.95rem]">
          <div className="flex flex-wrap items-baseline gap-x-3">
            <dt className="sourd">Relais psychologue</dt>
            <dd>
              <span className="donnee">{consentement.etat}</span>
              <span className="sourd"> — {consentement.precision}</span>
            </dd>
          </div>
          <div className="flex flex-wrap items-baseline gap-x-3">
            <dt className="sourd">Partage du dossier avec le binôme</dt>
            <dd>
              <span className="donnee">oui</span>
              <span className="sourd"> — à l’entrée, révocable à tout moment</span>
            </dd>
          </div>
          {relaisDemande && (
            <div className="mt-1 flex flex-wrap items-baseline gap-x-3 border-t border-dashed border-[var(--mode-filet)] pt-2">
              <dt className="sourd">Nouvelle demande</dt>
              <dd>
                Consentement du soignant requis — demande envoyée <span className="sourd">(fictif)</span>
              </dd>
            </div>
          )}
        </dl>
      </div>

      <div className="filet mt-5 pt-4">
        <h3 className="etiquette">Actions</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            className="bouton"
            aria-expanded={selecteurOuvert}
            aria-controls={idGroupe}
            onClick={() => setSelecteurOuvert((v) => !v)}
          >
            {creneauRetenu ? 'Replanifier 15 min' : 'Planifier 15 min'}
          </button>
          {consentement.etat === 'oui' ? (
            <span className="bouton bouton-second cursor-default" aria-disabled="true">
              Relais engagé
            </span>
          ) : (
            <button type="button" className="bouton bouton-second" onClick={onDemanderRelais} disabled={relaisDemande}>
              {relaisDemande ? 'Relais proposé' : 'Proposer un relais psy'}
            </button>
          )}
        </div>

        {selecteurOuvert && (
          <fieldset id={idGroupe} className="mt-4 rounded-[var(--radius-clinique)] border border-[var(--mode-filet)] p-3">
            <legend className="mono px-1 text-[0.72rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]">
              Trois créneaux dans le planning déclaré par le soignant
            </legend>
            <div className="grid gap-1">
              {creneaux.map((c) => (
                <label
                  key={c}
                  className={`fondu flex min-h-[2.75rem] cursor-pointer items-center gap-3 rounded-[var(--radius-clinique)] px-2 ${
                    choix === c ? 'bg-[var(--mode-surface-2)]' : 'hover:bg-[var(--mode-surface-2)]/60'
                  }`}
                >
                  <input
                    type="radio"
                    name={idGroupe}
                    value={c}
                    checked={choix === c}
                    onChange={() => setChoix(c)}
                    className="h-4 w-4 accent-[var(--mode-accent)]"
                  />
                  <span className="donnee">{c}</span>
                  <span className="sourd text-[0.85rem]">15 min · téléphone ou visio</span>
                </label>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button
                type="button"
                className="bouton bouton-second"
                disabled={!choix}
                onClick={() => {
                  onRetenirCreneau(choix)
                  setSelecteurOuvert(false)
                }}
              >
                Retenir ce créneau
              </button>
              <span className="sourd text-[0.85rem]">Le soignant reçoit un rappel du créneau. Reprenable si la garde l’interrompt.</span>
            </div>
          </fieldset>
        )}

        {creneauRetenu && (
          <p className="mt-3 text-[0.95rem]">
            <span className="sourd">Créneau retenu : </span>
            <span className="donnee">{creneauRetenu}</span>
            <span className="sourd"> — rappel envoyé au soignant (fictif).</span>
          </p>
        )}
      </div>

      <p className="sourd mt-auto pt-5 text-[0.78rem]">
        Démonstration : l’état de ce dossier vit dans la mémoire de la page. Rien n’est enregistré, rien n’est transmis, tout disparaît au rechargement.
      </p>
    </section>
  )
}

/**
  Zone défilable avec indication visible quand le contenu dépasse : le tableau ne doit
  jamais cacher la colonne « État » sans le dire. Mesure en lecture seule, rien n’est stocké.
*/
function Defilable({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const [deborde, setDeborde] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const mesurer = () => setDeborde(el.scrollWidth > el.clientWidth + 1)
    mesurer()
    const observateur = new ResizeObserver(mesurer)
    observateur.observe(el)
    return () => observateur.disconnect()
  }, [])

  return (
    <>
      <div ref={ref} className="defilable">
        {children}
      </div>
      {deborde && (
        <p className="mono px-5 pt-2 text-[0.7rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]" aria-live="polite">
          Tableau plus large que l’écran : faire défiler vers la droite pour lire l’état
        </p>
      )}
    </>
  )
}

export default function Transmissions() {
  const [codeOuvert, setCodeOuvert] = useState<string>(FILE_ACTIVE[0].code)
  const [creneaux, setCreneaux] = useState<Record<string, string>>({})
  const [relais, setRelais] = useState<Record<string, boolean>>({})
  const [debriefPropose, setDebriefPropose] = useState(false)

  const dossier = FILE_ACTIVE.find((d) => d.code === codeOuvert) ?? FILE_ACTIVE[0]
  const nbSignales = FILE_ACTIVE.filter((d) => d.signale).length
  const nbAPlanifier = FILE_ACTIVE.filter((d) => d.prochainRdv === 'À planifier').length
  const schwartz = FAITS.find((f) => f.valeur === '25 % → 12 %')

  return (
    <div className="conteneur pb-8 pt-10">
      {/* Garde du jour : un résumé en texte, sans voyant. */}
      <p className="mono flex flex-wrap gap-x-5 gap-y-1 text-[0.78rem] uppercase tracking-[0.12em] text-[var(--mode-sourd)]">
        <span>
          <span className="text-[var(--mode-texte)]">{FILE_ACTIVE.length}</span> dossiers en file active
        </span>
        <span>
          <span className="text-[var(--mode-texte)]">{nbSignales}</span> rappel demandé
        </span>
        <span>
          <span className="text-[var(--mode-texte)]">{nbAPlanifier}</span> créneau à planifier
        </span>
        <span>Délai de premier contact : <AMesurer /></span>
      </p>

      {/*
        Les colonnes sont en minmax(0, …) à toutes les largeurs : un item de grille a
        min-width:auto par défaut et prendrait la largeur intrinsèque du tableau, ce qui
        ferait déborder la page à 390 px malgré le .defilable.
        Le panneau Dossier passe à droite seulement à partir de xl, pour laisser au tableau
        la place de montrer la colonne « État » sans la rogner.
      */}
      <div className="mt-6 grid grid-cols-[minmax(0,1fr)] gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,24rem)] xl:items-start">
        {/* File active */}
        <section aria-labelledby="titre-file-active" className="plaque min-w-0 !p-0">
          <div className="flex flex-wrap items-baseline justify-between gap-2 px-5 pt-5">
            <h2 id="titre-file-active" className="titre titre-bloc">
              File active
            </h2>
            <p className="sourd text-[0.85rem]">Rien ne s’allume tant que tout est normal.</p>
          </div>
          <div className="mt-4">
            <Defilable>
              <table className="tableau [&_td]:px-2.5 [&_th]:px-2.5">
                <caption className="sr-only">File active du binôme : code pseudonyme, profession, étape du protocole, semaine, prochain créneau, état</caption>
                <thead>
                  <tr>
                    <th scope="col">Code</th>
                    <th scope="col">Profession</th>
                    <th scope="col">Étape</th>
                    <th scope="col">Sem.</th>
                    <th scope="col">Prochain créneau</th>
                    <th scope="col">État</th>
                  </tr>
                </thead>
                <tbody>
                  {FILE_ACTIVE.map((d) => (
                    <LigneDossier key={d.code} d={d} ouvert={d.code === dossier.code} onOuvrir={() => setCodeOuvert(d.code)} />
                  ))}
                </tbody>
              </table>
            </Defilable>
          </div>
          <p className="sourd px-5 pb-5 pt-3 text-[0.78rem]">
            Codes pseudonymes : aucun nom, aucun identifiant RH. Le repère d’étape suit les cinq étapes du protocole, de I (repérage) à V (continuité).
          </p>
        </section>

        {/* Dossier ouvert */}
        <PanneauDossier
          key={dossier.code}
          d={dossier}
          creneauRetenu={creneaux[dossier.code] ?? null}
          onRetenirCreneau={(c) => setCreneaux((s) => ({ ...s, [dossier.code]: c }))}
          relaisDemande={relais[dossier.code] ?? false}
          onDemanderRelais={() => setRelais((s) => ({ ...s, [dossier.code]: true }))}
        />
      </div>

      {/* Zéro administratif */}
      <section aria-labelledby="titre-zero-admin" className="mt-10 min-w-0">
        <h2 id="titre-zero-admin" className="sr-only">
          Zéro administratif
        </h2>
        <Encadre etiquette="Zéro administratif" accent>
          <p className="phrase max-w-[28ch]">Le pair soigne. La plateforme porte le reste.</p>
          <div className="mt-5 grid gap-5 text-[0.95rem] sm:grid-cols-2">
            <div>
              <p className="etiquette">Ce que le pair fait</p>
              <ul className="mt-2 grid gap-1">
                <li>Quinze minutes, au téléphone ou en visio.</li>
                <li>Une note rédigée à la main après chaque contact.</li>
                <li>Un relais proposé quand il le juge utile, jamais imposé.</li>
              </ul>
            </div>
            <div>
              <p className="etiquette">Ce que la plateforme porte, en tant qu’adresseur</p>
              <ul className="mt-2 grid gap-1">
                <li>La téléconsultation conventionnelle, facturée par le pair en son nom.</li>
                <li>Le parcours Mon soutien psy du psychologue partenaire.</li>
                <li>La planification, le rappel du créneau, la trace des consentements.</li>
              </ul>
            </div>
          </div>
          <p className="sourd mt-4 text-[0.85rem]">Le pair ne saisit aucun acte administratif. Rien n’est facturé à l’établissement par soignant.</p>
        </Encadre>
      </section>

      {/* Temps d’équipe */}
      <section aria-labelledby="titre-temps-equipe" className="mt-10 grid grid-cols-[minmax(0,1fr)] gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,24rem)]">
        <div className="plaque flex min-w-0 flex-col">
          <h2 id="titre-temps-equipe" className="titre titre-bloc">
            Temps d’équipe
          </h2>
          <p className="sourd mt-2 max-w-[60ch] text-[0.95rem]">
            Après un événement indésirable grave ou une agression, le pair peut proposer à un service un débriefing collectif facilité. Il l’anime de l’extérieur.
          </p>
          <dl className="mt-5 grid gap-x-6 gap-y-3 text-[0.95rem] sm:grid-cols-2">
            <div>
              <dt className="etiquette">Service</dt>
              <dd className="mt-1">{TEMPS_EQUIPE.service}</dd>
            </div>
            <div>
              <dt className="etiquette">Motif</dt>
              <dd className="mt-1">{TEMPS_EQUIPE.motif}</dd>
            </div>
            <div>
              <dt className="etiquette">Format</dt>
              <dd className="mt-1">{TEMPS_EQUIPE.format}</dd>
            </div>
            <div>
              <dt className="etiquette">Inscrits</dt>
              <dd className="donnee mt-1 text-2xl leading-none">{TEMPS_EQUIPE.inscrits}</dd>
            </div>
          </dl>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button type="button" className="bouton" onClick={() => setDebriefPropose(true)} disabled={debriefPropose}>
              {debriefPropose ? 'Débriefing proposé' : 'Proposer un débriefing'}
            </button>
            {debriefPropose && (
              <span className="text-[0.95rem]">
                Proposition transmise au cadre du service, réponse attendue <span className="sourd">(fictif)</span>.
              </span>
            )}
          </div>
          <p className="sourd mt-auto pt-5 text-[0.78rem]">
            Les inscrits ne sont jamais nommés à la direction. Aucune implantation française documentée de ce format, à notre connaissance : effet <AMesurer />.
          </p>
        </div>

        {schwartz && (
          <div className="plaque flex h-full min-w-0 flex-col">
            <p className="etiquette">Référence</p>
            <p className="donnee mt-3 text-4xl leading-none sm:text-5xl">{schwartz.valeur}</p>
            <p className="mt-3 text-[0.95rem]">{schwartz.texte}</p>
            <p className="sourd mt-2 text-[0.85rem]">Schwartz Rounds, Royaume-Uni. Le format dont le temps d’équipe s’inspire.</p>
            <p className="sourd mt-auto pt-4 text-[0.75rem]">
              <a href={schwartz.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-[var(--mode-texte)]">
                {schwartz.source} ↗
              </a>
            </p>
          </div>
        )}
      </section>

      {/* Garde-fous */}
      <section aria-labelledby="titre-garde-fous" className="filet mt-12 pt-6">
        <h2 id="titre-garde-fous" className="etiquette">
          Garde-fous
        </h2>
        <ul className="mt-3 grid gap-3 md:grid-cols-2">
          <li className="flex gap-3">
            <span className="donnee shrink-0 text-[var(--mode-sourd)]">01</span>
            <p className="text-[1.05rem]">Le pair n’est jamais un collègue du même établissement.</p>
          </li>
          <li className="flex gap-3">
            <span className="donnee shrink-0 text-[var(--mode-sourd)]">02</span>
            <p className="text-[1.05rem]">Aucun signalement nominatif à l’employeur.</p>
          </li>
        </ul>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <a href={TEL_3114_HREF} className="bouton bouton-3114">
            {TEL_3114_AFFICHE}
          </a>
          <p className="sourd max-w-[60ch] text-[0.95rem]">
            En cas de risque suicidaire : 3114, SAMU, médecin traitant, MOTS. Jamais l’employeur. Le médecin du travail n’est saisi qu’à l’initiative du soignant.
          </p>
        </div>
      </section>
    </div>
  )
}
