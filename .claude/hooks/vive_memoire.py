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
abandonnés par /rewind, ni les sous-agents). Quand plusieurs copies (utilisateur, dépôt)
reçoivent le même événement, une seule agit : la première à en poser le verrou.
État : $VM_ETAT ou ~/.claude/vive-memoire/ (jamais dans un dépôt). Python 3.8+.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

try:
    import fcntl
except ImportError:          # hors macOS / Linux : pas de sérialisation, le reste marche
    fcntl = None

VERSION = '3.17'
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


def reel(valeur, defaut: float = 0.0) -> float:
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return defaut


def entier(valeur, defaut: int = -1) -> int:
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return defaut


def liste(valeur) -> list:
    return [x for x in valeur if isinstance(x, dict)] if isinstance(valeur, list) else []


def ecrire_json(chemin: Path, valeur) -> bool:
    """Écriture atomique par un fichier temporaire propre à chaque écrivain (deux copies qui écrivent
    ensemble ne mélangent jamais leurs octets) ; False si impossible (lecture seule, disque plein…)."""
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(chemin.parent), prefix=chemin.name + '.', suffix='.tmp')
    except OSError:
        return False
    try:
        with os.fdopen(fd, 'w', encoding='ascii') as f:
            f.write(json.dumps(valeur, ensure_ascii=True))
        os.replace(tmp, chemin)
        return True
    except (OSError, ValueError):
        try:
            os.unlink(tmp)
        except OSError:
            pass
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
        direct, logique, debut, _ = liens[u]
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
    liens, candidats, avec_origine, ids_prompt, ecrits, points = {}, [], False, set(), [], {}
    sans_uuid = []                             # demandes sans uuid en attente de l'entrée qui les suit
    invites_uuid = set()                       # uuids des invites (tours de conversation)
    tete, fin = '', 0
    tapee = assistant = feuille_cc = ''
    try:
        with open(chemin, 'rb') as f:
            for brute in f:
                debut, fin = fin, fin + len(brute)
                if debut == 0:
                    tete = hashlib.sha1(brute).hexdigest()[:16] if brute.endswith(b'\n') else ''
                try:
                    o = json.loads(brute.decode('utf-8', 'replace'))
                except (ValueError, RecursionError):
                    continue
                if not isinstance(o, dict) or o.get('isSidechain'):
                    continue                   # sous-agent : ni demande, ni invite, ni branche
                uuid = str(o.get('uuid') or '')
                if uuid:
                    for c in sans_uuid:
                        c[5] = uuid
                    sans_uuid = []
                    liens[uuid] = (str(o.get('parentUuid') or ''), str(o.get('logicalParentUuid') or ''), debut,
                                   str(o.get('timestamp') or '')[:19])
                    if o.get('type') == 'assistant':
                        assistant = uuid
                if o.get('type') == 'last-prompt' and o.get('leafUuid'):
                    feuille_cc = str(o.get('leafUuid'))
                if o.get('promptId'):
                    ids_prompt.add(str(o.get('promptId')))
                fourche = o.get('forkedFrom')
                mere = str(fourche.get('sessionId')) if isinstance(fourche, dict) and fourche.get('sessionId') else ''
                if mere and uuid:
                    points[mere] = uuid            # dernière entrée héritée : le point de fourche
                cles = None                    # None : pas une demande ; [] : demande du repli, sans clé
                a = o.get('attachment')
                if invite(o) and uuid:
                    invites_uuid.add(uuid)
                if invite(o):                  # toute invite écrite, humaine ou non (tour planifié…),
                    fusion = o.get('mergedSendUuids')   # autant de fois qu'elle porte d'envois fusionnés
                    ecrits += [debut] * (1 + (len(fusion) if isinstance(fusion, list) else 0))
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
                    candidats.append([uuid, cles, debut, mere, str(o.get('parentUuid') or ''), ''])
                    if not uuid:
                        sans_uuid.append(candidats[-1])
    except OSError:
        pass
    ancre = max((u for u in (assistant, feuille_cc, tapee) if u in liens), key=lambda u: liens[u][2], default='')
    active, coupure = chaine_active(liens, ancre) if ancre else (None, -1)
    envois, positions, unites, herites, herites_uuids = set(), [], [], {}, {}
    def quittee(u):
        # Sur une branche quittée par /rewind : en remontant de u vers la branche active, on traverse une
        # invite hors branche (le tour que /rewind a abandonné). Une feuille latérale (résultat d'outils
        # parallèles, réponse orpheline après un redémarrage) rejoint la branche active sans en traverser.
        vus = set()
        while u in liens and u not in active and u not in vus:
            if u in invites_uuid:
                return True
            vus.add(u)
            u = liens[u][0] or liens[u][1]
        return False
    for uuid, cles, debut, mere, parent, suivante in candidats:
        if active is not None and coupure < debut < liens[ancre][2] and (
                (uuid in liens and uuid not in active) if uuid
                else quittee(parent if parent in liens else suivante)):
            continue                           # tour abandonné par /rewind (sans uuid : jugé par son parent,
                                               # à défaut par l'entrée écrite juste après lui)
        nouvelles = [c for c in dict.fromkeys(cles) if c not in envois] if cles else [None]
        envois.update(c for c in nouvelles if c)
        positions += [debut] * len(nouvelles)
        unites += [(uuid, debut)] * len(nouvelles)
        if mere:                               # ancien format sans clé : compté par sa position
            herites.setdefault(mere, set()).update(cles or ['repli:' + str(debut)])
            herites_uuids.setdefault(mere, []).extend([uuid] * len(nouvelles))
    return SimpleNamespace(nb=len(positions), positions=positions, unites=unites, liens=liens, active=active,
                           ancre=ancre, ids_prompt=ids_prompt, ecrits=ecrits, tete=tete, taille=fin, fourches=points,
                           herites_uuids=herites_uuids, parents={mere: len(c) for mere, c in herites.items()})


