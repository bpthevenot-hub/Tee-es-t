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
from collections import Counter
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


def dossier_config() -> Path:
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or (Path.home() / '.claude'))


def dossier_etat() -> Path:
    return Path(os.environ.get('VM_ETAT') or (dossier_config() / 'vive-memoire'))


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
    """(demandes humaines, empreintes des entrées utilisateur, {session mère: demandes héritées}).

    Une demande = un envoi distinct de Baptiste : entrée « user » d'origine « human » (son uuid,
    plus les envois antérieurs qu'elle fusionne : mergedSendUuids), ou commande envoyée en cours
    de tour (queued_command humanTurn, source_uuid). Une image seule compte aussi.
    Entrées sans champ « origin » (anciennes versions, avant la première entrée qui en porte un) :
    repli par préfixes techniques, additionné."""
    envois, empreintes, parents, repli, avec_origine = set(), Counter(), {}, 0, False
    herites, prompt_ids = {}, set()
    try:
        with open(chemin, encoding='utf-8', errors='replace') as f:
            for ligne in f:
                try:
                    o = json.loads(ligne)
                except ValueError:
                    continue
                if not isinstance(o, dict):
                    continue
                fourche = o.get('forkedFrom')
                mere = str(fourche.get('sessionId')) if isinstance(fourche, dict) and fourche.get('sessionId') else ''
                if o.get('type') == 'queued_command':          # format récent : commande en file au premier niveau
                    texte_file = texte_de(o.get('prompt')) or str(o.get('prompt') or '')
                    if texte_file:
                        empreintes[empreinte(texte_file)] += 1
                    origine_file = o.get('origin')
                    if (isinstance(origine_file, dict) and origine_file.get('kind') == 'human') or str(o.get('humanTurn')).lower() == 'true':
                        cle = str(o.get('source_uuid') or o.get('uuid') or empreinte(texte_file))
                        envois.add(cle)
                        if mere:
                            herites.setdefault(mere, set()).add(cle)
                    continue
                a = o.get('attachment')
                if isinstance(a, dict):
                    if a.get('type') == 'queued_command':
                        if a.get('prompt'):
                            empreintes[empreinte(texte_de(a.get('prompt')) or str(a.get('prompt')))] += 1
                        if str(a.get('humanTurn')).lower() == 'true':
                            cle = str(a.get('source_uuid') or a.get('delivery_id') or empreinte(str(a.get('prompt'))))
                            envois.add(cle)
                            if mere:
                                herites.setdefault(mere, set()).add(cle)
                    continue
                if o.get('type') != 'user' or o.get('isMeta') or o.get('isCompactSummary'):
                    continue
                m = o.get('message') if isinstance(o.get('message'), dict) else {}
                contenu = m.get('content')
                t = texte_de(contenu).strip()
                if o.get('promptId'):
                    prompt_ids.add(str(o.get('promptId')))
                if t:
                    empreintes[empreinte(t)] += 1
                origine = o.get('origin')
                if isinstance(origine, dict):
                    avec_origine = True
                    if origine.get('kind') == 'human' and (t or contenu):
                        fusion = o.get('mergedSendUuids')
                        cles = [str(o.get('uuid') or empreinte(t or json.dumps(contenu)[:200]))]
                        cles += [str(x) for x in fusion] if isinstance(fusion, list) else []
                        envois.update(cles)
                        if mere:
                            herites.setdefault(mere, set()).update(cles)
                elif t and not avec_origine and not t.startswith(TECHNIQUE):
                    repli += 1
    except OSError:
        pass
    parents = {mere: len(cles) for mere, cles in herites.items()}
    return repli + len(envois), (empreintes, prompt_ids), parents


def dossier_projets() -> Path:
    return dossier_config() / 'projects'


def trouver_transcript(session: str) -> str:
    motif = str(dossier_projets() / '*' / (session + '.jsonl'))
    trouves = glob.glob(motif)
    return trouves[0] if trouves else ''


