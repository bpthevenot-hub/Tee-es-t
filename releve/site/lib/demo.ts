// Données de démonstration — entièrement fictives, pseudonymes, aucune personne
// réelle. Elles existent pour montrer les écrans, jamais pour être crues.

export type Quadrant = 'ambre' | 'brique' | 'prune' | 'sauge'

export const QUADRANTS: Record<Quadrant, { nom: string; energie: 'haute' | 'basse'; agreabilite: 'agréable' | 'désagréable'; mots: string[] }> = {
  ambre: { nom: 'Ambre', energie: 'haute', agreabilite: 'agréable', mots: ['porté', 'vif', 'disponible'] },
  brique: { nom: 'Brique', energie: 'haute', agreabilite: 'désagréable', mots: ['tendu', 'en colère', 'à cran'] },
  prune: { nom: 'Prune', energie: 'basse', agreabilite: 'désagréable', mots: ['vidé', 'seul', 'éteint'] },
  sauge: { nom: 'Sauge', energie: 'basse', agreabilite: 'agréable', mots: ['posé', 'calme', 'soulagé'] },
}

/** Le soignant de la démo. */
export const SOIGNANT_DEMO = {
  prenom: 'Camille',
  profession: 'Infirmière de nuit, réanimation',
  pair: { prenom: 'Dr Lefort', profession: 'médecin pair, formée DIU « Soigner les soignants », hors établissement' },
  prochainRdv: { jour: 'Jeudi', heure: '14 h 15', mode: 'téléphone', duree: '15 min' },
  semaineProtocole: 4,
  semainesProtocole: 10,
  gardesDeclarees: ['Lun 20 h – 8 h', 'Mar 20 h – 8 h', 'Ven 20 h – 8 h'],
  journal: [
    { jour: 'Lun', quadrant: 'prune' as Quadrant, phrase: 'Trois admissions à 3 h. Pas eu le temps de manger.' },
    { jour: 'Mar', quadrant: 'brique' as Quadrant, phrase: 'Famille agressive au box 4. Débriefé avec l’interne.' },
    { jour: 'Mer', quadrant: 'sauge' as Quadrant, phrase: 'Repos. Dormi neuf heures.' },
    { jour: 'Jeu', quadrant: 'sauge' as Quadrant, phrase: 'Appel avec Dr Lefort. On a parlé du box 4.' },
    { jour: 'Ven', quadrant: 'ambre' as Quadrant, phrase: 'Garde fluide. Équipe complète.' },
  ],
}

/** La file active du binôme (espace Transmissions). Pseudonymes uniquement. */
export type Dossier = {
  code: string
  profession: string
  etape: 1 | 2 | 3 | 4 | 5
  semaine: number
  prochainRdv: string
  signale: boolean
  demande?: string
  derniereNote: string
}
export const FILE_ACTIVE: Dossier[] = [
  { code: 'R-0417', profession: 'IDE réanimation, nuit', etape: 4, semaine: 4, prochainRdv: 'Jeu 14 h 15', signale: true, demande: 'Je veux être rappelée avant vendredi.', derniereNote: 'Agression verbale box 4. Sommeil fragmenté. Consentement relais psychologue : non pour l’instant.' },
  { code: 'R-0402', profession: 'Médecin anesthésiste', etape: 3, semaine: 2, prochainRdv: 'Mar 7 h 30', signale: false, derniereNote: 'Deuxième contact. Évoque un EIGS d’octobre. Souhaite un pair hors région : fait.' },
  { code: 'R-0388', profession: 'Aide-soignante, SSR', etape: 5, semaine: 11, prochainRdv: 'Lun 12 h', signale: false, derniereNote: 'Retour d’arrêt long préparé avec la médecine du travail, à sa demande. Dernier créneau du protocole.' },
  { code: 'R-0421', profession: 'Interne, urgences', etape: 2, semaine: 1, prochainRdv: 'À planifier', signale: false, derniereNote: 'Entrée après prise de poste de nuit. Premier contact sous 48 h : délai tenu (31 h).' },
  { code: 'R-0395', profession: 'Sage-femme', etape: 4, semaine: 6, prochainRdv: 'Mer 16 h', signale: false, derniereNote: 'Relais psychologue (Mon soutien psy) engagé avec consentement tracé le 2 octobre.' },
]

export const ETAPES_PROTOCOLE = [
  'Repérage',
  'Orientation',
  'Premiers 15 min',
  'Binôme',
  'Continuité',
] as const

export const TEMPS_EQUIPE = {
  service: 'Réanimation polyvalente',
  motif: 'Événement indésirable grave du 2 octobre',
  format: 'Débriefing collectif facilité, 45 min, animé par un pair extérieur',
  inscrits: 9,
}

/** Agrégats pour la direction (espace Agrégats). Toute cellule < 10 est masquée. */
export const SEUIL_CELLULE = 10

export type Cellule = { categorie: string; effectif: number; recours: number }
export const RECOURS_PAR_CATEGORIE: Cellule[] = [
  { categorie: 'Infirmiers', effectif: 212, recours: 31 },
  { categorie: 'Aides-soignants', effectif: 148, recours: 17 },
  { categorie: 'Médecins', effectif: 64, recours: 11 },
  { categorie: 'Internes', effectif: 18, recours: 6 },
  { categorie: 'Sages-femmes', effectif: 9, recours: 3 },
  { categorie: 'Autres soignants', effectif: 41, recours: 4 },
]

export const THEMATIQUES = [
  { nom: 'Charge et organisation du travail', part: 38 },
  { nom: 'Événements indésirables, agressions', part: 24 },
  { nom: 'Sommeil et nuit', part: 19 },
  { nom: 'Conflits d’équipe', part: 11 },
  { nom: 'Autres', part: 8 },
]

/** Tendance mensuelle avec latence d'un mois (le dernier mois n'est pas affiché). */
export const TENDANCE = [
  { mois: 'Avr', recours: 9 },
  { mois: 'Mai', recours: 14 },
  { mois: 'Juin', recours: 19 },
  { mois: 'Juil', recours: 23 },
  { mois: 'Août', recours: 27 },
  { mois: 'Sept', recours: 34 },
]

/** Indicateurs saisis par l'établissement lui-même (jamais calculés par Relève). */
export const INDICATEURS_ETABLISSEMENT = [
  { nom: 'Absentéisme', valeur: '10,1 %', periode: '12 derniers mois', saisiPar: 'DRH' },
  { nom: 'Intérim', valeur: '184 k€', periode: 'trimestre', saisiPar: 'DAF' },
  { nom: 'Postes vacants', valeur: '7', periode: 'ce mois', saisiPar: 'DRH' },
]

export const QUI_VOIT_QUOI = [
  { qui: 'Direction', voit: 'Agrégats sous seuil, tendance avec latence, thématiques' },
  { qui: 'CSE / CSSCT', voit: 'Les mêmes agrégats, restitués chaque trimestre' },
  { qui: 'Santé au travail', voit: 'Les mêmes agrégats ; un soignant peut la saisir lui-même' },
  { qui: 'Le binôme', voit: 'Le dossier du soignant qui l’a choisi, avec son consentement' },
  { qui: 'L’employeur', voit: 'Jamais un nom, jamais un score, jamais un service de moins de dix' },
] as const