def ancre_au_temps(a, date: float) -> str:
    """Dernière entrée du transcript écrite au plus tard à « date » (heure UTC du transcript) ; '' si aucune."""
    if date <= 0:
        return ''
    limite = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(date))
    meilleur, position = '', -1
    for u, (_, _, debut, ts) in a.liens.items():
        if ts and ts <= limite and debut > position:
            meilleur, position = u, debut
    return meilleur


def couvertes(a, ancre: str, n: int, souple: bool = False) -> int:
    """Demandes déjà couvertes par une synthèse (ou une libération) faite à « ancre » quand la
    discussion comptait n demandes. Ancre sur la branche active, inconnue ou chaîne rompue : n.
    Ancre abandonnée par /rewind : seules les demandes actives qui en sont des ancêtres. Ancre
    absente d'un transcript lisible (fichier reconstruit depuis une compaction plus récente) : 0, sauf
    ancre « souple » (posée depuis une fourche, dont les uuids peuvent manquer à la mère) : n."""
    if n < 0 or not ancre or a.active is None:
        return n
    if ancre not in a.liens:
        return n if souple else 0
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
    # Transcript reconstruit depuis (première ligne changée, ou plus court que la position notée) :
    # la position ne veut plus rien dire, la demande est écartée (elle est relue au transcript).
    notees = sorted((p for p in liste(etat.get('prompts')) if isinstance(p.get('pos'), int)
                     and not (p.get('id') and p['id'] in a.ids_prompt)
                     and p['pos'] <= a.taille and not (p.get('tete') and a.tete and p['tete'] != a.tete)),
                    key=lambda p: p['pos'])
    attente = 0
    for i, p in enumerate(notees):
        ecrites = sum(1 for x in a.ecrits if x >= p['pos'])
        attente = max(attente, len(notees) - i - ecrites)
    return nb + attente


