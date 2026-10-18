# Dossier de recherche consolidé — « Clinique digitale du soignant » (France, 13 octobre 2026)

*Consolidation des cinq relevés vérifiés du 13 octobre 2026 : `eos-decode.md`, `marche-cliniques.md`, `reglementaire.md`, `preuves-chiffrees.md`, `design-etat-de-l-art.md`. Chaque chiffre porte sa source et le statut fixé par le relevé d'origine. Convention : **[E]** = affirmé par l'entreprise, l'association ou un acteur intéressé ; **[I]** = mesuré ou indépendant ; **[?]** = contradictoire ou non confirmé ; SOLIDE / FRAGILE / INTROUVABLE = grille de `preuves-chiffrees.md`. Avertissement commun : la passe de vérification adversariale n'a disposé d'aucun accès web (quota épuisé, DNS bloqué sur toutes les sources primaires). Aucune affirmation n'a été réfutée, mais presque aucune n'a été reconfirmée en ligne ce jour ; tout chiffre destiné à un usage externe doit être recoupé avant publication (§ 7).*

---

## 1. Commande et cadrage

**Commande (Baptiste, SNB Consulting)** : « un nouveau design, quelque chose d'hyper innovant pour les cliniques », inspiré de l'application Éos, transposable à l'association MOTS « sous une autre forme ».

**Ce que les relevés établissent** : l'« application Éos » est **Eos / Eos Care**, clinique digitale d'addictologie pour **patients** (marque CLEER, Paris), partenaire de Clariane/Inicea. Aucune appli « Éos » pour soignants n'existe (`marche-cliniques.md` § 5 ; `reglementaire.md` § 3). Éos est donc un **modèle à transposer** — clinique virtuelle, binôme médecin-infirmier, suivi court et fréquent, adressage par l'établissement — pas un concurrent.

**La cible « sous une autre forme »** : MOTS (Médecins Organisation Travail Santé, Toulouse, 2010) écoute et accompagne les soignants en détresse par des médecins pairs formés (DIU « Soigner les soignants »), ligne 06 08 28 25 89, 7 j/7, gratuite et confidentielle ; 1 700+ soignants accompagnés ; 9 professions à ordre (données transmises par le client, issues de la refonte du site MOTS). Les relevés confirment l'ossature — création 2010 à Toulouse, écoute 24 h/24, « médecins effecteurs » formés à la santé au travail, ouverture à tous les soignants depuis 2018 — avec un chiffre antérieur de « ~1 500 accompagnés en dix ans » [E, ~2020-2021], cohérent avec 1 700+ en 2026 (`marche-cliniques.md` § 1.1). Vigilance : le dépliant 2020 donne « 0608 282 589 » — numéro à vérifier sur association-mots.org avant diffusion. MOTS a développé **OASIS**, plateforme d'auto-évaluation financée depuis octobre 2024 par le fonds de dotation Nos Épaules et Nos Ailes [presse, carenews] (`reglementaire.md` § 5). Numéro national de prévention du suicide : **3114** (18 centres).

---

## 2. Éos décodé (source : `eos-decode.md`)

### 2.1 Identité

Marque Eos / Eos Care, app « Eos : Arrêt Alcool & Tabac » (iOS id6504914380, Android `com.eos.usermobile`) [I, stores]. Entité : CLEER CONSULT, SASU créée le 12/09/2024, SIREN 933 029 324, Paris 17e, NAF 86.21Z, filiale de CLEER (Nicolas Gueugnier) [I, pappers]. Marque déposée le 02/07/2024 [E]. Fondateurs : Nicolas Gueugnier (CEO), Maxime Bouré (CTO) ; direction médicale Dr Camille Perrotte (psychiatre-addictologue), Hugo Knoblock (infirmier coordinateur) [E]. Origine : venture-builder Kamet Ventures, partenariat Korian/Clariane–Kamet (VivaTech, 16/06/2022) [I/E]. Financement : « unfunded » (Tracxn) vs « fonds privés » (poster 2025) [?]. Effectifs : 12 employés (Tracxn 2026), « 21 médecins addictologues salariés » (LinkedIn, non daté) [E]. « EOS Renaissance » (prétendu lauréat du Grand Défi DMN) : **aucune occurrence trouvée** ; attribution retirée par `reglementaire.md`.

### 2.2 Le modèle

