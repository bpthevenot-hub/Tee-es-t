"""Banc des hooks « vive mémoire » : près de cent cinquante vérifications, dans un HOME et un état temporaires isolés.

Usage : python3 teste_vive_memoire.py      (code 0 si tout passe)
"""
import hashlib
import json
import os
import shlex
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


def vieillir(dossier, secondes=10):
    """Simule le temps qui passe pour les verrous par événement (valables 2 s)."""
    for f in Path(dossier).glob('*'):
        t = f.stat().st_mtime - secondes
        os.utime(f, (t, t))


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
vieillir(b.etat / 'evenements')    # reprise plus tard, sans les réglages utilisateur
rc, j2, _, _ = b.appel('stop', evt2, VERROU)
verifie('29g. reprise sans les réglages utilisateur (--setting-sources project) : la copie du dépôt agit', bloque(j) and bloque(j2), [j, j2])
cmd_u = ['bash', str(inst / 'vive-memoire-stop.sh'), 'stop']
cmd_d = ['bash', str(b.enveloppe), 'stop']
env_v = b.env(VERROU)
evt3 = json.dumps({'session_id': 'S20e', 'transcript_path': t4, 'stop_hook_active': False})
ps = [subprocess.Popen(c, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env_v) for c in (cmd_u, cmd_d)]
ps[0].stdin.write(evt3); ps[0].stdin.close()
with open(t4, 'a') as f:
    f.write(json.dumps({'type': 'queue-operation', 'operation': 'enqueue'}) + '\n')   # écriture entre les deux lectures
ps[1].stdin.write(evt3); ps[1].stdin.close()
sorties = [x.stdout.read() for x in ps]
[x.wait(timeout=30) for x in ps]
verifie('29i. deux copies en parallèle sur le même événement, transcript écrit entre elles : une seule agit',
        sum('"block"' in x for x in sorties) == 1, sorties)
verifie('29j. la copie utilisateur pose encore la marque lue par une copie de dépôt 3.5', (b.etat / 'actifs/S20').exists())
evtA = {'session_id': 'S20j', 'transcript_path': t4, 'stop_hook_active': False, 'background_tasks': [{'id': 'w9', 'status': 'running'}]}
rc, ja, _, _ = b.appel('stop', evtA, VERROU)
rc, jb, _, _ = b.appel('stop', dict(evtA, background_tasks=[]), VERROU)
verifie('29n. deux Stop distincts à moins de 2 s (tâche finie entre-temps) : le second n\'est pas avalé', not bloque(ja) and bloque(jb), [ja, jb])
(inst / 'vive_memoire.py').write_text("VERSION = '3.6'\n")
cle36 = json.dumps(['stop', 'S20k', t4, os.path.getsize(t4), None, None, False], ensure_ascii=True, default=str)
(b.etat / 'evenements' / hashlib.sha1(cle36.encode('ascii')).hexdigest()[:24]).touch()
rc, j, _, _ = b.appel('stop', {'session_id': 'S20k', 'transcript_path': t4, 'stop_hook_active': False}, VERROU)
cle36b = json.dumps(['stop', 'S20l', t4, os.path.getsize(t4), None, None, False], ensure_ascii=True, default=str)
rc2, j2, _, _ = b.appel('stop', {'session_id': 'S20l', 'transcript_path': t4, 'stop_hook_active': False}, VERROU)
verifie('29o. copie utilisateur 3.6 enregistrée : le dépôt se tait (comme ≤ 3.4 ; la 3.6 agit seule)', j == {} and j2 == {}, [j, j2])
def sous_claude(mode, entree, sources):
    """Lance l'enveloppe du dépôt sous un processus parent dont la ligne de commande porte --setting-sources."""
    code = 'import subprocess, sys; sys.exit(subprocess.run(sys.argv[1:4]).returncode)'
    r = subprocess.run([sys.executable, '-c', code, 'bash', str(b.enveloppe), mode, '--setting-sources', sources],
                       input=json.dumps(entree), capture_output=True, text=True, timeout=30, env=b.env(VERROU))
    brut = r.stdout.strip()
    return (json.loads(brut.splitlines()[-1]) if brut.startswith('{') else {}), r.stdout
jt, _ = sous_claude('stop', {'session_id': 'S20t', 'transcript_path': t4, 'stop_hook_active': False}, 'project')
jt2, _ = sous_claude('stop', {'session_id': 'S20u', 'transcript_path': t4, 'stop_hook_active': False}, 'user,project')
verifie('29t. copie utilisateur 3.6 enregistrée, session --setting-sources project : la copie du dépôt agit (et se tait avec « user »)',
        bloque(jt) and jt2 == {}, [jt, jt2])
def sous_chaine(mode, entree, externe, interne):
    """Claude Code « interne » (ses arguments : interne) lancé depuis un processus « externe » (ses arguments : externe)."""
    code = "import subprocess, sys; i = sys.argv.index('::'); sys.exit(subprocess.run(sys.argv[i + 1:]).returncode)"
    cmd = [sys.executable, '-c', code, *externe, '::', sys.executable, '-c', code, *interne, '::', 'bash', str(b.enveloppe), mode]
    r = subprocess.run(cmd, input=json.dumps(entree), capture_output=True, text=True, timeout=30, env=b.env(VERROU))
    brut = r.stdout.strip()
    return json.loads(brut.splitlines()[-1]) if brut.startswith('{') else {}
jn = sous_chaine('stop', {'session_id': 'S20w', 'transcript_path': t4, 'stop_hook_active': False},
                 ['claude', '--setting-sources', 'project'], ['claude', '-p', 'tâche'])
verifie('29t4. session sans drapeau lancée depuis un Claude Code qui en a un : seul le Claude Code de la session compte', jn == {}, jn)
jr = sous_chaine('stop', {'session_id': 'S20x', 'transcript_path': t4, 'stop_hook_active': False},
                 ['coquille'], ['claude', '--setting-sources', 'project', '--setting-sources', 'user,project'])
verifie('29t5. drapeau répété : le dernier l\'emporte, comme dans Claude Code', jr == {}, jr)
(inst / 'vive_memoire.py').write_text("VERSION = '3.5'\n")
b.poser_dette('VIEILLE35', nb=5, t=0)
rc, j35, out35, _ = b.appel('debut', {'session_id': 'S20r', 'source': 'startup'}, VERROU)
verifie('29r. copie utilisateur 3.5 : au démarrage, elle seule rappelle les dettes (pas de rappel en double)', 'VIEILLE35' not in out35, out35[:200])
sonde = ("import builtins, os, sys; sys.argv = ['x']; sys.path.insert(0, sys.argv[0] if False else %r); import vive_memoire as m\n"
         "vrai = builtins.open\n"
         "def faux(f, *a, **k):\n"
         "    if str(f).startswith('/proc/'): raise OSError('pas de /proc')\n"
         "    return vrai(f, *a, **k)\n"
         "builtins.open = faux\n"
         "lu = m.ligne_de_commande(os.getpid())\n"
         "texte = lu[0] if lu and isinstance(lu[0], str) else ' '.join(lu[0] if lu else [])\n"
         "print('PS-OK' if lu and lu[1] == os.getppid() and 'sonde-ps' in texte else 'PS-KO', m.reglages_utilisateur_charges())\n") % str(b.hooks)
