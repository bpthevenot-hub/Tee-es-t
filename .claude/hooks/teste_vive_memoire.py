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
            if k not in ('VM_ETAT', 'VM_MEMOIRE', 'CLAUDE_CONFIG_DIR', 'CLAUDE_CODE_REMOTE', 'CLAUDE_PROJECT_DIR', 'VM_VERROU')}
# Les scénarios rejouent souvent le même événement sur un transcript figé ; dans la vraie vie le
# transcript grandit d'un événement à l'autre. Le verrou par événement est donc coupé ici, sauf
# dans les scénarios 29 qui le testent (VERROU).
BASE_ENV['VM_VERROU'] = 'non'
VERROU = {'VM_VERROU': ''}


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
(inst / 'vive_memoire.py').write_text((ICI / 'vive_memoire.py').read_text(encoding='utf-8'), encoding='utf-8')
rc, j, _, _ = b.appel('stop', {'session_id': 'S20b', 'transcript_path': t4}, VERROU)
verifie('29b0. installation enregistrée mais copie utilisateur absente de la session : la copie du dépôt agit', bloque(j), j)
evt = {'session_id': 'S20', 'transcript_path': t4, 'stop_hook_active': False}
rc, j, _, _ = b.appel('stop', evt, VERROU, enveloppe=inst / 'vive-memoire-stop.sh')
verifie('29c. la copie utilisateur agit', bloque(j), j)
rc, j, _, _ = b.appel('stop', evt, VERROU)
verifie('29b. … et la copie du dépôt, qui reçoit le même événement, se tait', j == {}, j)
t4b = b.transcript('t4b', [humain(x) for x in 'abcd'])
evt2 = {'session_id': 'S20d', 'transcript_path': t4b, 'stop_hook_active': False}
rc, j, _, _ = b.appel('stop', evt2, VERROU, enveloppe=inst / 'vive-memoire-stop.sh')
ajouter(t4b, {'type': 'assistant', 'message': {'role': 'assistant', 'content': 'suite'}})
rc, j2, _, _ = b.appel('stop', evt2, VERROU)
verifie('29g. reprise sans les réglages utilisateur (--setting-sources project) : la copie du dépôt agit', bloque(j) and bloque(j2), [j, j2])
cmd_u = ['bash', str(inst / 'vive-memoire-stop.sh'), 'stop']
cmd_d = ['bash', str(b.enveloppe), 'stop']
env_v = b.env(VERROU)
evt3 = json.dumps({'session_id': 'S20e', 'transcript_path': t4, 'stop_hook_active': False})
ps = [subprocess.Popen(c, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env_v) for c in (cmd_u, cmd_d)]
sorties = [x.communicate(evt3, timeout=30)[0] for x in ps]
verifie('29i. deux copies lancées en parallèle sur le même événement : une seule agit',
        sum('"block"' in x for x in sorties) == 1, sorties)
(inst / 'vive_memoire.py').write_text("# sans numéro de version\n")
rc, j, out, _ = b.appel('debut', {'session_id': 'S20g', 'source': 'startup'})
verifie('29e2. copie utilisateur sans numéro de version : avis « antérieure à 3.5 », et elle seule agit',
        'antérieure à 3.5' in out and b.appel('stop', {'session_id': 'S20g', 'transcript_path': t4}, VERROU)[1] == {}, out[:200])
(inst / 'vive_memoire.py').write_text("VERSION = '3.5'\n")
verifie('29h. copie utilisateur d\'avant le verrou (≤ 3.5) enregistrée : la copie du dépôt se tait, comme avant',
        b.appel('stop', {'session_id': 'S20f', 'transcript_path': t4}, VERROU)[1] == {})