- **Protocole** : suivi intensif court par un binôme médecin addictologue + infirmier coordinateur, psychologue disponible ; « 2 rdv par semaine d'une quinzaine de minutes » (poster Albatros 2025) **vs** « 30 minutes en visio, deux fois par semaine » (site) — contradiction non tranchée [?] ; « modules de 6 semaines » et « pas de durée limite » ; **aucune source ne mentionne 12 semaines** ; téléconsultations programmées et non programmées ; RDV d'urgence si rechute ; outils partagés de TCC.
- **Trois portes d'entrée** : post-cure, pré-cure, complément d'un suivi (CSAPA, HDJ, libéral) [E]. **Cible** : patients « stables, abstinents, motivés » — phase aiguë et réduction des risques exclues.
- **App patient** : modes autonome / suivi, journal quotidien de consommation, humeur/sommeil, objectifs, rappels, graphiques simples, messagerie, téléconsultation intégrée ; **pas un dispositif médical**, « ne peut être utilisée pour de la télésurveillance médicale au sens du CSP » (CGU) [E].
- **Interface soignants** : dossier partagé médecin/infirmier/psychologue, protocoles structurés, aide à la prescription (VIDAL intégré le 04/06/2025 [E]), « prise de notes automatisée par IA » (fournisseur, hébergement, validation : inconnus), **zéro administratif** (facturation portée par la société), page d'adressage « sans formation ni intégration informatique ».
- **Statut et revenu** : **société de téléconsultation agréée** (art. L4081-1 s. CSP ; 23/05/2025 selon Medadom [concurrent], confirmé par Maillage 95 le 11/06/2025 [I]) — seule agréée spécialisée aux côtés de Medadom, Qare, Livi, Medaviz, MédecinDirect, Tessan ; FINESS depuis juin 2025 [E] ; médecins **salariés** (CDI temps partiel, télétravail, dès 4 h/semaine, « > 130 K€ brut ETP » [E]) ; revenu = actes facturés à l'AMO au tarif opposable (lecture corrigée : 70 % AMO + complémentaire en tiers payant, 100 % seulement en ALD) + psychologue 60 €/séance ; **aucun tarif B2B public**.
- **Échelle** : « 1 300 patients adressés, 90 établissements, 98 % recommandent » [E, invérifiable] ; pilote Clariane/Inicea à la clinique Le Haut Lignon (CP du 16/06/2025, date à recouper) puis Val Pyrène : **36 patients adressés** juin 2025-février 2026, poster Albatros 2026, évaluation descriptive sans groupe contrôle [E]. App Store 4,7/5 sur 72 notes [I, date incertaine] ; aucun avis négatif, aucune presse.

### 2.3 Réussites (cinq)

1. **Le statut** : seule société agréée spécialisée, FINESS, salariat — l'app devient un offreur de soins en tiers payant.
2. **Un format de soin** : binôme + 2 contacts courts/semaine, là où l'ambulatoire offre un RDV par mois.
3. **Le flux amont** : page d'adressage sans intégration SI pour SMR/CSAPA/ELSA/CPTS ; le patient arrive par l'établissement, pas par le marketing.
4. **L'administratif retiré au soignant** : facturation, VIDAL, notes IA — attractif pour des psychiatres à temps partiel.
5. **La crédibilité scientifique** : deux posters Albatros, comité scientifique, directrice médicale psychiatre.

### 2.4 Angles morts (cinq)

1. **Aucune preuve d'efficacité publiée** : quelques dizaines de patients, satisfaction déclarative (100 % « contrôle sur leur vie », 74 % estime de soi, 67 % relations — « non représentatifs », poster 2025), aucun critère dur, aucune publication.
2. **Ni DM ni télésurveillance réglementaire** ; contradiction entre partenaires (« télésurveillance ») et CGU.
3. **Ni réduction des risques ni phase aiguë**.
4. **Ni pair-aidance ni collectif** : aucun groupe, patient-expert, entourage ; accompagnement social absent.
5. **Packaging daté et dépendances** : nom « Arrêt Alcool & Tabac » alors que cannabis/cocaïne/jeu/écrans sont couverts ; design non différenciant ; un seul partenaire structurant ; 21 médecins pour 1 300 adressés ; IA sans information HDS/consentement ; agrément renouvelable exposé à un contrôle sur 2 actes/semaine.