r_ps = subprocess.run([sys.executable, '-I', '-c', sonde, 'sonde-ps'], capture_output=True, text=True, timeout=30, env=b.env())
verifie('29t3. sans /proc (macOS) : la ligne de commande est lue par « ps », sans erreur', 'PS-OK True' in r_ps.stdout, [r_ps.stdout, r_ps.stderr[-300:]])
sonde2 = ("import sys; sys.argv = ['x']; sys.path.insert(0, %r); import vive_memoire as m\n"
          "f = m.sources_reglages\n"
          "print(f('/opt/claude --setting-sources project, user --verbose'), f('node cli.js --setting-sources=project,local'),"
          " f('claude -- --setting-sources project'), f('claude --setting-sources project --setting-sources=user'))\n") % str(b.hooks)
r_ps2 = subprocess.run([sys.executable, '-I', '-c', sonde2], capture_output=True, text=True, timeout=30, env=b.env())
verifie('29t6. texte de « ps » : valeur avec espaces après les virgules, forme =, arrêt à --, dernier drapeau',
        r_ps2.stdout.strip() == "['project', 'user'] ['project', 'local'] None ['user']", [r_ps2.stdout, r_ps2.stderr[-300:]])
_, out35p = sous_claude('debut', {'session_id': 'S20v', 'source': 'startup'}, 'project,local')
verifie('29t2. copie utilisateur 3.5, session sans réglages utilisateur : le dépôt rappelle les dettes au démarrage', 'VIEILLE35' in out35p, out35p[:200])
b.python('tamponne', 'VIEILLE35') if False else (b.etat / 'dettes' / 'VIEILLE35.json').unlink()
(inst / 'vive_memoire.py').write_text("VERSION = '3.7'\n")
cle37 = json.dumps(['stop', 'S20p', t4, None, None, None, False], ensure_ascii=True, default=str)
(b.etat / 'evenements' / hashlib.sha1(cle37.encode('ascii')).hexdigest()[:24]).touch()
rc, j37, _, _ = b.appel('stop', {'session_id': 'S20p', 'transcript_path': t4, 'stop_hook_active': False}, VERROU)
verifie('29p. copie utilisateur 3.7 : son verrou (autre clé) fait taire le dépôt', j37 == {}, j37)
(inst / 'vive_memoire.py').write_text((ICI / 'vive_memoire.py').read_text(encoding='utf-8'), encoding='utf-8')
for pid in ('PA', 'PB'):
    b.appel('prompt', {'session_id': 'S20q', 'prompt': 'même texte', 'prompt_id': pid, 'transcript_path': t4}, VERROU, enveloppe=inst / 'vive-memoire-stop.sh')
notees_q = json.loads((b.etat / 'S20q.json').read_text()).get('prompts', [])
verifie('29q. même texte, deux prompt_id, sans copie 3.6 à côté : les deux demandes notées', len(notees_q) == 2, notees_q)
t4c = b.transcript('t4c', [humain(x) for x in 'abcd'] + [assistant('z1', None)])
evtS = {'session_id': 'S20s', 'transcript_path': t4c, 'stop_hook_active': False}
(inst / 'vive_memoire.py').write_text((ICI / 'vive_memoire.py').read_text(encoding='utf-8'), encoding='utf-8')
rc, js1, _, _ = b.appel('stop', evtS, VERROU)
rc, js1b, _, _ = b.appel('stop', evtS, VERROU)
ajouter(t4c, assistant('z2', 'z1'))
rc, js2, _, _ = b.appel('stop', evtS, VERROU)
verifie('29s. même entrée à moins de 2 s : même réponse = même événement (une copie), nouvelle réponse = autre Stop (il agit)',
        bloque(js1) and js1b == {} and bloque(js2), [bloque(js1), js1b, bloque(js2)])
(b.etat / 'evenements').rename(b.racine / 'evenements-fichier'); (b.etat / 'evenements').write_text('pas un dossier')
rc, j, _, _ = b.appel('stop', {'session_id': 'S20h', 'transcript_path': t4}, VERROU)
verifie('29m. verrou impossible (chemin occupé par un fichier) : la copie agit quand même', bloque(j), j)
(b.etat / 'evenements').unlink()
(inst / 'vive_memoire.py').write_text("# sans numéro de version\n")
rc, j, out, _ = b.appel('debut', {'session_id': 'S20g', 'source': 'startup'})
verifie('29e2. copie utilisateur sans numéro de version : avis « antérieure à 3.5 », et elle seule agit',
        'antérieure à 3.5' in out and b.appel('stop', {'session_id': 'S20g', 'transcript_path': t4}, VERROU)[1] == {}, out[:200])
(inst / 'vive_memoire.py').write_text("VERSION = '3.5'\n")
rc, j, _, _ = b.appel('stop', {'session_id': 'S20f', 'transcript_path': t4}, VERROU)
(b.etat / 'actifs').mkdir(parents=True, exist_ok=True); (b.etat / 'actifs/S20i').touch()
rc2, j2, _, _ = b.appel('stop', {'session_id': 'S20i', 'transcript_path': t4}, VERROU)
verifie('29h. copie utilisateur 3.5 enregistrée : le dépôt agit si elle n\'a pas tourné (pas de marque), se tait sinon',
        bloque(j) and j2 == {}, [j, j2])
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
b.stop('S66', str(trw3))           # le tour qui a écrit le compte rendu se termine par un Stop
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
tc7 = proj / 'S67.jsonl'
tc7.write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
b.python('tamponne', 'S67')
ajouter(str(tc7), *tours('c', 12, parent='a2', debut=3))
rc, j = b.stop('S67', str(tc7))
(mem / 'sessions/2026-10-15-i.md').write_text('Session : S67\nDemandes : 14\n')
rc2, j2 = b.stop('S67', str(tc7))
verifie('30ad. synthèse par compte rendu après /rewind : reconnue (plus de relance) et dette effacée',
        bloque(j) and not bloque(j2) and 'S67' not in b.dette(), [j.get('reason', '')[:80], j2, 'S67' in b.dette()])
tc8 = b.transcript('tc8', tours('', 10))
(mem / 'sessions/2026-10-15-j.md').write_text('Session : S68\nDemandes : 10\n')
rc, j = b.stop('S68', tc8)
ajouter(tc8, *tours('d', 8, parent='a2', debut=3))
rc2, j2 = b.stop('S68', tc8)
verifie('30ae. synthèse par compte rendu seul, puis /rewind : la relance a lieu', not bloque(j) and bloque(j2), [j, j2])
tc9 = b.transcript('tc9', [frontiere('ailleurs')] + tours('r', 2, parent='B'))
(mem / 'sessions/2026-10-15-k.md').write_text('Session : S69\nDemandes : 12\n')
b.stop('S69', tc9)
ajouter(tc9, *tours('s', 8, parent='ra2'))
rc, j = b.stop('S69', tc9)
nouveau = mem / 'sessions/2026-10-15-l.md'
nouveau.write_text('Session : S69\nDemandes : 10\n')
t_n = time.time() + 5; os.utime(nouveau, (t_n, t_n))
rc2, j2 = b.stop('S69', tc9)
rc3, j3, out, _ = b.appel('debut', {'session_id': 'S69', 'source': 'resume'})
verifie('30af. transcript reconstruit, nouveau compte rendu plus petit que l\'ancien : reconnu, dette effacée',
        bloque(j) and not bloque(j2) and 'S69' not in out and 'S69' not in b.dette(), [j.get('reason', '')[:60], j2, out[:120]])
