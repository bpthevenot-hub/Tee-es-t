# MOTS — Refonte du site de l'Association MOTS (démonstration non officielle)

Restauration du chantier MOTS après la recréation du dépôt Tee-es-t
(réconciliation du 2026-10-08, qui a emporté l'ancienne branche).

## Contenu

| Dossier | Rôle |
|---|---|
| `apercu/MOTS-site.html` | Le site complet en UN fichier autonome : page de garde immersive + 12 pages navigables (routeur hash), section « Ce que dit la science » avec 4 études sourcées, hors-ligne. Vérifié Chromium (0 erreur JS, focus-trap, 0 requête externe). |
| `deploy/index.html` | Le même site enveloppé pour la production (doctype, `lang="fr"`, viewport, `noindex`). **Racine du projet Vercel `mots-redesign-demo`.** |

## Où vit le reste du chantier

- **Application Apple (SwiftUI iOS + macOS)** : `claude-macos-app/MOTS-App/` — mergée dans main (PR claude-macos-app#5). Le site embarqué (`Resources/MOTS-site.html`) est identique à `apercu/`.
- **Kit d'intégration léger (WKWebView)** : `claude-macos-app/MOTS-integration/` (PR #3, mergée).
- **Application web avancée « MOTS Companion »** (Next.js + Recharts + framer-motion, générée et testée par v0) : https://v0.app/bthevenot-bp/chat/mots-companion-application-avancee-mj2vsNQWnUW
- **Artifacts Claude** (liens vivants) : « MOTS — Site complet » et le hub « MOTS — 5 directions de refonte ».

## Perdu dans la réconciliation (régénérable)

- Le **source Next.js** du site (l'app qui générait `apercu/`) — le fichier autonome reste la référence fonctionnelle.
- Les 4 **déclinaisons stylistiques** (Édition Nuit, À hauteur d'humain, Evidence, Maison) et l'audit `AUDIT-ET-PLAN.md`.

## Faits et sources scientifiques (vérifiés)

- Ligne d'écoute MOTS : 06 08 28 25 89 (7 j/7, confidentielle) · prévention du suicide : **3114** (24 h/24, gratuit).
- Burnout 49 % : Kansoun et al., *J Affect Disord*, 2019 (méta-analyse, 37 études, 15 183 médecins).
- Suicide +44 % (SMR 1,44) : Dutheil et al., *PLOS ONE*, 2019 (méta-analyse, 25 études).
- Jeunes médecins (66,2 % anxiété, 27,7 % dépression, 23,7 % idées suicidaires) : enquête nationale 2017 (ANEMF · ISNAR-IMG · ISNCCA · ISNI, ≈ 22 000 répondants).
- L'accompagnement fonctionne : West et al., *The Lancet*, 2016.

> Démonstration non officielle, non affiliée à l'Association MOTS — site officiel : https://www.association-mots.org
