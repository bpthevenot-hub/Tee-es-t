#!/bin/bash
# Hook Stop « vive mémoire » : impose la synthèse de fin de discussion
# (skill vive-memoire) pour toute session substantielle, quel que soit le
# modèle. Bloque la fin de tour (exit 2) avec la consigne et l'identifiant
# de session à tamponner ; se tait dès que le tampon correspond.
#
# Entrée : JSON Claude Code sur stdin (session_id, transcript_path,
# stop_hook_active, cwd). Tampon : .claude/.vive-memoire.stamp
# (« <session_id> <nb_messages> »), non versionné.

input=$(cat)

# Recursion : Claude vient de répondre à ce hook → on laisse terminer.
if [[ "$(echo "$input" | jq -r '.stop_hook_active // false')" == "true" ]]; then
  exit 0
fi

session_id=$(echo "$input" | jq -r '.session_id // empty')
transcript=$(echo "$input" | jq -r '.transcript_path // empty')
[[ -z "$session_id" || ! -f "$transcript" ]] && exit 0

# Racine du projet : celle que Claude Code annonce, sinon le dépôt git courant.
if [[ -n "$CLAUDE_PROJECT_DIR" && -d "$CLAUDE_PROJECT_DIR" ]]; then
  racine="$CLAUDE_PROJECT_DIR"
else
  racine=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi
mkdir -p "$racine/.claude" 2>/dev/null
stamp="$racine/.claude/.vive-memoire.stamp"
SEUIL_MIN=4      # messages de Baptiste avant d'exiger une synthèse
SEUIL_REFRESH=8  # nouveaux messages depuis la dernière synthèse

# Nombre de vrais messages utilisateur (texte, pas les résultats d'outils).
nb=$(python3 -I - "$transcript" <<'EOF'
import json, sys
# Entrées techniques à ne pas compter : notifications, commandes locales,
# rappels système, résumé de reprise, légendes d'images.
TECHNIQUE = ('<task-notification>', '<local-command', '<command-name>', '<command-message>',
             '<system-reminder>', '[Image:', '[SYSTEM NOTIFICATION', 'Continue from where you left off')
n = 0
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try:
        o = json.loads(line)
    except ValueError:
        continue
    if o.get("type") != "user" or o.get("isMeta") or o.get("isCompactSummary"):
        continue
    c = (o.get("message") or {}).get("content")
    texte = ""
    if isinstance(c, str):
        texte = c
    elif isinstance(c, list):
        texte = next((x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text" and x.get("text", "").strip()), "")
    texte = texte.strip()
    if texte and not texte.startswith(TECHNIQUE):
        n += 1
print(n)
EOF
)
nb=${nb:-0}
(( nb < SEUIL_MIN )) && exit 0

if [[ -f "$stamp" ]]; then
  read -r stamp_session stamp_nb < "$stamp"
  if [[ "$stamp_session" == "$session_id" ]] && (( nb - ${stamp_nb:-0} < SEUIL_REFRESH )); then
    exit 0
  fi
fi

cat >&2 <<EOF
Vive mémoire : cette discussion compte $nb demandes de Baptiste et aucune synthèse récente.
Avant de terminer, exécute la skill « vive-memoire » (si elle n'est pas chargée : lire
claude-macos-app/docs/context/skills/vive-memoire/SKILL.md) — compte rendu de session, décisions D-xxx,
backlog, skills à faire grossir, ponts IA, bilan interactif publié, commit + push), puis écris
« $session_id $nb » dans $stamp
EOF
exit 2