tc10 = b.transcript('tc10', tours('', 4))
b.stop('S70', tc10)
ajouter(tc10, humain('c bis', uuid='h3b', parentUuid='a2'), assistant('a3b', 'h3b'))
rc, j = b.stop('S70', tc10)
verifie('30ag. dette notée puis /rewind sous le seuil : dette effacée', 'S70' not in b.dette() and not bloque(j), [j, list(b.dette())])
b.poser_dette('MERE3', nb=5)
tf3 = b.transcript('FILLE3', [humain(x, forkedFrom={'sessionId': 'MERE3'}) for x in 'abcde'] + [humain('f')])
(mem / 'sessions/2026-10-15-m.md').write_text('Session : FILLE3\nDemandes : 6\n')
b.stop('FILLE3', tf3)
tf4 = b.transcript('FILLE4', [humain(x, forkedFrom={'sessionId': 'MERE4'}) for x in 'abcde'] + [humain('f')])
shutil.copy(tf4, proj / 'FILLE4.jsonl')
b.python('tamponne', 'FILLE4')
rc, j = b.stop('MERE4', b.transcript('MERE4', [humain(x) for x in 'abcde']))
verifie('30ah. fourche : son compte rendu efface la dette de la mère ; après son tampon, la mère reprise ne relance pas',
        'MERE3' not in b.dette() and not bloque(j), [list(b.dette()), j])
hmem = b.home / 'claude-macos-app/docs/context'; (hmem / 'sessions').mkdir(parents=True)
(hmem / 'decision-log.md').write_text('# D\n'); (hmem / 'sessions/x.md').write_text('Session : S71\nDemandes : 4\n')
verifie('30ai. mémoire dans ~/claude-macos-app trouvée aussi par une copie de dépôt ailleurs', not bloque(b.stop('S71', t4)[1]))
ecrits = [subprocess.Popen(['bash', str(b.enveloppe), 'prompt'], stdin=subprocess.PIPE, text=True, env=b.env())
          for _ in range(25)]
for k, x in enumerate(ecrits):
    x.stdin.write(json.dumps({'session_id': 'S72', 'prompt': f'demande {k}', 'transcript_path': t4})); x.stdin.close()
[x.wait(timeout=30) for x in ecrits]
try:
    json.loads((b.etat / 'S72.json').read_text()); valide = True
except ValueError:
    valide = False
verifie('30aj. 25 écritures simultanées de l\'état : jamais de JSON mélangé', valide and not list(b.etat.glob('S72.json.*')))
tpz = b.transcript('tpz', tours('', 12))
tache = [{'id': 'w7', 'status': 'running'}]
p1 = bloque(b.stop('S80', tpz, background_tasks=tache)[1])
ajouter(tpz, humain('c bis', uuid='h3b', parentUuid='a2'), assistant('a3b', 'h3b'))
p2 = bloque(b.stop('S80', tpz, background_tasks=tache)[1])
ajouter(tpz, *tours('z', 7, parent='a3b', debut=4))
rc, j = b.stop('S80', tpz, background_tasks=tache)
verifie('30al. pause par une tâche longue, puis /rewind et 8 demandes : la pause cesse', not p1 and not p2 and bloque(j), [p1, p2, j])
lots = [subprocess.Popen(['bash', str(b.enveloppe), 'prompt'], stdin=subprocess.PIPE, text=True, env=b.env()) for _ in range(15)]
for k, x in enumerate(lots):
    x.stdin.write(json.dumps({'session_id': 'S81', 'prompt': f'demande {k}', 'transcript_path': t4})); x.stdin.close()
[x.wait(timeout=60) for x in lots]
notees = json.loads((b.etat / 'S81.json').read_text()).get('prompts', [])
verifie('30ak. 15 demandes envoyées en même temps : aucune perdue (état sérialisé)', len(notees) == 15, len(notees))
def herite(entrees, mere):
    return [dict(x, forkedFrom={'sessionId': mere}) for x in entrees]
(proj / 'M1.jsonl').write_text('\n'.join(json.dumps(x) for x in tours('', 10) + tours('m', 8, parent='a2', debut=3)) + '\n')
b.python('tamponne', 'M1')
rc, j = b.stop('F1', b.transcript('F1', herite(tours('', 10), 'M1')))
verifie('30am. fourche : la synthèse de la mère faite après un /rewind ne couvre que les demandes héritées encore chez elle',
        bloque(j) and '10 demandes' in j.get('reason', ''), j)
(proj / 'F2.jsonl').write_text('\n'.join(json.dumps(x) for x in herite(tours('', 10), 'M2')) + '\n')
b.python('tamponne', 'F2')
tm2 = b.transcript('M2', tours('', 10))
ajouter(tm2, *tours('n', 8, parent='a2', debut=3))
rc, j = b.stop('M2', tm2)
verifie('30an. tampon posé par la fourche chez la mère : ramené par un /rewind de la mère', bloque(j) and '10 demandes' in j.get('reason', ''), j)
b.poser_dette('CLOS', nb=6, t=time.time())
rc, j, out, _ = b.appel('debut', {'session_id': 'NOUVELLE', 'source': 'clear'})
verifie('30ap. /clear : la dette récente de la session close est rappelée', 'CLOS' in out, out[:200])
(mem / 'sessions/2026-10-15-n.md').write_text('Session : M5\nDemandes : 4\n')
rc, j = b.stop('F5', b.transcript('F5', [dict(ancien(x), forkedFrom={'sessionId': 'M5'}) for x in 'abcd'] + [humain('e')]))
verifie('30aq. fourche d\'un ancien transcript (sans origine ni clé) : hérite de la synthèse de la mère', not bloque(j), j)
autre = proj / 'nom-libre.jsonl'
autre.write_text('\n'.join(json.dumps(x) for x in tours('', 10) + tours('m', 8, parent='a2', debut=3)) + '\n')
(b.etat / 'M6.json').write_text(json.dumps({'transcript': str(autre)}))
b.python('tamponne', 'M6')
rc, j = b.stop('F6', b.transcript('F6', herite(tours('', 10), 'M6')))
verifie('30ar. transcript de la mère au nom libre (noté dans son état) : sa synthèse après /rewind n\'est pas héritée en bloc',
        bloque(j) and '10 demandes' in j.get('reason', ''), j)
ok_mere = True
for tour in range(5):
    (b.etat / f'M7{tour}.json').unlink(missing_ok=True)
    for nom, k in ((f'F7a{tour}', 10), (f'F7b{tour}', 5)):
        shutil.copy(b.transcript(nom, [humain(str(i), forkedFrom={'sessionId': f'M7{tour}'}) for i in range(k)]), proj / f'{nom}.jsonl')
    duo = [subprocess.Popen([sys.executable, '-I', str(b.hooks / 'vive_memoire.py'), 'tamponne', n], env=b.env(), stdout=subprocess.DEVNULL)
           for n in (f'F7a{tour}', f'F7b{tour}')]
    [x.wait(timeout=60) for x in duo]
    ok_mere &= json.loads((b.etat / f'M7{tour}.json').read_text()).get('tampon') == 10
