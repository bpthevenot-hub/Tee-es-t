---
name: refonte-site
description: Construire, refondre ou décliner un site de démonstration de bout en bout et le mettre en ligne — « refais ce site », « clone amélioré », « déclinaisons », « nouveau design et déploie », « page de garde », « mets-le sur Vercel ». Pipeline éprouvé trois fois (MOTS juillet 2026, MOTS octobre 2026, Relève octobre 2026) : faits uniques, brief imposé, agents en parallèle, banc Chromium, revue à trois regards, déploiement Vercel d'un sous-dossier du monorepo.
---

# Refonte / construction de site

Baptiste veut un résultat **visible, en ligne, vérifié** — pas un plan. Il donne une intention en une phrase (« quelque chose d'hyper innovant pour les cliniques », « 4-5 versions complètement différentes ») et un mandat d'autonomie. Cette skill transforme l'intention en site déployé sans redemander.

## 1. Avant d'écrire une ligne

1. **Faits** : un seul fichier de faits (`FACTS-*.md` ou `lib/faits.ts`) — chaque chiffre avec sa source et son URL ; ce qui n'est pas sourcé est marqué « à mesurer » ; liste explicite des **chiffres interdits** (réfutés, invérifiables, trompeurs). Recherche : `WebSearch` multi-angles (le `WebFetch` du conteneur cloud est souvent bloqué), puis réfutation adversariale.
2. **Brief** (≤ 3 pages) : thèse en une phrase, promesses par public, parcours, écrans, innovations assumées, **direction artistique imposée** (palette en tokens, typographies, motion, ton), **lexique interdit**, transposition éventuelle (ex. « proposer à MOTS sous une autre forme »).
3. **Écrire tôt dans le dépôt** (`<projet>/docs/`) : le contexte peut être compacté, un fichier commité survit.

## 2. Socle

- Next.js 15.5.20 / React 19.2.7 / Tailwind 4.3.2 (`@theme`, tokens CSS), build statique — même socle que `mots-redesign/site` et `releve/site` : copier leur `package.json`, `next.config.mjs` (`outputFileTracingRoot`, en-têtes `noindex`/`nosniff`/`DENY`), `postcss.config.mjs`.
- Fondations d'abord (tokens, layout, header avec menu mobile `aria-controls="menu-mobile"`, footer, lien d'évitement, `robots.ts` qui interdit tout pour une démo, icône SVG, `lib/` de données) → build + `tsc --noEmit` verts **avant** de lancer les agents.
- Démo santé : 3114 sur chaque écran, bandeau « démonstration · données fictives », aucune promesse médicale, non-affiliation affichée.

## 3. Construction en parallèle (Workflow, si Baptiste a ouvert l'orchestration)

- Un agent par page ou par écran, chacun avec le brief, les fichiers de fondation à **ne pas modifier**, et les attributs de test attendus (`data-quadrant`, `data-mode-couloir`…).
- Puis intégration (build, `tsc`, `next start -p 39xx`, banc), revue à **trois regards** — banc Chromium, audit des faits contre les sources, revue visuelle sur captures — et boucle de corrections (3 tours max) jusqu'à zéro défaut bloquant.
- Piège : dans un script de workflow, **pas d'accent grave à l'intérieur d'un template literal** (le parseur échoue) ; concaténer les chaînes dynamiques.
- Sans orchestration : mêmes étapes, en séquence.

## 4. Banc de vérification — `verifie-site.mjs` (dans ce dossier)

```bash
cd <site> && npm run build && (npx next start -p 3921 &) && sleep 3
node .claude/skills/refonte-site/verifie-site.mjs http://localhost:3921 /tmp/captures
```

Vérifie par route : HTTP 200, 3114, bandeau démonstration, lexique interdit, emoji, chiffres interdits, un seul `h1`, `alt`, noms accessibles ; puis lien d'évitement au premier Tab, débordement à 390 px, menu mobile (ouverture/fermeture), interactions propres au site, `prefers-reduced-motion`, **zéro requête externe**, **zéro erreur JS**. Sortie JSON `{ ok, defauts[], mesures, captures[] }`. Adapter `ROUTES`, `INTERDITS`, `CHIFFRES_INTERDITS` et le bloc d'interaction au site. Chromium : `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` ; Playwright : `/opt/node22/lib/node_modules/playwright/index.mjs`. **Regarder les captures** avant de déclarer fini.

## 5. Mise en ligne — sous-dossier du monorepo sur Vercel (équipe `bthevenot-bp`)

1. Committer et pousser la branche (jamais `main` sur Tee-es-t).
2. `create_project` : `name`, `framework: nextjs`, `rootDirectory: <projet>/site`, `gitRepository: { type: github, repo: bpthevenot-hub/Tee-es-t }`.
3. `create_deployment` : `gitSource { type: github, org: bpthevenot-hub, repo: Tee-es-t, ref: <branche> }`, `target: production`, `project: <nom>`.
4. Suivre l'état (`get_deployment`) et les journaux de build (`list_deployment_events`) jusqu'à `READY` ; vérifier la prod avec `web_fetch_vercel_url` (le réseau du conteneur ne l'atteint pas toujours).
5. Domaine `<nom>.snb.center` avec `add_project_domain` s'il ne coûte rien ; jamais d'achat.

## 6. Livrer

PR (draft) mise à jour, lien de prod, captures, `README.md` du projet (provenance, lancement, garde-fous), entrée D-xxx et bilan interactif via la skill `vive-memoire`.

## Variante « déclinaisons »

Pour N directions stylistiques d'un même site : un fichier autonome par déclinaison (HTML + CSS inline, zéro ressource externe), même fichier de faits, brief DA distinct par direction, même banc, revue à trois regards par déclinaison, puis hub d'artifacts. Référence : `mots-redesign/declinaisons/` et son README.
