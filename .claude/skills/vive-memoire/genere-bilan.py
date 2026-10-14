#!/usr/bin/env python3
"""Génère un bilan interactif à partir de bilan-template.html et d'une spec JSON.

Usage :
  python3 genere-bilan.py spec.json sortie.html             # page autonome (doctype, à ouvrir en local / à versionner)
  python3 genere-bilan.py --artifact spec.json sortie.html  # même page sans enveloppe, prête à publier en artifact

La spec JSON :
{
  "titre": "phrase-titre affichée en h1", "titre_court": "Nom de l'onglet, 2 à 4 mots (obligatoire)",
  "date": "14 octobre 2026", "duree": "12 demandes", "modele": "Claude Code (cloud)", "nb_skills": 2,
  "livre":   [{"titre": "…", "texte": "…", "lien": "https://…", "lien_texte": "ouvrir"}],
  "decide":  [{"titre": "D-015 — …", "texte": "…"}],
  "attente": [{"titre": "…", "texte": "…", "lien": "…"}],          # cochables, mémorisés dans le navigateur
  "mots":    [{"mot": "déploie Relève", "sens": "ce que ça déclenche"}],  # un clic copie
  "quiz":    [{"question": "…", "choix": ["a", "b", "c"], "bonne": 1, "explication": "…"}],  # bonne : index à partir de 0
  "temps":   [{"quand": "13 oct.", "quoi": "…"}],
  "pieges":  "réseau du conteneur : WebFetch bloqué"
}
Les compteurs sont déduits des listes. Le script refuse : titre, titre_court ou date vides, titre_court de plus
de 4 mots ou de moins de 2, clé inconnue, type invalide, lien qui n'est pas en https://, quiz mal formé, et un bilan écrit dans un dossier « bilans/ » qui n'est
pas voisin d'un decision-log.md (évite d'écrire la mémoire dans le mauvais dépôt).
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent


def e(s) -> str:
    return html.escape(str(s), quote=True)


def refuse(message: str) -> None:
    sys.exit('spec refusée : ' + message)


def lien(c: dict) -> str:
    if not c.get('lien'):
        return ''
    url = str(c['lien']).strip()
    if not re.match(r'^https://', url):
        refuse(f'lien non https dans « {c.get("titre", "?")} » : {url[:60]}')
    return f' <a href="{e(url)}" target="_blank" rel="noopener">{e(c.get("lien_texte") or "ouvrir")} ↗</a>'


def slug(s: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', str(s).lower())
    return s.strip('-')[:30] or 'x'


def carte(c: dict, etat: str, libelle: str, coche_id: str = '') -> str:
    if not str(c.get('titre') or '').strip():
        refuse(f'carte sans titre dans « {libelle} »')
    coche = ''
    if coche_id:
        coche = (f'<label class="coche" for="{coche_id}"><input type="checkbox" id="{coche_id}"> '
                 f'fait<span class="sr-only"> : {e(c["titre"])}</span></label>')
    return (f'<article class="carte"><span class="etat {etat}">{e(libelle)}</span>'
            f'<h3>{e(c["titre"])}</h3><p>{e(c.get("texte") or "")}{lien(c)}</p>{coche}</article>')


def ids_cases(cartes: list) -> list:
    vus, ids = {}, []
    for c in cartes:
        base = 'fait-' + slug(c.get('titre', '')) + '-' + hashlib.sha1(str(c.get('titre', '')).encode('utf-8')).hexdigest()[:6]
        vus[base] = vus.get(base, 0) + 1
        ids.append(base if vus[base] == 1 else f'{base}-{vus[base]}')
    return ids


def question(q: dict, i: int) -> str:
    choix, bonne = q.get('choix'), q.get('bonne')
    if not str(q.get('question') or '').strip() or not isinstance(choix, list) or len(choix) < 2:
        refuse(f'question {i + 1} : texte vide ou moins de deux choix')
    if not all(isinstance(c, str) and c.strip() for c in choix) or len({c.strip() for c in choix}) != len(choix):
        refuse(f'question {i + 1} : chaque choix doit être un texte non vide et distinct')
    if not isinstance(bonne, int) or isinstance(bonne, bool) or not 0 <= bonne < len(choix):
        refuse(f'question {i + 1} : « bonne » doit être un index de 0 à {len(choix) - 1}')
    boutons = ''.join(
        f'<button type="button"{" data-juste" if j == bonne else ""}>{e(c)}</button>' for j, c in enumerate(choix))
    return (f'<article class="question" id="q-{i}"><h3 id="q-{i}-t">{e(q["question"])}</h3>'
            f'<div class="choix" role="group" aria-labelledby="q-{i}-t">{boutons}</div><p class="explication" hidden>{e(q.get("explication") or "")}</p></article>')


def vide(texte: str) -> str:
    return f'<p class="vide">{e(texte)}</p>'


def main(argv: list[str]) -> None:
    artifact = '--artifact' in argv
    args = [a for a in argv if a != '--artifact']
    if len(args) != 2:
        sys.exit(__doc__)
    spec = json.loads(Path(args[0]).read_text(encoding='utf-8'))
    if not isinstance(spec, dict):
        refuse('la spec doit être un objet JSON')
    connues = {'titre', 'titre_court', 'sujet', 'date', 'duree', 'modele', 'nb_skills',
               'livre', 'decide', 'attente', 'mots', 'quiz', 'temps', 'pieges'}
    if set(spec) - connues:
        refuse('clés inconnues : ' + ', '.join(sorted(set(spec) - connues)) + ' (faute de frappe ?)')
    for cle in ('titre', 'titre_court', 'date'):
        if not isinstance(spec.get(cle), str) or not spec[cle].strip():
            refuse(f'« {cle} » manquant ou vide')
    if not 2 <= len(spec['titre_court'].split()) <= 4:
        refuse('« titre_court » doit tenir en 2 à 4 mots (nom de l\'onglet et de la galerie)')
    nb_skills = spec.get('nb_skills', 0)
    if type(nb_skills) is not int or nb_skills < 0:
        refuse('« nb_skills » doit être un entier positif ou nul')
    for cle in ('livre', 'decide', 'attente', 'mots', 'quiz', 'temps'):
        v = spec.get(cle, [])
        if not isinstance(v, list) or not all(isinstance(x, dict) for x in v):
            refuse(f'« {cle} » doit être une liste d\'objets')
    for m in spec.get('mots', []):
        if not str(m.get('mot') or '').strip():
            refuse('un élément de « mots » n\'a pas de « mot »')
    for x in spec.get('temps', []):
        if not str(x.get('quand') or '').strip() or not str(x.get('quoi') or '').strip():
            refuse('un élément de « temps » n\'a pas de « quand » ou de « quoi »')
    gabarit = (ICI / 'bilan-template.html').read_text(encoding='utf-8')
    attente = spec.get('attente', [])
    pieges = spec.get('pieges', '')
    pieges = ' · '.join(map(str, pieges)) if isinstance(pieges, list) else str(pieges)
    ids = ids_cases(attente)
    valeurs = {
        'TITRE': e(spec['titre']),
        'TITRE_COURT': e(spec['titre_court']),
        'BILAN_ID': hashlib.sha1((spec['date'] + '|' + spec['titre']).encode('utf-8')).hexdigest()[:10],
        'DATE': e(spec['date']),
        'DUREE': e(spec.get('duree') or ''),
        'MODELE': e(spec.get('modele') or ''),
        'NB_LIVRES': str(len(spec.get('livre', []))),
        'NB_DECISIONS': str(len(spec.get('decide', []))),
        'NB_SKILLS': str(nb_skills),
        'NB_ATTENTE': str(len(attente)),
        'NB_QUIZ': str(len(spec.get('quiz', []))),
        'CARTES_LIVRE': ''.join(carte(c, 'ok', 'livré') for c in spec.get('livre', [])) or vide('Rien de livré cette fois.'),
        'CARTES_DECIDE': ''.join(carte(c, 'decision', 'décidé') for c in spec.get('decide', [])) or vide('Aucune décision cette fois.'),
        'CARTES_ATTENTE': ''.join(carte(c, 'attente', 'à toi', i) for c, i in zip(attente, ids)) or vide('Rien ne t\'attend.'),
        'MOTS': ''.join(f'<button type="button" class="mot" data-mot="{e(m["mot"])}">{e(m["mot"])}<small>{e(m.get("sens") or "")}</small></button>'
                        for m in spec.get('mots', [])) or vide('Pas de nouveau raccourci.'),
        'QUIZ': ''.join(question(q, i) for i, q in enumerate(spec.get('quiz', []))) or vide('Pas de quiz pour cette session.'),
        'LIGNE_TEMPS': ''.join(f'<li><time>{e(x["quand"])}</time>{e(x["quoi"])}</li>' for x in spec.get('temps', [])) or '<li>Pas de jalon.</li>',
        'PIEGES': e(pieges),
    }
    # Une seule passe sur le gabarit : le contenu inséré n'est jamais relu comme du gabarit.
    inconnus = sorted(set(re.findall(r'\{\{([A-Z_]+)\}\}', gabarit)) - set(valeurs))
    if inconnus:
        sys.exit('placeholders du gabarit sans valeur : ' + ', '.join(inconnus))
    page = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: valeurs[m.group(1)], gabarit)
    if not artifact:
        page = '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n' + page + '\n</body>\n</html>\n'
    sortie = Path(args[1]).resolve()
    if sortie.parent.name == 'bilans':
        if not (sortie.parent.parent / 'decision-log.md').exists():
            refuse(f'{sortie.parent} n\'est pas le dossier bilans/ de la mémoire (aucun decision-log.md à côté) : mauvais dépôt ?')
        sortie.parent.mkdir(exist_ok=True)
    else:
        sortie.parent.mkdir(parents=True, exist_ok=True)
    try:
        donnees = page.encode('utf-8')
    except UnicodeEncodeError as x:
        refuse(f'caractère invalide : {x}')
    sortie.write_bytes(donnees)
    print(f'bilan écrit : {args[1]} ({len(page)} caractères, {"artifact" if artifact else "autonome"})')


if __name__ == '__main__':
    main(sys.argv[1:])