def chemins_memoire() -> list:
    """Dossiers mémoire candidats, les mêmes quelle que soit la copie qui tourne (dépôt ou utilisateur) ;
    un dossier illisible est sauté (os.path.isfile ne lève jamais)."""
    try:
        racine = Path(os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
    except OSError:
        racine = Path.home()
    candidats = [os.environ.get('VM_MEMOIRE') or '', racine / 'docs/context', racine / 'claude-macos-app/docs/context',
                 racine.parent / 'claude-macos-app/docs/context', Path.home() / 'claude-macos-app/docs/context',
                 dossier_config().parent / 'claude-macos-app/docs/context', Path.home() / 'Documents/Claude/docs/context']
    candidats += [ICI.parents[k] / suite for k, suite in ((1, 'docs/context'), (2, 'claude-macos-app/docs/context'))
                  if len(ICI.parents) > k]
    vus = []
    for c in candidats:
        if c and os.path.isfile(os.path.join(str(c), 'decision-log.md')):
            try:
                r = Path(c).resolve()
            except (OSError, RuntimeError):
                continue
            if r not in vus:
                vus.append(r)
    return vus


def rapport_durable(session: str, toutes: bool = False):
    """(nb, date, ancre, empreinte) du compte rendu commité le plus récent portant le bloc « Session : <id> »,
    « Demandes : <nb> » et, depuis 3.11, « Ancre : <uuid> » (survit au conteneur) ; (-1, 0.0, '', '')
    sinon. Comptes rendus de même date (à 2 s près, ex. un clone frais) : le plus grand compte.
    L'empreinte (texte normalisé de la seule section de cette session, jusqu'au bloc d'une autre) distingue
    un compte rendu réécrit d'un fichier seulement touché ou complété par une autre session.
    toutes=True : pour chaque fichier de la session, (date, signature [nb, ancre, empreinte], signature de
    3.14, dont l'empreinte portait sur le fichier entier)."""
    deco = r'[ \t>*_`-]*'
    motif = re.compile(r'^' + deco + 'Session' + deco + ':' + deco + re.escape(session) + deco + r'\r?\n'
                       + deco + 'Demandes' + deco + ':' + deco + r'(\d+)'
                       + r'(?:' + deco + r'\r?\n' + deco + 'Ancre' + deco + ':' + deco + r'([0-9A-Za-z_-]+))?', re.M)
    autre_bloc = re.compile(r'^' + deco + 'Session' + deco + ':' + deco + r'\S+' + deco + r'\r?\n' + deco + 'Demandes' + deco + ':', re.M)
    trouves = []
    for memoire in chemins_memoire():
        try:
            fichiers = list((memoire / 'sessions').glob('*.md'))
        except OSError:
            continue
        for cr in fichiers:
            try:
                texte = cr.read_text(encoding='utf-8', errors='replace')
                date = cr.stat().st_mtime
            except OSError:
                continue
            blocs = list(motif.finditer(texte))
            if blocs:                          # compte rendu complété : son dernier bloc fait foi
                suite = autre_bloc.search(texte, blocs[-1].end())
                section = unicodedata.normalize('NFC', texte[blocs[-1].start():suite.start() if suite else len(texte)])
                lignes = [ligne.rstrip() for ligne in section.replace('\ufeff', '').splitlines()]
                while lignes and (not lignes[-1].strip() or re.match(r'\s*(#{1,6}\s|[-*_]{3,}$)', lignes[-1])):
                    lignes.pop()                  # titre ou filet qui introduit le bloc suivant : pas à elle
                normal = '\n'.join(lignes).strip()
                entier_314 = '\n'.join(ligne.rstrip() for ligne in texte.splitlines()).strip()
                trouves.append((date, int(blocs[-1].group(1)), blocs[-1].group(2) or '',
                                hashlib.sha1(normal.encode('utf-8', 'replace')).hexdigest()[:16],
                                hashlib.sha1(entier_314.encode('utf-8', 'replace')).hexdigest()[:16]))
    if toutes:
        return [(d, [n, x, h], [n, x, h314]) for d, n, x, h, h314 in trouves]
    if not trouves:
        return -1, 0.0, '', ''
    recente = max(t[0] for t in trouves)
    n, _, ancre, marque = max((n, d, x, h) for d, n, x, h, _ in trouves if d >= recente - 2)
    return n, recente, ancre, marque


def signatures_vues(valeur) -> list:
    """rapports_vus nettoyé : seules des listes de 2 ou 3 éléments simples (un état corrompu ne fait pas échouer le hook)."""
    return [x for x in (valeur if isinstance(valeur, list) else []) if isinstance(x, list) and len(x) in (2, 3)
            and all(isinstance(v, (int, str)) and not isinstance(v, bool) for v in x)]


def tampon_durable(session: str) -> int:
    return rapport_durable(session)[0]


def couvrir_mere(mere: str, herite: int, point: str) -> None:
    """La synthèse d'une fourche couvre sa mère jusqu'au point de fourche : tampon posé chez la mère (lu,
    mesuré et écrit sous son verrou), ancré au point de fourche pour qu'un /rewind de la mère le ramène.
    Transcript de la mère lisible : on mesure ce que ce nouveau tampon y couvre (point quitté par un
    /rewind : ses seuls ancêtres actifs ; point absent, transcript reconstruit : rien) et on ne le pose
    que s'il couvre plus que celui de la mère, à sa valeur effective. Transcript introuvable : tampon
    « souple » (ancre absente ne vaut pas zéro), comparé à la couverture notée de la mère."""
    f_mere = dossier_etat() / (nom_sur(mere) + '.json')
    with verrou_session(mere):
        etat_mere = lire_json(f_mere, {})
        etat_mere = etat_mere if isinstance(etat_mere, dict) else {}
        tampon = entier(etat_mere.get('tampon'))
        chemin = str(etat_mere.get('transcript') or '')
        if not chemin or not os.path.isfile(chemin):
            chemin = trouver_transcript(mere)
        am = analyser_transcript(chemin) if chemin else None
        if am is not None and am.taille:
            ancienne = couvertes(am, str(etat_mere.get('ancre_tampon') or ''), tampon, bool(etat_mere.get('ancre_souple')))
            nouvelle, souple = couvertes(am, point, herite), False
        else:
            ancienne = min(tampon, entier(etat_mere.get('couvert'), tampon))
            nouvelle, souple = herite, True
        if nouvelle > ancienne:
            if tampon < 0 and not isinstance(etat_mere.get('rapports_vus'), list):
                etat_mere['rapports_vus'] = []    # état né ici : son compte rendu n'est pas « déjà vu »
            etat_mere.update({'tampon': nouvelle, 'ancre_tampon': point, 'ancre_souple': souple, 't_tampon': time.time(),
                              'tampon_fourche': True, 'couvert': max(entier(etat_mere.get('couvert')), nouvelle)})
            ecrire_json(f_mere, etat_mere)


def abandonnee(a, ancre: str) -> bool:
    """L'ancre est-elle sur une branche quittée par /rewind (présente au transcript, hors branche active) ?"""
    return bool(ancre) and a.active is not None and ancre in a.liens and ancre not in a.active


def synthese_heritee(mere: str, herite: int, a) -> int:
    """Part des demandes héritées de « mere » que sa synthèse couvre. Si son tampon est ancré et que
    les deux transcripts partagent leurs uuids, seules comptent les demandes héritées qui sont des
    ancêtres de l'ancre chez la mère (elle a pu revenir en arrière avant de synthétiser) ; sinon,
    son tampon borné aux demandes héritées. État perdu : son compte rendu, borné de même."""
    etat = lire_json(dossier_etat() / (nom_sur(mere) + '.json'), {})
    etat = etat if isinstance(etat, dict) else {}
    tampon, ancre = entier(etat.get('tampon')), str(etat.get('ancre_tampon') or '')
    if tampon < 0:
        return min(tampon_durable(mere), herite)
    point = a.fourches.get(mere, '')
    chemin = str(etat.get('transcript') or '')            # chemin noté par la mère (nom de fichier libre)
    if not chemin or not os.path.isfile(chemin):
        chemin = trouver_transcript(mere)
    tampon = min(tampon, entier(etat.get('couvert'), tampon))    # sa couverture effective (après un /rewind chez elle)
    if not ancre or not point or not chemin:
        return min(tampon, herite)
    am = analyser_transcript(chemin)
    if ancre not in am.liens or point not in am.liens:
        return min(tampon, herite)        # uuids non partagés ou transcript reconstruit : pas de preuve contraire
    ancetres = chaine_active(am.liens, ancre)[0] or set()
    if point in ancetres:
        return min(tampon, herite)
    return min(tampon, sum(1 for u in a.herites_uuids.get(mere, []) if u in ancetres))


def synthese_session(session: str) -> int:
    """Plus grand tampon connu d'une autre session (état ou compte rendu), libération exclue."""
    etat = lire_json(dossier_etat() / (nom_sur(session) + '.json'), {})
    return max(entier(etat.get('tampon')) if isinstance(etat, dict) else -1, tampon_durable(session))


def chemin_skill() -> str:
    for c in ([ICI.parent / 'skills/vive-memoire/SKILL.md', ICI.parents[1] / 'skills/vive-memoire/SKILL.md',
               dossier_config() / 'skills/vive-memoire/SKILL.md']
              + [m / 'skills/vive-memoire/SKILL.md' for m in chemins_memoire()]):
        if os.path.isfile(str(c)):
            return str(c)
    return 'claude-macos-app/docs/context/skills/vive-memoire/SKILL.md'


def sortie(objet: dict) -> None:
    sys.stdout.write(json.dumps(objet, ensure_ascii=False) + '\n')


def tete_de(chemin: str) -> str:
    """Empreinte de la première ligne complète du transcript : ne change que s'il est reconstruit."""
    try:
        with open(chemin, 'rb') as f:
            ligne = f.readline(1 << 20)
    except OSError:
        return ''
    return hashlib.sha1(ligne).hexdigest()[:16] if ligne.endswith(b'\n') else ''


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
        etat['prompts'] = [p for p in liste(etat.get('prompts')) if 'pos' in p][-19:] + [
            {'pos': pos, 'id': str(entree.get('prompt_id') or ''), 'tete': tete_de(chemin) if pos else ''}]
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
    vus = signatures_vues(etat.get('rapports_vus'))
    for _, sig, sig314 in rapport_durable(session, toutes=True):    # comptes rendus présents : déjà connus
        vus += [x for x in (sig, sig314) if x not in vus]
    vus = vus[-40:]
    etat.update({'tampon': nb, 'ancre_tampon': a.ancre, 'ancre_souple': False, 't_tampon': time.time(), 'rapports_vus': vus,
                 'tampon_fourche': False,
                 'couvert': nb,
                 'relances': 0, 'date_tampon': time.strftime('%Y-%m-%d %H:%M')})
    ok = ecrire_json(f_etat, etat)
    if ok:                                 # sans tampon écrit, la dette reste pour le rappel suivant
        effacer_dette(session)
        for mere, herite in parents.items():   # une fourche synthétisée couvre ce qu'elle a hérité de sa mère
            if mere == session:
                continue                         # (jamais sa propre mère : pas de double verrou)
            effacer_dette_si(mere, lambda d, h=herite, m=mere: entier(d.get('nb'), 0) <= h
                             and dette_dans_fourche(d, m, a.fourches.get(m, '')))
            couvrir_mere(mere, herite, a.fourches.get(mere, ''))
    print(f'Vive mémoire : synthèse enregistrée pour la session {session} ({nb} demandes)'
          + ('' if ok else ' — ATTENTION : état non inscriptible, rien n\'a été écrit') + '.')
    print(f'Inscris aussi, sur trois lignes, « Session : {session} », « Demandes : {nb} » et « Ancre : {a.ancre} » '
          'dans le compte rendu de session.')
    return 0 if ok else 1


def dette_couverte(session: str, d: dict) -> bool:
    """Une synthèse faite depuis la dette la couvre-t-elle ? Tampon de la session posé après elle, d'au moins
    son compte ; ou compte rendu jamais vu (ni dans l'état, ni parmi ceux présents quand la dette a été
    notée), daté après elle, d'au moins son compte, et dont l'ancre, si elle est vérifiable, descend de
    celle de la dette (un compte rendu d'une branche quittée par /rewind ne couvre rien)."""
    t, nb = reel(d.get('t')), entier(d.get('nb'), 0)
    etat = lire_json(dossier_etat() / (nom_sur(session) + '.json'), {})
    etat = etat if isinstance(etat, dict) else {}
    if reel(etat.get('t_tampon')) > t and entier(etat.get('tampon')) >= nb:
        return True
    vus = signatures_vues(etat.get('rapports_vus')) + signatures_vues(d.get('rapports'))
    nouveaux = [sig for date, sig, sig314 in rapport_durable(session, toutes=True)
                if date > t and sig[0] >= nb and sig not in vus and sig314 not in vus and sig[:2] not in vus]
    if not nouveaux:
        return False
    ancre_d = str(d.get('ancre') or '')
    chemin = str(etat.get('transcript') or '')
    if not chemin or not os.path.isfile(chemin):
        chemin = trouver_transcript(session)
    a = analyser_transcript(chemin) if ancre_d and chemin else None
    if a is None or ancre_d not in a.liens:
        return True                          # rien à vérifier : un contenu neuf, daté après la dette
    return any(not sig[1] or sig[1] not in a.liens or ancre_d in (chaine_active(a.liens, sig[1])[0] or set())
               for sig in nouveaux)


def mode_debut(session: str, source: str) -> int:
    dette = lire_dettes()
    maintenant = time.time()
    dues = {}
    for s, v in dette.items():
        if not isinstance(v, dict):
            continue
        if effacer_dette_si(s, lambda d, s=s: dette_couverte(s, d)):
            continue                         # une synthèse faite depuis la dette la couvre (tampon ou compte rendu)
        if s == session and source == 'resume':
            dues[s] = v                      # on reprend la discussion qui doit sa synthèse
        elif s != session and (source == 'clear' or maintenant - reel(v.get('t')) > 3600):
            dues[s] = v                      # une autre session, abandonnée depuis plus d'une heure (ou que /clear vient de clore)
    if dues:
        lignes = [f'- session {s} : {v.get("nb", "?")} demandes, le {v.get("date", "?")}, sans synthèse' for s, v in dues.items()]
        print('Vive mémoire : synthèse due. Commence par la rattraper avec la skill « vive-memoire » '
              f'({chemin_skill()}), puis lance « python3 "{ICI / "vive_memoire.py"}" tamponne <id> » pour chaque session :\n'
              + '\n'.join(lignes))
    return 0


def dossier_dettes() -> Path:
    return dossier_etat() / 'dettes'


def noter_dette(session: str, nb: int, ancre: str = '', a=None) -> bool:
    # « t » date la dette : au démarrage, seule une synthèse faite après elle l'efface, et une autre session ne
    # la rappelle qu'au bout d'une heure ; même compte sur la même branche (Stop répétés pendant une pause,
    # relances) : la dette garde son âge. « ancre » la situe dans la conversation : une fourche ne l'efface que
    # si elle porte sur des demandes héritées. « rapports » : comptes rendus déjà là, qui ne la solderont pas.
    avant = lire_dette(session)
    if (isinstance(avant, dict) and entier(avant.get('nb')) == nb and reel(avant.get('t')) > 0
            and not (a is not None and abandonnee(a, str(avant.get('ancre') or '')))):
        t, date, rapports = reel(avant.get('t')), str(avant.get('date') or ''), signatures_vues(avant.get('rapports'))
    else:
        t, date, rapports = time.time(), time.strftime('%Y-%m-%d %H:%M'), []
        for _, sig, sig314 in rapport_durable(session, toutes=True):
            rapports += [sig, sig314]
    return ecrire_json(dossier_dettes() / (nom_sur(session) + '.json'),
                       {'session': session, 'nb': nb, 'ancre': ancre, 'date': date, 't': t, 'rapports': rapports[-40:]})


def dette_dans_fourche(d: dict, mere: str, point: str) -> bool:
    """La dette de la mère ne porte-t-elle que sur des demandes héritées par la fourche (son ancre est un
    ancêtre du point de fourche chez la mère) ? Invérifiable (pas d'ancre, uuids non partagés,
    transcript introuvable) : oui, la règle du compte suffit."""
    ancre = str(d.get('ancre') or '')
    if not ancre or not point:
        return True
    etat_m = lire_json(dossier_etat() / (nom_sur(mere) + '.json'), {})
    chemin = str(etat_m.get('transcript') or '') if isinstance(etat_m, dict) else ''
    if not chemin or not os.path.isfile(chemin):
        chemin = trouver_transcript(mere)
    if not chemin:
        return True
    am = analyser_transcript(chemin)
    if ancre in am.liens and point not in am.liens and am.taille:
        return False                     # point perdu, dette présente : notée sur un transcript reconstruit après la fourche
    if ancre not in am.liens or point not in am.liens:
        return True
    return ancre in (chaine_active(am.liens, point)[0] or set())


def lire_dette(session: str):
    v = lire_json(dossier_dettes() / (nom_sur(session) + '.json'), None)
    if isinstance(v, dict) and v.get('session'):
        return v
    ancien = lire_json(dossier_etat() / 'dette.json', {})
    return ancien.get(session) if isinstance(ancien, dict) and isinstance(ancien.get(session), dict) else None


def effacer_dette_si(session: str, couverte) -> bool:
    """Sous le verrou de la session, relit sa dette et ne l'efface que si « couverte(dette) » est vrai :
    une dette plus récente notée entre-temps par un Stop n'est jamais effacée sur une lecture périmée."""
    with verrou_session(session):
        v = lire_dette(session)
        if isinstance(v, dict) and couverte(v):
            return effacer_dette(session)
    return False


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
    with verrou_fichier(dossier_etat() / 'dette.json.verrou'):   # fichier partagé par toutes les sessions (format v3.1)
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
    if not planifie:          # au Stop suivant, ces demandes-là sont au transcript (ou ne le seront jamais)
        etat['prompts'] = []  # tour planifié : gardées (une demande de Baptiste a pu arriver pendant ce tour ;
                              # l'invite du tour planifié, une fois écrite, répond à la sienne)
    # Références : tampon et libération ramenés à la branche active (après /rewind, seules les
    # demandes encore actives restent couvertes). Un compte rendu nouveau (synthèse écrite sans
    # « tamponne », état perdu, transcript reconstruit) est ancré ici comme un tampon, plafonné au
    # compte du transcript, dès le premier Stop qui le voit : /rewind le ramène ensuite de même.
    valeur = rapport_durable(session)[0]
    souple = bool(etat.get('ancre_souple'))
    actif = couvertes(a, str(etat.get('ancre_tampon') or ''), entier(etat.get('tampon')), souple)
    rapport = -1
    # Un compte rendu se reconnaît à son contenu (compte, ancre, empreinte de sa section), pas à la date du
    # fichier (un checkout ou un clone la change) : réécrit après un /rewind avec le même en-tête, il est
    # relu. On examine le plus récent des comptes rendus jamais vus (une nouvelle synthèse dans un second
    # fichier n'est pas masquée par un ancien fichier touché après elle), puis tous ceux présents sont vus.
    # Il n'est adopté que s'il couvre davantage que le tampon actuel, mesuré sur la branche active.
    # État d'avant 3.13 : les comptes rendus présents sont réputés déjà vus ; signatures de 3.13 (sans
    # empreinte) et de 3.14 (empreinte du fichier entier) : reconnues.
    presentes = rapport_durable(session, toutes=True)
    vus = etat.get('rapports_vus')
    if not isinstance(vus, list):
        vus = [sig for _, sig, _ in presentes] if valeur >= 0 and (entier(etat.get('tampon')) >= 0 or etat.get('rapport_vu')) else []
    vus = signatures_vues(vus)
    anciennes = [x for x in vus if len(x) == 2]                     # signatures de 3.13, converties une fois
    vus = [x for x in vus if len(x) == 3] + [sig for _, sig, _ in presentes if sig[:2] in anciennes]
    deja_vu = lambda sig, sig314: sig in vus or sig314 in vus
    if valeur >= 0 and not a.ancre:
        rapport = valeur                 # transcript sans uuid : compte rendu pris tel quel
    else:
        nouveaux = [(d, sig) for d, sig, sig314 in presentes if not deja_vu(sig, sig314)]
        if nouveaux:
            date_r, (valeur_r, ancre_lue, _) = max(nouveaux, key=lambda x: (x[0], x[1][0]))
            # ancre du compte rendu : sa ligne « Ancre » si elle est au transcript, sinon l'entrée écrite
            # juste avant lui ; il ne couvre que les demandes écrites jusque-là (pas celles d'après lui,
            # ni les demandes de remplacement d'un /rewind)
            ancre_r = ancre_lue if ancre_lue in a.liens else (ancre_au_temps(a, date_r) or a.ancre)
            limite = a.liens[ancre_r][2] if ancre_r in a.liens else a.taille
            candidat = min(valeur_r, sum(1 for _, debut in a.unites if debut <= limite))
            if couvertes(a, ancre_r, candidat) > actif:
                etat.update({'tampon': candidat, 'ancre_tampon': ancre_r, 'ancre_souple': False, 't_tampon': date_r,
                             'tampon_fourche': False})
                souple = False
    for _, sig, sig314 in presentes:                      # tous les fichiers présents : vus (aussi sous la
        vus += [x for x in (sig, sig314) if x not in vus]   # forme de 3.14, pour une copie 3.14 à côté)
    etat['rapports_vus'] = vus[-40:]
    propre = max(couvertes(a, str(etat.get('ancre_tampon') or ''), entier(etat.get('tampon')), souple), rapport)
    synthese = max([propre] + [synthese_heritee(p, n, a) for p, n in a.parents.items() if p != session])
    etat['couvert'] = synthese          # couverture effective, lue par les fourches de cette session
    reference = max(synthese, couvertes(a, str(etat.get('ancre_libere') or ''), entier(etat.get('libere_a'))))
    dettes = lire_dettes()
    due = nb >= SEUIL_MIN and not (reference >= 0 and nb - reference < SEUIL_REFRESH)
    due_synthese = nb >= SEUIL_MIN and not (synthese >= 0 and nb - synthese < SEUIL_REFRESH)
    d = dettes.get(session)
    if isinstance(d, dict):
        rembobinee = abandonnee(a, str(d.get('ancre') or ''))       # la dette est sur une branche quittée par /rewind
        # Preuve que la synthèse couvre la dette : elle en couvre au moins le compte ; la session elle-même
        # (pas une fourche, qui ne couvre que jusqu'à son point) l'a faite après elle ; ou le transcript
        # garde, jusqu'à l'ancre de la dette, au moins autant de demandes qu'elle en comptait (comptes
        # comparables). Un transcript reconstruit depuis une compaction, plus court, ne la solde pas.
        nb_d, ancre_d = entier(d.get('nb'), 0), str(d.get('ancre') or '')
        preuve = (synthese >= nb_d
                  or (reel(etat.get('t_tampon')) > reel(d.get('t')) and not etat.get('tampon_fourche'))
                  or (ancre_d in a.liens and sum(1 for _, x in a.unites if x <= a.liens[ancre_d][2]) >= nb_d)
                  or 'ancre' not in d)            # dette d'avant 3.12 : invérifiable, règle de 3.13
        if synthese >= 0 and not due_synthese and preuve:
            effacer_dette(session)       # synthèse reconnue (même sans « tamponne »)
        elif rembobinee and not due_synthese:
            effacer_dette(session)       # /rewind sous le seuil : plus rien à synthétiser
        elif rembobinee and entier(d.get('nb'), 0) > nb:
            noter_dette(session, nb, a.ancre, a)     # /rewind : la dette suit la branche active
    elif due_synthese and not due:
        noter_dette(session, nb, a.ancre, a)         # seule la libération retient : la dette doit rester notée
    for mere, herite in a.parents.items():   # la synthèse propre de cette fourche couvre ce qu'elle a hérité
        if mere != session and propre >= herite:
            couvrir_mere(mere, herite, a.fourches.get(mere, ''))
            effacer_dette_si(mere, lambda d, h=herite, m=mere: entier(d.get('nb'), 0) <= h
                             and dette_dans_fourche(d, m, a.fourches.get(m, '')))
    # Pause quand la session attend du travail né depuis la dernière demande humaine (tâche en
    # cours ou en file, réveil planifié) : jusqu'à la demande suivante. Une attente plus ancienne
    # (serveur de dev, surveillance sans fin) ne suspend plus rien.
    attente = set()
    for x in entree.get('background_tasks') or []:
        if isinstance(x, dict) and x.get('status', 'running') in ('running', 'pending'):
            attente.add('t:' + str(x.get('id') or x.get('description') or len(attente)))
    for x in entree.get('session_crons') or []:
        if isinstance(x, dict):
            attente.add('c:' + str(x.get('id') or x.get('prompt') or len(attente)))
    pause = etat.get('pause') if isinstance(etat.get('pause'), dict) else {}
    vues = {k: min(entier(n, nb), nb) for k, n in pause.items() if k in attente}   # /rewind : jamais au-delà du compte actif
    for k in attente:
        vues.setdefault(k, nb)
    etat['pause'] = vues
    etat.pop('pause_ids', None); etat.pop('pause_nb', None)
    if any(n >= nb for n in vues.values()):
        if due:
            noter_dette(session, nb, a.ancre, a)     # si la discussion est abandonnée pendant l'attente
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
        notee = noter_dette(session, nb, a.ancre, a)
        if os.environ.get('CLAUDE_CODE_REMOTE') or not notee:
            ou = (('la dette n\'a pas pu être notée (' + str(dossier_dettes()) + ') ; ' if not notee else
                   'en cloud, le rappel ne survit pas au conteneur : ')
                  + 'ajoute « Synthèse due : session ' + session + ' » en P0 de next-actions.md')
        else:
            ou = 'elle sera rappelée au prochain démarrage sur cette machine'
        sortie({'systemMessage': f'Vive mémoire : synthèse non faite après {MAX_RELANCES} relances ({nb} demandes) ; {ou}.'})
        return 0
    etat['relances'] = relances + 1
    if not ecrire_json(f_etat, etat):
        sortie({'systemMessage': 'Vive mémoire : état non inscriptible (' + str(f_etat.parent) + '), synthèse non vérifiée.'})
        return 0
    noter_dette(session, nb, a.ancre, a)   # effacée par « tamponne » ; rappelée si la discussion est abandonnée
    commande = f'python3 "{ICI / "vive_memoire.py"}" tamponne {session}'
    sortie({'decision': 'block', 'reason': (
        f'Vive mémoire : cette discussion compte {nb} demandes de Baptiste et aucune synthèse récente '
        f'(relance {relances + 1}/{MAX_RELANCES}). Exécute la skill « vive-memoire » (fichier : {chemin_skill()}) : '
        'compte rendu de session (avec les lignes « Session : ' + session + ' » puis « Demandes : ' + str(nb) + ' »), décisions D-xxx, backlog, '
        'skills à faire grossir, ponts IA, journal Notion, bilan interactif publié, commit + push. '
        f'Termine par : {commande}. Si cette synthèse est déjà faite dans cette discussion, lance seulement cette commande.')})
    return 0


def derniere_assistant(chemin: str) -> str:
    """uuid de la dernière entrée assistant du transcript (lu par la fin) ; '' sinon."""
    try:
        with open(chemin, 'rb') as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 262144))
            bloc = f.read()
    except OSError:
        return ''
    for ligne in reversed(bloc.split(b'\n')):
        if b'"assistant"' not in ligne:
            continue
        try:
            o = json.loads(ligne.decode('utf-8', 'replace'))
        except (ValueError, RecursionError):
            continue
        if isinstance(o, dict) and o.get('type') == 'assistant' and o.get('uuid') and not o.get('isSidechain'):
            return str(o['uuid'])
    return ''