(inst / 'vive_memoire.py').write_text((ICI / 'vive_memoire.py').read_text(encoding='utf-8'), encoding='utf-8')
(b.home / '.claude/settings.json').write_text('{\n  // mes réglages\n' + json.dumps({'hooks': {'Stop': [{'hooks': [{'command': f'bash "{inst}/vive-memoire-stop.sh" stop'}]}]}})[1:])
verifie('29b2. réglages utilisateur invalides (Claude Code les ignore) : la copie du dépôt agit', bloque(b.stop('S20c', t4)[1]))
rc, j, _, _ = b.appel('stop', {'session_id': 'S21', 'transcript_path': t4}, {'CLAUDE_CODE_REMOTE': '1'})
verifie('29d. en cloud, la copie du dépôt ne se tait jamais', bloque(j), j)
(b.home / '.claude/settings.json').write_text(json.dumps({'hooks': {'Stop': [{'hooks': [{'command': f'bash "{inst}/vive-memoire-stop.sh" stop'}]}]}}))
(inst / 'vive_memoire.py').write_text("# ancienne version\nVERSION = '3.1'\n")
rc, j, out, _ = b.appel('debut', {'session_id': 'S20', 'source': 'startup'})
verifie('29e. copie utilisateur plus ancienne : signalée au démarrage', 'plus ancienne' in out, out[:200])
(inst / 'vive_memoire.py').write_text("VERSION = '99.0'\n")
rc, j, out, _ = b.appel('debut', {'session_id': 'S20', 'source': 'startup'})
verifie('29f. copie utilisateur plus récente que le dépôt : pas d\'invitation à « mettre à jour » en arrière', 'plus ancienne' not in out, out[:200])
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
tor = b.transcript('tor', [humain('a'), humain('b'), humain('c'),
                           {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': 'x', 'source_uuid': 'Z1', 'origin': {'kind': 'human'}}}])
rc, j = b.stop('S48', tor)
verifie('30u. commande en file d\'origine humaine sans humanTurn : comptée', bloque(j) and '4 demandes' in j.get('reason', ''), j)
canal = {'type': 'user', 'isMeta': True, 'origin': {'kind': 'channel'}, 'userType': 'external', 'message': {'role': 'user', 'content': 'depuis Discord'}}
rc, j = b.stop('S49', b.transcript('tcan', [humain('a'), humain('b'), humain('c'), canal]))
verifie('30v. message reçu par un canal (isMeta, origin channel) : compté', bloque(j) and '4 demandes' in j.get('reason', ''), j)
retour = {'type': 'user', 'isMeta': True, 'message': {'role': 'user', 'content': 'Stop hook feedback: synthèse'}}
verifie('30v2. retour de hook (isMeta sans origin) : toujours exclu',
        not bloque(b.stop('S50', b.transcript('tret', [humain('a'), humain('b'), humain('c'), retour]))[1]))
def tours(prefixe, n, parent=None, debut=1):
    sortie = []
    for i in range(debut, debut + n):
        sortie += [humain(prefixe + str(i), uuid=prefixe + 'h' + str(i), parentUuid=parent), assistant(prefixe + 'a' + str(i), prefixe + 'h' + str(i))]
        parent = prefixe + 'a' + str(i)
    return sortie
trw = proj / 'S51.jsonl'
trw.write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
r = b.python('tamponne', 'S51')
ajouter(str(trw), *tours('bis', 8, parent='a2', debut=3))
rc, j = b.stop('S51', str(trw))
verifie('30w. /rewind après une synthèse : la référence revient aux demandes encore actives',
        '10 demandes' in r.stdout and bloque(j) and '10 demandes' in j.get('reason', ''), [r.stdout, j])
trw2 = proj / 'S52.jsonl'
trw2.write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
b.python('tamponne', 'S52')
ajouter(str(trw2), *tours('', 7, parent='a10', debut=11))
verifie('30w2. sans /rewind, la synthèse garde toute sa portée (7 nouvelles : pas de relance)', not bloque(b.stop('S52', str(trw2))[1]))
rc, j, out, _ = b.appel('debut', {'session_id': 'S51', 'source': 'resume'})
verifie('30w3. dette notée après /rewind (tampon brut plus grand) : rappelée, pas effacée au démarrage', 'S51' in out and 'S51' in b.dette(), [out[:200], list(b.dette())])
trw3 = proj / 'S66.jsonl'
trw3.write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
b.python('tamponne', 'S66')
(mem / 'sessions/2026-10-15-h.md').write_text('Session : S66\nDemandes : 11\n')
ajouter(str(trw3), *tours('bis', 8, parent='a2', debut=3))
rc, j = b.stop('S66', str(trw3))
verifie('30w4. /rewind avec un compte rendu un peu plus grand que le tampon : la relance a lieu', bloque(j) and '10 demandes' in j.get('reason', ''), j)
frontiere = lambda amont: {'type': 'system', 'subtype': 'compact_boundary', 'uuid': 'B', 'parentUuid': None, 'logicalParentUuid': amont}
trb = proj / 'S53.jsonl'
trb.write_text('\n'.join(json.dumps(x) for x in tours('', 12)) + '\n')
b.python('tamponne', 'S53')
trb.write_text('\n'.join(json.dumps(x) for x in [frontiere('a16')] + tours('r', 9, parent='B')) + '\n')
rc, j = b.stop('S53', str(trb))
verifie('30x. transcript reconstruit depuis une compaction : la synthèse d\'avant ne masque plus les demandes', bloque(j) and '9 demandes' in j.get('reason', ''), j)
(mem / 'sessions/2026-10-14-e.md').write_text('Session : S54\nDemandes : 12\n')
trd = b.transcript('trd', [frontiere('ailleurs')] + tours('r', 2, parent='B'))
c1 = bloque(b.stop('S54', trd)[1])
ajouter(trd, *tours('s', 6, parent='ra2'))
c2 = bloque(b.stop('S54', trd)[1])
ajouter(trd, *tours('t', 2, parent='sa6'))
rc, j = b.stop('S54', trd)
verifie('30x2. compte rendu durable plus grand que le transcript : on repart du transcript (relance après 8 nouvelles)',
        not c1 and not c2 and bloque(j) and '10 demandes' in j.get('reason', ''), [c1, c2, j])
tlp = b.transcript('tlp', tours('', 3) + [frontiere('MANQUE')] + tours('p', 2, parent='B'))
rc, j = b.stop('S55', tlp)
verifie('30y. compaction dont l\'amont manque, au milieu du fichier : rien n\'est perdu avant elle', bloque(j) and '5 demandes' in j.get('reason', ''), j)
tid = b.transcript('tid', [humain('a', promptId='P1'), humain('b', promptId='P2'), humain('c', promptId='P3')])
b.appel('prompt', {'session_id': 'S56', 'prompt': '/model opus', 'prompt_id': 'P4', 'transcript_path': tid})
ajouter(tid, {'type': 'user', 'promptId': 'P4', 'message': {'role': 'user', 'content': '<command-name>/model</command-name>'}})
verifie('30z. commande locale écrite sans origine humaine (même promptId) : pas comptée', not bloque(b.stop('S56', tid)[1]))
trn = b.transcript('trn', tours('', 6) + [dict(notif('<task-notification> fin'), uuid='n1', parentUuid='a4'), assistant('a7', 'n1')])
rc, j = b.stop('S57', trn)
verifie('30r4. /rewind puis tour automatique sans demande tapée : branche active quand même', bloque(j) and '4 demandes' in j.get('reason', ''), j)
profond = '[' * 200000 + ']' * 200000
tdeep = b.racine / 'tdeep.jsonl'
tdeep.write_text('\n'.join([profond] + [json.dumps(humain(x)) for x in 'abcd']) + '\n')
rc, j = b.stop('S58', str(tdeep))
verifie('30s2. ligne JSON trop imbriquée : ignorée, le reste compte', bloque(j) and '4 demandes' in j.get('reason', ''), j)
(b.etat / 'S59.json').write_text(json.dumps({'prompts': 7, 'tampon': 'x', 'relances': None, 'pause': 3}))
shutil.copy(t4, proj / 'S59.jsonl')
r = b.python('tamponne', 'S59')
rc, j = b.stop('S59', t4)
trc = b.transcript('trc', tours('', 10))
b.appel('prompt', {'session_id': 'S64', 'prompt': 'quatrième', 'transcript_path': trc})
Path(trc).write_text('\n'.join(json.dumps(x) for x in [frontiere('a10')] + tours('r', 3, parent='B')
                                + [humain('quatrième', uuid='rh4', parentUuid='ra3')]) + '\n')
rc, j64 = b.stop('S64', trc)
verifie('30aa. transcript reconstruit entre l\'envoi et le Stop : la demande déjà relue ne compte pas deux fois',
        bloque(j64) and '4 demandes' in j64.get('reason', ''), j64)
side = [dict(ancien('Warmup'), isSidechain=True) for _ in range(4)]
verifie('30ab. entrées de sous-agent (isSidechain) : ni demandes ni invites', not bloque(b.stop('S65', b.transcript('tside', side + [humain('a')]))[1]))
verifie('30s3. état corrompu (types inattendus) : tamponne et Stop fonctionnent', r.returncode == 0 and 'S59' in r.stdout and rc == 0, [r.returncode, r.stdout, j])
tpl2 = b.transcript('tpl2', [humain('a'), humain('b'), humain('c')])
b.appel('prompt', {'session_id': 'S60', 'prompt': 'Point de contrôle : relire les PR', 'transcript_path': tpl2})
ajouter(tpl2, {'type': 'user', 'origin': {'kind': 'scheduled'}, 'message': {'role': 'user', 'content': 'Point de contrôle : relire les PR'}})
verifie('30m2. tour planifié écrit, sans tâche listée à ce Stop : pas compté', not bloque(b.stop('S60', tpl2)[1]))
b.stop('S61', t4)
(mem / 'sessions/2026-10-14-f.md').write_text('Session : S61\nDemandes : 4\n')
rc, j = b.stop('S61', t4)
verifie('30g2. synthèse reconnue par le compte rendu (sans tamponne) : dette effacée', not bloque(j) and 'S61' not in b.dette(), [j, b.dette()])
b.poser_dette('S62', nb=4)
(mem / 'sessions/2026-10-14-g.md').write_text('Session : S62\nDemandes : 4\n')
rc, j, out, _ = b.appel('debut', {'session_id': 'S63', 'source': 'startup'})
verifie('30g3. démarrage : dette déjà couverte par un compte rendu, pas rappelée', 'S62' not in out and 'S62' not in b.dette(), out[:200])
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
def installer(home, *args, cwd=None, sup=None, script=None):
    return subprocess.run(['bash', str(script or (ICI / 'installe-mac.sh')), *args], capture_output=True, text=True,
                          cwd=cwd, env=dict(BASE_ENV, HOME=str(home), **(sup or {})))
h3 = b.racine / 'mac3'; (h3 / '.claude').mkdir(parents=True)
casse = '{\n  // commentaire\n  "model": "opus"\n}\n'
(h3 / '.claude/settings.json').write_text(casse)
r = installer(h3)
verifie('35. réglages en JSON invalide : refus, fichier intact, rien d\'installé',
        r.returncode != 0 and (h3 / '.claude/settings.json').read_text() == casse and not (h3 / '.claude/hooks/vive-memoire').exists(), [r.returncode, r.stderr[-200:]])
forme = json.dumps({'hooks': {'Stop': {'pas': 'une liste'}}})
(h3 / '.claude/settings.json').write_text(forme)
r = installer(h3)
verifie('36. forme inattendue des hooks : refus, fichier intact', r.returncode != 0 and (h3 / '.claude/settings.json').read_text() == forme, r.stderr[-200:])
(h3 / '.claude/settings.json').write_text(json.dumps({'hooks': {'Stop': ['brut', {'hooks': ['brut2', {'command': 'echo v'}]}, {'matcher': 'x'}]}}))
r = installer(h3)
st = json.loads((h3 / '.claude/settings.json').read_text())['hooks']['Stop']
verifie('36b. entrées voisines atypiques gardées telles quelles', r.returncode == 0 and 'brut' in st and {'matcher': 'x'} in st
        and any(isinstance(g, dict) and g.get('hooks') == ['brut2', {'command': 'echo v'}] for g in st), [r.stderr[-200:], st])
(h3 / '.claude/settings.json').write_text('{"note": "\\ud800", "model": "opus"}')
r = installer(h3)
txt = (h3 / '.claude/settings.json').read_text()
verifie('37. texte non encodable (demi-paire) : écrit échappé, jamais un fichier vide', r.returncode == 0 and json.loads(txt).get('model') == 'opus', [r.stderr[-200:], txt[:80]])
h4 = b.racine / 'mac4'; (h4 / '.claude').mkdir(parents=True)
original = json.dumps({'model': 'sonnet'})
(h4 / '.claude/settings.json').write_text(original)
installer(h4); installer(h4)
sauvegardes = sorted((h4 / '.claude').glob('settings.json.avant-vive-memoire.*'))
verifie('38. deux installations dans la même seconde : la sauvegarde d\'origine survit',
        len(sauvegardes) == 2 and any(x.read_text() == original for x in sauvegardes), [x.name for x in sauvegardes])
h5 = b.racine / 'mac5'; (h5 / '.claude').mkdir(parents=True); (h5 / '.claude/settings.json').write_text(original)
r = installer(h5, '--help')
verifie('39. argument inconnu : usage, rien de modifié', r.returncode == 1 and (h5 / '.claude/settings.json').read_text() == original
        and not (h5 / '.claude/hooks').exists() and not list((h5 / '.claude').glob('*.avant-vive-memoire.*')), r.stdout)
arbre = b.racine / 'arbre/.claude/hooks'; arbre.mkdir(parents=True)
for f in ('vive_memoire.py', 'vive-memoire-stop.sh', 'vive-memoire-prompt.sh', 'installe-mac.sh'):
    shutil.copy(ICI / f, arbre / f)
shutil.copy(next(c / 'SKILL.md' for c in (ICI, ICI.parent / 'skills/vive-memoire', ICI.parents[1] / 'docs/context/skills/vive-memoire') if (c / 'SKILL.md').exists()), arbre / 'SKILL.md')
leurre = b.racine / 'leurre'; (leurre / 'hooks').mkdir(parents=True)
h6 = b.racine / 'mac6'; h6.mkdir()
r = installer(h6, cwd=str(arbre.parent), script='hooks/installe-mac.sh', sup={'CDPATH': str(leurre)})
verifie('40. CDPATH exporté + chemin relatif : installation correcte', r.returncode == 0 and (h6 / '.claude/skills/vive-memoire/SKILL.md').exists(), [r.returncode, r.stdout[-200:], r.stderr[-200:]])
ss = json.loads((h6 / '.claude/settings.json').read_text())['hooks']['SessionStart']
verifie('41. SessionStart couvre aussi les fourches (fork)', any(g.get('matcher') == 'startup|resume|clear|fork' for g in ss), ss)
cfg2 = b.racine / 'cfg2'
r = installer(b.racine / 'mac7', sup={'CLAUDE_CONFIG_DIR': str(cfg2)})
(cfg2 / 'vive-memoire/dettes').mkdir(parents=True)
(cfg2 / 'vive-memoire/dettes/VX.json').write_text(json.dumps({'session': 'VX', 'nb': 5, 'date': 'x', 't': 0}))
d = subprocess.run(['bash', str(cfg2 / 'hooks/vive-memoire/vive-memoire-stop.sh'), 'debut'], input=json.dumps({'session_id': 'VY', 'source': 'startup'}),
                   capture_output=True, text=True, env=dict(BASE_ENV, HOME=str(b.racine / 'mac7'), CLAUDE_CONFIG_DIR=str(cfg2)))
verifie('42. CLAUDE_CONFIG_DIR : la skill citée est celle de cette config', str(cfg2 / 'skills/vive-memoire/SKILL.md') in d.stdout, [r.returncode, d.stdout[:300]])
h8 = b.racine / 'mac8'; h8.mkdir()
installer(h8)
r = subprocess.run(['bash', str(h8 / '.claude/hooks/vive-memoire/installe-mac.sh'), '--retirer'], capture_output=True, text=True, env=dict(BASE_ENV, HOME=str(h8)))
reg = (h8 / '.claude/settings.json').read_text()
verifie('43. la copie installée de l\'installeur sait tout retirer', r.returncode == 0 and 'vive-memoire-stop.sh' not in reg
        and not (h8 / '.claude/skills/vive-memoire/SKILL.md').exists(), [r.returncode, r.stdout[-200:], r.stderr[-200:]])
h9 = b.racine / 'mac9'; h9.mkdir()
r = subprocess.run(['bash', '-c', 'umask 077; bash "$0"', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=dict(BASE_ENV, HOME=str(h9)))
mode = oct((h9 / '.claude/settings.json').stat().st_mode & 0o777)
verifie('44. settings.json créé : droits selon l\'umask (077 → 600)', r.returncode == 0 and mode == '0o600', [r.returncode, mode])
h10 = b.racine / 'maçon é'; (h10 / '.claude').mkdir(parents=True)
(h10 / '.claude/settings.json').write_text('{"note": "\\ud800"}')
r = installer(h10)
txt = (h10 / '.claude/settings.json').read_text(encoding='utf-8')
verifie('45. demi-paire dans les réglages : seule elle est échappée, notre chemin reste en clair',
        r.returncode == 0 and str(h10 / '.claude/hooks/vive-memoire/vive-memoire-stop.sh') in txt and json.loads(txt).get('note') == '\ud800', [r.stderr[-200:], txt[:200]])
shutil.rmtree(b.racine, ignore_errors=True)
print(f'\n{total} vérifications, {len(echecs)} échec(s)')
sys.exit(1 if echecs else 0)
