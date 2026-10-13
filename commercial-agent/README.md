# Commercial Agent - L-FDS

Agent commercial autonome pour la gestion CRM HubSpot, l'envoi d'emails et la strategie de prospection.

## Prerequisites

1. **Python 3.12** (version du Dockerfile et du robot GitHub Actions ; 3.10+ fonctionne)
2. **Cle API Anthropic** : Creer un compte sur [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key
3. **Cle API HubSpot** : Settings → Integrations → Private Apps → Create private app
4. **Credentials Gmail API** : [Google Cloud Console](https://console.cloud.google.com) → APIs → Gmail API → Credentials

## Installation

```bash
cd commercial-agent
pip install -r requirements.txt
```

## Configuration

Copier le fichier `.env.example` en `.env` et remplir les valeurs :

```bash
cp .env.example .env
```

`.env`, `config/gmail_token.json` et `config/gmail_credentials.json` sont ignores par Git.

## Lancement

```bash
python main.py                    # mode interactif
python autonomous.py morning      # routine autonome (morning, followup, weekly_audit, email_prospection)
```

`autonomous.py` sort avec le code 1 si la routine echoue (erreur API, cle Anthropic absente,
routine inconnue, limite d'iterations) ; le rapport est quand meme ecrit dans `reports/`.

## Emplacements des fichiers

Tous les chemins sont resolus depuis la racine du projet (`config/paths.py`), quel que soit
le dossier depuis lequel on lance les scripts. Variables optionnelles :

| Variable | Contenu | Defaut |
|---|---|---|
| `AGENT_DATA_DIR` | `agent.log`, `reports/`, `livrables/` | racine du projet |
| `AGENT_STATUS_FILE` | statut du site (`update_status.py`) | `../docs/status.json` (racine du site dans Tee-es-t) |
| `GMAIL_TOKEN_PATH` | token Gmail autorise | `config/gmail_token.json` |
| `GMAIL_CREDENTIALS_PATH` | client OAuth Gmail | `config/gmail_credentials.json` |

## Gmail en mode autonome (cron, CI, cloud)

L'autorisation Gmail demande un navigateur : elle se fait une fois, en local, avec
`python setup_gmail.py`. Fournir ensuite le token a l'environnement non interactif, soit via
`GMAIL_TOKEN_JSON` (contenu de `config/gmail_token.json`), soit via le fichier token.

Sans token valide, les outils Gmail renvoient une erreur explicite au lieu d'attendre un
navigateur (avant, la routine restait bloquee jusqu'au timeout du job).

`GITHUB_TOKEN` est lu en priorite ; `GH_TOKEN` est utilise s'il est vide.

## Structure

```
commercial-agent/
├── main.py              # Point d'entree interactif
├── autonomous.py        # Point d'entree cron (routines)
├── agent_loop.py        # Boucle agent partagee
├── update_status.py     # Statut du site apres une routine
├── setup_gmail.py       # Autorisation Gmail (navigateur, une fois)
├── config/
│   ├── paths.py         # Emplacements des fichiers
│   ├── routines.py      # Prompts des routines autonomes
│   └── system_prompt.py # Prompt systeme de l'agent
├── tools/
│   ├── __init__.py
│   ├── hubspot.py       # Outils CRM HubSpot
│   ├── gmail.py         # Outils Gmail
│   ├── notion.py        # Outils Notion
│   ├── github_tools.py  # Outils GitHub
│   └── livrables.py     # Devis et propositions
├── tests/
├── requirements.txt
└── .env.example
```