def compter(etat: dict, transcript: str, avec_attente: bool = True):
    nb, (empreintes, prompt_ids), _ = analyser_transcript(transcript)
    if not avec_attente:
        return nb
    # Demandes envoyées mais pas encore écrites au transcript (écriture différée), comptées une fois.
    # Rapprochement par identifiant de prompt ; à défaut, par nombre d'occurrences du même texte.
    restantes = Counter(empreintes)
    attente = 0
    for p in etat.get('prompts', []):
        if p.get('technique'):
            continue
        if p.get('id'):
            attente += p['id'] not in prompt_ids
        elif restantes[p.get('e')] > 0:
            restantes[p.get('e')] -= 1
        else:
            attente += 1
    return nb + attente


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
    """Compte rendu commité portant le bloc « Session : <id> » puis « Demandes : <nb> » (survit au conteneur)."""
    deco = r'[ \t>*_`-]*'
    motif = re.compile(r'^' + deco + 'Session' + deco + ':' + deco + re.escape(session) + deco + r'\r?\n'
                       + deco + 'Demandes' + deco + ':' + deco + r'(\d+)', re.M)
    meilleur = -1
    for memoire in chemins_memoire():
        for cr in (memoire / 'sessions').glob('*.md'):
            try:
                m = motif.search(cr.read_text(encoding='utf-8', errors='replace'))
            except OSError:
                continue
            if m:
                meilleur = max(meilleur, int(m.group(1)))
    return meilleur


def reference_session(session: str) -> int:
    etat = lire_json(dossier_etat() / (nom_sur(session) + '.json'), {})
    etat = etat if isinstance(etat, dict) else {}
    return max(int(etat.get('tampon', -1)), int(etat.get('libere_a', -1)), tampon_durable(session))


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
    if entree.get('transcript_path'):
        etat['transcript'] = str(entree['transcript_path'])
    if t:
        prompts = (etat.get('prompts') or [])[-19:]
        prompts.append({'e': empreinte(t), 'id': str(entree.get('prompt_id') or ''), 'technique': t.startswith(TECHNIQUE)})
        etat['prompts'] = prompts
        ecrire_json(f_etat, etat)
    return 0


def mode_tamponne(session: str, transcript: str) -> int:
    f_etat = dossier_etat() / (nom_sur(session) + '.json')
    etat = lire_json(f_etat, {})
    etat = etat if isinstance(etat, dict) else {}
    chemin = transcript or etat.get('transcript') or trouver_transcript(session)
    dette = lire_dettes()
    if not chemin or not Path(chemin).is_file():
        if session in dette and effacer_dette(session):
            print(f'Vive mémoire : transcript de la session {session} disparu ; dette effacée sans compte.')
            return 0
        print(f'Vive mémoire : transcript de la session {session} introuvable (dossier {dossier_projets()}) ; rien n\'a été tamponné.')
        return 1
    nb = compter(etat, chemin)
    _, _, parents = analyser_transcript(chemin)
    etat.update({'tampon': nb, 'relances': 0, 'date_tampon': time.strftime('%Y-%m-%d %H:%M')})
    ok = ecrire_json(f_etat, etat)
    effacer_dette(session)
    for mere, herite in parents.items():   # une fourche synthétisée couvre ce qu'elle a hérité de sa mère
        if isinstance(dette.get(mere), dict) and int(dette[mere].get('nb', 0)) <= herite:
            effacer_dette(mere)
    print(f'Vive mémoire : synthèse enregistrée pour la session {session} ({nb} demandes)'
          + ('' if ok else ' — ATTENTION : état non inscriptible, rien n\'a été écrit') + '.')
    print(f'Inscris aussi « Session : {session} » et « Demandes : {nb} » dans le compte rendu de session.')
    return 0 if ok else 1


def mode_debut(session: str, source: str) -> int:
    dette = lire_dettes()
    maintenant = time.time()
    dues = {}
    for s, v in dette.items():
        if not isinstance(v, dict):
            continue
        if s == session and source == 'resume':
            dues[s] = v                      # on reprend la discussion qui doit sa synthèse
        elif s != session and maintenant - float(v.get('t', 0)) > 3600:
            dues[s] = v                      # une autre session, abandonnée depuis plus d'une heure
    if dues:
        lignes = [f'- session {s} : {v.get("nb", "?")} demandes, le {v.get("date", "?")}, sans synthèse' for s, v in dues.items()]
        print('Vive mémoire : synthèse due. Commence par la rattraper avec la skill « vive-memoire » '
              f'({chemin_skill()}), puis lance « python3 "{ICI / "vive_memoire.py"}" tamponne <id> » pour chaque session :\n'
              + '\n'.join(lignes))
    return 0


def dossier_dettes() -> Path:
    return dossier_etat() / 'dettes'


def noter_dette(session: str, nb: int) -> None:
    ecrire_json(dossier_dettes() / (nom_sur(session) + '.json'),
                {'session': session, 'nb': nb, 'date': time.strftime('%Y-%m-%d %H:%M'), 't': time.time()})