verifie('30as. deux fourches tamponnent en même temps : la mère garde le plus grand tampon', ok_mere)
etat_d = b.racine / 'etat-dettes-fichier'; etat_d.mkdir(); (etat_d / 'dettes').write_text('pas un dossier')
msgs = [b.appel('stop', {'session_id': 'S90', 'transcript_path': t4}, {'VM_ETAT': str(etat_d)})[1] for _ in range(4)]
verifie('30at. dette impossible à noter : le message ne promet pas de rappel', 'pas pu être notée' in msgs[-1].get('systemMessage', '')
        and 'rappelée au prochain démarrage' not in msgs[-1].get('systemMessage', ''), msgs[-1])
import calendar
def horodate(entrees, debut_min):
    for k, x in enumerate(entrees):
        x['timestamp'] = '2026-10-15T01:%02d:%02d.000Z' % (debut_min + k // 60, k % 60)
    return entrees
avant = horodate(tours('', 10), 0)
apres = horodate(tours('r', 8, parent='a2', debut=3), 10)
for nom, ancre_ligne in (('S92', ''), ('S93', '\nAncre : a10')):
    cr = mem / f'sessions/2026-10-15-{nom}.md'
    cr.write_text(f'Session : {nom}\nDemandes : 10{ancre_ligne}\n')
    t_cr = calendar.timegm(time.strptime('2026-10-15T01:05:00', '%Y-%m-%dT%H:%M:%S')) if not ancre_ligne else time.time()
    os.utime(cr, (t_cr, t_cr))
    tr = b.transcript(nom, avant + apres)
    rc_au, j_au = b.stop(nom, tr)
    verifie(f'30au. compte rendu d\'avant un /rewind, état perdu ({"ligne Ancre" if ancre_ligne else "ancré par sa date"}) : la relance a lieu',
            bloque(j_au) and '10 demandes' in j_au.get('reason', ''), j_au)
r_av = b.python('tamponne', 'S1')
verifie('30av. tamponne donne aussi la ligne « Ancre : » à recopier', 'Ancre :' in r_av.stdout, r_av.stdout)
(proj / 'M8.jsonl').write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
(proj / 'F8.jsonl').write_text('\n'.join(json.dumps(x) for x in herite(tours('', 10), 'M8')) + '\n')
ajouter(str(proj / 'M8.jsonl'), *tours('p', 8, parent='a2', debut=3))
b.stop('M8', str(proj / 'M8.jsonl'))
b.python('tamponne', 'F8')
verifie('30aw. dette de la mère née après la fourche (sur une autre branche) : la synthèse de la fourche ne l\'efface pas', 'M8' in b.dette(), list(b.dette()))
tmg = b.transcript('tmg', [humain('a', uuid='ma', parentUuid=None), humain('b', uuid='mb', parentUuid='ma')])
b.appel('prompt', {'session_id': 'S94', 'prompt': 'c', 'transcript_path': tmg})
b.appel('prompt', {'session_id': 'S94', 'prompt': 'd', 'transcript_path': tmg})
ajouter(tmg, humain('c\nd', uuid='mc', parentUuid='mb', mergedSendUuids=['U-d']))
rc, j = b.stop('S94', tmg)
verifie('30ax. deux envois fusionnés en une entrée : comptés deux fois exactement, pas trois', bloque(j) and '4 demandes' in j.get('reason', ''), j)
tlib = b.transcript('tlib', tours('', 4))
[b.stop('S95', tlib) for _ in range(4)]
ajouter(tlib, humain('c bis', uuid='h3b', parentUuid='a2'), assistant('a3b', 'h3b'))
b.stop('S95', tlib)
ajouter(tlib, *tours('g', 6, parent='a3b', debut=4))
b.stop('S95', tlib)
verifie('30ay. libération puis /rewind sous le seuil, puis la session regrossit : la dette est notée de nouveau', 'S95' in b.dette(), list(b.dette()))
crh = mem / 'sessions/2026-10-15-S98.md'
crh.write_text('Session : S98\nDemandes : 12\n')
t_crh = calendar.timegm(time.strptime('2026-10-15T01:00:30', '%Y-%m-%dT%H:%M:%S')); os.utime(crh, (t_crh, t_crh))
trh = b.transcript('trh', horodate([frontiere('perdu')] + tours('r', 2, parent='B'), 0) + horodate(tours('s', 1, parent='ra2', debut=3), 1))
b.stop('S98', trh)
verifie('30az. clone frais, transcript reconstruit : le compte rendu ne couvre que les demandes écrites avant lui',
        json.loads((b.etat / 'S98.json').read_text()).get('tampon') == 2, json.loads((b.etat / 'S98.json').read_text()).get('tampon'))
(b.etat / 'M9.json').write_text(json.dumps({'tampon': 10, 'couvert': 2}))
rc, j = b.stop('F9', b.transcript('F9', [humain(str(i), forkedFrom={'sessionId': 'M9'}) for i in range(10)]))
verifie('30ba. fourche (uuids non partagés) : hérite de la couverture effective de la mère, pas de son tampon brut', bloque(j), j)
(mem / 'sessions/2026-10-15-F10.md').write_text('Session : F10\nDemandes : 6\n')
b.stop('F10', b.transcript('F10', [humain(str(i), forkedFrom={'sessionId': 'M10'}) for i in range(5)] + [humain('f')]))
rc, j = b.stop('M10', b.transcript('M10', [humain(str(i)) for i in range(5)]))
verifie('30bb. fourche synthétisée par compte rendu : la mère reprise ne relance pas', not bloque(j), j)
(mem / 'sessions/2026-10-15-S96.md').write_text('Session : S96\nDemandes : 4\n\n…\n\nSession : S96\nDemandes : 12\n')
verifie('30bc. compte rendu complété par un second bloc : le dernier fait foi', not bloque(b.stop('S96', b.transcript('S96', tours('', 12)))[1]))
tc97 = b.transcript('tc97', tours('', 10))
cr97 = mem / 'sessions/2026-10-15-S97.md'; cr97.write_text('Session : S97\nDemandes : 10\n')
b.stop('S97', tc97)
ajouter(tc97, *tours('q', 8, parent='a2', debut=3))
rc, j1 = b.stop('S97', tc97)
t_n = time.time() + 30; os.utime(cr97, (t_n, t_n))
rc, j2 = b.stop('S97', tc97, stop_hook_active=True)
verifie('30bd. compte rendu touché par un checkout (même contenu) : pas réadopté, la relance continue', bloque(j1) and bloque(j2), [j1, j2])
b.poser_dette('S99', nb=6, ancre='a6', t=time.time())
rc, j = b.stop('S99', b.transcript('S99', [frontiere('ailleurs')] + tours('r', 2, parent='B')))
verifie('30be. transcript reconstruit sous le seuil : la dette jamais synthétisée reste', 'S99' in b.dette(), list(b.dette()))
# --- v3.14 (revue Codex sur bde2315)
tq = b.transcript('tq', tours('', 3) + [file_humaine('en file, abandonnée', 'QA1')] + tours('', 1, parent='a3', debut=4)
                  + tours('bis', 1, parent='a2', debut=3))
rc, j = b.stop('S100', tq)
tq2 = b.transcript('tq2', tours('', 4) + [humain('c bis', uuid='bish3', parentUuid='a2'), file_humaine('en file, active', 'QA2'),
                                          assistant('bisa3', 'bish3')])
rc2, j2 = b.stop('S101', tq2)
verifie('30bf. /rewind : commande en file sans uuid sur la branche quittée exclue, sur la branche active comptée',
        not bloque(j) and bloque(j2) and '4 demandes' in j2.get('reason', ''), [j, j2])
(proj / 'M11.jsonl').write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
b.python('tamponne', 'M11')
ajouter(str(proj / 'M11.jsonl'), *tours('m', 8, parent='a2', debut=3))
actifs_m11 = tours('', 2) + tours('m', 3, parent='a2', debut=3)
(proj / 'F11.jsonl').write_text('\n'.join(json.dumps(x) for x in herite(actifs_m11, 'M11')) + '\n')
b.python('tamponne', 'F11')
rc, j = b.stop('M11', str(proj / 'M11.jsonl'))
verifie('30bg. fourche synthétisée après un /rewind de la mère : comparée à sa couverture effective, pas à son tampon brut',
        not bloque(j) and json.loads((b.etat / 'M11.json').read_text()).get('tampon') == 5, [j, json.loads((b.etat / 'M11.json').read_text()).get('tampon')])
t102 = proj / 'S102.jsonl'
t102.write_text('\n'.join(json.dumps(x) for x in tours('', 4)) + '\n')
b.python('tamponne', 'S102')
ajouter(str(t102), *tours('', 8, parent='a4', debut=5))
rc, j1 = b.stop('S102', str(t102))
t102.write_text('\n'.join(json.dumps(x) for x in [frontiere('a12')] + tours('r', 2, parent='B')) + '\n')
rc, j2 = b.stop('S102', str(t102))
verifie('30bh. transcript reconstruit qui perd les ancres : la dette jamais synthétisée reste',
        bloque(j1) and 'S102' in b.dette(), [j1.get('reason', '')[:60], j2, list(b.dette())])
t103 = b.transcript('t103', tours('', 10))
cr103 = mem / 'sessions/2026-10-15-S103.md'; cr103.write_text('Session : S103\nDemandes : 10\n\nPremière synthèse.\n')
r0 = bloque(b.stop('S103', t103)[1])
ajouter(t103, *tours('w', 8, parent='a2', debut=3))
rc, j1 = b.stop('S103', t103)
cr103.write_text('Session : S103\nDemandes : 10\n\nSynthèse refaite après le /rewind.\n')
t_n = time.time() + 30; os.utime(cr103, (t_n, t_n))
rc, j2 = b.stop('S103', t103)
verifie('30bi. compte rendu réécrit après /rewind, même en-tête : reconnu par son contenu', not r0 and bloque(j1) and not bloque(j2), [r0, j1, j2])
tq3 = b.transcript('tq3', tours('', 3) + [dict(file_humaine('en file, fin de branche quittée', 'QA3'), parentUuid='a3')]
                  + tours('bis', 1, parent='a2', debut=3))
verifie('30bf2. commande en file sans uuid, dernière de la branche quittée (parent quitté) : exclue', not bloque(b.stop('S104', tq3)[1]))
def resultat(uuid, parent):
    return {'type': 'user', 'uuid': uuid, 'parentUuid': parent,
            'message': {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'x', 'content': 'ok'}]}}
