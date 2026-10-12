# MOTS — Refonte du site de l'Association MOTS (démonstration non officielle)

Chantier complet de la refonte : le site Next.js (source restauré), sa version
autonome en un fichier, et quatre déclinaisons stylistiques.

## Contenu

| Dossier | Rôle |
|---|---|
| `site/` | **Le source Next.js 15** (App Router, React 19, Tailwind v4) : page de garde immersive, 12 routes statiques, section « Ce que dit la science ». C'est ce qui tourne en production sur https://mots-redesign-demo.snb.center. |
| `apercu/MOTS-site.html` | Le même site en UN fichier autonome (routeur hash, hors-ligne) — embarqué tel quel dans l'application Apple. |
| `deploy/index.html` | Le fichier autonome enveloppé pour un hébergement statique (doctype, `lang="fr"`, `noindex`). |
| `declinaisons/` | Quatre directions artistiques complètes, chacune en un fichier autonome : **Édition Nuit** (magazine nocturne), **À hauteur d'humain** (chaleureuse), **Evidence** (revue scientifique), **Maison** (prestige à la française). |

## Lancer le site

```bash
cd mots-redesign/site
npm ci
npm run dev      # http://localhost:3000
npm run build    # 17 pages statiques
```

Déploiement : projet Vercel `mots-redesign-demo` (équipe `bthevenot-bp`), framework Next.js, **Root Directory = `mots-redesign/site`**.

## Provenance du source (`site/`)

Le source avait été perdu lors de la réinitialisation du dépôt (2026-10-08). Il a été
restauré depuis le **déploiement Vercel de production** `dpl_4VGueSVcHBpypVy9UtsEq5ztyj5s`
(créé en CLI : Vercel conserve l'arborescence des sources, chaque fichier identifié par son SHA-1).

| Origine | Fichiers | Fidélité |
|---|---|---|
| API Vercel (fichiers < ~1,5 Ko) | 14 | identiques à l'octet (SHA-1 vérifié) |
| Historique de session (lectures + éditions rejouées) | 4 | identiques à l'octet (SHA-1 vérifié) |
| Reconstruction tombée exactement sur l'empreinte | 1 (`LiteYouTube.tsx`) | identique à l'octet (SHA-1 vérifié) |
| Reconstruction (l'API tronque au-delà de ~1,5 Ko) | 13 + `package-lock.json` | rendu identique à la prod |
| Reconstruction (arborescence tronquée par l'API) | 2 (`lassociation/lequipe`, `lassociation/notre-histoire`) | rendu identique à la prod |

Les fichiers reconstruits reprennent leurs ~1 450 premiers octets exacts et suivent la
vérité de production : payload RSC et DOM pré-rendu de chaque page, CSS et JS compilés.
**Preuves** : le build local produit un CSS **identique octet pour octet** à la prod
(même SHA-1, même nom haché `79f4596a20fdeb96.css`) et un DOM pré-rendu identique sur
les **12 routes** ; `tsc` sans erreur ; interactions vérifiées sous Playwright (page de
garde, menu mobile, façade YouTube, accordéon FAQ). Ce qui peut différer de l'original
ne change pas le rendu : retours à la ligne, commentaires, noms de variables locales.

## Où vit le reste du chantier

- **Application Apple (SwiftUI iOS + macOS)** : `claude-macos-app/MOTS-App/` — le site embarqué (`Resources/MOTS-site.html`) est identique à `apercu/`.
- **Kit d'intégration léger (WKWebView)** : `claude-macos-app/MOTS-integration/`.
- **Application web avancée « MOTS Companion »** (Next.js + Recharts + framer-motion, générée et testée par v0) : https://v0.app/bthevenot-bp/chat/mots-companion-application-avancee-mj2vsNQWnUW
- **Hub des directions** (artifact Claude) : https://claude.ai/artifact/SDKLzPMze23DZuAcf5QvPc
- **Déclinaisons en ligne** (artifacts Claude, privés) : [Édition Nuit](https://claude.ai/artifact/Qx9cJCu1PT4b4WQHgaLrYZ) · [À hauteur d'humain](https://claude.ai/artifact/SZY2K1AJq47HZzekmpx3f4) · [Evidence](https://claude.ai/artifact/8mmgq1Z7gxwXxcXhbHjbyZ) · [Maison](https://claude.ai/artifact/7GMCoyxyCKaNCoPbDkJ2yV)

## Faits et sources scientifiques (vérifiés)

- Ligne d'écoute MOTS : 06 08 28 25 89 (7 j/7, confidentielle) · prévention du suicide : **3114** (24 h/24, gratuit).
- Burnout 49 % : Kansoun et al., *J Affect Disord*, 2019 (méta-analyse, 37 études, 15 183 médecins).
- Suicide +44 % (SMR 1,44) : Dutheil et al., *PLOS ONE*, 2019 (méta-analyse, 25 études).
- Jeunes médecins (66,2 % anxiété, 27,7 % dépression, 23,7 % idées suicidaires) : enquête nationale 2017 (ANEMF · ISNAR-IMG · ISNCCA · ISNI, ≈ 22 000 répondants).
- L'accompagnement fonctionne : West et al., *The Lancet*, 2016.

> Démonstration non officielle, non affiliée à l'Association MOTS — site officiel : https://www.association-mots.org
