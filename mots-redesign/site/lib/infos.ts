// Informations factuelles publiques de l'Association MOTS, réunies lors de
// l'audit (2026-07). Source unique pour tout le site.

export const TEL_AFFICHE = '06 08 28 25 89'
export const TEL_HREF = 'tel:+33608282589'

export const ADRESSE = {
  ligne1: 'Maison des professions de santé',
  ligne2: '9 avenue Jean Gonord',
  ville: '31500 Toulouse',
}

export const HELLOASSO_URL =
  'https://www.helloasso.com/associations/mots-medecins-organisation-travail-sante'

export const SITE_OFFICIEL = 'https://www.association-mots.org'

// Vidéo officielle « Association MOTS, prendre soin des soignants » (chaîne YouTube de l'association)
export const YOUTUBE_ID = 'ZwXafxJvkTo'

export const PROFESSIONS = [
  'Médecins',
  'Infirmiers',
  'Chirurgiens-dentistes',
  'Masseurs-kinésithérapeutes',
  'Pharmaciens',
  'Pédicures-podologues',
  'Sages-femmes',
  'Orthoptistes',
  'Biologistes',
]

export const CHIFFRES = [
  { valeur: '2010', legende: 'Création à Toulouse' },
  { valeur: '1 700+', legende: 'Soignants accompagnés' },
  { valeur: '7 j/7', legende: 'Ligne d’écoute dédiée' },
  { valeur: '9', legende: 'Professions accompagnées' },
]

// Études scientifiques publiées sur la santé des soignants (vérifiées 2026-07).
// Chaque chiffre affiché sur le site renvoie à sa publication.
export const ETUDES = [
  {
    valeur: '49 %',
    texte:
      'des médecins français sont touchés par le burnout au cours de leur carrière, dont 5 % sous une forme sévère.',
    source:
      'Kansoun et al., Journal of Affective Disorders, 2019 — méta-analyse de 37 études, 15 183 médecins',
    url: 'https://www.sciencedirect.com/science/article/abs/pii/S0165032718314873',
  },
  {
    valeur: '+44 %',
    texte:
      'de risque de décès par suicide chez les médecins par rapport à la population générale.',
    source: 'Dutheil et al., PLOS ONE, 2019 — méta-analyse de 25 études',
    url: 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0226361',
  },
  {
    valeur: '66 %',
    texte:
      'des jeunes médecins présentent des symptômes anxieux ; 27,7 % des symptômes dépressifs, et 23,7 % ont déjà eu des idées suicidaires.',
    source:
      'Enquête nationale santé mentale, 2017 — ANEMF · ISNAR-IMG · ISNCCA · ISNI, ≈ 22 000 répondants',
    url: 'https://www.revue-hospitaliere.fr/Actualites/Sante-mentale-des-jeunes-medecins-Enquete-et-resultats',
  },
] as const

export const ETUDE_ESPOIR = {
  texte:
    'Les interventions individuelles comme organisationnelles produisent des réductions cliniquement significatives du burnout des médecins.',
  source:
    'West, Dyrbye, Erwin & Shanafelt, The Lancet, 2016 — revue systématique et méta-analyse',
  url: 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(16)31279-X/abstract',
} as const

export const NAVIGATION = [
  { href: '/lassociation', label: 'L’association' },
  { href: '/aide-accompagnement', label: 'Aide & accompagnement' },
  { href: '/nos-cooperations', label: 'Nos coopérations' },
  { href: '/je-deviens-adherent', label: 'Devenir adhérent' },
  { href: '/faq', label: 'FAQ' },
  { href: '/ressources', label: 'Ressources' },
  { href: '/actualites', label: 'Actualités' },
  { href: '/nous-ecrire', label: 'Nous écrire' },
] as const
