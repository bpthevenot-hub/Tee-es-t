# Tee-es-t — SNB Consulting monorepo

Monorepo opérationnel de [SNB Consulting](https://snbbm-consulting.com) et de ses
side-projects. Chaque sous-dossier est un système autonome orienté vers un
résultat business concret : automatisation, lead generation, produit déployable.

## Sous-projets

| Dossier              | Stack                     | Rôle business                                           | État          |
| -------------------- | ------------------------- | ------------------------------------------------------- | ------------- |
| `commercial-agent/`  | Python + Claude Agent SDK | Agent commercial autonome (Gmail + HubSpot + Notion)    | **En prod**   |
| `studentflow/`       | Python 3.11 + FastAPI     | Matching temps-réel jobs ↔ étudiants (produit SaaS)     | **MVP**       |
| `docs/`              | HTML statique             | Page publique "statut du robot" (Netlify)               | En prod       |
| `daleme-scoop-2.html`| HTML + CSS                | Article one-shot (désaligné du reste, à archiver)       | Legacy        |

## Systèmes en production

### Robot commercial (`commercial-agent/`)
Agent autonome qui tourne toutes les 10 minutes via GitHub Actions
(`.github/workflows/robot.yml`) et opère trois routines :

- **morning** — traite les emails Gmail non-lus, rédige des brouillons, liste les
  contacts HubSpot à relancer, génère devis/propositions
- **followup** — relance les prospects OPEN non-répondus (3j / 7j / 14j)
- **weekly_audit** — audit CRM hebdomadaire (vendredi PM), KPIs, actions correctives

Les outils (`commercial-agent/tools/`) exposent HubSpot, Gmail, Notion, GitHub
et un générateur de livrables au modèle Claude via le pattern tool-use.
Les résultats sont publiés sur `docs/status.json` et commités à chaque run.

#### Secrets GitHub Actions

Pour activer le robot, ajouter les secrets dans **Settings → Secrets and variables
→ Actions → New repository secret** du dépôt qui exécute le workflow
([ouvrir les secrets Actions](https://github.com/bpthevenot-hub/Tee-es-t/settings/secrets/actions)).
Les deux secrets obligatoires vérifiés par le workflow sont :

- `ANTHROPIC_API_KEY`
- `HUBSPOT_API_KEY`

Pour activer également les intégrations Gmail et Notion, ajouter
`GMAIL_CREDENTIALS_JSON` et `NOTION_API_KEY`. `GITHUB_TOKEN` est fourni
automatiquement par GitHub Actions. Ne jamais mettre les valeurs des clés dans
le dépôt, un fichier versionné ou un commit. Après leur ajout, lancer le
workflow depuis l'onglet **Actions** avec `configuration_only` coché pour
vérifier leur présence.

### Page de statut (`docs/`)
Déployée via Netlify (`netlify.toml`) — lecture seule, mise à jour par le robot
à chaque exécution.

## Systèmes en développement

### StudentFlow (`studentflow/`)
Marketplace de jobs étudiants temps-réel. Trois agents Python autonomes
(scraper / matcher / notifier) + API FastAPI + schéma Supabase.

- **23/23 tests passent**, moteur de matching pur testé en isolation
- Scraper **France Travail** fonctionnel (API publique OAuth2)
- 4 autres scrapers en stubs documentés (Indeed, HelloWork, StudentJob, JobTeaser)
- Fallback in-memory : `cd studentflow && make run-api` démarre sans aucune dépendance externe

Voir [`studentflow/README.md`](./studentflow/README.md) et
[`studentflow/CLAUDE.md`](./studentflow/CLAUDE.md) pour le détail.

## Conventions transverses

- **Python** : 3.11+, type hints, Pydantic v2, ruff pour lint/format
- **Commits** : conventionnels (`feat:`, `fix:`, `refactor:`, `docs:`, `ci:`)
- **Branches** : `claude/<slug>` pour le travail piloté par Claude Code
- **Secrets** : jamais commiter de `.env`, toujours un `.env.example`
- **CI** : `.github/workflows/studentflow-ci.yml` pour StudentFlow, `robot.yml`
  pour le robot commercial

## Pour Claude Code

Le fichier [`CLAUDE.md`](./CLAUDE.md) à la racine définit la posture attendue :
ingénieur senior + opérateur business, jamais un simple assistant passif.
Chaque sous-projet qui le mérite a son propre `CLAUDE.md` avec l'architecture
détaillée — consulte-les avant toute modification.

## Licence

Apache-2.0 — voir [`LICENSE`](./LICENSE).