tpar = b.transcript('tpar', [humain('a', uuid='h1', parentUuid=None), assistant('a1', 'h1'), humain('b', uuid='h2', parentUuid='a1'),
                             assistant('t1', 'h2'), assistant('t2', 't1'), file_humaine('en file pendant les outils', 'QP1'),
                             resultat('r1', 't1'), resultat('r2', 't2'), assistant('a2', 'r2'),
                             humain('c', uuid='h3', parentUuid='a2'), assistant('a3', 'h3')])
torph = b.transcript('torph', tours('', 3)[:5] + [assistant('t3', 'h3'), resultat('r3', 't3'), file_humaine('en file avant le redémarrage', 'QO1'),
                              assistant('x1', 'r3'), {'type': 'user', 'isMeta': True, 'uuid': 'c1', 'parentUuid': 'r3',
                              'message': {'role': 'user', 'content': 'Continue from where you left off.'}}, assistant('a3', 'c1')])
rc, jp = b.stop('S107', tpar)
rc, jo = b.stop('S108', torph)
verifie('30bf3. sans /rewind, commande en file sans uuid suivie d\'une feuille latérale (outils parallèles, réponse orpheline) : comptée',
        bloque(jp) and '4 demandes' in jp.get('reason', '') and bloque(jo) and '4 demandes' in jo.get('reason', ''), [jp, jo])
def ecrire_t(nom, entrees):
    (proj / (nom + '.jsonl')).write_text('\n'.join(json.dumps(x) for x in entrees) + '\n')
    return str(proj / (nom + '.jsonl'))
etat_de = lambda s: json.loads((b.etat / (s + '.json')).read_text()) if (b.etat / (s + '.json')).exists() else {}
# fourche dont le point a été quitté par la mère : ne remplace pas une synthèse de la mère qui couvre plus
tmb = ecrire_t('MB', tours('', 10)); ecrire_t('FB', herite(tours('', 10), 'MB'))
ajouter(tmb, *tours('m', 10, parent='a2', debut=3)); b.python('tamponne', 'MB')
ajouter(tmb, *tours('n', 2, parent='ma6', debut=7)); b.stop('MB', tmb)
b.python('tamponne', 'FB')
ajouter(tmb, *tours('n', 2, parent='na8', debut=9))
rc, jb1 = b.stop('MB', tmb)
tme = ecrire_t('ME', tours('', 10)); tfe = ecrire_t('FE', herite(tours('', 10), 'ME'))
b.python('tamponne', 'FE'); ajouter(tme, *tours('m', 4, parent='a2', debut=3)); b.python('tamponne', 'ME')
ajouter(tfe, *tours('f', 1, parent='a10', debut=11)); b.stop('FE', tfe)
ajouter(tme, *tours('m', 4, parent='ma6', debut=7))
rc, jb2 = b.stop('ME', tme)
verifie('30bk. fourche au point quitté par la mère : la synthèse plus large de la mère n\'est pas écrasée',
        not bloque(jb1) and not bloque(jb2), [jb1, jb2, etat_de('MB').get('tampon'), etat_de('ME').get('tampon')])
# mère au transcript reconstruit : la fourche n'y pose pas d'ancre absente (ni de date de synthèse)
tma = ecrire_t('MA', tours('', 12)); ecrire_t('FA', herite(tours('', 10), 'MA'))
b.python('tamponne', 'MA')
Path(tma).write_text('\n'.join(json.dumps(x) for x in [frontiere('a16')] + tours('r', 9, parent='B')) + '\n')
b.python('tamponne', 'FA')
rc, ja1 = b.stop('MA', tma)
tmd = ecrire_t('MD', tours('', 12)); ecrire_t('FD', herite(tours('', 10), 'MD'))
b.python('tamponne', 'MD'); ajouter(tmd, *tours('', 8, parent='a12', debut=13))
[b.stop('MD', tmd) for _ in range(4)]
Path(tmd).write_text('\n'.join(json.dumps(x) for x in [frontiere('a20')] + tours('r', 2, parent='B')) + '\n')
b.python('tamponne', 'FD')
b.stop('MD', tmd)
verifie('30bl. mère au transcript reconstruit : la synthèse de la fourche ne masque ni ses nouvelles demandes ni sa dette',
        bloque(ja1) and '9 demandes' in ja1.get('reason', '') and 'MD' in b.dette(), [ja1, list(b.dette())])
