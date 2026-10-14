"""Banc des hooks « vive mémoire » : 20 scénarios, dans un HOME et un état temporaires.

Usage : python3 teste_vive_memoire.py      (code 0 si tout passe)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
ENVELOPPE = ICI / 'vive-memoire-stop.sh'
echecs = []


def verifie(nom, condition, detail=''):
    print(('ok   ' if condition else 'ÉCHEC') + ' ' + nom + ('' if condition else '  → ' + detail))
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
        self.enveloppe = self.projet / '.claude/hooks/vive-memoire-stop.sh'

    def transcript(self, nom, entrees):
        p = self.racine / (nom + '.jsonl')
        p.write_text('\n'.join(json.dumps(e) for e in entrees) + '\n', encoding='utf-8')
        return str(p)

    def appel(self, mode, entree, env_sup=None, enveloppe=None):
        env = dict(os.environ, HOME=str(self.home), CLAUDE_PROJECT_DIR=str(self.projet))
        env.update(env_sup or {})
        r = subprocess.run(['bash', str(enveloppe or self.enveloppe), mode], input=json.dumps(entree) if not isinstance(entree, str) else entree,
                           capture_output=True, text=True, env=env, timeout=30)
        sortie = r.stdout.strip()
        try:
            j = json.loads(sortie.splitlines()[-1]) if sortie else {}
        except ValueError:
            j = {'brut': sortie}
        return r.returncode, j, r.stderr

    def stop(self, session, transcript, **kw):
        return self.appel('stop', {'session_id': session, 'transcript_path': transcript, 'stop_hook_active': False, **kw})


def humain(t):
    return {'type': 'user', 'origin': {'kind': 'human'}, 'message': {'role': 'user', 'content': t}}


def notif(t):
    return {'type': 'user', 'origin': {'kind': 'task-notification'}, 'message': {'role': 'user', 'content': t}}


def ancien(t):
    return {'type': 'user', 'message': {'role': 'user', 'content': t}}


def bloque(j):
    return j.get('decision') == 'block'


b = Bac()
t3 = b.transcript('t3', [humain('a'), humain('b'), notif('<task-notification> x'), humain('c')])
t4 = b.transcript('t4', [humain('a'), humain('b'), humain('c'), humain('d')])
rc, j, _ = b.stop('S1', t3)
verifie('1. trois demandes humaines : pas de blocage', rc == 0 and not bloque(j), str(j))
rc, j, _ = b.stop('S1', t4)
verifie('2. quatre demandes : blocage JSON, code 0', rc == 0 and bloque(j) and '4 demandes' in j.get('reason', ''), str(j))
verifie('2b. la consigne donne la commande tamponne', 'tamponne S1' in j.get('reason', ''), j.get('reason', '')[:200])
tw = b.transcript('tw', [humain('a')] + [notif('<github-webhook-activity> ci')] * 5)
rc, j, _ = b.stop('S2', tw)
verifie('3. webhooks et notifications ne comptent pas', not bloque(j), str(j))
ta = b.transcript('ta', [ancien('a'), ancien('b'), ancien('<github-webhook-activity> x'), ancien('<task-notification> y'), ancien('c')])
rc, j, _ = b.stop('S3', ta)
verifie('4. repli sans « origin » : préfixes techniques exclus', not bloque(j), str(j))
tq = b.transcript('tq', [humain('a'), humain('b'), humain('c'),
                         {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': 'merge', 'source_uuid': 'U1', 'humanTurn': True}},
                         {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': 'merge', 'source_uuid': 'U1', 'humanTurn': True}},
                         {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': '<github-webhook-activity>', 'source_uuid': 'U2'}}])
rc, j, _ = b.stop('S4', tq)
verifie('5. commande en file humaine comptée une fois', bloque(j) and '4 demandes' in j.get('reason', ''), str(j))
b.appel('prompt', {'session_id': 'S5', 'prompt': 'quatrième demande pas encore écrite'})
b.appel('prompt', {'session_id': 'S5', 'prompt': '<task-notification> automatique'})
rc, j, _ = b.stop('S5', t3)
verifie('6. demande pas encore au transcript comptée (écriture différée)', bloque(j) and '4 demandes' in j.get('reason', ''), str(j))
codes = [bloque(b.stop('S6', t4)[1]) for _ in range(3)]
rc, j, _ = b.stop('S6', t4)
verifie('7. trois relances puis libération', codes == [True] * 3 and not bloque(j) and 'systemMessage' in j, str(codes) + str(j))
dette = json.loads((b.home / '.claude/vive-memoire/dette.json').read_text())
verifie('7b. dette enregistrée', 'S6' in dette, str(dette))
rc, j, _ = b.stop('S6', t4)
verifie('8. après libération, plus de relance sans nouvelles demandes', not bloque(j), str(j))
t12 = b.transcript('t12', [humain(str(i)) for i in range(12)])
rc, j, _ = b.stop('S6', t12)
verifie('8b. huit nouvelles demandes : relance de nouveau', bloque(j), str(j))
rc, j, _ = b.appel('debut', {'session_id': 'S7', 'source': 'startup'})
r = subprocess.run(['bash', str(b.enveloppe), 'debut'], input=json.dumps({'session_id': 'S7'}), capture_output=True, text=True,
                   env=dict(os.environ, HOME=str(b.home), CLAUDE_PROJECT_DIR=str(b.projet)))
verifie('9. le démarrage suivant rappelle la dette', 'S6' in r.stdout and 'tamponne' in r.stdout, r.stdout[:200])
r = subprocess.run([sys.executable, '-I', str(b.projet / '.claude/hooks/vive_memoire.py'), 'tamponne', 'S6'], capture_output=True, text=True,
                   env=dict(os.environ, HOME=str(b.home)))
dette = json.loads((b.home / '.claude/vive-memoire/dette.json').read_text())
verifie('10. tamponne efface la dette', r.returncode == 0 and 'S6' not in dette, r.stdout + str(dette))
rc, j, _ = b.stop('S1', t4)
rc2, j2, _ = b.stop('S9', t4)
verifie('11. deux sessions ont chacune leur état', bloque(j) and bloque(j2) and 'relance 2/3' in j['reason'] and 'relance 1/3' in j2['reason'], str(j)[:120] + str(j2)[:120])
rc, j, _ = b.stop('S10', t4, background_tasks=[{'id': 'w1', 'type': 'workflow', 'status': 'running'}])
etat = b.home / '.claude/vive-memoire/S10.json'
verifie('12. travail en arrière-plan : pas de blocage ni de relance', not bloque(j) and not etat.exists(), str(j))
bloqueur = b.racine / 'fichier-ordinaire'; bloqueur.write_text('')
rc, j, _ = b.appel('stop', {'session_id': 'S11', 'transcript_path': t4}, {'VM_ETAT': str(bloqueur / 'etat')})
verifie('13. état non inscriptible : message, pas de blocage', not bloque(j) and 'systemMessage' in j, str(j))
seul = b.racine / 'seul'; seul.mkdir(); shutil.copy(ICI / 'vive-memoire-stop.sh', seul / 'vive-memoire-stop.sh')
rc, j, err = b.appel('stop', {'session_id': 'S12', 'transcript_path': t4}, enveloppe=seul / 'vive-memoire-stop.sh')
verifie('14. vive_memoire.py absent : silence, code 0', rc == 0 and j == {}, str(j) + err)
faux = b.racine / 'bin'; faux.mkdir()
for c in ('bash', 'cat', 'dirname', 'printf'):
    w = shutil.which(c)
    if w:
        os.symlink(w, faux / c)
rc, j, err = b.appel('stop', {'session_id': 'S13', 'transcript_path': t4}, {'PATH': str(faux)})
verifie('15. sans python3 : message, pas de blocage', rc == 0 and 'systemMessage' in j and not bloque(j), str(j) + err)
mem = b.projet / 'docs/context'; (mem / 'sessions').mkdir(parents=True); (mem / 'decision-log.md').write_text('# D\n')
(mem / 'sessions/2026-10-14-x.md').write_text('Session : S14\nDemandes : 4\n')
rc, j, _ = b.stop('S14', t4)
verifie('16. tampon durable (compte rendu commité) reconnu', not bloque(j), str(j))
inst = b.home / '.claude/hooks/vive-memoire'; inst.mkdir(parents=True)
for f in ('vive_memoire.py', 'vive-memoire-stop.sh'):
    shutil.copy(ICI / f, inst / f)
rc, j, _ = b.stop('S15', t4)
verifie('17. installation utilisateur présente : la copie du dépôt se tait', j == {}, str(j))
rc, j, _ = b.appel('stop', {'session_id': 'S15', 'transcript_path': t4}, enveloppe=inst / 'vive-memoire-stop.sh')
verifie('17b. … et la copie utilisateur prend le relais', bloque(j), str(j))
shutil.rmtree(inst)
rc, j, _ = b.appel('stop', 'pas du json')
verifie('18. entrée invalide : code 0, rien', rc == 0 and j == {}, str(j))
rc, j, _ = b.stop('S16', str(b.racine))
verifie('19. transcript illisible (dossier) : pas de blocage', rc == 0 and not bloque(j), str(j))
codes = {b.stop('S17', t4)[0] for _ in range(5)}
verifie('20. le hook ne sort jamais en code 2', codes == {0}, str(codes))
shutil.rmtree(b.racine, ignore_errors=True)
print(f'\n{20 - len([e for e in echecs if e[:2].strip(".").isdigit()])} scénarios, {len(echecs)} échec(s)')
sys.exit(1 if echecs else 0)
