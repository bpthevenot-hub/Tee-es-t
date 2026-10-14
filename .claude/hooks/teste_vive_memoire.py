"""Banc des hooks « vive mémoire » : 30 scénarios, dans un HOME et un état temporaires isolés.

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
        try:
            return json.loads((self.etat / 'dette.json').read_text())
        except OSError:
            return {}


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
tf = b.transcript('tf', [humain('a'), humain('b'), file_humaine('c', 'U9'), humain('c', mergedSendUuids=['U9'])])
rc, j = b.stop('S5', tf)
verifie('08. message en file puis fusionné : compté une fois', not bloque(j), j)
b.appel('prompt', {'session_id': 'S6', 'prompt': 'quatrième demande pas encore écrite'})
b.appel('prompt', {'session_id': 'S6', 'prompt': '<task-notification> automatique'})
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
d = b.dette(); d['S7']['t'] = time.time() - 7200; (b.etat / 'dette.json').write_text(json.dumps(d))
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
verifie('20. tâche en file (pending) : pause aussi', not bloque(b.stop('S11', t4, background_tasks=[{'id': 'q1', 'status': 'pending'}])[1]))
verifie('21. réveil ponctuel planifié : pause aussi', not bloque(b.stop('S12', t4, session_crons=[{'id': 'c1', 'recurring': False}])[1]))
t5 = b.transcript('t5', [humain(str(i)) for i in range(5)])
rc, j = b.stop('S10', t5, background_tasks=[{'id': 'w1', 'status': 'running'}])
verifie('22. même tâche sans fin + nouvelle demande : la pause cesse', bloque(j), j)
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
tk = b.transcript('tk', [humain('a', forkedFrom={'sessionId': 'S16'}), humain('b'), humain('c'), humain('d')])
verifie('28. fourche : hérite de la synthèse de la session mère', not bloque(b.stop('S18', tk)[1]))
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
shutil.rmtree(b.home / '.claude/hooks'); (b.home / '.claude/settings.json').unlink()
rc, j, _, _ = b.appel('stop', 'pas du json')
verifie('30a. entrée invalide : code 0, rien', rc == 0 and j == {}, j)
verifie('30b. transcript illisible (dossier) : pas de blocage', not bloque(b.stop('S22', str(b.racine))[1]))
verifie('30c. le hook ne sort jamais en code 2', {b.stop('S23', t4)[0] for _ in range(5)} == {0})

# --- installeur Mac, dans un HOME temporaire
h = b.racine / 'mac'; (h / '.claude').mkdir(parents=True)
(h / '.claude/settings.json').write_text(json.dumps({'model': 'opus', 'hooks': {'Stop': [{'matcher': '', 'hooks': [
    {'type': 'command', 'command': 'echo voisin'}, {'type': 'command', 'command': 'bash /ancien/vive-memoire-stop.sh stop'}]}]}}))
env_mac = dict(BASE_ENV, HOME=str(h))
r1 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=env_mac)
r2 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=env_mac)
s = json.loads((h / '.claude/settings.json').read_text())
cmds = [x['command'] for g in s['hooks']['Stop'] for x in g['hooks']]
verifie('31. installeur idempotent, voisin conservé, ancienne entrée remplacée',
        r1.returncode == r2.returncode == 0 and s.get('model') == 'opus' and 'echo voisin' in cmds
        and sum('vive-memoire' in c for c in cmds) == 1 and (h / '.claude/skills/vive-memoire/SKILL.md').exists(), [r1.stdout, r2.stderr, cmds])
r3 = subprocess.run(['bash', str(ICI / 'installe-mac.sh'), '--retirer'], capture_output=True, text=True, env=env_mac)
s = json.loads((h / '.claude/settings.json').read_text())
verifie('32. --retirer enlève hooks et skill, garde le voisin',
        r3.returncode == 0 and not (h / '.claude/skills/vive-memoire/SKILL.md').exists()
        and [x['command'] for g in s['hooks']['Stop'] for x in g['hooks']] == ['echo voisin'], [r3.stdout, s])
r4 = subprocess.run(['bash', str(ICI / 'installe-mac.sh')], capture_output=True, text=True, env=dict(env_mac, CLAUDE_CODE_REMOTE='1'))
verifie('33. installeur refusé en cloud', r4.returncode == 1, r4.stdout)
shutil.rmtree(b.racine, ignore_errors=True)
print(f'\n{total} vérifications, {len(echecs)} échec(s)')
sys.exit(1 if echecs else 0)
