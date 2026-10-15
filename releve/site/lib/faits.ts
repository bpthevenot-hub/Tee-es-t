// Faits autorisés pour la démonstration (brief § 7). Chaque chiffre porte sa
// source ; rien d'autre ne doit apparaître sur le site. « À mesurer » partout
// où la preuve n'existe pas encore.

export type Fait = {
  valeur: string
  texte: string
  source: string
  url: string
  nature: 'mesuré' | 'déclaré'
}

export const FAITS: Fait[] = [
  {
    valeur: '49 %',
    texte: 'des médecins français présentent au moins un symptôme de burnout ; 5 % une forme sévère.',
    source: 'Kansoun et al., Journal of Affective Disorders, 2019 — méta-analyse, 37 études, 15 183 praticiens',
    url: 'https://www.sciencedirect.com/science/article/abs/pii/S0165032718314873',
    nature: 'mesuré',
  },
  {
    valeur: '+44 %',
    texte: 'de risque de décès par suicide chez les médecins par rapport à la population générale (+90 % chez les femmes). Données mondiales, en baisse en Europe.',
    source: 'Dutheil et al., PLOS ONE, 2019 — méta-analyse, 25 études',
    url: 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0226361',
    nature: 'mesuré',
  },
  {
    valeur: '1 sur 10',
    texte: 'médecins et infirmiers ont eu des pensées de mort ou d’automutilation dans les quinze derniers jours.',
    source: 'OMS/Europe, 2025 — plus de 90 000 réponses',
    url: 'https://www.who.int/europe',
    nature: 'mesuré',
  },
  {
    valeur: '1 sur 2',
    texte: 'infirmières hospitalières, près d’une sur deux, ont quitté l’hôpital ou changé de métier dans les dix ans (ordre de grandeur arrondi).',
    source: 'DREES, Études & Résultats n° 1277, 2023',
    url: 'https://drees.solidarites-sante.gouv.fr',
    nature: 'mesuré',
  },
  {
    valeur: '10,4 %',
    texte: 'd’absentéisme chez Clariane en 2024 ; 12,8 % chez Ramsay France (exercice 2023) ; 9,2 % dans les hôpitaux publics (FHF, 2024) ; 7,22 % dans la santé privée contre 4,68 % tous secteurs.',
    source: 'Rapports annuels Clariane et Ramsay Santé ; FHF 2024 ; baromètre APICIL–JLO 2026',
    url: 'https://www.clariane.com',
    nature: 'déclaré',
  },
  {
    valeur: '147 M€',
    texte: 'd’intérim médical en 2022, de 559 à 662 M€ en comptant les contrats courts.',
    source: 'Cour des comptes, rapport sur l’application des lois de financement de la sécurité sociale, 2024',
    url: 'https://www.ccomptes.fr',
    nature: 'mesuré',
  },
  {
    valeur: '–0,45',
    texte: 'd’effet des interventions organisationnelles contre le burnout, contre –0,18 pour les interventions individuelles (effet global –0,29).',
    source: 'Panagioti et al., JAMA Internal Medicine, 2017 — méta-analyse',
    url: 'https://jamanetwork.com/journals/jamainternalmedicine',
    nature: 'mesuré',
  },
  {
    valeur: '25 % → 12 %',
    texte: 'de détresse psychologique chez les participants réguliers aux Schwartz Rounds (débriefings collectifs facilités). Étude non randomisée.',
    source: 'Maben et al., NIHR, 2018',
    url: 'https://www.journalslibrary.nihr.ac.uk',
    nature: 'mesuré',
  },
  {
    valeur: '6 339',
    texte: 'inscriptions au NHS Practitioner Health en 2024/25 ; un inscrit sur trois avec des idées suicidaires ; plus de 800 retours au travail.',
    source: 'NHS Practitioner Health, rapport annuel 2024/25',
    url: 'https://www.practitionerhealth.nhs.uk',
    nature: 'déclaré',
  },
  {
    valeur: '1 700+',
    texte: 'soignants accompagnés par les médecins pairs de l’association MOTS depuis 2010, neuf professions à ordre, ligne ouverte 7 j/7.',
    source: 'Association MOTS, Toulouse',
    url: 'https://www.association-mots.org',
    nature: 'déclaré',
  },
]

/** Ce que Relève s'engage à mesurer avant de parler chiffres (brief § 11). */
export const A_MESURER = [
  'Délai de premier contact avec un pair',
  'Taux de recours à 3, 6 et 12 mois, par grande catégorie',
  'Rétention du suivi et durée réelle du protocole',
  'Retours au travail après arrêt ou hospitalisation',
  'Satisfaction des soignants et des pairs',
  'Usage du mode nuit et du mode couloir',
  'Coût complet par soignant suivi',
] as const

/** Le modèle d'inspiration : ce qu'Éos a réussi et laissé ouvert (dossier). */
export const EOS = {
  reussites: [
    'Devenir un offreur de soins : société de téléconsultation agréée (2025), médecins salariés, actes remboursés, tiers payant.',
    'Inventer un format : binôme médecin-infirmier, deux contacts courts par semaine, là où l’ambulatoire offre un rendez-vous par mois.',
    'Se brancher sur le flux amont : une page d’adressage sans intégration informatique, un pilote avec un groupe de cliniques (Clariane/Inicea).',
    'Enlever l’administratif au soignant : facturation portée par la société, aide à la prescription, notes assistées.',
    'Rendre le travail visible : posters en congrès, comité scientifique, direction médicale psychiatre.',
  ],
  ouvert: [
    'Aucune preuve d’efficacité publiée : ni rechute, ni abstinence, ni hospitalisations évitées.',
    'Ni dispositif médical, ni télésurveillance réglementaire.',
    'Ni pair-aidance, ni collectif, ni entourage.',
    'Cible « stable et abstinent » : pas de phase aiguë, pas de réduction des risques.',
    'Aucune offre pour les soignants eux-mêmes.',
  ],
} as const