# dette de la mère sur une nouvelle branche : la fourche ne la solde pas au démarrage
tmg = ecrire_t('MG', tours('', 10)); ecrire_t('FG', herite(tours('', 10), 'MG'))
ajouter(tmg, *tours('p', 8, parent='a2', debut=3)); b.stop('MG', tmg)
b.python('tamponne', 'FG')
d_mg = json.loads((b.etat / 'dettes/MG.json').read_text()); d_mg['t'] -= 7200
(b.etat / 'dettes/MG.json').write_text(json.dumps(d_mg))
rc, j, out_mg, _ = b.appel('debut', {'session_id': 'AUTRE-MG', 'source': 'startup'})
verifie('30bm. dette de la mère née sur une autre branche que la fourche : rappelée au démarrage, pas soldée',
        'MG' in out_mg and 'MG' in b.dette(), [out_mg[:160], etat_de('MG').get('tampon')])
# état de la mère créé par la fourche : le compte rendu de la mère reste reconnu
tmc = ecrire_t('MC', tours('', 12)); ecrire_t('FC', herite(tours('', 4), 'MC'))
(mem / 'sessions/2026-10-15-MC.md').write_text('Session : MC\nDemandes : 12\nAncre : a12\n')
b.python('tamponne', 'FC')
rc, jc = b.stop('MC', tmc)
verifie('30bn. état de la mère créé par la synthèse d\'une fourche : son propre compte rendu est encore adopté', not bloque(jc), [jc, etat_de('MC')])
# dettes : preuves plus strictes
t110 = ecrire_t('S110', tours('', 4)); b.python('tamponne', 'S110')
ajouter(t110, *tours('', 6, parent='a4', debut=5), frontiere('a10'), *tours('', 2, parent='B', debut=11))
rc, j110 = b.stop('S110', t110)
Path(t110).write_text('\n'.join(json.dumps(x) for x in [frontiere('a10')] + tours('', 2, parent='B', debut=11)) + '\n')
b.stop('S110', t110)
verifie('30bo. transcript reconstruit depuis une compaction antérieure à la dette (ancre gardée) : la dette reste',
        bloque(j110) and 'S110' in b.dette(), [j110.get('reason', '')[:60], list(b.dette())])
t111 = ecrire_t('S111', tours('', 12)); ecrire_t('F111', herite(tours('', 4), 'S111'))
b.stop('S111', t111)
b.python('tamponne', 'F111')
Path(t111).write_text('\n'.join(json.dumps(x) for x in [frontiere('a12')] + tours('r', 2, parent='B')) + '\n')
b.stop('S111', t111)
verifie('30bp. synthèse d\'une fourche (jusqu\'à son point) après la dette, puis reconstruction : la dette reste', 'S111' in b.dette(), list(b.dette()))
t112 = ecrire_t('S112', tours('', 4)); b.python('tamponne', 'S112')
ajouter(t112, *tours('', 8, parent='a4', debut=5))
(b.etat / 'dettes').mkdir(parents=True, exist_ok=True)
(b.etat / 'dettes/S112.json').write_text(json.dumps({'session': 'S112', 'nb': 12, 'date': 'x', 't': time.time()}))
ajouter(t112, humain('e bis', uuid='h5b', parentUuid='a4'), assistant('a5b', 'h5b'))
b.stop('S112', t112)
verifie('30bq. dette d\'avant 3.12 (sans ancre), /rewind sous le seuil : effacée comme en 3.13', 'S112' not in b.dette(), list(b.dette()))
# comptes rendus : empreinte de la seule section de la session, toutes les signatures présentes vues
t113 = b.transcript('t113', tours('', 10))
cr113 = mem / 'sessions/2026-10-15-journee.md'; cr113.write_text('Session : S113\nDemandes : 10\n\nSynthèse de S113.\n')
r0 = bloque(b.stop('S113', t113)[1])
ajouter(t113, *tours('bis', 8, parent='a2', debut=3))
rc, j1 = b.stop('S113', t113)
with open(cr113, 'a', encoding='utf-8') as f:
    f.write('\n---\n\n## Suite (autre discussion)\n\nSession : T113\nDemandes : 5\n\nAutre session, même fichier.\n')
t_n = time.time() + 30; os.utime(cr113, (t_n, t_n))
rc, j2 = b.stop('S113', t113)
verifie('30br. bloc d\'une autre session ajouté au même fichier : le compte rendu d\'avant le /rewind n\'est pas réadopté',
        not r0 and bloque(j1) and bloque(j2) and 'S113' in b.dette(), [r0, j1.get('reason', '')[:40], j2])
t114 = b.transcript('t114', tours('', 10))
cr114 = mem / 'sessions/2026-10-15-S114.md'; cr114.write_text('Session : S114\nDemandes : 10\n')
b.stop('S114', t114)
ajouter(t114, *tours('bis', 8, parent='a2', debut=3))
[b.stop('S114', t114) for _ in range(4)]
t_n = time.time() + 30; os.utime(cr114, (t_n, t_n))
rc, j, out114, _ = b.appel('debut', {'session_id': 'S114', 'source': 'resume'})
verifie('30bs. démarrage : un compte rendu déjà vu, seulement touché par un checkout, ne solde pas la dette',
        'S114' in out114 and 'S114' in b.dette(), [out114[:160], list(b.dette())])
