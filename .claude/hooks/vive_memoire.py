"""Hooks « vive mémoire » : impose la synthèse de fin de discussion (skill vive-memoire).

Modes (appelés par les enveloppes bash de ce dossier, ou à la main) :
  python3 -I vive_memoire.py prompt          UserPromptSubmit : note les demandes pas encore écrites au transcript
  python3 -I vive_memoire.py stop            Stop : demande la synthèse quand elle manque (JSON « block »)
  python3 -I vive_memoire.py debut           SessionStart : rappelle les synthèses dues par d'autres sessions
  python3 -I vive_memoire.py tamponne [id]   Après la synthèse : enregistre qu'elle est faite pour cette session

Où ça marche (doc Claude Code, vérifiée le 14/10/2026) : hooks d'un dépôt dans une session
locale ou dans une session cloud ouverte sur CE SEUL dépôt ; hooks utilisateur sur le Mac
(installe-mac.sh). Une session cloud ouverte sur plusieurs dépôts ne charge aucun hook :
seule la consigne des CLAUDE.md s'applique (D-019).

Garanties : ne bloque jamais sur une erreur (toute exception rend la main sans bloquer),
au plus 3 relances consécutives puis libération mémorisée + dette rappelée au démarrage
suivant, état propre à chaque session, ne compte que les demandes humaines.
État : $VM_ETAT ou ~/.claude/vive-memoire/ (jamais dans un dépôt). Python 3.8+.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

SEUIL_MIN = 4        # demandes humaines avant d'exiger une synthèse
SEUIL_REFRESH = 8    # nouvelles demandes depuis la dernière synthèse (ou libération)
MAX_RELANCES = 3     # blocages consécutifs avant de laisser finir
ICI = Path(__file__).resolve().parent

# Repli quand le transcript ne porte pas encore le champ « origin » (anciennes versions).
TECHNIQUE = ('<task-notification>', '<local-command', '<command-name>', '<command-message>',
             '<system-reminder>', '[Image:', '[SYSTEM NOTIFICATION', 'Continue from where you left off',
             'Stop hook feedback', 'Vive mémoire :', '<github-webhook-activity>', '<wake ',
             '<webhook-payload', '<scheduled', '<agent-message', '<child-session-event')


def dossier_etat() -> Path:
    return Path(os.environ.get('VM_ETAT') or (Path.home() / '.claude' / 'vive-memoire'))


def nom_sur(session: str) -> str:
    return re.sub(r'[^A-Za-z0-9_-]', '_', session)[:80] or 'inconnue'


def lire_json(chemin: Path, defaut):
    try:
        return json.loads(chemin.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return defaut


def ecrire_json(chemin: Path, valeur) -> bool:
    """Écriture atomique ; False si impossible (dossier en lecture seule, disque plein…)."""
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        tmp = chemin.with_name(chemin.name + '.tmp')
        tmp.write_text(json.dumps(valeur, ensure_ascii=False), encoding='utf-8')
        os.replace(tmp, chemin)
        return True
    except OSError:
        return False


def empreinte(texte: str) -> str:
    return hashlib.sha1(' '.join((texte or '').split())[:300].encode('utf-8', 'replace')).hexdigest()[:16]


def texte_de(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    if isinstance(contenu, list):
        for x in contenu:
            if isinstance(x, dict) and x.get('type') == 'text' and str(x.get('text') or '').strip():
                return str(x.get('text'))
    return ''


def analyser_transcript(chemin: str):
    """(nombre de demandes humaines, empreintes de toutes les entrées utilisateur).

    Demande humaine = entrée « user » d'origine « human », ou commande envoyée en cours de
    tour (attachment queued_command, humanTurn) comptée une fois par source_uuid.
    Sans champ « origin » (anciennes versions) : repli sur les préfixes techniques."""
    humaines, file_humaine, empreintes, repli, avec_origine = 0, set(), set(), 0, False
    try:
        with open(chemin, encoding='utf-8', errors='replace') as f:
            for ligne in f:
                try:
                    o = json.loads(ligne)
                except ValueError:
                    continue
                if not isinstance(o, dict):
                    continue
                a = o.get('attachment')
                if isinstance(a, dict):
                    if a.get('type') == 'queued_command' and str(a.get('humanTurn')).lower() == 'true':
                        file_humaine.add(str(a.get('source_uuid') or a.get('delivery_id') or empreinte(str(a.get('prompt')))))
                    continue
                if o.get('type') != 'user' or o.get('isMeta') or o.get('isCompactSummary'):
                    continue
                m = o.get('message') if isinstance(o.get('message'), dict) else {}
                t = texte_de(m.get('content')).strip()
                if not t:
                    continue
                empreintes.add(empreinte(t))
                origine = o.get('origin')
                if isinstance(origine, dict):
                    avec_origine = True
                    humaines += origine.get('kind') == 'human'
                elif not t.startswith(TECHNIQUE):
                    repli += 1
    except OSError:
        pass
    return (humaines if avec_origine else repli) + len(file_humaine), empreintes


def trouver_transcript(session: str) -> str:
    motif = str(Path.home() / '.claude' / 'projects' / '*' / (session + '.jsonl'))
    trouves = glob.glob(motif)
    return trouves[0] if trouves else ''


def compter(etat: dict, transcript: str):
    nb, empreintes = analyser_transcript(transcript)
    # Demandes envoyées mais pas encore écrites au transcript (écriture différée) :
    # comptées une fois, seulement si elles ressemblent à une demande humaine.
    attente = [p for p in etat.get('prompts', []) if p.get('e') not in empreintes and not p.get('technique')]
    return nb + len(attente)


def chemins_memoire() -> list:
    racine = Path(os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
    candidats = [os.environ.get('VM_MEMOIRE') or '', racine / 'docs/context', racine / 'claude-macos-app/docs/context',
                 racine.parent / 'claude-macos-app/docs/context', ICI.parents[1] / 'docs/context',
                 ICI.parents[2] / 'claude-macos-app/docs/context', Path.home() / 'Documents/Claude/docs/context']
    vus = []
    for c in candidats:
        if c and Path(c, 'decision-log.md').exists() and Path(c).resolve() not in vus:
            vus.append(Path(c).resolve())
    return vus


def tampon_durable(session: str) -> int:
    """Compte rendu commité qui porte « Session : <id> » et « Demandes : <nb> » (survit au conteneur)."""
    for memoire in chemins_memoire():
        for cr in sorted((memoire / 'sessions').glob('*.md')):
            try:
                t = cr.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            if session in t:
                m = re.search(r'Demandes\s*:\s*(\d+)', t)
                return int(m.group(1)) if m else 0
    return -1


def chemin_skill() -> str:
    for c in ([ICI.parent / 'skills/vive-memoire/SKILL.md', Path.home() / '.claude/skills/vive-memoire/SKILL.md']
              + [m / 'skills/vive-memoire/SKILL.md' for m in chemins_memoire()]):
        if c.exists():
            return str(c)
    return 'claude-macos-app/docs/context/skills/vive-memoire/SKILL.md'


def sortie(objet: dict) -> None:
    sys.stdout.write(json.dumps(objet, ensure_ascii=False) + '\n')


def mode_prompt(entree: dict, etat: dict, f_etat: Path) -> int:
    t = str(entree.get('prompt') or '').strip()
    if t:
        prompts = (etat.get('prompts') or [])[-19:]
        prompts.append({'e': empreinte(t), 'technique': t.startswith(TECHNIQUE)})
        etat['prompts'] = prompts
        ecrire_json(f_etat, etat)
    return 0


def mode_tamponne(session: str, transcript: str) -> int:
    f_etat = dossier_etat() / (nom_sur(session) + '.json')
    etat = lire_json(f_etat, {})
    nb = compter(etat, transcript or trouver_transcript(session))
    etat.update({'tampon': nb, 'relances': 0, 'date_tampon': time.strftime('%Y-%m-%d %H:%M')})
    ok = ecrire_json(f_etat, etat)
    dette = lire_json(dossier_etat() / 'dette.json', {})
    if isinstance(dette, dict) and dette.pop(session, None) is not None:
        ecrire_json(dossier_etat() / 'dette.json', dette)
    print(f'Vive mémoire : synthèse enregistrée pour la session {session} ({nb} demandes)'
          + ('' if ok else ' — ATTENTION : état non inscriptible, rien n\'a été écrit') + '.')
    print(f'Inscris aussi « Session : {session} » et « Demandes : {nb} » dans le compte rendu de session.')
    return 0 if ok else 1


def mode_debut(session: str) -> int:
    dette = lire_json(dossier_etat() / 'dette.json', {})
    if not isinstance(dette, dict):
        return 0
    autres = {s: v for s, v in dette.items() if s != session and isinstance(v, dict)}
    if autres:
        lignes = [f'- session {s} : {v.get("nb", "?")} demandes, libérée le {v.get("date", "?")} sans synthèse' for s, v in autres.items()]
        print('Vive mémoire : synthèse due par une discussion précédente. Commence par la rattraper avec la skill '
              f'« vive-memoire » ({chemin_skill()}), puis lance « python3 {ICI / "vive_memoire.py"} tamponne <id> » pour chaque session :\n'
              + '\n'.join(lignes))
    return 0


def mode_stop(entree: dict, session: str, etat: dict, f_etat: Path) -> int:
    taches = entree.get('background_tasks')
    if isinstance(taches, list) and any(isinstance(t, dict) and t.get('status', 'running') == 'running' for t in taches):
        return 0   # session en pause : du travail en arrière-plan la réveillera
    nb = compter(etat, str(entree.get('transcript_path') or '') or trouver_transcript(session))
    reference = max(int(etat.get('tampon', -1)), int(etat.get('libere_a', -1)), tampon_durable(session))
    if nb < SEUIL_MIN or (reference >= 0 and nb - reference < SEUIL_REFRESH):
        if etat.get('relances'):
            etat['relances'] = 0
            ecrire_json(f_etat, etat)
        return 0
    relances = int(etat.get('relances', 0))
    if relances >= MAX_RELANCES:
        etat.update({'relances': 0, 'libere_a': nb})
        ecrire_json(f_etat, etat)
        dette = lire_json(dossier_etat() / 'dette.json', {})
        dette = dette if isinstance(dette, dict) else {}
        dette[session] = {'nb': nb, 'date': time.strftime('%Y-%m-%d %H:%M')}
        ecrire_json(dossier_etat() / 'dette.json', dette)
        sortie({'systemMessage': f'Vive mémoire : synthèse non faite après {MAX_RELANCES} relances ({nb} demandes). '
                                 'Elle sera rappelée au début de la prochaine discussion.'})
        return 0
    etat['relances'] = relances + 1
    if not ecrire_json(f_etat, etat):
        # Sans état durable, impossible de borner les relances : on prévient sans bloquer.
        sortie({'systemMessage': 'Vive mémoire : état non inscriptible (' + str(f_etat.parent) + '), synthèse non vérifiée.'})
        return 0
    commande = f'python3 "{ICI / "vive_memoire.py"}" tamponne {session}'
    sortie({'decision': 'block', 'reason': (
        f'Vive mémoire : cette discussion compte {nb} demandes de Baptiste et aucune synthèse récente '
        f'(relance {relances + 1}/{MAX_RELANCES}). Exécute la skill « vive-memoire » (fichier : {chemin_skill()}) : '
        'compte rendu de session (avec « Session : ' + session + ' » et « Demandes : ' + str(nb) + ' »), décisions D-xxx, backlog, '
        'skills à faire grossir, ponts IA, journal Notion, bilan interactif publié, commit + push. '
        f'Termine par : {commande}. Si cette synthèse est déjà faite dans cette discussion, lance seulement cette commande.')})
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'stop'
    if mode == 'tamponne':
        session = (sys.argv[2] if len(sys.argv) > 2 else '') or os.environ.get('CLAUDE_CODE_SESSION_ID', '')
        if not session:
            print('Vive mémoire : identifiant de session inconnu (argument ou CLAUDE_CODE_SESSION_ID).')
            return 1
        return mode_tamponne(session, '')
    brut = sys.stdin.read()
    entree = json.loads(brut) if brut.strip() else {}
    if not isinstance(entree, dict):
        return 0
    session = str(entree.get('session_id') or '')
    if not session:
        return 0
    if mode == 'debut':
        return mode_debut(session)
    f_etat = dossier_etat() / (nom_sur(session) + '.json')
    etat = lire_json(f_etat, {})
    etat = etat if isinstance(etat, dict) else {}
    if mode == 'prompt':
        return mode_prompt(entree, etat, f_etat)
    if mode == 'stop':
        return mode_stop(entree, session, etat, f_etat)
    return 0


if __name__ == '__main__':
    try:
        code = main()
    except Exception:          # jamais de blocage sur une erreur du hook
        code = 0
    sys.exit(code if len(sys.argv) > 1 and sys.argv[1] == 'tamponne' else 0)
