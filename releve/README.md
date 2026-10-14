# Relève — la clinique digitale du soignant (démonstration)

Proposition de produit de SNB Consulting : une clinique digitale **vendue à
l'établissement**, soignée par des **pairs** (réseau MOTS, DIU « Soigner les
soignants »), **conçue pour la garde**, qui ne remonte à la direction que des
**agrégats** sous seuil. Modèle d'inspiration : Eos Care (clinique digitale
d'addictologie). Transposable à l'association MOTS « sous une autre forme ».

| Dossier | Contenu |
|---|---|
| `docs/brief.md` | **Le brief produit & design** (thèse, nom, parcours en 5 étapes, 3 espaces, 5 innovations, faits autorisés, direction artistique « Salle de garde », interdits) |
| `docs/dossier.md` | Dossier de recherche consolidé, avec vérification |
| `docs/eos-decode.md` · `marche-cliniques.md` · `reglementaire.md` · `preuves-chiffrees.md` · `design-etat-de-l-art.md` | Les cinq relevés d'origine (13 octobre 2026) |
| `site/` | Le site / la démo Next.js 15 (App Router, React 19, Tailwind v4) |

## Lancer

```bash
cd releve/site && npm ci && npm run dev   # http://localhost:3000
npm run build                              # pages statiques
```

Déploiement : Vercel, projet `releve` (équipe `bthevenot-bp`), **Root Directory = `releve/site`**.

## Garde-fous (non négociables, repris dans l'interface)

Anonymat structurel vis-à-vis de l'employeur (pas de connexion RH, agrégats seuls, seuil ≥ 10), consentement révocable, aucun signalement nominatif, le 3114 sur chaque écran, V1 hors dispositif médical et hors agrément : l'outil ne dépiste pas, ne diagnostique pas, ne recommande pas. Aucune donnée réelle, aucune collecte dans la démo.