t115 = b.transcript('t115', tours('', 10))
cra = mem / 'sessions/2026-10-15-S115.md'; crb = mem / 'sessions/2026-10-15-S115-annexe.md'
cra.write_text('Session : S115\nDemandes : 10\n\nCorps principal.\n'); crb.write_text('Session : S115\nDemandes : 10\n\nAnnexe.\n')
t0 = time.time(); os.utime(cra, (t0 - 1, t0 - 1)); os.utime(crb, (t0, t0))
r0 = bloque(b.stop('S115', t115)[1])
ajouter(t115, *tours('bis', 8, parent='a2', debut=3))
rc, j1 = b.stop('S115', t115)
os.utime(cra, (t0 + 30, t0 + 30))
rc, j2 = b.stop('S115', t115)
verifie('30bt. deux comptes rendus de la même session : toucher l\'autre fichier ne le réadopte pas', not r0 and bloque(j1) and bloque(j2), [r0, j1.get('reason', '')[:40], j2])
# adoption d'un compte rendu : seulement s'il couvre davantage
tm122 = ecrire_t('M122', tours('', 10)); ajouter(tm122, *tours('m', 6, parent='a2', debut=3))
(mem / 'sessions/2026-10-15-M122.md').write_text('Session : M122\nDemandes : 10\nAncre : a10\n')
ecrire_t('F122', herite(tours('', 2) + tours('m', 6, parent='a2', debut=3), 'M122'))
b.python('tamponne', 'F122')
b.stop('M122', tm122)
ajouter(tm122, *tours('m', 2, parent='ma8', debut=9))
rc, j122 = b.stop('M122', tm122)
verifie('30bu. compte rendu d\'avant le /rewind vu pour la première fois : ne remplace pas une couverture plus large', not bloque(j122), [j122, etat_de('M122')])
# signatures de 3.14 (empreinte du fichier entier) : reconnues
t123 = b.transcript('t123', tours('', 10))
cr123 = mem / 'sessions/2026-10-15-S123.md'; cr123.write_text('Session : S123\nDemandes : 10\n\nSynthèse.\n')
h314 = hashlib.sha1('\n'.join(x.rstrip() for x in cr123.read_text().splitlines()).strip().encode()).hexdigest()[:16]
(b.etat / 'S123.json').write_text(json.dumps({'tampon': 10, 'ancre_tampon': 'a10', 'rapports_vus': [[10, '', h314]], 'transcript': t123}))
ajouter(t123, *tours('v', 8, parent='a2', debut=3))
t_n = time.time() + 30; os.utime(cr123, (t_n, t_n))
rc, j123 = b.stop('S123', t123)
verifie('30bv. état de 3.14 (empreinte du fichier entier) : compte rendu déjà vu, pas réadopté', bloque(j123), j123)
# mère reconstruite après la fourche : sa nouvelle dette n'est pas effacée par la fourche
tmr = ecrire_t('M124', tours('', 10)); ecrire_t('F124', herite(tours('', 10), 'M124'))
Path(tmr).write_text('\n'.join(json.dumps(x) for x in [frontiere('a10')] + tours('r', 9, parent='B')) + '\n')
b.stop('M124', tmr)
b.python('tamponne', 'F124')
verifie('30bx. mère au transcript reconstruit après la fourche : la synthèse de la fourche n\'efface pas sa nouvelle dette', 'M124' in b.dette(), list(b.dette()))
# nouvelle synthèse dans un second fichier, l'ancien touché ensuite
t125 = b.transcript('t125', tours('', 10))
ca = mem / 'sessions/2026-10-15-S125.md'; ca.write_text('Session : S125\nDemandes : 10\n\nPremière synthèse.\n')
b.stop('S125', t125)
ajouter(t125, *tours('w', 8, parent='a2', debut=3))
rc, j1 = b.stop('S125', t125)
cb = mem / 'sessions/2026-10-15-S125-bis.md'; cb.write_text('Session : S125\nDemandes : 10\n\nSynthèse refaite.\n')
t_n = time.time() + 30; os.utime(cb, (t_n, t_n)); os.utime(ca, (t_n + 10, t_n + 10))
rc, j2 = b.stop('S125', t125)
verifie('30by. synthèse refaite dans un second fichier, le premier touché après : la nouvelle est adoptée', bloque(j1) and not bloque(j2), [j1.get('reason', '')[:40], j2])
# section : finit au bloc d'une autre session, pas à une ligne qui commence par « Session : »
t126 = b.transcript('t126', tours('', 10))
c126 = mem / 'sessions/2026-10-15-S126.md'; c126.write_text('Session : S126\nDemandes : 10\n\nSession : reprise prévue demain.\n')
b.stop('S126', t126)
ajouter(t126, *tours('w', 8, parent='a2', debut=3))
rc, j1 = b.stop('S126', t126)
with open(c126, 'a', encoding='utf-8') as f:
    f.write('\nSynthèse refaite après le /rewind.\n')
t_n = time.time() + 30; os.utime(c126, (t_n, t_n))
rc, j2 = b.stop('S126', t126)
verifie('30bz. complément écrit après une ligne « Session : » qui n\'est pas un bloc : reconnu', bloque(j1) and not bloque(j2), [j1.get('reason', '')[:40], j2])
# démarrage : état perdu, compte rendu déjà présent à la dette ou ancré sur une branche quittée
t127 = b.transcript('t127', tours('', 10))
c127 = mem / 'sessions/2026-10-15-S127.md'; c127.write_text('Session : S127\nDemandes : 10\n')
b.stop('S127', t127)
ajouter(t127, *tours('w', 8, parent='a2', debut=3))
[b.stop('S127', t127) for _ in range(4)]
(b.etat / 'S127.json').unlink()
t_n = time.time() + 30; os.utime(c127, (t_n, t_n))
rc, j, out127, _ = b.appel('debut', {'session_id': 'S127', 'source': 'resume'})
t128 = ecrire_t('S128', tours('', 10)); ajouter(t128, *tours('p', 8, parent='a2', debut=3))
b.stop('S128', t128)
(mem / 'sessions/2026-10-15-S128.md').write_text('Session : S128\nDemandes : 10\nAncre : a10\n')
(b.etat / 'S128.json').unlink()
rc, j, out128, _ = b.appel('debut', {'session_id': 'S128', 'source': 'resume'})
verifie('30ca. démarrage, état perdu : un compte rendu touché par un checkout, ou ancré sur une branche quittée, ne solde pas la dette',
        'S127' in out127 and 'S127' in b.dette() and 'S128' in out128 and 'S128' in b.dette(), [out127[:120], out128[:120], list(b.dette())])
# pause sans fin : la dette garde son âge
t129 = b.transcript('t129', tours('', 6))
b.stop('S129', t129, background_tasks=[{'id': 'w1', 'status': 'running'}])
d129 = json.loads((b.etat / 'dettes/S129.json').read_text()); d129['t'] -= 7200
(b.etat / 'dettes/S129.json').write_text(json.dumps(d129))
b.stop('S129', t129, background_tasks=[{'id': 'w1', 'status': 'running'}])
rc, j, out129, _ = b.appel('debut', {'session_id': 'AUTRE-129', 'source': 'startup'})
verifie('30cb. Stop répétés pendant une pause, même compte : la dette garde son âge et est rappelée', 'S129' in out129, out129[:160])
t105 = b.transcript('t105', tours('', 10))
cr105 = mem / 'sessions/2026-10-15-S105.md'; cr105.write_text('Session : S105\nDemandes : 10\n')
(b.etat / 'S105.json').write_text(json.dumps({'tampon': 10, 'ancre_tampon': 'a10', 'rapports_vus': [[10, '']], 'transcript': t105}))
ajouter(t105, *tours('v', 8, parent='a2', debut=3))
t_n = time.time() + 30; os.utime(cr105, (t_n, t_n))
rc, j1 = b.stop('S105', t105)
cr105.write_text('Session : S105\nDemandes : 10\n\nRéécrit après le /rewind.\n'); os.utime(cr105, (t_n + 5, t_n + 5))
rc, j2 = b.stop('S105', t105)
verifie('30bj. état de 3.13 (signature sans empreinte) : compte rendu présent non réadopté, réécrit reconnu',
        bloque(j1) and not bloque(j2), [j1.get('reason', '')[:60], j2])
tcr = b.transcript('tcr', [humain('a'), humain('b'), humain('c')])
b.appel('prompt', {'session_id': 'S106', 'prompt': 'Point de contrôle : relire les PR', 'transcript_path': tcr})
b.appel('prompt', {'session_id': 'S106', 'prompt': 'quatrième, envoyée pendant le tour planifié', 'transcript_path': tcr})
ajouter(tcr, {'type': 'user', 'origin': {'kind': 'scheduled'}, 'message': {'role': 'user', 'content': 'Point de contrôle : relire les PR'}})
rc, j1 = b.stop('S106', tcr, session_crons=[{'id': 'c1', 'prompt': 'Point de contrôle'}])
rc, j2 = b.stop('S106', tcr)
verifie('30m3. demande humaine envoyée pendant un tour planifié, pas encore écrite : gardée jusqu\'au Stop suivant',
        not bloque(j1) and bloque(j2) and '4 demandes' in j2.get('reason', ''), [j1, j2])
