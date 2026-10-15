#!/bin/bash
# Enveloppe des hooks « vive mémoire » (Stop, UserPromptSubmit, SessionStart).
# Usage : bash vive-memoire-stop.sh [stop|prompt|debut]   (défaut : stop)
# Ne bloque jamais elle-même : seul vive_memoire.py décide, par un JSON sur stdout.
# Quand plusieurs copies reçoivent le même événement, une seule agit (verrou par événement,
# dans vive_memoire.py). L'enveloppe dit à vive_memoire.py laquelle elle est :
#   utilisateur  copie installée dans ~/.claude/hooks/vive-memoire
#   doublon      copie d'un dépôt alors qu'une installation utilisateur est enregistrée dans
#                ~/.claude/settings.json (hors cloud) : si celle-ci est d'avant le verrou
#                (≤ 3.5), elle seule agit ; sinon le verrou départage
#   depot        copie d'un dépôt, seule
mode="${1:-stop}"
entree=$(cat)
ici=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
config="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
utilisateur="$config/hooks/vive-memoire"
copie=depot
if [ -d "$utilisateur" ] && [ "$ici" = "$(CDPATH= cd -- "$utilisateur" && pwd)" ]; then
  copie=utilisateur
elif [ -z "${CLAUDE_CODE_REMOTE:-}" ] && [ -f "$utilisateur/vive_memoire.py" ] \
   && grep -qF "$utilisateur/vive-memoire-stop.sh" "$config/settings.json" 2>/dev/null; then
  copie=doublon
fi
[ -f "$ici/vive_memoire.py" ] || exit 0
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
  [ "$mode" = stop ] && printf '%s\n' '{"systemMessage":"Vive mémoire : python3 (3.8 ou plus) est introuvable, la synthèse de fin de discussion n'"'"'est pas vérifiée. macOS : xcode-select --install."}'
  exit 0
fi
printf '%s' "$entree" | VM_COPIE="$copie" VM_COPIE_UTILISATEUR="$utilisateur/vive_memoire.py" python3 -I "$ici/vive_memoire.py" "$mode"
exit 0