def prendre_verrou(dossier: Path, cle: str, contenu: str = '') -> bool:
    """Pose le verrou de « cle », valable 2 s (au-delà : un autre événement, le verrou est remplacé).
    False : une autre copie le tient ; True : posé, ou impossible à poser (agir quand même)."""
    verrou = dossier / hashlib.sha1(cle.encode('ascii')).hexdigest()[:24]
    for _ in range(2):
        try:
            fd = os.open(str(verrou), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, contenu.encode('ascii', 'replace'))
            finally:
                os.close(fd)
            return True
        except FileExistsError:
            try:
                lu = verrou.read_text(encoding='ascii', errors='replace') if contenu else ''
                if time.time() - verrou.stat().st_mtime < 2 and not (contenu and lu and lu != contenu):
                    return False          # une autre copie traite cet événement (même entrée, même feuille)
                os.rename(str(verrou), f'{verrou}.perime.{os.getpid()}')   # une seule copie y parvient
            except OSError:
                pass
        except OSError:
            return True
    return False


def cles_anciennes(mode: str, entree: dict, pairs: set) -> list:
    """Clés de verrou des versions 3.6 et 3.7, à prendre aussi quand une copie de cette version tourne à côté."""
    cles = []
    if (3, 7) in pairs:
        cles.append(json.dumps([mode, entree.get('session_id'), entree.get('transcript_path'), entree.get('prompt'),
                                entree.get('prompt_id'), entree.get('source'), entree.get('stop_hook_active')],
                               ensure_ascii=True, default=str))
    if (3, 6) in pairs:
        chemin = str(entree.get('transcript_path') or '')
        try:
            taille = os.path.getsize(chemin) if chemin else -1
        except OSError:
            taille = -1
        cles.append(json.dumps([mode, entree.get('session_id'), chemin, taille, entree.get('prompt'), entree.get('source'),
                                entree.get('stop_hook_active')], ensure_ascii=True, default=str))
    return cles


