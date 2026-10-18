// Relève — constantes produit et faits d'identité. Source unique pour tout le
// site. Démonstration : aucune donnée réelle, aucune collecte.

export const PRODUIT = 'Relève'
export const SIGNATURE = 'La clinique digitale du soignant'
export const THESE =
  'Un pair qui a fait le même métier, joignable entre deux gardes, que votre employeur ne verra jamais.'

export const BANDEAU_DEMO =
  'Démonstration — proposition de produit par SNB Consulting. Aucune donnée réelle, aucune collecte. Non affiliée à l’association MOTS ni à Eos Care.'

/** Numéro national de prévention du suicide — gratuit, 24 h/24, 7 j/7. */
export const TEL_3114_AFFICHE = '3114'
export const TEL_3114_HREF = 'tel:3114'
/** Ligne d’écoute de l’association MOTS — médecins pairs, 7 j/7, confidentielle. */
export const TEL_MOTS_AFFICHE = '06 08 28 25 89'
export const TEL_MOTS_HREF = 'tel:+33608282589'
/** SAMU : numéro national d’aide médicale urgente (source : service-public.fr, « Numéros d’urgence »). */
export const TEL_SAMU_AFFICHE = '15'
export const TEL_SAMU_HREF = 'tel:15'
export const MOTS_SITE = 'https://www.association-mots.org'
export const SNB_SITE = 'https://snb.center'

export const NAVIGATION = [
  { href: '/', label: 'Pourquoi' },
  { href: '/methode', label: 'La méthode' },
  { href: '/demo/soignant', label: 'Journal de garde' },
  { href: '/demo/equipe', label: 'Transmissions' },
  { href: '/demo/direction', label: 'Agrégats' },
  { href: '/preuves', label: 'Preuves' },
  { href: '/mots', label: 'Pour MOTS' },
] as const

/** Les cinq étapes du parcours (brief § 4). */
export const PARCOURS = [
  {
    numero: 'I',
    titre: 'Repérage discret',
    texte:
      'L’entrée se fait par les moments à risque de l’établissement — après un événement indésirable grave, une agression, un retour d’arrêt long, une prise de poste de nuit — via un lien générique affiché dans les transmissions et les vestiaires. Jamais par un identifiant RH.',
    gardeFou: 'Pas de connexion employeur. Aucune donnée ne quitte l’appareil avant un consentement explicite.',
  },
  {
    numero: 'II',
    titre: 'Orientation vers un pair',
    texte:
      'Un médecin pair formé au soin des soignants (DIU « Soigner les soignants », réseau MOTS), choisi par profession et, si on le souhaite, hors région. Premier contact sous 48 h : délai à mesurer.',
    gardeFou: 'Le pair n’est jamais un collègue du même établissement. Consentement libre et révocable.',
  },
  {
    numero: 'III',
    titre: 'Quinze minutes entre deux gardes',
    texte:
      'Des créneaux de 15 minutes, au téléphone ou en visio, calés sur le planning que le soignant déclare lui-même, reprenables s’ils sont interrompus.',
    gardeFou: 'Téléconsultation conventionnelle facturée par le pair en son nom. Rien n’est facturé à l’établissement par soignant.',
  },
  {
    numero: 'IV',
    titre: 'Huit à douze semaines en binôme',
    texte:
      'Un binôme pair + infirmier coordinateur, un psychologue partenaire si besoin, un check-in quotidien facultatif : une couleur, une phrase. La durée est une hypothèse de conception, à mesurer.',
    gardeFou: 'Tout score est produit et interprété par un humain. Aucun module thérapeutique automatisé.',
  },
  {
    numero: 'V',
    titre: 'Continuité après l’arrêt',
    texte:
      'Le fil reprend après un arrêt, une hospitalisation ou un changement d’établissement : le dossier suit le soignant, pas l’employeur. On prépare le retour à l’exercice.',
    gardeFou: 'Aucun signalement nominatif à l’employeur, y compris en cas de risque suicidaire : 3114, SAMU, médecin traitant, MOTS.',
  },
] as const

/** Les cinq innovations assumées (brief § 6). */
export const INNOVATIONS = [
  { titre: 'Le pair avant le psy', texte: 'Un médecin pair formé, hors établissement, en premier contact — le seul format de suivi longitudinal qui existe en France pour les soignants.' },
  { titre: 'Des événements, pas un numéro', texte: 'Les portes d’entrée sont les moments à risque de l’établissement, pas une ligne anonyme que presque personne n’appelle.' },
  { titre: 'Le mur de verre', texte: 'La direction reçoit des agrégats sous seuil, posés à côté de ses propres indicateurs — et jamais un nom.' },
  { titre: 'Conçu pour la garde, et pour être fermé', texte: 'Sessions de quarante secondes reprenables, aucune modale, mode nuit ambre, mode couloir, aucune notification hors service.' },
  { titre: 'Résultats ouverts', texte: 'Un registre de recours, de rétention et de retours au travail rendu aux établissements et à MOTS chaque année.' },
] as const

/** Ce que Relève ne fait pas (brief § 9). */
export const INTERDITS = [
  'Ne dépiste pas, ne diagnostique pas, ne recommande pas : hors dispositif médical au départ.',
  'N’affiche aucun score d’office, n’attribue ni récompense, ni série, ni niveau.',
  'N’envoie aucune notification hors service et ne se connecte jamais au système RH.',
  'Ne transmet aucun nom à l’employeur, aucune cellule de moins de dix personnes.',
] as const