(b.etat / 'S121.json').write_text(json.dumps({'rapports_vus': [None, 5, [4, '', 'x'], ['a', ['b']], 'z']}))
(mem / 'sessions/2026-10-15-S121.md').write_text('Session : S121\nDemandes : 2\n')
rc121, j121 = b.stop('S121', b.transcript('t121', tours('', 12)))
verifie('30s4. rapports_vus aux éléments invalides : le Stop fonctionne et relance', rc121 == 0 and bloque(j121), j121)
egare = b.home / '.claude/projects/-tmp-agent'; egare.mkdir(parents=True, exist_ok=True)
(egare / 'S130.jsonl').write_text(json.dumps(ancien('une')) + '\n')
principal = proj / 'S130.jsonl'; principal.write_text('\n'.join(json.dumps(x) for x in tours('', 10)) + '\n')
sonde3 = ("import sys; sys.argv = ['x']; sys.path.insert(0, %r); import vive_memoire as m\n"
          "m.glob.glob = lambda motif: [%r, %r]\n"
          "print(m.trouver_transcript('S130'))\n") % (str(b.hooks), str(egare / 'S130.jsonl'), str(principal))
r130 = subprocess.run([sys.executable, '-I', '-c', sonde3], capture_output=True, text=True, timeout=30, env=b.env())
verifie('30cd. deux transcripts du même nom (un agent lancé ailleurs) : le principal est choisi', r130.stdout.strip() == str(principal), [r130.stdout, r130.stderr[-200:]])
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
conf = b.racine / 'conf-$HOME-"x" y'
r = installer(b.racine / 'mac11', sup={'CLAUDE_CONFIG_DIR': str(conf)})
cmd_stop = json.loads((conf / 'settings.json').read_text())['hooks']['Stop'][-1]['hooks'][0]['command']
verifie('46. chemin de config avec $, " et espace : commande citée, script trouvé', r.returncode == 0 and Path(shlex.split(cmd_stop)[1]).is_file(), [r.stderr[-200:], cmd_stop])
(b.racine / 'travail').mkdir()
r = installer(b.racine / 'mac12', cwd=str(b.racine / 'travail'), sup={'CLAUDE_CONFIG_DIR': 'conf-relative'})
cmd_rel = json.loads((b.racine / 'travail/conf-relative/settings.json').read_text())['hooks']['Stop'][-1]['hooks'][0]['command']
verifie('47. CLAUDE_CONFIG_DIR relatif : commande enregistrée en chemin absolu', r.returncode == 0 and Path(shlex.split(cmd_rel)[1]).is_absolute(), cmd_rel)
ami = b.racine / "conf l'ami"
installer(b.racine / 'mac13', sup={'CLAUDE_CONFIG_DIR': str(ami)})
installer(b.racine / 'mac13', sup={'CLAUDE_CONFIG_DIR': str(ami)})
nos = [h['command'] for g in json.loads((ami / 'settings.json').read_text())['hooks']['Stop'] for h in g['hooks']]
r = installer(b.racine / 'mac13', '--retirer', sup={'CLAUDE_CONFIG_DIR': str(ami)})
reste = json.loads((ami / 'settings.json').read_text()).get('hooks', {})
verifie('48. chemin avec espace et apostrophe : une seule inscription, et --retirer l\'enlève', len(nos) == 1 and r.returncode == 0 and not reste, [nos, reste])
h14 = b.racine / 'mac14'; h14.mkdir()
installer(h14)
(h14 / '.claude/skills/vive-memoire/notes-perso.txt').write_text('à garder')
(h14 / '.claude/hooks/vive-memoire/vive_memoire.py').write_text('# version tronquée\n')
r = installer(h14)
restes = [x.name for x in (h14 / '.claude/hooks').iterdir()] + [x.name for x in (h14 / '.claude/skills').iterdir()]
verifie('49. mise à jour par échange de dossiers : fichiers neufs, ajouts gardés, aucun reste',
        r.returncode == 0 and (h14 / '.claude/skills/vive-memoire/notes-perso.txt').exists()
        and 'VERSION' in (h14 / '.claude/hooks/vive-memoire/vive_memoire.py').read_text() and sorted(restes) == ['vive-memoire', 'vive-memoire'], restes)
# mise à jour qui échoue en route : l'installation précédente reste entière
h15 = b.racine / 'mac15'; h15.mkdir()
installer(h15)
inst15 = h15 / '.claude/hooks/vive-memoire'
(inst15 / 'vive_memoire.py').write_text("VERSION = '0.1'\n")
(inst15 / 'gros-perso.bin').write_bytes(b'x' * 2_000_000)
r = subprocess.run(['bash', '-c', 'ulimit -f 1000; exec bash "$0"', str(ICI / 'installe-mac.sh')], capture_output=True, text=True,
                   env=dict(BASE_ENV, HOME=str(h15)))
taille = (inst15 / 'gros-perso.bin').stat().st_size if (inst15 / 'gros-perso.bin').exists() else -1
verifie('50. fichier ajouté à la main impossible à recopier (disque plein) : mise à jour annulée, rien de perdu',
        r.returncode != 0 and taille == 2_000_000 and (inst15 / 'vive_memoire.py').read_text() == "VERSION = '0.1'\n", [r.returncode, taille, r.stdout[-200:]])
h16 = b.racine / 'mac16'; h16.mkdir()
installer(h16)
(h16 / '.claude/hooks/vive-memoire/vive_memoire.py').write_text("VERSION = '0.1'\n")
(h16 / '.claude/skills/vive-memoire/SKILL.md').write_text('ancienne skill\n')
faux = b.racine / 'faux-mv'; faux.mkdir()
(faux / 'mv').write_text('#!/bin/bash\nfor x in "$@"; do last="$x"; done\ncase "$last" in */skills/vive-memoire) exit 1;; esac\nexec /bin/mv "$@"\n')
os.chmod(faux / 'mv', 0o755)
r = installer(h16, sup={'PATH': str(faux) + os.pathsep + BASE_ENV.get('PATH', '')})
restes16 = sorted(x.name for x in (h16 / '.claude/hooks').iterdir()) + sorted(x.name for x in (h16 / '.claude/skills').iterdir())
verifie('51. échange de la skill impossible après celui des hooks : les deux reviennent à l\'ancienne version',
        r.returncode != 0 and (h16 / '.claude/hooks/vive-memoire/vive_memoire.py').read_text() == "VERSION = '0.1'\n"
        and (h16 / '.claude/skills/vive-memoire/SKILL.md').read_text() == 'ancienne skill\n' and restes16 == ['vive-memoire', 'vive-memoire'],
        [r.returncode, restes16, r.stdout[-200:]])
# ancien fichier de dettes partagé : effacements simultanés sérialisés
etat17 = b.racine / 'etat-dettes-anciennes'; etat17.mkdir()
perdus = 0
for tour in range(3):
    noms = [f'L{tour}-{k}' for k in range(16)]
    (etat17 / 'dette.json').write_text(json.dumps({n: {'nb': 5, 'date': 'x', 't': 0} for n in noms}))
    code = "import sys; n = sys.argv[-1]; sys.argv = ['x']; sys.path.insert(0, %r); import vive_memoire as m; m.effacer_dette(n)" % str(b.hooks)
    lots = [subprocess.Popen([sys.executable, '-I', '-c', code, n], env=b.env({'VM_ETAT': str(etat17)})) for n in noms]
    [x.wait(timeout=60) for x in lots]
    perdus += len(json.loads((etat17 / 'dette.json').read_text()))
verifie('30cc. ancien fichier de dettes : 16 effacements simultanés, aucun ne revient', perdus == 0, perdus)
shutil.rmtree(b.racine, ignore_errors=True)
print(f'\n{total} vérifications, {len(echecs)} échec(s)')
sys.exit(1 if echecs else 0)