def premiere_copie(mode: str, entree: dict, pairs: set = frozenset()) -> bool:
    """Plusieurs copies (utilisateur, dépôt) reçoivent le même événement en parallèle, avec la même
    entrée : seule la première à en poser le verrou agit. Clé FIGÉE depuis 3.8 (toute l'entrée) : ne
    plus jamais la changer, une copie d'une autre version ne la verrait pas. Avec une copie 3.6 ou 3.7
    à côté (« pairs »), sa clé est prise aussi. VM_VERROU=non coupe tout (banc)."""
    if os.environ.get('VM_VERROU') == 'non':
        return True
    dossier = dossier_etat() / 'evenements'
    try:
        dossier.mkdir(parents=True, exist_ok=True)
    except OSError:
        return True                       # verrou impossible : agir quand même (au pire deux fois)
    # Stop : deux Stop distincts peuvent avoir la même entrée ; la dernière réponse écrite les distingue
    # (la même pour toutes les copies d'un événement), gardée dans le verrou sans changer sa clé.
    feuille = derniere_assistant(str(entree.get('transcript_path') or '')) if mode == 'stop' else ''
    with verrou_fichier(dossier / '.prise'):     # décision sérialisée entre copies (plus de course stat/renommage)
        for cle in [json.dumps([mode, entree], sort_keys=True, ensure_ascii=True, default=str)] + cles_anciennes(mode, entree, pairs):
            if not prendre_verrou(dossier, cle, feuille):
                return False
    try:
        limite = time.time() - 60
        for f in dossier.iterdir():
            if f.stat().st_mtime < limite:
                f.unlink()
    except OSError:
        pass
    return True


