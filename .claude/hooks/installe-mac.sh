#!/bin/bash
# Installe la mémoire vive au niveau UTILISATEUR (toutes les sessions locales du Mac,
# quel que soit le dossier ouvert) : hooks Stop / UserPromptSubmit / SessionStart dans
# ~/.claude/settings.json et skill vive-memoire dans ~/.claude/skills/.
# Idempotent ; sauvegarde ~/.claude/settings.json avant de l'écrire (écriture atomique, lien
# symbolique respecté) ; ne touche qu'à ses propres commandes.
#   bash installe-mac.sh              installer ou mettre à jour
#   bash installe-mac.sh --retirer    tout retirer (les sauvegardes restent)
# Rappel (doc Claude Code) : les sessions cloud hébergées par Anthropic ne lisent PAS les
# réglages utilisateur ; en cloud, la consigne vient des CLAUDE.md (et des hooks d'un dépôt unique).
set -e
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--retirer" ]; }; then
  echo "Usage : bash installe-mac.sh [--retirer]   (rien n'a été modifié)"; exit 1
fi
ici=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [ -n "${CLAUDE_CODE_REMOTE:-}" ]; then
  echo "Session cloud : ~/.claude/settings.json n'y est pas lu, l'installation serait sans effet."; exit 1
fi
skill_src=""
# Dépôt (hooks/ + skills/ ou docs/context/skills/) ou copie installée (~/.claude/hooks/vive-memoire + ~/.claude/skills/).
for c in "$ici" "$ici/../skills/vive-memoire" "$ici/../../docs/context/skills/vive-memoire" "$ici/../../skills/vive-memoire"; do
  if [ -f "$c/SKILL.md" ]; then skill_src="$c"; break; fi
done
if [ -z "$skill_src" ] && [ "${1:-}" != "--retirer" ]; then
  echo "Skill vive-memoire introuvable à côté de ce script ; rien n'a été installé."; exit 1
