import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import Link from 'next/link'
import { PRODUIT, PARCOURS, TEL_3114_AFFICHE, TEL_3114_HREF } from '@/lib/infos'
import { Encadre, AMesurer, Pastille } from '@/components/ui'

export const metadata: Metadata = {
  title: 'La méthode',
  description:
    'Les cinq étapes du parcours Relève, transposées d’Éos aux soignants, avec leur garde-fou ; les garde-fous transversaux ; le cadre de la V1 hors dispositif médical ; les phases suivantes, options et non promesses.',
}

// ---------------------------------------------------------------------------
// Contenu des cinq étapes. Le texte et le garde-fou viennent de lib/infos.ts ;
// l'équivalent Éos et le détail reprennent le brief § 4. Aucun chiffre qui
// ne soit déjà dans lib/infos.ts ou lib/faits.ts.
// ---------------------------------------------------------------------------
type Etape = {
  eos: string
  detail: string
  precisions: readonly string[]
}

const COMPLEMENTS: readonly Etape[] = [
  {
    eos: 'Adressage par la structure de soins : une page d’adressage, sans intégration informatique, pour les patients qu’un service oriente à la sortie.',
    detail:
      'Le soignant arrive par un lien générique, jamais par un identifiant. Une auto-évaluation validée (MBI, PHQ-9) peut être saisie ; elle n’est jamais interprétée par la machine.',
    precisions: ['Pas de connexion employeur, pas d’identifiant RH', 'Questionnaire HAS de niveau B ou C', 'Rien ne quitte l’appareil avant un consentement explicite'],
  },
  {
    eos: 'Médecin référent et infirmier coordinateur, salariés de la société, qui ouvrent le dossier et tiennent le fil.',
    detail:
      'Le soignant choisit son pair par profession et, s’il le souhaite, hors région. Le premier contact est visé sous 48 h ; le délai réel sera mesuré, pas promis.',
    precisions: ['Consentement libre et révocable', 'Information RGPD, article 13, en langage clair', 'Le pair n’exerce jamais dans le même établissement'],
  },
  {
    eos: 'Deux rendez-vous courts par semaine, là où l’ambulatoire propose un rendez-vous par mois.',
    detail:
      'Les créneaux sont calés sur les gardes que le soignant déclare lui-même. Un appel coupé se reprend ; rien n’est perdu, rien n’est à refaire.',
    precisions: ['Téléconsultation conventionnelle, facturée par le pair en son nom', 'Règles de droit commun : territorialité, durée d’arrêt limitée', 'Aucune facturation à l’établissement par soignant'],
  },
  {
    eos: 'Modules successifs, « pas de durée limite », avec un dossier partagé entre médecin et infirmier.',
    detail:
      'Le binôme pair et infirmier coordinateur tient le protocole ; un psychologue partenaire prend le relais si le soignant y consent, dans le cadre de Mon soutien psy. Le check-in du jour est facultatif : une couleur, une phrase.',
    precisions: ['Tout score est produit et lu par un humain', 'Aucun module thérapeutique automatisé : ce serait un dispositif médical', 'Relais entre pair et psychologue tracé avec consentement'],
  },
  {
    eos: 'Post-cure après un séjour en soins médicaux et de réadaptation, pour que le fil ne casse pas à la sortie.',
    detail:
      'Après un arrêt, une hospitalisation ou un changement d’établissement, le dossier suit le soignant. Le retour à l’exercice se prépare avec lui, à son rythme.',
    precisions: ['Aucun signalement nominatif à l’employeur, y compris en cas de risque suicidaire', 'En urgence : 3114, SAMU, médecin traitant, MOTS', 'Le médecin du travail n’est saisi qu’à l’initiative du soignant'],
  },
] as const

const ETAPES = PARCOURS.map((p, i) => ({ ...p, ...COMPLEMENTS[i], id: `etape-${i + 1}` }))

