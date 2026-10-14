#!/bin/bash
# Enveloppe des hooks « vive mémoire » (Stop, UserPromptSubmit, SessionStart).
# Usage : bash vive-memoire-stop.sh [stop|prompt|debut]   (défaut : stop)
# Ne bloque jamais elle-même : seul vive_memoire.py décide, par un JSON sur stdout.
# Si l'installation utilisateur du Mac est en place (fichiers ET enregistrement dans
# ~/.claude/settings.json, hors cloud où ce fichier n'est pas lu), la copie du dépôt se tait
# pour ne pas compter deux fois.
mode="${1:-stop}"
entree=$(cat)
ici=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
utilisateur="$HOME/.claude/hooks/vive-memoire"
if [ -z "${CLAUDE_CODE_REMOTE:-}" ] && [ -f "$utilisateur/vive_memoire.py" ] \
   && grep -qF "$utilisateur/vive-memoire-stop.sh" "$HOME/.claude/settings.json" 2>/dev/null \
   && [ "$ici" != "$(cd "$utilisateur" && pwd)" ]; then exit 0; fi
[ -f "$ici/vive_memoire.py" ] || exit 0
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
  [ "$mode" = stop ] && printf '%s\n' '{"systemMessage":"Vive mémoire : python3 (3.8 ou plus) est introuvable, la synthèse de fin de discussion n'"'"'est pas vérifiée. macOS : xcode-select --install."}'
  exit 0
fi
printf '%s' "$entree" | python3 -I "$ici/vive_memoire.py" "$mode"
exit 0