@contextmanager
def verrou_fichier(chemin: Path):
    """Verrou exclusif (flock) sur un fichier ; sans fcntl ou sans dossier inscriptible : sans effet."""
    fd = None
    if fcntl is not None:
        try:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(chemin), os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
        except OSError:
            pass
    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


@contextmanager
def verrou_session(session: str):
    """Sérialise lecture-modification-écriture de l'état d'une session : un UserPromptSubmit pendant
    un Stop (ou un tampon) ne perd plus la mise à jour de l'autre. Sans fcntl : sans effet."""
    with verrou_fichier(dossier_etat() / (nom_sur(session) + '.verrou')):
        yield


def commande_vive_memoire(commande) -> str:
    """Chemin du script si la commande est l'une des nôtres (bash <…>/vive-memoire-stop.sh|prompt.sh [mode],
    quelle que soit la façon de la citer) ; '' sinon."""
    try:
        mots = shlex.split(str(commande or ''))
    except ValueError:
        return ''
    if mots and mots[0] == 'bash':
        mots = mots[1:]
    if 1 <= len(mots) <= 2 and re.search(r'(^|/)vive-memoire-(stop|prompt)\.sh$', mots[0]) \
            and (len(mots) == 1 or mots[1] in ('stop', 'prompt', 'debut')):
        return mots[0]
    return ''