def lire_dettes() -> dict:
    dettes = {}
    for f in dossier_dettes().glob('*.json'):
        v = lire_json(f, None)
        if isinstance(v, dict) and v.get('session'):
            dettes[str(v['session'])] = v
    ancien = lire_json(dossier_etat() / 'dette.json', {})          # format v3.1, encore lu
    if isinstance(ancien, dict):
        for s, v in ancien.items():
            if isinstance(v, dict):
                dettes.setdefault(s, dict(v, session=s))
    return dettes


def effacer_dette(session: str) -> bool:
    efface = False
    try:
        (dossier_dettes() / (nom_sur(session) + '.json')).unlink()
        efface = True
    except OSError:
        pass
    ancien = lire_json(dossier_etat() / 'dette.json', {})
    if isinstance(ancien, dict) and ancien.pop(session, None) is not None:
        efface = ecrire_json(dossier_etat() / 'dette.json', ancien) or efface
    return efface


def mode_stop(entree: dict, session: str, etat: dict, f_etat: Path) -> int:
    chemin = str(entree.get('transcript_path') or '') or etat.get('transcript') or trouver_transcript(session)
    etat['transcript'] = chemin
    _, _, parents = analyser_transcript(chemin)
    planifie = any(isinstance(x, dict) for x in entree.get('session_crons') or [])
    nb = compter(etat, chemin, avec_attente=not planifie)   # un tour planifié n'est pas une demande de Baptiste
    reference = max([int(etat.get('tampon', -1)), int(etat.get('libere_a', -1)), tampon_durable(session)]
                    + [min(reference_session(p), n) for p, n in parents.items() if p != session])
    due = nb >= SEUIL_MIN and not (reference >= 0 and nb - reference < SEUIL_REFRESH)
    # Pause quand la session attend du travail né depuis la dernière demande humaine (tâche en
    # cours ou en file, réveil ponctuel planifié). Une attente plus ancienne (serveur de dev,
    # surveillance sans fin) ne suspend plus rien.
    attente = set()
    for x in entree.get('background_tasks') or []:
        if isinstance(x, dict) and x.get('status', 'running') in ('running', 'pending'):
            attente.add('t:' + str(x.get('id') or x.get('description') or len(attente)))
    for x in entree.get('session_crons') or []:
        if isinstance(x, dict):
            attente.add('c:' + str(x.get('id') or x.get('prompt') or len(attente)))
    vues = {k: int(n) for k, n in (etat.get('pause') or {}).items() if k in attente}
    for k in attente:
        vues.setdefault(k, nb)
    etat['pause'] = vues
    etat.pop('pause_ids', None); etat.pop('pause_nb', None)
    if any(n >= nb for n in vues.values()):
        if due:
            noter_dette(session, nb)     # si la discussion est abandonnée pendant l'attente
        ecrire_json(f_etat, etat)
        return 0
    if not due:
        if etat.get('relances'):
            etat['relances'] = 0
        ecrire_json(f_etat, etat)
        return 0
    relances = int(etat.get('relances', 0))
    if relances >= MAX_RELANCES:
        etat.update({'relances': 0, 'libere_a': nb})
        ecrire_json(f_etat, etat)
        noter_dette(session, nb)
        ou = ('en cloud, le rappel ne survit pas au conteneur : ajoute « Synthèse due : session ' + session + ' » en P0 de next-actions.md'
              if os.environ.get('CLAUDE_CODE_REMOTE') else 'elle sera rappelée au prochain démarrage sur cette machine')
        sortie({'systemMessage': f'Vive mémoire : synthèse non faite après {MAX_RELANCES} relances ({nb} demandes) ; {ou}.'})
        return 0
    etat['relances'] = relances + 1
    if not ecrire_json(f_etat, etat):
        sortie({'systemMessage': 'Vive mémoire : état non inscriptible (' + str(f_etat.parent) + '), synthèse non vérifiée.'})
        return 0
    noter_dette(session, nb)   # effacée par « tamponne » ; rappelée si la discussion est abandonnée
    commande = f'python3 "{ICI / "vive_memoire.py"}" tamponne {session}'
    sortie({'decision': 'block', 'reason': (
        f'Vive mémoire : cette discussion compte {nb} demandes de Baptiste et aucune synthèse récente '
        f'(relance {relances + 1}/{MAX_RELANCES}). Exécute la skill « vive-memoire » (fichier : {chemin_skill()}) : '
        'compte rendu de session (avec les lignes « Session : ' + session + ' » puis « Demandes : ' + str(nb) + ' »), décisions D-xxx, backlog, '
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
        return mode_debut(session, str(entree.get('source') or ''))
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