/** Garde-fous transversaux (brief § 4, dossier § 4.2). */
const GARDE_FOUS = [
  { titre: 'Agrégats seuls', texte: 'L’établissement ne reçoit que des agrégats. Aucun nom, aucun score, aucun dossier, jamais.' },
  { titre: 'Seuil d’au moins dix', texte: 'Toute cellule de moins de dix personnes est masquée. C’est un seuil contractuel : la CNIL n’en fixe aucun, nous en fixons un et nous l’écrivons.' },
  { titre: 'Pas de croisement', texte: 'Interdiction de croiser service, métier et genre. Un croisement rend une personne identifiable même sous seuil.' },
  { titre: 'Latence', texte: 'La tendance mensuelle est restituée avec un décalage, un mois dans la démonstration. Personne ne peut relier un recours à un événement de la semaine.' },
  { titre: 'CSE, CSSCT et santé au travail', texte: 'Information et consultation du CSE avant tout déploiement. Les mêmes agrégats sont restitués au CSE, à la CSSCT et au service de santé au travail.' },
  { titre: 'Hébergement de données de santé', texte: 'Hébergeur certifié HDS. Les données du soignant sont des données de santé et sont traitées comme telles.' },
  { titre: 'Délégué à la protection des données', texte: 'Un DPO distinct de la direction de l’établissement et distinct de Relève, joignable par le soignant.' },
  { titre: 'Pas de dispositif médical', texte: 'Les conditions d’utilisation le disent en toutes lettres : l’outil ne dépiste pas, ne diagnostique pas, ne recommande pas.' },
] as const

/** Le cadre de la V1 : trois lignes, trois statuts. */
const CADRE_V1 = [
  {
    etiquette: 'Statut réglementaire',
    titre: 'Hors dispositif médical, hors agrément',
    texte:
      'La V1 ne dépiste pas, ne diagnostique pas, ne recommande pas. Elle adresse, planifie, trace. Aucun algorithme ne lit un score ; aucune société de téléconsultation n’est à agréer.',
  },
  {
    etiquette: 'Qui paie le soin',
    titre: 'Le soin est facturé par les professionnels',
    texte:
      'Le pair facture une téléconsultation conventionnelle en son nom et le soignant est remboursé dans le droit commun. Le psychologue partenaire relève de Mon soutien psy, pris en charge dans le droit commun. La plateforme porte l’administratif, pas la facturation du soin.',
  },
  {
    etiquette: 'Qui paie le dispositif',
    titre: 'L’établissement finance le dispositif',
    texte:
      'Le dispositif s’inscrit au DUERP de l’établissement. Il peut être financé par les appels à projets ARS QVCT et CLACT, sous réserve d’éligibilité de l’établissement et du calendrier de chaque ARS.',
  },
] as const