COQUILLES = {'sh', 'bash', 'dash', 'zsh', 'ksh', 'fish', 'env', 'nohup', 'timeout', 'nice', 'stdbuf', 'script'}


def ligne_de_commande(pid: int):
    """(arguments, pid parent) d'un processus : liste exacte par /proc (Linux), sinon texte de « ps »
    (macOS : arguments joints par des espaces) ; None si illisible."""
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            args = [x.decode('utf-8', 'replace') for x in f.read().split(b'\0') if x]
        with open(f'/proc/{pid}/stat', 'rb') as f:
            parent = int(f.read().rsplit(b')', 1)[1].split()[1])
        return args, parent
    except (OSError, ValueError, IndexError):
        pass
    try:
        r = subprocess.run(['ps', '-ww', '-o', 'ppid=', '-o', 'command=', '-p', str(pid)], capture_output=True, text=True, timeout=2)
        parent, _, texte = r.stdout.strip().partition(' ')
        return texte.strip(), int(parent)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def sources_reglages(args):
    """Sources de réglages demandées par --setting-sources (la dernière occurrence l'emporte, comme dans
    Claude Code ; rien après « -- ») ; None sans le drapeau. args : liste exacte, ou texte de « ps »."""
    if isinstance(args, str):
        texte = (' ' + args + ' ').split(' -- ')[0]
        trouves = re.findall(r'\s--setting-sources(?:=|\s+)((?:[\w-]+\s*,\s*)*[\w-]*)', texte)
        valeur = trouves[-1] if trouves else None
    else:
        valeur = None
        for k, x in enumerate(args):
            if x == '--':
                break
            if x == '--setting-sources' and k + 1 < len(args):
                valeur = args[k + 1]
            elif x.startswith('--setting-sources='):
                valeur = x.split('=', 1)[1]
    return None if valeur is None else [v.strip() for v in valeur.split(',') if v.strip()]


