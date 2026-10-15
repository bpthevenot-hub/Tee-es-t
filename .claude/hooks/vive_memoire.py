"""Hooks « vive mémoire » : impose la synthèse de fin de discussion (skill vive-memoire).

Modes (appelés par les enveloppes bash de ce dossier, ou à la main) :
  python3 -I vive_memoire.py prompt          UserPromptSubmit : note les demandes pas encore écrites au transcript
  python3 -I vive_memoire.py stop            Stop : demande la synthèse quand elle manque (JSON « block »)
  python3 -I vive_memoire.py debut           SessionStart : rappelle les synthèses dues par d'autres sessions
  python3 -I vive_memoire.py tamponne [id]   Après la synthèse : enregistre qu'elle est faite pour cette session

Où ça marche (doc Claude Code, vérifiée le 14/10/2026) : hooks d'un dépôt dans une session
locale ou dans une session cloud ouverte sur CE SEUL dépôt ; hooks utilisateur sur le Mac
(installe-mac.sh). Une session cloud hébergée par Anthropic ouverte sur plusieurs dépôts ne
charge ni les hooks des dépôts ni les réglages utilisateur (seuls d'éventuels hooks gérés par
une organisation s'y appliquent) : seule la consigne des CLAUDE.md s'applique (D-019).

Garanties : ne bloque jamais sur une erreur (toute exception rend la main sans bloquer ;
« tamponne » signale la sienne), au plus 3 relances consécutives puis libération mémorisée
+ dette rappelée sur la même machine (au démarrage d'une autre session plus d'une heure après,
ou à la reprise de la même ; pas en cloud, où le conteneur ne survit pas), état propre à
chaque session, ne compte que les demandes humaines de la branche active (pas les tours
abandonnés par /rewind). Une seule copie agit par session : la copie utilisateur, quand elle
tourne vraiment (marque par session), sinon celle du dépôt.
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
from types import SimpleNamespace

VERSION = '3.5'
SEUIL_MIN = 4        # demandes humaines avant d'exiger une synthèse
SEUIL_REFRESH = 8    # nouvelles demandes depuis la dernière synthèse (ou libération)
MAX_RELANCES = 3     # blocages consécutifs avant de laisser finir
ICI = Path(__file__).resolve().parent

# Repli quand le transcript ne porte pas encore le champ « origin » (anciennes versions).
TECHNIQUE = ('<task-notification>', '<local-command', '<command-name>', '<command-message>',
             '<system-reminder>', '[Image:', '[SYSTEM NOTIFICATION', 'Continue from where you left off',
             'Stop hook feedback', 'Vive mémoire :', '<github-webhook-activity>', '<wake ',
             '<webhook-payload', '<scheduled', '<agent-message', '<child-session-event')


HUMAINES = ('human', 'channel')   # envoi tapé par Baptiste, ici ou depuis un canal (Discord, Telegram…)


def humaine(x: dict) -> bool:
    origine = x.get('origin')
    return isinstance(origine, dict) and origine.get('kind') in HUMAINES


def dossier_config() -> Path:
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or (Path.home() / '.claude'))


def dossier_etat() -> Path:
    return Path(os.environ.get('VM_ETAT') or (dossier_config() / 'vive-memoire'))


def nom_sur(session: str) -> str:
    return re.sub(r'[^A-Za-z0-9_-]', '_', session)[:80] or 'inconnue'


def lire_json(chemin: Path, defaut):
    try:
        return json.loads(chemin.read_text(encoding='utf-8'))
    except (OSError, ValueError, RecursionError):
        return defaut


def entier(valeur, defaut: int = -1) -> int:
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return defaut


def liste(valeur) -> list:
    return [x for x in valeur if isinstance(x, dict)] if isinstance(valeur, list) else []


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


def chaine_active(liens: dict, feuille):
    """(uuids des ancêtres de « feuille », coupure) en suivant parentUuid, et logicalParentUuid à
    travers une compaction. Chaîne rompue (parent absent du fichier) : (None, -1), on ne filtre rien.
    Compaction dont l'amont manque au fichier : coupure = sa position, rien n'est filtré avant."""
    vus, u, coupure = set(), feuille, -1
    while u and u not in vus:
        if u not in liens:
            return None, -1
        vus.add(u)
        direct, logique, debut = liens[u]
        if not direct and logique and logique not in liens:
            coupure = debut
        u = direct or (logique if logique in liens else None)
    return (vus or None), coupure


def invite(o: dict) -> bool:
    """Entrée qui porte une invite (ce que UserPromptSubmit a vu), quelle qu'en soit l'origine :
    commande en file, ou entrée « user » qui n'est ni un retour d'outil, ni un résumé, ni une méta."""
    a = o.get('attachment')
    if o.get('type') == 'queued_command' or (isinstance(a, dict) and a.get('type') == 'queued_command'):
        return True
    if o.get('type') != 'user' or o.get('isCompactSummary') or (o.get('isMeta') and not humaine(o)):
        return False
    m = o.get('message') if isinstance(o.get('message'), dict) else {}
    contenu = m.get('content')
    if isinstance(contenu, list):
        return bool(contenu) and not any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in contenu)
    return bool(str(contenu or '').strip())


def analyser_transcript(chemin: str):
    """Analyse : nb (demandes humaines), positions (octet de chaque demande dans le fichier),
    parents ({session mère: demandes héritées}), liens, active, ancre, unites (pour « couvertes »).

    Une demande = un envoi distinct de Baptiste : entrée « user » d'origine « human » ou
    « channel » (son uuid, plus les envois antérieurs qu'elle fusionne : mergedSendUuids), ou
    commande envoyée en cours de tour (queued_command humanTurn ou d'origine humaine, source_uuid).
    Une image seule compte aussi.
    Entrées sans champ « origin » (anciennes versions, avant la première entrée qui en porte un) :
    repli par préfixes techniques, additionné.
    Seule compte la branche active : après /rewind, les tours abandonnés restent dans le fichier.
    Elle se remonte depuis l'ancre, la plus récente de : dernière entrée assistant, feuille notée
    par Claude Code (last-prompt.leafUuid), dernière demande tapée (une feuille quelconque peut être
    le résultat latéral d'un appel d'outil parallèle) ; ce qui est écrit après l'ancre compte toujours."""
    liens, candidats, avec_origine, ids_prompt, ecrits = {}, [], False, set(), []
    tapee = assistant = feuille_cc = ''
    try:
        with open(chemin, 'rb') as f:
            fin = 0
            for brute in f:
                debut, fin = fin, fin + len(brute)
                try:
                    o = json.loads(brute.decode('utf-8', 'replace'))
                except (ValueError, RecursionError):
                    continue
                if not isinstance(o, dict):
                    continue
                uuid = str(o.get('uuid') or '')
                if uuid and not o.get('isSidechain'):
                    liens[uuid] = (str(o.get('parentUuid') or ''), str(o.get('logicalParentUuid') or ''), debut)
                    if o.get('type') == 'assistant':
                        assistant = uuid
                if o.get('type') == 'last-prompt' and o.get('leafUuid'):
                    feuille_cc = str(o.get('leafUuid'))
                if o.get('promptId'):
                    ids_prompt.add(str(o.get('promptId')))
                fourche = o.get('forkedFrom')
                mere = str(fourche.get('sessionId')) if isinstance(fourche, dict) and fourche.get('sessionId') else ''
                cles = None                    # None : pas une demande ; [] : demande du repli, sans clé
                a = o.get('attachment')
                if invite(o):
                    ecrits.append(debut)       # toute invite écrite, humaine ou non (tour planifié…)
                if o.get('type') == 'queued_command':          # format récent : commande en file au premier niveau
                    texte_file = texte_de(o.get('prompt')) or str(o.get('prompt') or '')
                    if humaine(o) or str(o.get('humanTurn')).lower() == 'true':
                        cles = [str(o.get('source_uuid') or o.get('uuid') or empreinte(texte_file))]
                elif isinstance(a, dict):
                    if a.get('type') == 'queued_command' and (str(a.get('humanTurn')).lower() == 'true'
                                                              or (humaine(a) and not a.get('isMeta'))):
                        cles = [str(a.get('source_uuid') or a.get('delivery_id') or empreinte(str(a.get('prompt'))))]
                elif (o.get('type') == 'user' and not o.get('isCompactSummary')
                      and (not o.get('isMeta') or (humaine(o) and o['origin'].get('kind') == 'channel'))):
                    # isMeta : retours de hook, rappels… sauf un message reçu par un canal (isMeta, origin channel)
                    m = o.get('message') if isinstance(o.get('message'), dict) else {}
                    contenu = m.get('content')
                    t = texte_de(contenu).strip()
                    origine = o.get('origin')
                    if isinstance(origine, dict):
                        avec_origine = True
                        if origine.get('kind') in HUMAINES and (t or contenu):
                            fusion = o.get('mergedSendUuids')
                            cles = [uuid or empreinte(t or json.dumps(contenu)[:200])]
                            cles += [str(x) for x in fusion] if isinstance(fusion, list) else []
                            if uuid:
                                tapee = uuid
                    elif t and not avec_origine and not t.startswith(TECHNIQUE):
                        cles = []
                if cles is not None:
                    candidats.append((uuid, cles, debut, mere))
    except OSError:
        pass
    ancre = max((u for u in (assistant, feuille_cc, tapee) if u in liens), key=lambda u: liens[u][2], default='')
    active, coupure = chaine_active(liens, ancre) if ancre else (None, -1)
    envois, positions, unites, herites = set(), [], [], {}
    for uuid, cles, debut, mere in candidats:
        if active is not None and uuid in liens and uuid not in active and coupure < debut < liens[ancre][2]:
            continue                           # tour abandonné par /rewind
        nouvelles = [c for c in dict.fromkeys(cles) if c not in envois] if cles else [None]
        envois.update(c for c in nouvelles if c)
        positions += [debut] * len(nouvelles)
        unites += [(uuid, debut)] * len(nouvelles)
        if mere and cles:
            herites.setdefault(mere, set()).update(cles)
    return SimpleNamespace(nb=len(positions), positions=positions, unites=unites, liens=liens, active=active,
                           ancre=ancre, ids_prompt=ids_prompt, ecrits=ecrits, parents={mere: len(c) for mere, c in herites.items()})


def couvertes(a, ancre: str, n: int) -> int:
    """Demandes déjà couvertes par une synthèse (ou une libération) faite à « ancre » quand la
    discussion comptait n demandes. Ancre sur la branche active, inconnue ou chaîne rompue : n.
    Ancre abandonnée par /rewind : seules les demandes actives qui en sont des ancêtres. Ancre
    absente d'un transcript lisible (fichier reconstruit depuis une compaction plus récente) : 0."""
    if n < 0 or not ancre or a.active is None:
        return n
    if ancre not in a.liens:
        return 0
    if ancre in a.active:
        return n
    ancetres = chaine_active(a.liens, ancre)[0] or set()
    limite = a.liens[ancre][2]
    return min(n, sum(1 for u, debut in a.unites if ((u in ancetres) if u in a.liens else debut <= limite)))


def dossier_projets() -> Path:
    return dossier_config() / 'projects'


def trouver_transcript(session: str) -> str:
    motif = str(dossier_projets() / '*' / (session + '.jsonl'))
    trouves = glob.glob(motif)
    return trouves[0] if trouves else ''


def compter(etat: dict, a, avec_attente: bool = True):
    nb = a.nb
    if not avec_attente:
        return nb
    # Demandes envoyées depuis le dernier Stop mais pas encore écrites au transcript (écriture
    # différée). Chacune porte la taille du transcript à son envoi : toute invite écrite après cette
    # position lui répond (quels qu'en soient le texte, l'identifiant ou l'origine : un tour
    # planifié écrit ne compte pas comme une demande), le reste est en attente.
    # Une demande dont l'identifiant figure au transcript y est écrite (même sous une autre forme).
    notees = sorted((p for p in liste(etat.get('prompts')) if isinstance(p.get('pos'), int)
                     and not (p.get('id') and p['id'] in a.ids_prompt)), key=lambda p: p['pos'])
    attente = 0
    for i, p in enumerate(notees):
        ecrites = sum(1 for x in a.ecrits if x >= p['pos'])
        attente = max(attente, len(notees) - i - ecrites)
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
    return max(entier(etat.get('tampon')), entier(etat.get('libere_a')), tampon_durable(session))


def chemin_skill() -> str:
    for c in ([ICI.parent / 'skills/vive-memoire/SKILL.md', ICI.parents[1] / 'skills/vive-memoire/SKILL.md',
               dossier_config() / 'skills/vive-memoire/SKILL.md']
              + [m / 'skills/vive-memoire/SKILL.md' for m in chemins_memoire()]):
        if c.exists():
            return str(c)
    return 'claude-macos-app/docs/context/skills/vive-memoire/SKILL.md'


def sortie(objet: dict) -> None:
    sys.stdout.write(json.dumps(objet, ensure_ascii=False) + '\n')


def mode_prompt(entree: dict, session: str, etat: dict, f_etat: Path) -> int:
    t = str(entree.get('prompt') or '').strip()
    chemin = str(entree.get('transcript_path') or '') or etat.get('transcript') or trouver_transcript(session)
    if chemin:
        etat['transcript'] = chemin
    if t and not t.startswith(TECHNIQUE):
        try:
            pos = os.path.getsize(chemin) if chemin else 0
        except OSError:
            pos = 0                            # transcript pas encore créé (première demande)
        etat['prompts'] = [p for p in liste(etat.get('prompts')) if 'pos' in p][-19:] + [{'pos': pos, 'id': str(entree.get('prompt_id') or '')}]
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
    a = analyser_transcript(chemin)
    nb, parents = compter(etat, a), a.parents
    etat.update({'tampon': nb, 'ancre_tampon': a.ancre, 'relances': 0, 'date_tampon': time.strftime('%Y-%m-%d %H:%M')})
    ok = ecrire_json(f_etat, etat)
    if ok:                                 # sans tampon écrit, la dette reste pour le rappel suivant
        effacer_dette(session)
        for mere, herite in parents.items():   # une fourche synthétisée couvre ce qu'elle a hérité de sa mère
            if isinstance(dette.get(mere), dict) and entier(dette[mere].get('nb'), 0) <= herite:
                effacer_dette(mere)
    print(f'Vive mémoire : synthèse enregistrée pour la session {session} ({nb} demandes)'
          + ('' if ok else ' — ATTENTION : état non inscriptible, rien n\'a été écrit') + '.')
    print(f'Inscris aussi « Session : {session} » et « Demandes : {nb} » dans le compte rendu de session.')
    return 0 if ok else 1


def synthese_connue(session: str) -> int:
    """Plus grand tampon connu d'une session (état ou compte rendu durable), libération exclue."""
    etat = lire_json(dossier_etat() / (nom_sur(session) + '.json'), {})
    return max(entier(etat.get('tampon')) if isinstance(etat, dict) else -1, tampon_durable(session))


def mode_debut(session: str, source: str) -> int:
    dette = lire_dettes()
    maintenant = time.time()
    dues = {}
    for s, v in dette.items():
        if not isinstance(v, dict):
            continue
        if synthese_connue(s) >= entier(v.get('nb'), 0):
            effacer_dette(s)                 # la synthèse a été faite depuis (tampon ou compte rendu)
            continue
        if s == session and source == 'resume':
            dues[s] = v                      # on reprend la discussion qui doit sa synthèse
        elif s != session and maintenant - entier(v.get('t'), 0) > 3600:
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
    a = analyser_transcript(chemin)
    planifie = any(isinstance(x, dict) for x in entree.get('session_crons') or [])
    nb = compter(etat, a, avec_attente=not planifie)   # un tour planifié n'est pas une demande de Baptiste
    etat['prompts'] = []      # au Stop suivant, ces demandes-là sont au transcript (ou ne le seront jamais)
    # Références : tampon et libération ramenés à la branche active (après /rewind, seules les
    # demandes encore actives restent couvertes) ; le compte rendu durable ne compte que s'il est
    # plus récent que l'état (sinon c'est la même synthèse, déjà ramenée).
    brut = max(entier(etat.get('tampon')), entier(etat.get('libere_a')))
    durable = tampon_durable(session)
    if durable <= max(brut, entier(etat.get('durable_vu'))):
        durable = -1
    elif durable > nb and a.ancre:
        # Compte rendu plus grand que le transcript (fichier reconstruit depuis une compaction) :
        # on repart d'ici, une fois pour toutes, plutôt que de masquer les demandes à venir.
        etat.update({'tampon': nb, 'ancre_tampon': a.ancre, 'durable_vu': durable})
        durable = -1
    synthese = max([couvertes(a, str(etat.get('ancre_tampon') or ''), entier(etat.get('tampon'))), durable]
                   + [min(reference_session(p), n) for p, n in a.parents.items() if p != session])
    reference = max(synthese, couvertes(a, str(etat.get('ancre_libere') or ''), entier(etat.get('libere_a'))))
    dette = lire_dettes().get(session)
    if synthese >= 0 and isinstance(dette, dict) and entier(dette.get('nb'), 0) <= synthese:
        effacer_dette(session)       # synthèse reconnue (même sans « tamponne ») : plus de rappel
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
    pause = etat.get('pause') if isinstance(etat.get('pause'), dict) else {}
    vues = {k: entier(n, nb) for k, n in pause.items() if k in attente}
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
        if entier(etat.get('relances'), 0):
            etat['relances'] = 0
        ecrire_json(f_etat, etat)
        return 0
    relances = entier(etat.get('relances'), 0)
    if relances >= MAX_RELANCES:
        etat.update({'relances': 0, 'libere_a': nb, 'ancre_libere': a.ancre})
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


def version_de(fichier: Path) -> tuple:
    try:
        m = re.search(r"^VERSION = '([0-9.]+)'", fichier.read_text(encoding='utf-8', errors='replace'), re.M)
    except OSError:
        return ()
    return tuple(int(x) for x in m.group(1).split('.') if x) if m else (0,)


def signaler_version(installee: Path) -> None:
    """Copie utilisateur plus ancienne que celle du dépôt : le dire (jamais l'inverse, pour ne pas
    pousser à réinstaller une version plus ancienne depuis un vieux checkout)."""
    v = version_de(installee)
    if v and v < version_de(Path(__file__)):
        print(f'Vive mémoire : la copie installée dans {installee.parent} (version {".".join(map(str, v))}) est plus ancienne '
              f'que celle du dépôt ({VERSION}) ; relance « bash {ICI / "installe-mac.sh"} » pour la mettre à jour.')


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
    # Une seule copie agit par session. L'enveloppe dit laquelle on est : « utilisateur » (copie
    # installée dans la config) pose une marque pour la session ; « doublon » (copie d'un dépôt
    # alors qu'une installation utilisateur est enregistrée) se tait seulement si cette marque
    # existe : réglages utilisateur illisibles ou non chargés (--setting-sources) = elle agit.
    copie = os.environ.get('VM_COPIE', '')
    marque = dossier_etat() / 'actifs' / nom_sur(session)
    if copie == 'utilisateur':
        try:
            marque.parent.mkdir(parents=True, exist_ok=True)
            marque.touch()
        except OSError:
            pass
    elif copie == 'doublon':
        if mode == 'debut':
            signaler_version(Path(os.environ.get('VM_COPIE_UTILISATEUR') or ''))
        if marque.exists():
            return 0
    if mode == 'debut':
        return mode_debut(session, str(entree.get('source') or ''))
    f_etat = dossier_etat() / (nom_sur(session) + '.json')
    etat = lire_json(f_etat, {})
    etat = etat if isinstance(etat, dict) else {}
    if mode == 'prompt':
        return mode_prompt(entree, session, etat, f_etat)
    if mode == 'stop':
        return mode_stop(entree, session, etat, f_etat)
    return 0


if __name__ == '__main__':
    tampon = len(sys.argv) > 1 and sys.argv[1] == 'tamponne'
    try:
        code = main()
    except Exception as erreur:   # jamais de blocage sur une erreur du hook ; « tamponne » le dit
        code = 1
        if tampon:
            print(f'Vive mémoire : erreur pendant le tampon ({type(erreur).__name__}) ; rien n\'a été tamponné, la dette reste.')
    sys.exit(code if tampon else 0)
