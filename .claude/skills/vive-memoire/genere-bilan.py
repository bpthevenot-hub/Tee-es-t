#!/usr/bin/env python3
"""Génère un bilan interactif à partir de bilan-template.html et d'une spec JSON.

Usage :
  python3 genere-bilan.py spec.json sortie.html             # page autonome (doctype, à ouvrir en local / à versionner)
  python3 genere-bilan.py --artifact spec.json sortie.html  # même page sans enveloppe, prête à publier en artifact

La spec JSON :
{
  "titre": "phrase-titre affichée en h1", "titre_court": "Nom court de l'onglet (2-4 mots)",
  "date": "14 octobre 2026", "duree": "12 demandes", "modele": "Claude Code (cloud)", "nb_skills": 2,
  "livre":   [{"titre": "…", "texte": "…", "lien": "https://…", "lien_texte": "ouvrir"}],
  "decide":  [{"titre": "D-015 — …", "texte": "…"}],
  "attente": [{"titre": "…", "texte": "…", "lien": "…"}],          # cochables, mémorisés dans le navigateur
  "mots":    [{"mot": "déploie Relève", "sens": "ce que ça déclenche"}],  # un clic copie
  "quiz":    [{"question": "…", "choix": ["a", "b", "c"], "bonne": 1, "explication": "…"}],
  "temps":   [{"quand": "13 oct.", "quoi": "…"}],
  "pieges":  "réseau du conteneur : WebFetch bloqué"
}
Les compteurs sont déduits des listes. Le script refuse une page dont un placeholder reste vide.
"""
import html
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent


def e(s) -> str:
    return html.escape(str(s), quote=True)


def lien(c: dict) -> str:
    if not c.get('lien'):
        return ''
    return f' <a href="{e(c["lien"])}" target="_blank" rel="noopener">{e(c.get("lien_texte", "ouvrir"))} ↗</a>'


def carte(c: dict, etat: str, libelle: str, coche_id: str | None = None) -> str:
    coche = ''
    if coche_id:
        coche = f'<label class="coche" for="{coche_id}"><input type="checkbox" id="{coche_id}"> fait</label>'
    return (f'<article class="carte"><span class="etat {etat}">{e(libelle)}</span>'
            f'<h3>{e(c["titre"])}</h3><p>{e(c.get("texte", ""))}{lien(c)}</p>{coche}</article>')


def slug(s: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', s.lower())
    return s.strip('-')[:40] or 'x'


def question(q: dict, i: int) -> str:
    boutons = ''.join(
        f'<button type="button"{" data-juste" if j == q["bonne"] else ""}>{e(c)}</button>'
        for j, c in enumerate(q['choix']))
    return (f'<article class="question" id="q-{i}"><h3>{e(q["question"])}</h3>'
            f'<div class="choix">{boutons}</div><p class="explication" hidden>{e(q.get("explication", ""))}</p></article>')


def main(argv: list[str]) -> None:
    artifact = '--artifact' in argv
    args = [a for a in argv if a != '--artifact']
    if len(args) != 2:
        sys.exit(__doc__)
    spec = json.loads(Path(args[0]).read_text(encoding='utf-8'))
    gabarit = (ICI / 'bilan-template.html').read_text(encoding='utf-8')
    attente = spec.get('attente', [])
    valeurs = {
        'TITRE': e(spec['titre']),
        'TITRE_COURT': e(spec.get('titre_court', spec['titre'])),
        'DATE': e(spec['date']),
        'DUREE': e(spec.get('duree', '')),
        'MODELE': e(spec.get('modele', '')),
        'NB_LIVRES': str(len(spec.get('livre', []))),
        'NB_DECISIONS': str(len(spec.get('decide', []))),
        'NB_SKILLS': str(spec.get('nb_skills', 0)),
        'NB_ATTENTE': str(len(attente)),
        'NB_QUIZ': str(len(spec.get('quiz', []))),
        'CARTES_LIVRE': ''.join(carte(c, 'ok', 'livré') for c in spec.get('livre', [])),
        'CARTES_DECIDE': ''.join(carte(c, 'decision', 'décidé') for c in spec.get('decide', [])),
        'CARTES_ATTENTE': ''.join(carte(c, 'attente', 'à toi', f'fait-{i}-{slug(c["titre"])}') for i, c in enumerate(attente)),
        'MOTS': ''.join(f'<button type="button" class="mot" data-mot="{e(m["mot"])}">{e(m["mot"])}<small>{e(m.get("sens", ""))}</small></button>'
                        for m in spec.get('mots', [])),
        'QUIZ': ''.join(question(q, i) for i, q in enumerate(spec.get('quiz', []))) or '<p>Pas de quiz pour cette session.</p>',
        'LIGNE_TEMPS': ''.join(f'<li><time>{e(t["quand"])}</time>{e(t["quoi"])}</li>' for t in spec.get('temps', [])),
        'PIEGES': e(spec.get('pieges', '')),
    }
    page = gabarit
    for cle, val in valeurs.items():
        page = page.replace('{{' + cle + '}}', val)
    reste = re.findall(r'\{\{[A-Z_]+\}\}', page)
    if reste:
        sys.exit('placeholders non remplis : ' + ', '.join(sorted(set(reste))))
    if not artifact:
        page = '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n' + page + '\n</body>\n</html>\n'
    Path(args[1]).write_text(page, encoding='utf-8')
    print(f'bilan écrit : {args[1]} ({len(page)} caractères, {"artifact" if artifact else "autonome"})')


if __name__ == '__main__':
    main(sys.argv[1:])