def reglages_utilisateur_charges() -> bool:
    """Faux seulement si le processus qui a lancé le hook (Claude Code : le premier ancêtre qui n'est pas
    un shell) porte --setting-sources sans « user » : les réglages utilisateur, donc la copie qui y est
    enregistrée, ne sont pas chargés dans cette session. On ne remonte jamais au-delà de lui."""
    pid = os.getppid()
    for _ in range(8):
        lu = ligne_de_commande(pid) if pid > 1 else None
        if not lu:
            return True
        args, parent = lu
        premier = args[0] if isinstance(args, list) and args else (args.split() or [''])[0] if isinstance(args, str) else ''
        if os.path.basename(premier).lstrip('-') in COQUILLES:
            pid = parent
            continue
        sources = sources_reglages(args)
        return sources is None or 'user' in sources
    return True


def installation_enregistree(dossier: Path) -> bool:
    """La copie de « dossier » est-elle enregistrée dans les réglages utilisateur, lisibles par Claude Code ?"""
    reglages = lire_json(dossier_config() / 'settings.json', None)
    hooks = reglages.get('hooks') if isinstance(reglages, dict) else None
    cible = os.path.normpath(str(dossier / 'vive-memoire-stop.sh'))
    for groupes in (hooks.values() if isinstance(hooks, dict) else []):
        for g in (groupes if isinstance(groupes, list) else []):
            for h in (g.get('hooks') if isinstance(g, dict) and isinstance(g.get('hooks'), list) else []):
                chemin = commande_vive_memoire(h.get('command') if isinstance(h, dict) else '')
                if chemin and os.path.normpath(os.path.expanduser(chemin)) == cible:
                    return True
    return False


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
        quelle = 'antérieure à 3.5' if v == (0,) else '.'.join(map(str, v))
        print(f'Vive mémoire : la copie installée dans {installee.parent} (version {quelle}) est plus ancienne '
              f'que celle du dépôt ({VERSION}) ; relance « bash {ICI / "installe-mac.sh"} » pour la mettre à jour.')


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'stop'
    if mode == 'tamponne':
        session = (sys.argv[2] if len(sys.argv) > 2 else '') or os.environ.get('CLAUDE_CODE_SESSION_ID', '')
        if not session:
            print('Vive mémoire : identifiant de session inconnu (argument ou CLAUDE_CODE_SESSION_ID).')
            return 1
        with verrou_session(session):
            return mode_tamponne(session, '')
    brut = sys.stdin.read()
    entree = json.loads(brut) if brut.strip() else {}
    if not isinstance(entree, dict):
        return 0
    session = str(entree.get('session_id') or '')
    if not session:
        return 0
    # L'enveloppe dit quelle copie on est. « doublon » : copie d'un dépôt alors qu'une installation
    # utilisateur est enregistrée. Celle-ci d'avant le verrou par événement : ≤ 3.4, elle seule agit
    # (comme avant) ; 3.5, elle seule agit si sa marque montre qu'elle a tourné dans la session.
    # Sinon toute copie passe par le verrou : réglages utilisateur illisibles ou non chargés
    # (--setting-sources, lu sur la ligne de commande de Claude Code) = la copie du dépôt agit. La copie utilisateur pose encore la marque,
    # pour qu'une copie de dépôt 3.5 (sans verrou) se taise.
    copie = os.environ.get('VM_COPIE', '')
    installee = Path(os.environ.get('VM_COPIE_UTILISATEUR') or '')
    if copie in ('doublon', 'depot') and not os.environ.get('CLAUDE_CODE_REMOTE') and installee.is_file():
        # l'enveloppe devine par grep ; ici on lit vraiment les réglages (JSON invalide = ignoré par Claude Code)
        copie = 'doublon' if installation_enregistree(installee.parent) else 'depot'
    if copie == 'doublon' and not reglages_utilisateur_charges():
        copie = 'depot'                   # --setting-sources sans « user » : la copie installée ne tourne pas ici
    marque = dossier_etat() / 'actifs' / nom_sur(session)
    if copie == 'utilisateur':
        try:                              # marque lue par une copie de dépôt 3.5 (qui se tait alors)
            marque.parent.mkdir(parents=True, exist_ok=True)
            marque.touch()
        except OSError:
            pass
    elif copie == 'doublon':
        v = version_de(installee)
        if mode == 'debut':
            signaler_version(installee)
        if v in ((0,), (3, 6)) or ((0,) < v < (3, 6) and (marque.exists() or mode == 'debut')):
            return 0                      # ≤ 3.4 et 3.6 : elle agit seule ; 3.5 : elle a tourné (au démarrage : elle seule)
    # Une copie 3.6 ou 3.7 à côté (installée, ou dans le dépôt ouvert) a sa propre clé de verrou : la
    # prendre aussi, seulement dans ce cas (sinon des événements distincts se confondraient).
    pairs = set()
    if copie == 'doublon':
        pairs.add(v)
    elif copie == 'utilisateur' and os.environ.get('CLAUDE_PROJECT_DIR'):
        pairs.add(version_de(Path(os.environ['CLAUDE_PROJECT_DIR']) / '.claude/hooks/vive_memoire.py'))
    if not premiere_copie(mode, entree, pairs):
        return 0
    if mode == 'debut':
        return mode_debut(session, str(entree.get('source') or ''))
    f_etat = dossier_etat() / (nom_sur(session) + '.json')
    with verrou_session(session):
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
