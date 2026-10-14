"""Banc des hooks « vive mémoire » : une soixantaine de vérifications, dans un HOME et un état temporaires isolés.

Usage : python3 teste_vive_memoire.py      (code 0 si tout passe)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
echecs, total = [], 0
BASE_ENV = {k: v for k, v in os.environ.items()
            if k not in ('VM_ETAT', 'VM_MEMOIRE', 'CLAUDE_CONFIG_DIR', 'CLAUDE_CODE_REMOTE', 'CLAUDE_PROJECT_DIR')}


def verifie(nom, condition, detail=''):
    global total
    total += 1
    print(('ok   ' if condition else 'ÉCHEC') + ' ' + nom + ('' if condition else '  → ' + str(detail)[:300]))
    if not condition:
        echecs.append(nom)


class Bac:
    def __init__(self):
        self.racine = Path(tempfile.mkdtemp(prefix='vm-'))
        self.home = self.racine / 'home'
        self.projet = self.racine / 'projet'
        (self.projet / '.claude/hooks').mkdir(parents=True)
        self.home.mkdir()
        for f in ('vive_memoire.py', 'vive-memoire-stop.sh', 'vive-memoire-prompt.sh'):
            shutil.copy(ICI / f, self.projet / '.claude/hooks' / f)
        self.hooks = self.projet / '.claude/hooks'
        self.enveloppe = self.hooks / 'vive-memoire-stop.sh'
        self.etat = self.home / '.claude/vive-memoire'

    def env(self, sup=None):
        e = dict(BASE_ENV, HOME=str(self.home), CLAUDE_PROJECT_DIR=str(self.projet))
        e.update(sup or {})
        return e

    def transcript(self, nom, entrees):
        p = self.racine / (nom + '.jsonl')
        p.write_text('\n'.join(json.dumps(x) for x in entrees) + '\n', encoding='utf-8')
        return str(p)

    def appel(self, mode, entree, sup=None, enveloppe=None):
        r = subprocess.run(['bash', str(enveloppe or self.enveloppe), mode], capture_output=True, text=True, timeout=30,
                           input=entree if isinstance(entree, str) else json.dumps(entree), env=self.env(sup))
        brut = r.stdout.strip()
        try:
            j = json.loads(brut.splitlines()[-1]) if brut else {}
        except ValueError:
            j = {'brut': brut}
        return r.returncode, j, r.stdout, r.stderr

    def stop(self, session, transcript, **kw):
        return self.appel('stop', {'session_id': session, 'transcript_path': transcript, 'stop_hook_active': False, **kw})[:2]

    def python(self, *args, sup=None):
        return subprocess.run([sys.executable, '-I', str(self.hooks / 'vive_memoire.py'), *args], capture_output=True, text=True, env=self.env(sup))

    def dette(self):
        dettes = {}
        for f in (self.etat / 'dettes').glob('*.json'):
            v = json.loads(f.read_text())
            dettes[v['session']] = v
        return dettes

    def poser_dette(self, session, **v):
        (self.etat / 'dettes').mkdir(parents=True, exist_ok=True)
        (self.etat / 'dettes' / (session + '.json')).write_text(json.dumps(dict({'session': session, 'nb': 4, 'date': 'x', 't': 0}, **v)))


def humain(t, **kw):
    return {'type': 'user', 'origin': {'kind': 'human'}, 'message': {'role': 'user', 'content': t}, **kw}


def notif(t):
    return {'type': 'user', 'origin': {'kind': 'task-notification'}, 'message': {'role': 'user', 'content': t}}


def ancien(t):
    return {'type': 'user', 'message': {'role': 'user', 'content': t}}


def file_humaine(t, uuid):
    return {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': t, 'source_uuid': uuid, 'humanTurn': True}}


def bloque(j):
    return j.get('decision') == 'block'


def assistant(uuid, parent):
    return {'type': 'assistant', 'uuid': uuid, 'parentUuid': parent, 'message': {'role': 'assistant', 'content': 'ok'}}


def ajouter(chemin, *entrees):
    with open(chemin, 'a', encoding='utf-8') as f:
        for x in entrees:
            f.write(json.dumps(x) + '\n')


b = Bac()
t3 = b.transcript('t3', [humain('a'), humain('b'), notif('<task-notification> x'), humain('c')])
t4 = b.transcript('t4', [humain('a'), humain('b'), humain('c'), humain('d')])
rc, j = b.stop('S1', t3)
verifie('01. trois demandes humaines : pas de blocage', rc == 0 and not bloque(j), j)
rc, j = b.stop('S1', t4)
verifie('02. quatre demandes : blocage JSON, code 0', rc == 0 and bloque(j) and '4 demandes' in j.get('reason', ''), j)
verifie('03. la consigne donne la commande tamponne (chemin cité)', 'vive_memoire.py" tamponne S1' in j.get('reason', ''), j.get('reason', '')[:200])
verifie('04. dette notée dès le premier blocage', 'S1' in b.dette(), b.dette())
tw = b.transcript('tw', [humain('a')] + [notif('<github-webhook-activity> ci')] * 5)
verifie('05. webhooks et notifications ne comptent pas', not bloque(b.stop('S2', tw)[1]))
ta = b.transcript('ta', [ancien('a'), ancien('b'), ancien('<github-webhook-activity> x'), ancien('<task-notification> y'), ancien('c')])
verifie('06. repli sans « origin » : préfixes techniques exclus', not bloque(b.stop('S3', ta)[1]))
tq = b.transcript('tq', [humain('a'), humain('b'), humain('c'), file_humaine('merge', 'U1'), file_humaine('merge', 'U1'),
                         {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': '<github-webhook-activity>', 'source_uuid': 'U2'}}])
rc, j = b.stop('S4', tq)
verifie('07. commande en file humaine comptée une fois', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tf = b.transcript('tf', [humain('a'), humain('b'), file_humaine('c', 'U9'), humain('c\nd', uuid='E1', mergedSendUuids=['U9'])])
rc, j = b.stop('S5', tf)
verifie('08. fusion réelle : envoi en file + envoi propre = 2 demandes, pas 1 ni 3', bloque(j) and '4 demandes' in j.get('reason', ''), j)
b.appel('prompt', {'session_id': 'S6', 'prompt': 'quatrième demande pas encore écrite', 'transcript_path': t3})
b.appel('prompt', {'session_id': 'S6', 'prompt': '<task-notification> automatique', 'transcript_path': t3})
rc, j = b.stop('S6', t3)
verifie('09. demande pas encore au transcript comptée (écriture différée)', bloque(j) and '4 demandes' in j.get('reason', ''), j)
codes = [bloque(b.stop('S7', t4)[1]) for _ in range(3)]
rc, j = b.stop('S7', t4)
verifie('10. trois relances puis libération avec message', codes == [True] * 3 and not bloque(j) and 'systemMessage' in j, [codes, j])
verifie('11. après libération, plus de relance sans nouvelles demandes', not bloque(b.stop('S7', t4)[1]))
t12 = b.transcript('t12', [humain(str(i)) for i in range(12)])
verifie('12. huit nouvelles demandes : relance de nouveau', bloque(b.stop('S7', t12)[1]))
rc, j, out, _ = b.appel('debut', {'session_id': 'S8', 'source': 'startup'})
verifie('13. dette récente d\'une autre session : pas rappelée (session peut-être en cours)', 'S7' not in out, out[:200])
b.poser_dette('S7', nb=b.dette()['S7']['nb'], t=time.time() - 7200)
rc, j, out, _ = b.appel('debut', {'session_id': 'S8', 'source': 'startup'})
verifie('14. dette de plus d\'une heure : rappelée au démarrage, chemin cité', 'S7' in out and 'vive_memoire.py" tamponne' in out, out[:200])
rc, j, out, _ = b.appel('debut', {'session_id': 'S7', 'source': 'resume'})
verifie('15. reprise de la session endettée : sa propre dette est rappelée', 'S7' in out, out[:200])
r = b.python('tamponne', 'S7')
verifie('16. tamponne enregistre et efface la dette', r.returncode == 0 and 'S7' not in b.dette(), r.stdout + str(b.dette()))
r = b.python('tamponne', 'INCONNUE')
verifie('17. tamponne sans transcript : erreur, rien d\'écrit', r.returncode == 1 and not (b.etat / 'INCONNUE.json').exists(), r.stdout)
rc, j = b.stop('S1', t4)
rc2, j2 = b.stop('S9', t4)
verifie('18. deux sessions ont chacune leur état', 'relance 2/3' in j.get('reason', '') and 'relance 1/3' in j2.get('reason', ''), [j, j2])
verifie('19. tâche en cours : pause sans relance', not bloque(b.stop('S10', t4, background_tasks=[{'id': 'w1', 'status': 'running'}])[1]))
verifie('19b. … et la dette est notée pendant la pause', 'S10' in b.dette(), b.dette())
verifie('20. tâche en file (pending) : pause aussi', not bloque(b.stop('S11', t4, background_tasks=[{'id': 'q1', 'status': 'pending'}])[1]))
verifie('21. réveil planifié (ponctuel ou récurrent) : pause aussi', not bloque(b.stop('S12', t4, session_crons=[{'id': 'c1', 'recurring': True}])[1]))
t5 = b.transcript('t5', [humain(str(i)) for i in range(5)])
rc, j = b.stop('S10', t5, background_tasks=[{'id': 'w1', 'status': 'running'}])
verifie('22. même tâche sans fin + nouvelle demande : la pause cesse', bloque(j), j)
t6 = b.transcript('t6', [humain(str(i)) for i in range(6)])
rc, j = b.stop('S10', t6, background_tasks=[{'id': 'w1', 'status': 'running'}, {'id': 'b6', 'status': 'running'}])
verifie('22b. tâche courte née de la nouvelle demande : pause', not bloque(j), j)
rc, j = b.stop('S10', t6, background_tasks=[{'id': 'w1', 'status': 'running'}])
verifie('22c. tâche courte finie, serveur sans fin restant : la pause cesse', bloque(j), j)
bloqueur = b.racine / 'fichier-ordinaire'; bloqueur.write_text('')
rc, j, _, _ = b.appel('stop', {'session_id': 'S13', 'transcript_path': t4}, {'VM_ETAT': str(bloqueur / 'etat')})
verifie('23. état non inscriptible : message, pas de blocage', not bloque(j) and 'systemMessage' in j, j)
seul = b.racine / 'seul'; seul.mkdir(); shutil.copy(ICI / 'vive-memoire-stop.sh', seul / 'vive-memoire-stop.sh')
rc, j, out, err = b.appel('stop', {'session_id': 'S14', 'transcript_path': t4}, enveloppe=seul / 'vive-memoire-stop.sh')
verifie('24. vive_memoire.py absent : silence, code 0', rc == 0 and j == {}, [j, err])
faux = b.racine / 'bin'; faux.mkdir()
for c in ('bash', 'cat', 'dirname', 'printf', 'grep'):
    w = shutil.which(c)
    if w:
        os.symlink(w, faux / c)
rc, j, _, err = b.appel('stop', {'session_id': 'S15', 'transcript_path': t4}, {'PATH': str(faux)})
verifie('25. sans python3 : message, pas de blocage', rc == 0 and 'systemMessage' in j and not bloque(j), [j, err])
mem = b.projet / 'docs/context'; (mem / 'sessions').mkdir(parents=True); (mem / 'decision-log.md').write_text('# D\n')
(mem / 'sessions/2026-10-14-a.md').write_text('# CR\n\nSession : S16\nDemandes : 4\n')
(mem / 'sessions/2026-10-14-b.md').write_text('Rattrapage de la session S17 (citée, sans bloc)\nDemandes : 99\n')
verifie('26. tampon durable (bloc Session/Demandes) reconnu', not bloque(b.stop('S16', t4)[1]))
verifie('27. compte rendu tiers citant l\'id : ignoré', bloque(b.stop('S17', t4)[1]))
(mem / 'sessions/2026-10-14-c.md').write_text('# CR\n\n`Session : S24`\n**Demandes** : 4\n')
verifie('27b. tampon durable mis en forme Markdown reconnu', not bloque(b.stop('S24', t4)[1]))
tk = b.transcript('tk', [humain(x, forkedFrom={'sessionId': 'S16'}) for x in 'abcd'] + [humain('e')])
verifie('28. fourche : hérite de la synthèse de la session mère', not bloque(b.stop('S18', tk)[1]))
(mem / 'sessions/2026-10-14-d.md').write_text('Session : S25\nDemandes : 40\n')
tk2 = b.transcript('tk2', [humain(x, forkedFrom={'sessionId': 'S25'}) for x in 'ab'] + [humain(str(i)) for i in range(10)])
verifie('28b. fourche : héritage plafonné aux demandes copiées (mère synthétisée plus tard)', bloque(b.stop('S26', tk2)[1]))
inst = b.home / '.claude/hooks/vive-memoire'; inst.mkdir(parents=True)
for f in ('vive_memoire.py', 'vive-memoire-stop.sh'):
    shutil.copy(ICI / f, inst / f)
verifie('29a. fichiers utilisateur sans enregistrement : la copie du dépôt reste active', bloque(b.stop('S19', t4)[1]))
(b.home / '.claude/settings.json').write_text(json.dumps({'hooks': {'Stop': [{'hooks': [{'command': f'bash "{inst}/vive-memoire-stop.sh" stop'}]}]}}))
verifie('29b. installation utilisateur enregistrée : la copie du dépôt se tait', b.stop('S20', t4)[1] == {})
rc, j, _, _ = b.appel('stop', {'session_id': 'S20', 'transcript_path': t4}, enveloppe=inst / 'vive-memoire-stop.sh')
verifie('29c. … et la copie utilisateur prend le relais', bloque(j), j)
rc, j, _, _ = b.appel('stop', {'session_id': 'S21', 'transcript_path': t4}, {'CLAUDE_CODE_REMOTE': '1'})
verifie('29d. en cloud, la copie du dépôt ne se tait jamais', bloque(j), j)
(inst / 'vive_memoire.py').write_text('# ancienne version\n')
rc, j, out, _ = b.appel('debut', {'session_id': 'S20', 'source': 'startup'})
verifie('29e. copie utilisateur périmée : signalée au démarrage', 'diffère' in out, out[:200])
shutil.rmtree(b.home / '.claude/hooks'); (b.home / '.claude/settings.json').unlink()
ti = b.transcript('ti', [humain('a'), humain('b'), humain('c'),
                         {'type': 'user', 'origin': {'kind': 'human'}, 'uuid': 'IMG', 'message': {'role': 'user', 'content': [{'type': 'image', 'source': {}}]}}])
verifie('30d. image seule envoyée par Baptiste : comptée', bloque(b.stop('S27', ti)[1]))
tm = b.transcript('tm', [ancien('a'), ancien('b'), ancien('c'), humain('d')])
verifie('30e. transcript mixte (ancien format puis origin) : demandes additionnées', bloque(b.stop('S28', tm)[1]))
tq2 = b.transcript('tq2', [humain('a'), humain('b'), humain('c')])
b.appel('prompt', {'session_id': 'S29', 'prompt': 'merge', 'transcript_path': tq2})
ajouter(tq2, file_humaine('merge', 'Q1'))
rc, j = b.stop('S29', tq2)
verifie('30f. demande absorbée en cours de tour : pas comptée deux fois', bloque(j) and '4 demandes' in j.get('reason', ''), j)
b.poser_dette('ANCIENNE')
r = b.python('tamponne', 'ANCIENNE')
verifie('30g. dette dont le transcript a disparu : effacée', r.returncode == 0 and 'ANCIENNE' not in b.dette(), r.stdout)
b.poser_dette('MERE', nb=5)
tfm = b.transcript('FILLE', [humain(x, forkedFrom={'sessionId': 'MERE'}) for x in 'abcde'] + [humain('f')])
proj = b.home / '.claude/projects/p'; proj.mkdir(parents=True); shutil.copy(tfm, proj / 'FILLE.jsonl')
r = b.python('tamponne', 'FILLE')
verifie('30h. tamponner une fourche efface la dette de sa mère', r.returncode == 0 and 'MERE' not in b.dette(), [r.stdout, b.dette()])
cfg = b.racine / 'cfg'; (cfg / 'projects/q').mkdir(parents=True); shutil.copy(t4, cfg / 'projects/q/CFG.jsonl')
r = b.python('tamponne', 'CFG', sup={'CLAUDE_CONFIG_DIR': str(cfg)})
verifie('30i. CLAUDE_CONFIG_DIR respecté (transcripts et état)', r.returncode == 0 and (cfg / 'vive-memoire/CFG.json').exists(), r.stdout)
b.poser_dette('MERE2', nb=10)
tfm2 = b.transcript('FILLE2', [humain(x, forkedFrom={'sessionId': 'MERE2'}) for x in 'abcde'] + [humain(str(i)) for i in range(6)])
shutil.copy(tfm2, proj / 'FILLE2.jsonl')
r = b.python('tamponne', 'FILLE2')
verifie('30j. dette de la mère comparée aux seules demandes héritées', 'MERE2' in b.dette(), [r.stdout, b.dette()])
ttl = b.transcript('ttl', [humain('a'), humain('b'), humain('c'),
                           {'type': 'queued_command', 'prompt': [{'type': 'text', 'text': 'en cours de tour'}], 'source_uuid': 'TL1', 'origin': {'kind': 'human'}}])
verifie('30k. commande en file au premier niveau (format récent) : comptée', bloque(b.stop('S30', ttl)[1]))
tr = b.transcript('tr', [humain('continue', promptId='P1'), humain('b', promptId='P2'), humain('c', promptId='P3')])
b.appel('prompt', {'session_id': 'S31', 'prompt': 'continue', 'prompt_id': 'P4', 'transcript_path': tr})
verifie('30l. même texte répété, pas encore écrit : compté', bloque(b.stop('S31', tr)[1]))
b.appel('prompt', {'session_id': 'S32', 'prompt': 'vérifie le build', 'prompt_id': 'P9', 'transcript_path': t3})
rc, j = b.stop('S32', t3, session_crons=[{'id': 'loop1', 'recurring': True}])
verifie('30m. tour planifié pas encore écrit : pas compté comme une demande', not bloque(j) and 'S32' not in b.dette(), j)
dettes_avant = set(b.dette())
for s in ('C1', 'C2'):
    b.stop(s, t4)
verifie('30n. deux sessions notent leur dette sans s\'écraser', {'C1', 'C2'} <= set(b.dette()), b.dette())
t40 = b.transcript('t40', [])
def envoyer(session, chemin, texte, ecrire=True):
    b.appel('prompt', {'session_id': session, 'prompt': texte, 'transcript_path': chemin})
    if ecrire:
        ajouter(chemin, humain(texte))
envoyer('S40', t40, 'go')
for i in range(2, 21):
    envoyer('S40', t40, f'demande {i}')
r = b.python('tamponne', 'S40')
for i in range(21, 28):
    envoyer('S40', t40, f'demande {i}')
envoyer('S40', t40, 'go', ecrire=False)
rc, j = b.stop('S40', t40)
verifie('30o. plus de 20 envois, texte d\'une vieille demande répété : la demande en attente compte',
        '20 demandes' in r.stdout and bloque(j) and '28 demandes' in j.get('reason', ''), [r.stdout, j])
tqc = b.transcript('tqc', [humain('a'), humain('b'), humain('c')])
b.appel('prompt', {'session_id': 'S41', 'prompt': 'ajoute ça', 'prompt_id': 'PQ', 'transcript_path': tqc})
ajouter(tqc, file_humaine('ajoute ça', 'AUTRE-ID'))
rc, j = b.stop('S41', tqc)
verifie('30p. commande absorbée sous un autre identifiant que le prompt_id : comptée une fois', bloque(j) and '4 demandes' in j.get('reason', ''), j)
branche = [humain('a', uuid='h1', parentUuid=None), assistant('a1', 'h1'), humain('b', uuid='h2', parentUuid='a1'), assistant('a2', 'h2'),
           humain('c', uuid='h3', parentUuid='a2'), assistant('a3', 'h3'), humain('d', uuid='h4', parentUuid='a3'), assistant('a4', 'h4'),
           humain('c bis', uuid='h3b', parentUuid='a2'), assistant('a3b', 'h3b')]
tbr = b.transcript('tbr', branche)
verifie('30q. /rewind : les tours abandonnés ne comptent pas (3 demandes actives sur 5 écrites)', not bloque(b.stop('S43', tbr)[1]))
ajouter(tbr, humain('d bis', uuid='h4b', parentUuid='a3b'), assistant('a4b', 'h4b'))
rc, j = b.stop('S43', tbr)
verifie('30q2. … et la branche active compte toutes ses demandes', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tcp = b.transcript('tcp', [humain('a', uuid='h1', parentUuid=None), assistant('a1', 'h1'), humain('b', uuid='h2', parentUuid='a1'), assistant('a2', 'h2'),
                           humain('c', uuid='h3', parentUuid='a2'), assistant('a3', 'h3'),
                           {'type': 'system', 'subtype': 'compact_boundary', 'uuid': 'B', 'parentUuid': None, 'logicalParentUuid': 'a3'},
                           humain('d', uuid='h4', parentUuid='B'), assistant('a4', 'h4')])
rc, j = b.stop('S44', tcp)
verifie('30r. compaction : la chaîne passe la frontière (logicalParentUuid)', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tpl = b.transcript('tpl', [humain('a', uuid='h1', parentUuid=None), assistant('a1', 'h1'), humain('b', uuid='h2', parentUuid='a1'),
                           assistant('t1', 'h2'), assistant('t2', 't1'),
                           {'type': 'user', 'uuid': 'r1', 'parentUuid': 't1', 'message': {'role': 'user', 'content': [{'type': 'tool_result'}]}},
                           {'type': 'user', 'uuid': 'r2', 'parentUuid': 't2', 'message': {'role': 'user', 'content': [{'type': 'tool_result'}]}},
                           assistant('a3', 'r2'), humain('c', uuid='h3', parentUuid='a3'), assistant('a4', 'h3'),
                           humain('d', uuid='h4', parentUuid='a4'),
                           {'type': 'user', 'uuid': 'r9', 'parentUuid': 't1', 'message': {'role': 'user', 'content': [{'type': 'tool_result'}]}}])
rc, j = b.stop('S45', tpl)
verifie('30r2. appels d\'outils parallèles (feuilles latérales) : aucune demande perdue', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tcs = b.transcript('tcs', [humain('a', uuid='h1', parentUuid='ABSENT'), humain('b', uuid='h2', parentUuid='h1'),
                           humain('c', uuid='h3', parentUuid='h1'), humain('d', uuid='h4', parentUuid='h3')])
rc, j = b.stop('S46', tcs)
verifie('30r3. chaîne rompue (parent absent du fichier) : rien n\'est filtré', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tann = b.transcript('tann', [humain('a'), humain('b'), humain('c')])
b.appel('prompt', {'session_id': 'S47', 'prompt': 'demande annulée avant écriture', 'transcript_path': tann})
rc, j = b.stop('S47', tann)
rc2, j2 = b.stop('S47', tann)
verifie('30t. demande jamais écrite : comptée à son Stop, plus aux suivants', bloque(j) and not bloque(j2), [j, j2])
b.poser_dette('D1', nb=4)
shutil.copy(t4, proj / 'D1.jsonl')
(b.etat / 'D1.json').mkdir()
r = b.python('tamponne', 'D1')
verifie('30s. tampon non inscriptible : la dette reste', r.returncode == 1 and 'D1' in b.dette(), [r.returncode, r.stdout, b.dette()])
rc, j, _, _ = b.appel('stop', 'pas du json')
verifie('30a. entrée invalide : code 0, rien', rc == 0 and j == {}, j)
verifie('30b. transcript illisible (dossier) : pas de blocage', not bloque(b.stop('S22', str(b.racine))[1]))
verifie('30c. le hook ne sort jamais en code 2', {b.stop('S23', t4)[0] for _ in range(5)} == {0})

# --- installeur Mac, dans un HOME temporaire
h = b.racine / 'mac'; (h / '.claude').mkdir(parents=True)
(h / '.claude/settings.json').write_text(json.dumps({'model': 'opus', 'hooks': {'Stop': [{'matcher': '', 'hooks': [
    {'type': 'command', 'command': 'echo voisin'}, {'type': 'command', 'command': 'bash ~/bin/vive-memoire-audit stop'},
    {'type': 'command', 'command': 'bash /ancien/vive-memoire-stop.sh stop'}]}]}}))
env_mac = dict(BASE_ENV, HOME=str(h))
r1 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=env_mac)
r2 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=env_mac)
s = json.loads((h / '.claude/settings.json').read_text())
cmds = [x['command'] for g in s['hooks']['Stop'] for x in g['hooks']]
verifie('31. installeur idempotent, voisins conservés (même « vive-memoire-audit »), ancienne entrée remplacée',
        r1.returncode == r2.returncode == 0 and s.get('model') == 'opus' and 'echo voisin' in cmds
        and 'bash ~/bin/vive-memoire-audit stop' in cmds and sum('vive-memoire-stop.sh' in c for c in cmds) == 1 and (h / '.claude/skills/vive-memoire/SKILL.md').exists(), [r1.stdout, r2.stderr, cmds])
r3 = subprocess.run(['bash', str(ICI / 'installe-mac.sh'), '--retirer'], capture_output=True, text=True, env=env_mac)
s = json.loads((h / '.claude/settings.json').read_text())
verifie('32. --retirer enlève hooks et skill, garde les voisins',
        r3.returncode == 0 and not (h / '.claude/skills/vive-memoire/SKILL.md').exists()
        and [x['command'] for g in s['hooks']['Stop'] for x in g['hooks']] == ['echo voisin', 'bash ~/bin/vive-memoire-audit stop'], [r3.stdout, s])
r4 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=dict(env_mac, CLAUDE_CODE_REMOTE='1'))
verifie('33. installeur refusé en cloud', r4.returncode == 1, r4.stdout)
h2 = b.racine / 'mac2'; (h2 / '.claude').mkdir(parents=True); (h2 / '.claude/hooks').write_text('un fichier, pas un dossier')
r5 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=dict(BASE_ENV, HOME=str(h2)))
reg = (h2 / '.claude/settings.json').read_text() if (h2 / '.claude/settings.json').exists() else ''
verifie('34. copie impossible : aucune commande enregistrée', r5.returncode != 0 and 'vive-memoire' not in reg, [r5.returncode, reg[:120]])
shutil.rmtree(b.racine, ignore_errors=True)
print(f'\n{total} vérifications, {len(echecs)} échec(s)')
sys.exit(1 if echecs else 0)