**Pour la transposition** : reprendre le *format* (binôme, contacts courts et fréquents, adressage par l'établissement, zéro administratif, posters) ; construire ce qu'Éos n'a pas (pairs, collectif, résultats publiés, continuité après hospitalisation, design) ; éviter ce qu'Éos subit (dépendance à l'agrément et à un seul partenaire, IA opaque).

---

## 3. Marché et acheteurs : les cliniques (source : `marche-cliniques.md`)

### 3.1 Dispositifs existants et leurs limites

- **MOTS** : seul acteur français de **suivi longitudinal médical par des pairs** ; association sans produit numérique ni tableau de bord employeur ; cherche des « institutions et groupes de santé » financeurs ; partenariat pérenne ONCD (lettre n° 221, avril 2025) ; aucun bilan d'activité 2024 en ligne.
- **SPS / Pros-Consulte** : 0 805 23 23 36, 24 h/24, 100+ psychologues ; **~5 500 appels en 2025** (15/jour) contre 7 000 en 2024 (titre « en hausse » : base de comptage à vérifier) [E] ; pour ~1,5 million de professionnels, **recours < 0,5 %** (calcul propre) ; ni contrat établissement, ni reporting, ni prévention.
- **CNOM entraide** : 0800 288 038 ; 389 dossiers en 2024 ; ~2 M€/an ; médecins seulement, surtout financier et juridique [E].
- **Mon soutien psy** : 12 séances/an à 50 €, 60 % AMO / 40 % complémentaire, accès direct (juin 2024 selon `reglementaire.md`, « 2025 » selon `marche-cliniques.md` — à trancher sur ameli.fr) ; aucun volet soignants ; bilan avril 2025 : 5 217 psychologues, 586 858 patients, 3,1 M séances [officiel].
- **Médecine du travail** : 5 108 médecins (2012) → 4 265 (2023), **–16,5 % sur onze ans** (corrigé), creux vers 2030 (QE 15700) ; les cliniques privées relèvent de SPST interentreprises.
- **EAP corporate** (Moodwork — 110 000 salariés via Harmonie Mutuelle [E] ; teale ; moka.care ; Alan Mind ; Qualisocial, Stimulus, Psya) : **aucune référence hôpital/clinique trouvée** ; contenus pensés pour le tertiaire, pas pour les 12 h, la mort de patients, l'EIGS, la violence.
- **Étranger** : **NHS Practitioner Health** — 6 339 inscriptions 2024/25, ~37 000 cumulées, 1 inscrit sur 3 avec idées ou plan suicidaire, > 800 retours au travail, ~7 M£/an (fragile) soit **~1 100 £ par inscription** (calcul propre) ; **Lyra Health** — « 10 health systems », 100 % de renouvellement, 84,1 % d'amélioration [E, méthode non décrite] ; **Atalan Tech** et **vellum** (modèles vendus à l'établissement) ; **RISE** (Johns Hopkins, pairs formés, demandes surtout infirmières, BMJ Open 2016 [I]) ; **Schwartz Rounds** (UK) — **aucune implantation française**.
- **Seconde victime** : ~2 400 EIGS/an (HAS), 60 % des médecins confrontés au moins une fois ; fiche SFAR/CFAR 2020 ; aucun programme outillé à l'échelle d'un groupe.

### 3.2 Les acheteurs

| Acteur | Taille | Absentéisme | Ce qu'il fait déjà |
|---|---|---|---|
| FHP (secteur) | 1 030 établissements, ~170 000 salariés, ~40 000 médecins (29/09/2025) ; **46 % déficitaires en 2025** vs 26 % en 2021 [E] | santé = 7,22 % vs privé 4,68 % (APICIL–JLO 2026) [I] | 100 000 postes vacants public+privé (2021) |
| **Ramsay Santé** | ~38 000 collaborateurs | France **12,8 %** (FY23), 13,9 % (FY22), 15,2 % (FY21) [E, PDF à relire] | **Clinique Le Gouz** (Louhans, 2017), seule clinique dédiée à la psychiatrie des soignants (38 lits + 10 HDJ) ; **MédiPsy-Care** (sept. 2024) — curatif, pas un outil employeur |
| **Clariane** | 63 000 | **10,4 %** (2024), 11,4 % (2023) [E, DEU/SASB] | semaine QVCT, Université Clariane ; **Eos Care** = appli patients |
| **Elsan** | 28 000 collaborateurs, 7 500 praticiens, ~212-217 sites | non extrait | prévention vendue **aux entreprises tierces** ; rien pour ses salariés ; héberge le dépliant MOTS |
| **Vivalto** | entreprise à mission | non trouvé | rien trouvé |
| Hôpital public (FHF) | — | 8,9 % (2019), 11,1 % (2022), 9,5 % (2023), **9,2 % (2024)** [E, série cohérente] | 98 % en difficulté pour recruter des médecins (2022) |

Guichets : **AAP ARS QVCT / CLACT** (Grand Est 2025-2026, PACA « Prendre soin de ceux qui soignent », Normandie, Hauts-de-France) — **éligibilité du privé lucratif non uniforme, à relire règlement par règlement** ; **FACT (Anact)** 2026 « usure professionnelle », 350 000 €, < 300 salariés ; **ANFH / OPCO Santé** = formation seulement ; **FIPHFP** = handicap ; mécénat ; **Grande cause nationale santé mentale 2025 prolongée en 2026** (label, pas de financement direct) (`reglementaire.md` § 5-7). Achats constatés : formations santé mentale, planning IA, plateformes de remplacement, EAP génériques — « rien qui relie prévention psychique → indicateur RH → P&L ».

### 3.3 Le vide à occuper

**Il n'existe pas en France de clinique digitale du soignant B2B** combinant (a) parcours clinique conçu pour les soignants, (b) vente à l'établissement, (c) reporting anonymisé relié à l'absentéisme/turnover, (d) addictions et retour à l'exercice. Sur la carte « individu gratuit/anonyme → établissement payant/piloté » × « écoute → parcours clinique long », le quadrant haut-droit est vide ; seul voisin : NHS PH. Plus proches : Ramsay/Le Gouz (curatif, captif), SPS (gratuit, sans contrat), MOTS (sans produit), Moodwork/teale/moka (sans contenu soignant), Atalan/vellum (US), ThIA (cible les prescripteurs).

**Cinq arguments d'achat** : 1) « votre absentéisme est à 10-13 %, le privé est à 4,7 % » ; 2) « 46 % de vos confrères sont en déficit : plus de QVCT sans ROI mesuré » ; 3) « vos soignants n'appellent pas le 0 805 : < 0,5 % de recours » — un parcours intégré aux moments à risque (EIGS, agression, retour d'arrêt, onboarding) multiplie le recours (RISE) ; 4) « finançable hors budget via CLACT/QVCT ARS » (à nuancer) ; 5) « trou juridique seconde victime + addictions » (L. 4121-1, DUERP, certification HAS). Angle : *le NHS Practitioner Health des cliniques françaises, vendu au groupe, financé par les CLACT, avec MOTS comme réseau clinique et un tableau de bord relié à l'absentéisme.*

---

## 4. Cadre réglementaire et garde-fous (source : `reglementaire.md`)

### 4.1 Ce qui s'applique, par statut

| Brique | **V1 sans DM, sans agrément** | **V2 DM classe IIa** | **V3 agrément téléconsultation** |
|---|---|---|---|
| Information, auto-questionnaires validés (MBI, PHQ-9…) **non interprétés automatiquement** | Oui (HAS niveau B/C) | Oui | Oui |
| Score de risque, dépistage automatisé, module thérapeutique | **Non** (règle 11 RDM 2017/745, confirmée) | Oui, après organisme notifié + preuve clinique | Non en soi |
| Écoute / orientation par pairs ou psychologues | Oui (hors remboursement) | Oui | Oui |
| Téléconsultation facturée à l'AM | Par des médecins libéraux/associatifs utilisant l'outil | Idem | Par des médecins salariés (tarif conventionnel, territorialité, arrêt ≤ 3 j) |
| Psychologues remboursés | **Mon soutien psy** (12 × 50 €) | Idem | Idem |
| Forfait télésurveillance LATM / PECAN | **Non** (aucune ligne psychiatrie ; REMOOD en construction) | Possible si ligne inscrite ; PECAN 1 an | Non |
| Hébergement | **HDS v2** dès qu'une donnée de santé est hébergée | HDS v2 | HDS v2 + certificat ANS |
| Délai indicatif | **3-6 mois** | 18-36 mois | 6-12 mois ; agrément 2 ans puis 3 ans (décret 2024-164 ; décret 2026-626 à lire) |

Doctrine : la CNIL considère qu'un **indicateur ou code couleur de vulnérabilité est une donnée de santé** [presse CFDT] et **ne fixe aucun seuil chiffré d'agrégation** — le ≥ 10 est une bonne pratique contractuelle à arbitrer par le DPO. **Seule la médecine du travail** collecte des données de santé des salariés ; l'employeur n'a que les avis d'aptitude et rapports collectifs (L. 4624-8) ; le **CSE** est informé-consulté avant tout outil traitant des données des salariés. L'obligation de sécurité (L. 4121-1) couvre la santé **mentale** ; les RPS doivent figurer au **DUERP**, à jour dans moins d'un service sur deux (DARES 2019).

### 4.2 Les cinq garde-fous non négociables

1. **Anonymat structurel vis-à-vis de l'employeur** : l'établissement finance mais n'est jamais responsable de traitement ; accès sans identifiant RH (pas de SSO employeur), HDS, DPO distinct ; agrégats seuls, seuil de cellule ≥ 10, interdiction de croiser service × métier × genre, latence ; restitution au CSE/CSSCT et au service de santé au travail, pas à la ligne managériale.
2. **Consentement libre, explicite, révocable** ; effacement sans trace côté employeur ; interdiction contractuelle de conditionner évaluation, mobilité ou prime à l'usage.
3. **Aucune donnée individuelle, aucun score, aucun signalement nominatif à l'employeur**, y compris en cas de risque suicidaire : la chaîne d'urgence passe par le **3114**, le SAMU, le médecin traitant, MOTS/SPS — jamais par la DRH.
4. **Pas de revendication médicale sans statut** : hors DM, l'outil ne dépiste pas, ne diagnostique pas, ne recommande pas ; tout score est produit et interprété par un humain qualifié.
5. **Souveraineté et sécurité** : HDS v2 (EEE), référentiel ANS si téléconsultation, Pro Santé Connect/INS, audit annuel, auditabilité par le CSE et le DPO.

### 4.3 Architecture retenue

**V1 = hors DM, hors agrément, financée par l'établissement** ; le soin remboursé passe **par les professionnels** (médecins pairs facturant en leur nom en téléconsultation conventionnelle ; psychologues Mon soutien psy), la plateforme étant adresseur et dossier partagé. L'agrément (modèle Éos) et le DM classe IIa sont des options de phase 2-3, à n'ouvrir que sur un périmètre clinique précis et avec financement (Grand Défi DMN santé mentale : 25 M€, vague 3 non annoncée).

---

## 5. Preuves chiffrées sourcées (source : `preuves-chiffrees.md`, complété par `marche-cliniques.md`)

| # | Chiffre | Détail | Source | Statut |
|---|---|---|---|---|
| 1 | **49 %** des médecins français : au moins un symptôme de burnout ; **5 %** sévère ; urgentistes 57 % | 37 études, 15 183 praticiens | Kansoun et al., *J Affect Disord* 2019;246:132-147 | SOLIDE |
| 2 | **SMR 1,44** (IC 1,16-1,72) suicide des médecins ; **1,90** chez les femmes | Méta-analyse mondiale, baisse en Europe | Dutheil et al., *PLOS ONE*, 12/12/2019 | SOLIDE (non français) |
| 3 | **23,7 %** d'idées suicidaires, 27,7 % dépression, 66,2 % anxiété, 3,4 % (ou 3,8 %) tentative | 21 768 jeunes médecins et étudiants, 2017 | ANEMF-ISNAR-ISNCCA-ISNI via Allo Docteurs, L'Étudiant | SOLIDE (déclaratif) |
| 4 | **21 %** d'idées suicidaires (12 mois), 66 % burnout | ISNI 2024, 8 307 réponses | L'Étudiant 2024 | SOLIDE (déclaratif) |
| 5 | **1 médecin et 1 infirmier sur 10** : pensées de mort ou d'automutilation (2 semaines) ; dépression 32 % vs 6 % | 29 pays, > 90 000 réponses | OMS/Europe MeND, 10/10/2025 | SOLIDE (OMS) |
| 6 | **35 %** des professionnels en mauvaise santé psychologique (2,5×) ; 34 % des médecins ont vécu un burn-out | 1 164 pros, mars 2025 | Odoxa–MNH | FRAGILE (sondage) |
| 7 | **Près d'1 infirmière hospitalière sur 2** a quitté l'hôpital ou changé de métier à 10 ans | Panel Insee 1989-2019 | DREES ER 1277, 24/08/2023 | SOLIDE |
| 8 | **10 %** d'abandon en 1re année d'IFSI (2021) vs 3 % (2011) | — | DREES ER 1266, mai 2023 | SOLIDE |
| 9 | Infirmiers : 57 % burnout / 43 % envisagent de quitter (2020) ; 29 % dans 12 mois (2022) | OpinionWay/ONI ; IFOP 2023 | ONI, IFOP | FRAGILE ; **aucun chiffre ONI 2024** |
| 10 | Absentéisme FHF **9,2 % (2024)**, pic 11,1 % (2022) | inclut maternité | FHF, Essentiel RH 2025 (URL à revalider) | SOLIDE (série) |
| 11 | **18,1 jours** d'absence santé/agent FPH (2022) ; 14,5 j FP vs 11,7 j privé | — | IGF/IGAS, juillet 2024 | FRAGILE (18,1 via presse) |
| 12 | Clariane **10,4 %** (2024) ; Ramsay France **12,8 %** (FY23) ; santé **7,22 %** vs 4,68 % (2025) | — | DEU/SASB ; People Scorecard ; APICIL–JLO | [E] / [E, à relire] / [I] |
| 13 | Intérim médical **147 M€** (2022), **559-662 M€** avec contrats courts ; jusqu'à 1 300 €/24 h | — | Cour des comptes, RALFSS 2024 | SOLIDE |
| 14 | Coût d'un départ d'IDE : **56 300 $** (2023), **61 110 $** (2024) ; 86 j de recrutement | 400 hôpitaux US | NSI via Becker's | SOLIDE (US) ; **France : INTROUVABLE** |
| 15 | Interventions anti-burnout : **SMD –0,29** ; organisationnel **–0,45** vs individuel **–0,18** | 19 études, 1 550 médecins | Panagioti, *JAMA Intern Med* 2017 | SOLIDE |
| 16 | 52 études, 3 630 médecins : effet réel, durabilité non établie | — | West, *Lancet* 2016 | SOLIDE |
| 17 | Schwartz Rounds : détresse **25 % → 12 %** chez les participants réguliers | ~500 agents, 8 mois, non randomisé | Maben, NIHR 2018 | SOLIDE |
| 18 | PHP US : **78 %** sans test positif sur 5 ans ; 72 % en exercice | 904 médecins, surveillance contractuelle | DuPont, *J Subst Abuse Treat* 2009 | SOLIDE (US, non transposable) |
| 19 | TCC numérique / burnout soignants : **effet non significatif** en méta-analyse | 4 études | Maldonado Ladino, 2023 | FRAGILE |
| 20 | ROI santé mentale au travail **4,2:1** (2017), 5:1 (2020), 5,3:1 (2022) | tous secteurs, UK | Deloitte | FRAGILE (cabinet) |
| 21 | **39,5 %** des médecins US hésitent à consulter par peur pour leur licence | n = 5 829 | Dyrbye, *Mayo Clin Proc* 2017 | SOLIDE (US) |
| 22 | **71 %** des médecins gênés de consulter un confrère | revue systématique | Kay, *BJGP* 2008 | SOLIDE |
| 23 | **80 %** des praticiens sans médecin traitant | campagne CFAR (~2017) | Allo Docteurs | FRAGILE |
| 24 | **71 %** des infirmiers ayant eu des idées suicidaires n'en ont parlé à personne ; 1 médecin sur 4 | 710 soignants | SPS via QdM | FRAGILE |
| 25 | Addictions : 10,9 % des anesthésistes (CFAR 2005) ; 10-15 % des médecins sur la carrière (FIDES 2017) | anciens | QdM ; CME AP-HP | FRAGILE ; **prévalence récente FR : INTROUVABLE** |
| 26 | SPS **~5 500 appels** (2025) ; NHS PH **6 339** inscriptions 2024/25, ~7 M£/an | — | infirmiers.com ; NHS PH ; Pulse | [E] (comptage et budget à vérifier) |
| 27 | ~2 400 EIGS/an ; 60 % des médecins confrontés | — | HAS via QdM ; SFAR 2020 | [I/presse] |
| 28 | MOTS : ~1 500 accompagnés (~2020-2021) ; 1 700+ (2026, client) ; ~13 % d'idées suicidaires parmi les médecins accompagnés | — | QdM ; CNOM 03/02/2025 ; client | FRAGILE (association) |

**Interdits sans vérification supplémentaire** : tout « chiffre ONI 2024 » ; un SMR suicide des infirmiers français ; une prévalence française récente d'addictions chez les soignants ; un coût par ETP de l'absentéisme ou un coût de remplacement d'une IDE en France ; un ROI « mesuré en hôpital français » ; un effet poolé positif de la TCC numérique ; un résultat français de télésurveillance en addictologie ; « 180 000 infirmiers ont quitté la profession » ; « Hospi-Up » ; « Zhang 2020 ».

---

## 6. État de l'art design (source : `design-etat-de-l-art.md`)

### 6.1 Références

- **Gentler Streak** (Apple Design Award 2024, Social Impact — vérifié sur developer.apple.com) : refus de la performance, « zone douce » qu'on quitte sans culpabilité, ton « optimiste et encourageant » plutôt que rappels insistants, vue mensuelle relative à son propre historique. **ADA 2025** : aucun lauréat santé (confirmé). **ADA 2026** : lauréats non confirmés.
- **Fast Company IBD 2025** : *855-HOW-TO-QUIT* — une idée de service, pas une interface. **Awwwards** : aucun « Site of the Day » clinique 2025-2026 ; la santé y est un angle mort.
- **How We Feel** (Yale) : la **couleur est le vocabulaire** (énergie × agréabilité), données sur l'appareil. **Oura** (refonte 20/10/2025) : couleur sémantique, serif italique sur une phrase-clé [E]. **Apple Vitals** : « typique / atypique » plutôt que chiffres bruts, critiqué pour « ne pas dire quoi faire ».
- **Abridge** (n° 1 Best in KLAS 2025) : la preuve vendue est **un chiffre signé par un établissement nommé** (UVM « –60 % de documentation hors horaires » ; Riverside « –55 % de burnout ») et **un taux de rétention** (« 95 %+ ») [E] ; adoption volontaire et bouche-à-oreille entre pairs (Cleveland Clinic, WVU), jamais de mandat ; page /clinicians organisée avant/pendant/après.

### 6.2 Faits mesurés utiles

- **« Quiet dark »** (KLAS) : rien ne s'allume en situation normale ; ~1 médecin sur 3 en burnout, plus de la moitié l'attribuant au DPI [I, enquête 216 organisations].
- **Glanceable** (JMIR mHealth 2026) : rappel moins bon mais utilité et focalisation supérieures ; l'abstrait doit ouvrir sur le chiffre (IASDR 2025).
- **Interruptions** : 4,4 à 12/h aux urgences (Westbrook 2010 : 6,6/h, 11 % des tâches) [I] → sessions < 60 s, état persistant, aucune modale.
- **Voix** : 40-100 % des événements captés en per-opératoire, 0-12 % en post-opératoire (Kyoto, JMIR AI 2026, 5 infirmières) → la voix capte, l'écran confirme.
- **Nuit** : la lumière bleue supprime la mélatonine, la rouge non (NIOSH, LRC) ; le rouge pur est inconfortable (Aalborg) → mode nuit **ambre**, pas noir.
- **Déconnexion** : retirer les apps de travail hors service réduit le stress (Michigan, J. Med. Systems, janv. 2026) → **conçu pour être fermé**.
- **Confiance** : premier facteur d'engagement pour 40,8 % ; l'adoption « plafonne ou chute brutalement après le lancement » (Wolters Kluwer, 2025).

### 6.3 Pièges

1. **Le bleu hôpital et la « mer de similitude »** (Creative Review ; NRC Health : 32 % de consommateurs « sans préférence ») ; en France, le vocabulaire des refontes de sites de cliniques date de 2015 (Elsan/Vitalia). 2. **L'esthétique wellness lisse** (lacs, couchers de soleil, pastel ; ~2 500 apps 2015-2021). 3. **Gamification** (revue 2019 : motivateurs extrinsèques ; Finch) — « pour un médecin en détresse, un oiseau à nourrir est une insulte ». 4. **Paternalisme et médicalisation** (Maturo 2016) — les soignants détectent instantanément la condescendance. 5. **Le score sans conséquence**.

### 6.4 Huit principes

1. Quiet dark par défaut, une seule information saillante. 2. Sessions de 40 s, reprenables, sans modale. 3. Conçu pour être fermé. 4. Mesure relative, jamais absolue ; chiffre brut en un tap. 5. Voix pour capter, écran pour confirmer. 6. Mode nuit ambre. 7. Preuve avant promesse. 8. Ton de pair, pas de coach : vocabulaire clinique assumé, pas de mascotte, pas de badge ; la couleur porte un sens.

### 6.5 Trois pistes de direction artistique

- **A. « Salle de garde »** : cockpit de nuit, anthracite chaud, un seul accent ambre, instruments plutôt qu'illustrations, grille serrée, pas de dégradé ; monospace humaniste pour les données, grotesque condensée pour les titres, chiffres tabulaires ; motion quasi nulle (anomalies à 1 Hz, fondus de 120 ms). Risque : austère ; mais « le seul monde que les soignants reconnaissent comme le leur ».
- **B. « Mood Meter »** : aplats saturés pleine page qui *sont* l'état du jour, aucune icône, pas de photo ; serif éditoriale en très grand corps, une phrase par écran ; couleur qui dérive lentement. Risque : « app bien-être de plus » si pastel.
- **C. « Fiche de liaison »** : bordereau, étiquette, tampon ; noir sur papier, un rouge ; une famille utilitaire ; motion mécanique. Risque : autodérision pouvant déplaire à une direction ou à l'Ordre.

Lacunes : lauréats 2026 ; shoulder surfing non recherché ; aucune étude sur le dark mode de nuit ni la typographie en santé ; interface Eos non décrite ; chiffres d'adoption tous vendeurs.

---

## 7. Vérification — verdicts des cinq relevés

**Conditions communes** : **0 requête WebSearch** et **toutes les tentatives WebFetch en échec** (DNS bloqué ou 403) sur les sources primaires. Verdicts fondés sur la cohérence interne, le croisement entre relevés et la connaissance antérieure des publications. **Aucune affirmation réfutée ; aucune recoupée contre une source indépendante lue ce jour.**

| Relevé | Requêtes (1re passe) | Confirmées | Nuancées (corrigées) | Réfutées | Invérifiables | Corrections notables |
|---|---|---|---|---|---|---|
| `eos-decode.md` | ≈ 30 | 0 | 1 | 0 | 11 | « 100 % Sécurité sociale » relu comme 70 % AMO + complémentaire ; date du CP Clariane à recouper ; « EOS Renaissance » inexistant |
| `marche-cliniques.md` | ≈ 35 | 0 | 2 | 0 | 10 | médecins du travail –16,5 % sur onze ans ; Lyra 900 M$ = cumul ; tension SPS « en hausse » vs 7 000 → 5 500 ; éligibilité CLACT du privé lucratif non uniforme |
| `reglementaire.md` | 25 | 1 (règle 11 RDM) | 3 | 0 | 9 | « Eos Renaissance = Cleer » retiré ; Eos relève de l'agrément, pas du DM ; accès direct Mon soutien psy : juin 2024 probable |
| `preuves-chiffrees.md` | 33 | 4 (Kansoun ; Dutheil ; Maben ; Dyrbye/Kay) | 4 | 0 | 5 | 3,4 % vs 3,8 % non tranché ; Cour des comptes = RALFSS 2024 ; sous-valeurs Panagioti dans l'article ; Deloitte 2017 = 4,2:1 |
| `design-etat-de-l-art.md` | 31 | 1 (ADA 2025) | 2 | 0 | 9 | Gentler Streak : « pas de rappels insistants » ; Chisholm 11,15/h non retrouvé |
| **Total** | ≈ 154 | **6** | **12** | **0** | **44** | — |

**À recouper en priorité dès que le réseau le permet** : 1) arrêté d'agrément Eos et liste officielle des sociétés agréées ; 2) lauréats vague 2 du Grand Défi (Cleer ou non) ; 3) poster Albatros 2025 (15 vs 30 min) et CP Clariane ; 4) règlements CLACT/QVCT 2026 ; 5) rapport NHS PH 2024/25 ; 6) communiqué Odoxa–MNH 2025 ; 7) DEU Clariane et People Scorecard Ramsay ; 8) décret 2026-626, arrêté forfaits du 14/09/2026, décret HDS du 24/03/2026 ; 9) bilan MOTS 2024-2025 et numéro officiel ; 10) palmarès design 2026.

---

## 8. Lacunes consolidées

- **Éos** : interface, palette, typographie non documentables ; tarif B2B ; résultats cliniques ; liste des 90 établissements.
- **MOTS** : bilan 2024-2025 (appels, financement, conventions ARS), numéro officiel, contenu d'OASIS, statut du DIU.
- **Marché** : turnover et postes vacants FHP 2024-2025 ; indicateurs RH Ramsay/Clariane 2025 ; contrats et prix des EAP en clinique ; fenêtres AAP ARS 2026 ; **coût d'un départ d'IDE en France** (à modéliser explicitement).
- **Réglementaire** : montants LATM 2026 ; parcours simplifiés Mon espace santé ; séances Mon soutien psy à distance ; plafond 20 % de téléconsultation ; seuil d'agrégation (DPO).
- **Preuves** : SMR suicide des infirmiers français ; addictions récentes chez les soignants français ; efficacité française de tout dispositif numérique pour soignants ; raisons chiffrées du non-recours en France.
- **Design** : shoulder surfing ; dark mode de nuit ; typographie en santé ; critique française de DA santé.

Le brief produit (`brief.md`) ne contient aucun chiffre absent de ce dossier et dit « à mesurer » partout où la preuve manque.
