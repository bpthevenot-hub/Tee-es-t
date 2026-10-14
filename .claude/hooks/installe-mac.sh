#!/bin/bash
# Installe la mémoire vive au niveau UTILISATEUR (toutes les sessions locales du Mac,
# quel que soit le dossier ouvert) : hooks Stop / UserPromptSubmit / SessionStart dans
# ~/.claude/settings.json et skill vive-memoire dans ~/.claude/skills/.
# Idempotent ; sauvegarde ~/.claude/settings.json avant de l'écrire.
#   bash installe-mac.sh              installer ou mettre à jour
#   bash installe-mac.sh --retirer    tout retirer (les sauvegardes restent)
# Rappel (doc Claude Code) : les réglages utilisateur ne sont PAS lus par les sessions
# cloud ; en cloud, la consigne vient des CLAUDE.md (et des hooks d'un dépôt unique).
set -e
ici=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
skill_src="$ici/../skills/vive-memoire"
[ -f "$skill_src/SKILL.md" ] || skill_src="$ici/../../docs/context/skills/vive-memoire"
cible_hooks="$HOME/.claude/hooks/vive-memoire"
cible_skill="$HOME/.claude/skills/vive-memoire"
reglages="$HOME/.claude/settings.json"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || { echo "python3 3.8+ requis (macOS : xcode-select --install)"; exit 1; }
mkdir -p "$HOME/.claude"
[ -f "$reglages" ] && cp "$reglages" "$reglages.avant-vive-memoire.$(date +%Y%m%d%H%M%S)"
if [ "${1:-}" = "--retirer" ]; then
  rm -f "$cible_hooks"/vive_memoire.py "$cible_hooks"/vive-memoire-stop.sh "$cible_hooks"/vive-memoire-prompt.sh
  rmdir "$cible_hooks" 2>/dev/null || true
else
  mkdir -p "$cible_hooks" "$cible_skill"
  cp "$ici/vive_memoire.py" "$ici/vive-memoire-stop.sh" "$ici/vive-memoire-prompt.sh" "$cible_hooks/"
  for f in SKILL.md bilan-template.html genere-bilan.py teste-bilan.mjs; do
    [ -f "$skill_src/$f" ] && cp "$skill_src/$f" "$cible_skill/"
  done
fi
python3 - "$reglages" "$cible_hooks" "${1:-}" <<'PYEOF'
import json, sys
from pathlib import Path
reglages, cible, mode = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
s = json.loads(reglages.read_text(encoding='utf-8')) if reglages.exists() and reglages.read_text().strip() else {}
h = s.setdefault('hooks', {})
for evt in ('Stop', 'UserPromptSubmit', 'SessionStart'):
    h[evt] = [e for e in h.get(evt, []) if 'vive-memoire' not in json.dumps(e)]
if mode != '--retirer':
    cmd = 'bash "' + cible + '/vive-memoire-stop.sh" '
    h['Stop'].append({'matcher': '', 'hooks': [{'type': 'command', 'command': cmd + 'stop', 'timeout': 30}]})
    h['UserPromptSubmit'].append({'matcher': '', 'hooks': [{'type': 'command', 'command': cmd + 'prompt', 'timeout': 10}]})
    h['SessionStart'].append({'matcher': 'startup|resume|clear', 'hooks': [{'type': 'command', 'command': cmd + 'debut', 'timeout': 10}]})
for evt in list(h):
    if not h[evt]:
        del h[evt]
reglages.write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(('Retiré de ' if mode == '--retirer' else 'Installé dans ') + str(reglages))
PYEOF