/** Phases suivantes : des options, jamais des promesses. */
const PHASES = [
  { phase: 'V1', statut: 'périmètre', titre: 'Clinique digitale hors dispositif médical', texte: 'Pair, binôme, agrégats sous seuil. Soin facturé par les professionnels et remboursé dans le droit commun, dispositif financé par l’établissement.' },
  { phase: 'Phase 2', statut: 'option', titre: 'Dispositif médical, marquage CE', texte: 'Si un module d’aide à la décision devait exister, il passerait par un marquage CE de dispositif médical, dont la classe resterait à qualifier. Rien n’est engagé.' },
  { phase: 'Phase 3', statut: 'option', titre: 'Agrément société de téléconsultation', texte: 'Devenir offreur de soins, comme Éos l’a fait : médecins salariés, actes facturés par la société. Une voie, pas un plan.' },
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

/** Une étape du parcours : numéro, titre, trois colonnes (Éos, Relève, garde-fou). */
function EtapeBloc({ etape }: { etape: (typeof ETAPES)[number] }) {
  return (
    <section id={etape.id} aria-labelledby={`${etape.id}-titre`} className="filet">
      <div className="conteneur py-14 sm:py-20">
        <div className="grid gap-6 lg:grid-cols-[7rem_1fr] lg:gap-10">
          <p className="donnee text-5xl leading-none text-[var(--mode-accent)] sm:text-6xl" aria-hidden="true">
            {etape.numero}
          </p>
          <div>
            <h2 id={`${etape.id}-titre`} className="titre titre-section">
              <span className="sr-only">Étape {etape.numero}. </span>
              {etape.titre}
            </h2>

            <div className="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-[1fr_1.35fr_1fr] lg:gap-8">
              <div>
                <h3 className="etiquette">Chez Éos · patients</h3>
                <p className="sourd mt-3 text-[0.95rem]">{etape.eos}</p>
              </div>

              <div>
                <h3 className="etiquette">Chez {PRODUIT} · soignants</h3>
                <p className="mt-3 text-[1.05rem]">{etape.texte}</p>
                <p className="sourd mt-3 text-[0.95rem]">{etape.detail}</p>
              </div>

              <div className="md:col-span-2 lg:col-span-1">
                <Encadre etiquette="Garde-fou" accent>
                  <p className="text-[1.02rem]">{etape.gardeFou}</p>
                  <ul className="mt-4 flex flex-col gap-2" aria-label={`Précisions, étape ${etape.numero}`}>
                    {etape.precisions.map((x) => (
                      <li key={x} className="grid grid-cols-[1.2rem_1fr] gap-2 text-[0.88rem]">
                        <span className="donnee text-[var(--mode-sourd)]" aria-hidden="true">
                          —
                        </span>
                        <span>{x}</span>
                      </li>
                    ))}
                  </ul>
                </Encadre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function Methode() {
  return (
    <>
      {/* Héro */}
      <section className="conteneur py-20 sm:py-28" aria-labelledby="methode-titre">
        <p className="etiquette">La méthode</p>
        <h1 id="methode-titre" className="titre titre-hero mt-4">
          Cinq étapes, un <span className="whitespace-nowrap">garde-fou</span> à chacune
        </h1>
        <p className="phrase mt-10 max-w-4xl">
          Éos a ouvert en France un parcours court, en binôme, branché sur le flux d’un groupe de cliniques. {PRODUIT} le transpose aux soignants et dit, à chaque étape, ce qui ne se fera pas.
        </p>
        <p className="sourd texte mt-6 text-[1.05rem]">
          Chaque étape se lit en trois colonnes : ce qu’Éos fait pour ses patients, ce que {PRODUIT} en fait pour les soignants, et la limite que personne ne franchit. Les éléments Éos sont publics et déclarés ; aucun chiffre Éos n’est présenté comme vérifié.
        </p>

        <nav aria-label="Sommaire de la méthode" className="mt-12">
          <ol className="flex flex-wrap gap-2">
            {ETAPES.map((e) => (
              <li key={e.id}>
                <a href={`#${e.id}`} className="bouton bouton-second !text-[0.9rem]">
                  <span className="donnee text-[var(--mode-accent)]" aria-hidden="true">
                    {e.numero}
                  </span>
                  <span className="sr-only">Étape {e.numero}, </span>
                  {e.titre}
                </a>
              </li>
            ))}
            <li>
              <a href="#garde-fous" className="bouton bouton-second !text-[0.9rem]">
                Garde-fous transversaux
              </a>
            </li>
            <li>
              <a href="#cadre" className="bouton bouton-second !text-[0.9rem]">
                Le cadre V1
              </a>
            </li>
            <li>
              <a href="#phases" className="bouton bouton-second !text-[0.9rem]">
                Phases suivantes
              </a>
            </li>
          </ol>
        </nav>
      </section>

      {/* Les cinq étapes */}
      {ETAPES.map((e) => (
        <EtapeBloc key={e.id} etape={e} />
      ))}

      {/* Garde-fous transversaux */}
      <Section etiquette="À toutes les étapes" titre="Garde-fous transversaux" id="garde-fous">
        <p className="phrase max-w-4xl">L’outil ne dépiste pas, ne diagnostique pas, ne recommande pas. La direction ne voit jamais un nom.</p>
        <ol className="mt-12 grid gap-x-10 gap-y-8 md:grid-cols-2" aria-label="Les huit garde-fous transversaux">
          {GARDE_FOUS.map((g, i) => (
            <li key={g.titre} className="grid grid-cols-[2.6rem_1fr] gap-3">
              <span className="donnee pt-1 text-[1.05rem] text-[var(--mode-sourd)]" aria-hidden="true">
                {String(i + 1).padStart(2, '0')}
              </span>
              <div>
                <h3 className="titre titre-bloc">
                  <span className="sr-only">{i + 1}. </span>
                  {g.titre}
                </h3>
                <p className="mt-2 text-[0.95rem]">{g.texte}</p>
              </div>
            </li>
          ))}
        </ol>
        <div className="mt-12 border-l-4 border-[var(--mode-accent)] pl-5 sm:pl-6">
          <p className="etiquette">Ce que ces règles coûtent</p>
          <p className="texte mt-3 text-[1.02rem]">
            Un seuil, une latence et l’absence de croisement rendent certains agrégats illisibles dans un petit établissement. C’est voulu. Un tableau de bord plus fin serait un tableau de bord qui désigne quelqu’un.
          </p>
        </div>
      </Section>

      {/* Le cadre V1 */}
      <Section etiquette="Périmètre" titre="Le cadre V1" id="cadre">
        <p className="texte text-[1.05rem]">
          Trois lignes tiennent la V1 : son statut réglementaire, qui paie le soin, qui paie le dispositif. Rien d’autre n’est promis.
        </p>
        <ul className="mt-8 grid gap-4 lg:grid-cols-3" aria-label="Les trois lignes du cadre V1">
          {CADRE_V1.map((c) => (
            <li key={c.titre} className="plaque flex h-full flex-col">
              <p className="etiquette">{c.etiquette}</p>
              <h3 className="titre titre-bloc mt-3">{c.titre}</h3>
              <p className="mt-3 text-[0.95rem]">{c.texte}</p>
            </li>
          ))}
        </ul>
        <p className="sourd mt-6 text-[0.8rem]">
          Éligibilité aux appels à projets ARS : sous réserve, établissement par établissement. Aucun financement n’est acquis à la démonstration.
        </p>
      </Section>

      {/* Phases 2-3 */}
      <Section etiquette="Et après" titre="Phases suivantes : des options, pas des promesses" id="phases">
        <ol className="grid gap-4 lg:grid-cols-3" aria-label="Périmètre V1 et phases suivantes">
          {PHASES.map((p, i) => (
            <li
              key={p.phase}
              className={`plaque flex h-full flex-col ${i === 0 ? 'border-l-4 border-l-[var(--mode-accent)]' : 'border-dashed'}`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="donnee text-[1.05rem]">{p.phase}</span>
                <Pastille ton={i === 0 ? 'ambre' : 'neutre'}>{p.statut}</Pastille>
              </div>
              <h3 className="titre titre-bloc mt-4">{p.titre}</h3>
              <p className="mt-3 text-[0.95rem]">{p.texte}</p>
              {i > 0 && (
                <p className="mt-auto pt-5">
                  <AMesurer>sans date, sans engagement</AMesurer>
                </p>
              )}
            </li>
          ))}
        </ol>
        <p className="texte mt-8 text-[0.95rem]">
          Chacune de ces phases changerait le statut juridique du produit, son modèle de revenus et ses obligations. Elles sont écrites ici pour que personne ne les découvre plus tard. Aucune n’est engagée, aucune n’est datée.
        </p>
      </Section>

      {/* Et maintenant */}
      <section className="filet" aria-labelledby="suite-titre">
        <div className="conteneur py-20 sm:py-28">
          <p className="etiquette">Et maintenant</p>
          <h2 id="suite-titre" className="titre titre-section mt-3">
            Voir les trois écrans
          </h2>
          <p className="phrase mt-8 max-w-4xl">La méthode se juge sur l’écran du soignant, pas sur une liste de principes.</p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/demo/soignant" className="bouton">
              Ouvrir le journal de garde
            </Link>
            <Link href="/preuves" className="bouton bouton-second">
              Les preuves
            </Link>
            <a href={TEL_3114_HREF} className="bouton bouton-3114">
              {TEL_3114_AFFICHE} — si ça ne va pas, maintenant
            </a>
          </div>
          <p className="sourd mt-6 text-[0.8rem]">Démonstration : rien n’est enregistré sur ce site, aucune donnée n’est collectée.</p>
        </div>
      </section>
    </>
  )
}