fi
config="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$config"
config=$(CDPATH= cd -- "$config" && pwd)      # chemin absolu : les hooks tournent depuis n'importe quel dossier
cible_hooks="$config/hooks/vive-memoire"
cible_skill="$config/skills/vive-memoire"
reglages="$config/settings.json"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || { echo "python3 3.8+ requis (macOS : xcode-select --install)"; exit 1; }
# Ordre sûr : réglages vérifiés d'abord ; à l'installation, fichiers ensuite (préparés puis
# vérifiés), enregistrement en dernier ; au retrait, enregistrement retiré d'abord, fichiers
# ensuite. Jamais de commande vers un fichier absent.
installer_fichiers() {
  prep="$config/hooks/.vive-memoire-prep.$$"      # même disque que la cible : renommage atomique
  rm -rf "$prep"; mkdir -p "$prep/hooks" "$prep/skill"
  cp "$ici/vive_memoire.py" "$ici/vive-memoire-stop.sh" "$ici/vive-memoire-prompt.sh" "$ici/installe-mac.sh" "$prep/hooks/"
  for f in SKILL.md bilan-template.html genere-bilan.py teste-bilan.mjs; do
    if [ -f "$skill_src/$f" ]; then cp "$skill_src/$f" "$prep/skill/"; fi
  done
  [ -s "$prep/hooks/vive_memoire.py" ] && [ -s "$prep/hooks/vive-memoire-stop.sh" ] && [ -s "$prep/skill/SKILL.md" ] \
    || { rm -rf "$prep"; echo "Copie incomplète ; rien n'a été installé."; exit 1; }
  # Remplacement d'un bloc : chaque dossier préparé prend la place de l'installé par renommage (même
  # disque), avec retour à l'ancien en cas d'échec ; jamais de copie à moitié faite sous des hooks enregistrés.
  mkdir -p "$config/hooks" "$config/skills"
  echanger "$prep/hooks" "$cible_hooks" && echanger "$prep/skill" "$cible_skill" \
    || { rm -rf "$prep"; echo "Remplacement impossible ; l'installation précédente est restée en place."; exit 1; }
  rm -rf "$prep"
}
echanger() {   # echanger <dossier préparé> <dossier installé>
  if [ -d "$2" ]; then
    cp -Rn "$2/." "$1/" 2>/dev/null || true      # fichiers ajoutés à la main : gardés (les nôtres priment)
    mv "$2" "$2.ancien.$$" || return 1
  fi
  if mv "$1" "$2"; then
    rm -rf "$2.ancien.$$"
  else
    if [ -d "$2.ancien.$$" ]; then mv "$2.ancien.$$" "$2"; fi
    return 1
  fi
}
enregistrer() {
python3 - "$reglages" "$cible_hooks" "${1:-}" <<'PYEOF'
import json, os, re, shlex, stat, sys, tempfile
from pathlib import Path
reglages, cible, mode = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
EVTS = ('Stop', 'UserPromptSubmit', 'SessionStart')
# Nos commandes : un de nos deux scripts, quel que soit son dossier, suivi au plus d'un de nos modes.
# Une commande voisine qui contient seulement « vive-memoire » (ex. ~/bin/vive-memoire-audit) reste.
def notre(commande):
    """Une de nos commandes : bash <…>/vive-memoire-stop.sh|prompt.sh [stop|prompt|debut], quelle que soit la citation."""
    try:
        mots = shlex.split(str(commande or ''))
    except ValueError:
        return False
    if mots and mots[0] == 'bash':
        mots = mots[1:]
    return 1 <= len(mots) <= 2 and bool(re.search(r'(^|/)vive-memoire-(stop|prompt)\.sh$', mots[0])) \
        and (len(mots) == 1 or mots[1] in ('stop', 'prompt', 'debut'))
texte = reglages.read_text(encoding='utf-8') if reglages.exists() else ''
try:
    s = json.loads(texte) if texte.strip() else {}
except ValueError as e:
    sys.exit(f'{reglages} n\'est pas du JSON valide ({e}) : Claude Code l\'ignore. Corrige-le puis relance ; rien n\'a été modifié.')
h = s.get('hooks', {}) if isinstance(s, dict) else None
if not isinstance(h, dict) or any(not isinstance(h.get(e, []), list) for e in EVTS) \
        or any(isinstance(g, dict) and not isinstance(g.get('hooks', []), list) for e in EVTS for g in h.get(e, [])):
    sys.exit(f'{reglages} : forme inattendue (réglages, « hooks », événements ou groupes) ; rien n\'a été modifié.')
if mode == 'verifier':
    sys.exit(0)
s['hooks'] = h
for evt in EVTS:
    groupes = []
    for g in h.get(evt, []):     # ne retirer que nos commandes ; tout le reste est gardé tel quel
        if isinstance(g, dict) and isinstance(g.get('hooks'), list):
            avant = len(g['hooks'])
            g['hooks'] = [x for x in g['hooks'] if not (isinstance(x, dict) and notre(x.get('command', '')))]
            if avant and not g['hooks']:
                continue
        groupes.append(g)
    h[evt] = groupes
if mode != '--retirer':
    cmd = 'bash ' + shlex.quote(cible + '/vive-memoire-stop.sh') + ' '     # $, " ou espace dans le chemin : sans danger
    h['Stop'].append({'matcher': '', 'hooks': [{'type': 'command', 'command': cmd + 'stop', 'timeout': 30}]})
    h['UserPromptSubmit'].append({'matcher': '', 'hooks': [{'type': 'command', 'command': cmd + 'prompt', 'timeout': 10}]})
    h['SessionStart'].append({'matcher': 'startup|resume|clear|fork', 'hooks': [{'type': 'command', 'command': cmd + 'debut', 'timeout': 10}]})
for evt in EVTS:
    if not h.get(evt, True):
        del h[evt]
# Demi-paires (\ud800…) non encodables en UTF-8 : seules elles sont échappées, le reste (nos chemins
# compris, que l'enveloppe cherche tels quels) reste en clair.
texte = json.dumps(s, ensure_ascii=False, indent=2) + '\n'
octets = re.sub('[\ud800-\udfff]', lambda m: '\\u%04x' % ord(m.group()), texte).encode('utf-8')
cible_fichier = Path(os.path.realpath(reglages))   # lien symbolique (dotfiles) : on écrit sa cible
fd, tmp = tempfile.mkstemp(dir=str(cible_fichier.parent), prefix='.settings.', suffix='.tmp')
try:
    with os.fdopen(fd, 'wb') as f:
        f.write(octets)
    masque = os.umask(0); os.umask(masque)           # fichier neuf : droits selon l'umask, comme avant
    os.chmod(tmp, stat.S_IMODE(os.stat(cible_fichier).st_mode) if cible_fichier.exists() else 0o666 & ~masque)
    os.replace(tmp, cible_fichier)
except BaseException:
    os.unlink(tmp)
    raise
print(('Retiré de ' if mode == '--retirer' else 'Installé dans ') + str(reglages))
PYEOF
}
enregistrer verifier
[ -f "$reglages" ] && cp "$reglages" "$reglages.avant-vive-memoire.$(date +%Y%m%d%H%M%S).$$"
if [ "${1:-}" = "--retirer" ]; then
  enregistrer --retirer
  rm -f "$cible_hooks"/vive_memoire.py "$cible_hooks"/vive-memoire-stop.sh "$cible_hooks"/vive-memoire-prompt.sh "$cible_hooks"/installe-mac.sh
  rm -f "$cible_skill"/SKILL.md "$cible_skill"/bilan-template.html "$cible_skill"/genere-bilan.py "$cible_skill"/teste-bilan.mjs
  rmdir "$cible_hooks" "$cible_skill" 2>/dev/null || true
else
  installer_fichiers
  enregistrer
  echo "Hooks : $cible_hooks — skill : $cible_skill"
fi
