---
name: vive-memoire
description: Mémoire vive de fin de discussion — à exécuter automatiquement avant de terminer toute discussion substantielle (le hook Stop le rappelle), ou sur « vive mémoire », « fais le point », « ménage général », « bilan ». Synthétise la session, journalise les décisions, fait grossir les skills/agents/commandes à partir des demandes récurrentes, régénère les ponts vers les autres IA, et publie un bilan interactif ludique. Vaut pour tout modèle et toute session (cloud, desktop, Cursor…).
---

# Vive mémoire

Baptiste (consultant IA, SNB Consulting) veut que **chaque discussion importante laisse une trace exploitable** par la suivante, quel que soit le modèle, l'outil ou la machine, et qu'il n'ait **jamais à redemander** ce qu'il a déjà demandé. Réponses en français, directes.

## 0. Où vit la mémoire

| Quoi | Où | Pourquoi là |
|---|---|---|
| Journal des décisions (append-only, `D-xxx`) | `claude-macos-app/docs/context/decision-log.md` | protocole D-004 : ordre de lecture figé |
| Backlog priorisé | `claude-macos-app/docs/context/next-actions.md` | P0 du haut = tâche courante |
| Chronologie factuelle | `claude-macos-app/docs/context/history.md` | reconstruction SYNC-0002 |
| Reprise Claude / pont ChatGPT | `claude-macos-app/docs/context/claude-handoff.md`, `chatgpt-handoff.md` | pont entre IA |
| **Comptes rendus de session** | `claude-macos-app/docs/context/sessions/AAAA-MM-JJ-sujet.md` | une discussion = un fichier |
| **Candidats skills / agents / commandes** | `claude-macos-app/docs/context/skills-candidats.md` | liste qui grossit, à promouvoir |
| **Bilans interactifs** | `claude-macos-app/docs/context/bilans/AAAA-MM-JJ-sujet.html` + artifact privé | résultat visible, ludique |
| Skills vivantes | `Tee-es-t/.claude/skills/<nom>/` (suivi par git : `.claude/*` avec exceptions) | chargées à chaque session sur le dépôt |
| Hooks | `Tee-es-t/.claude/hooks/` et `claude-macos-app/.claude/hooks/` (copies identiques) | voir § 1 |

`claude-macos-app` est **privé** ; `Tee-es-t` est **public** : jamais de mémoire dans Tee-es-t. Si `claude-macos-app` n'est pas dans la session, l'attacher (`add_repo bpthevenot-hub/claude-macos-app`) ; à défaut, écrire la synthèse dans le scratchpad et la publier en artifact privé, avec la mention « à rapatrier dans claude-macos-app ».

Dans les commandes ci-dessous, `$SKILL` est le dossier de ce fichier (Tee-es-t `.claude/skills/vive-memoire`, ou la copie de secours `claude-macos-app/docs/context/skills/vive-memoire`, ou `~/.claude/skills/vive-memoire` sur le Mac) et `$MEM` le dossier `claude-macos-app/docs/context`.

## 1. Quand, et ce qui l'impose réellement (D-019)

- **Sur demande** : « vive mémoire », « fais le point », « bilan », « ménage général ».
- **Jamais** pour une question triviale ou une session sans décision ni livrable.
- **Automatiquement**, selon l'endroit (documentation Claude Code vérifiée le 14/10/2026) :

| Session | Ce qui s'applique |
|---|---|
| Mac, CLI ou desktop, après `bash Tee-es-t/.claude/hooks/installe-mac.sh` | hooks **utilisateur** : toutes les sessions locales, quel que soit le dossier ; skill copiée dans `~/.claude/skills/` |
| Locale ouverte dans un des deux dépôts, sans installation utilisateur | hooks du dépôt (`.claude/settings.json`) |
| Cloud ouverte sur **un seul** dépôt | hooks du dépôt |
| Cloud hébergée par Anthropic, ouverte sur **plusieurs** dépôts | **aucun hook de dépôt** (ni plugin de dépôt, ni réglages utilisateur ; seuls d'éventuels hooks gérés par une organisation s'appliqueraient) : seule la consigne des `CLAUDE.md` vaut ; Claude doit appliquer cette skill de lui-même |

Hooks (Python 3.8+, aucune autre dépendance, logique dans `vive_memoire.py`) : **Stop** demande la synthèse quand la discussion compte ≥ 4 demandes humaines (champ `origin` du transcript, `human` ou `channel` ; notifications, webhooks, tâches planifiées exclus), puis toutes les ~8 nouvelles demandes ; au plus 3 relances, puis la fin est autorisée. Une **dette** (un fichier par session) est notée dès le premier blocage, et aussi quand la discussion se met en pause alors que la synthèse est due ; **SessionStart** (démarrage, reprise, `/clear`, fourche) la rappelle **sur la même machine** (autre session abandonnée depuis plus d'une heure, ou reprise de la même), sauf si un tampon ou un compte rendu la couvre déjà — en cloud, le conteneur ne survit pas : inscrire la dette dans `next-actions.md`. **UserPromptSubmit** note les demandes pas encore écrites au transcript (avec la taille du transcript à l'envoi : toute invite écrite après leur répond, quels qu'en soient le texte ou l'origine) ; au Stop d'un tour planifié, elles sont gardées pour le Stop suivant. Seule compte la branche active : après `/rewind`, les tours abandonnés ne comptent pas, et une synthèse faite sur un tour abandonné ne couvre plus que les demandes encore actives ; un transcript reconstruit depuis une compaction repart de son propre compte. Quand plusieurs copies reçoivent le même événement (installation utilisateur et dépôt), une seule agit — une session lancée avec `--setting-sources` sans `user` (lu sur la ligne de commande du Claude Code qui a lancé le hook, la dernière occurrence l'emportant) ne charge pas la copie utilisateur : celle du dépôt agit alors seule : la première à en poser le verrou, posé sur toute l'entrée de l'événement, clé figée depuis 3.8 (copie utilisateur ≤ 3.4 ou 3.6 : elle agit seule ; 3.5 : seule si elle a tourné dans la session, et seule au démarrage ; 3.7 : sa clé est prise aussi ; un vieux checkout 3.5 ou 3.6 du dépôt à côté d'une copie utilisateur récente peut encore, rarement, agir en double : réinstaller ou mettre le dépôt à jour). L'état d'une session est lu et écrit sous verrou exclusif : un envoi pendant un Stop ne se perd plus. Un compte rendu portant les lignes « Session : » / « Demandes : » vaut tampon dès le premier Stop qui le voit (ancré comme lui, donc ramené par `/rewind`) ; il est reconnu par son contenu (sa seule section, jusqu'au bloc d'une autre session), pas par la date du fichier : réécrit après un `/rewind`, même avec le même en-tête, il est relu ; touché par un checkout ou complété par une autre session, il ne l'est pas. Une dette n'est effacée que sur preuve qu'une synthèse la couvre (faite après elle par la session elle-même, ou couvrant au moins son compte) : un transcript reconstruit plus court, ou la synthèse d'une fourche qui s'arrête à son point, ne suffit pas. Les entrées de sous-agent (`isSidechain`) ne comptent jamais. Le hook ne bloque jamais sur une erreur ; il se met en pause, jusqu'à la demande suivante, quand du travail lancé depuis la dernière demande est en cours, en file ou planifié (une tâche sans fin plus ancienne, serveur ou surveillance, ne suspend rien) ; une fourche (`/branch`) hérite de la synthèse de sa session mère (seulement pour les demandes héritées que cette synthèse couvre encore), et sa propre synthèse couvre la mère jusqu'au point de fourche. État : `~/.claude/vive-memoire/<session>.json`. Banc : `python3 .claude/hooks/teste_vive_memoire.py` (175 vérifications).

## 2. Procédure (dans l'ordre, sans sauter d'étape)

1. **Lire** (protocole D-004) : `claude-handoff.md` → `next-actions.md` → 10 dernières entrées de `decision-log.md` → `skills-candidats.md`. Ne rien réécrire de mémoire : tout vient du transcript, de git et des outils.
2. **Compte rendu de session** → `$MEM/sessions/AAAA-MM-JJ-sujet.md` (≤ 1 page). En tête, sur deux lignes consécutives : « Session : <session_id> » puis « Demandes : <nombre> » (ce qui permet au hook de reconnaître une synthèse faite, même dans un nouveau conteneur) ; si possible une troisième, « Ancre : <uuid> », affichée par la commande `tamponne` : elle situe le compte rendu dans la conversation (sans elle, le hook le situe à sa date d'écriture), pour qu'un `/rewind` ultérieur en réduise la portée. Puis : Contexte · Ce qui a été livré (liens : PR, URLs, artifacts, fichiers) · Décisions prises (→ D-xxx) · Ce qui reste (→ next-actions) · Ce que Baptiste n'aura plus à redemander · Pièges rencontrés et parades. Si le compte rendu de cette session existe déjà, le compléter au lieu d'en écrire un second ; dans un fichier partagé avec d'autres sessions, ou pour une synthèse refaite après un `/rewind`, faire précéder le complément d'un nouveau bloc « Session : » / « Demandes : » (/ « Ancre : ») : le dernier bloc fait foi.
3. **Journaliser** : chaque décision tranchée → nouvelle entrée `D-xxx` (date, source, statut, contexte, décision, conséquences). Jamais d'effacement ; une décision remplacée est marquée `superseded-by`. **Avant de numéroter une décision ou un Sync ID**, `git fetch` puis relire la fin de `decision-log.md` sur `main` **et** sur la branche distante : des sessions parallèles écrivent aussi. Une entrée déjà publiée sur `main` garde son numéro ; c'est la plus récente, encore sur une branche, qui change (collision D-014 du 14/10, cf. D-019).
4. **Backlog** : mettre à jour `next-actions.md` (P0 du haut = tâche courante ; cocher ce qui est fait, dater).
5. **Faire grossir les skills** — le cœur de la demande :
   - repérer dans la session ce qui a été demandé **plus d'une fois**, ou ce qui a nécessité une longue explication, ou une procédure que l'on refera (pipeline de build, banc de test, restauration, déploiement, revue) ;
   - l'écrire dans `skills-candidats.md` (nom, déclencheurs, ce qu'elle ferait, preuves : où ça a servi) ;
   - **promouvoir** en skill réelle (`Tee-es-t/.claude/skills/<nom>/SKILL.md`, `git add -f`) dès qu'un candidat a servi 2 fois ou que Baptiste l'a demandé ; enrichir une skill existante plutôt qu'en créer une proche (`chaine-produit`, `atelier-design`, `copilote-freelance`, `auto`, `commercial-agent`…) ;
   - proposer de même des **agents** (`.claude/agents/`) ou des **commandes** quand une tâche est répétitive et bornée ;
   - rappeler à Baptiste qu'une skill utile partout doit aussi être **téléversée dans ses skills claude.ai** (le fichier `SKILL.md` suffit) — on ne peut pas le faire à sa place.
6. **Pont vers les autres IA** : régénérer `claude-handoff.md` (§2 tâches en cours, §3 état des dépôts, §8 prochaines actions) et `chatgpt-handoff.md` (résumé neutre, sans secret ni donnée personnelle, lisible par n'importe quel assistant). **Write-back Notion (D-014, obligatoire)** : ajouter en fin de la page « SNB Center — Control Plane & Reprise totale » (`notion-fetch` id `3d8fd451-0cd1-81d2-a56f-ef99964e85e1`) une entrée « Journal de vérification — Claude Code — <date> » au format des entrées précédentes : faits vérifiés avec sources (SHA, déploiements, PR), statut de chaque élément, limites, prochaine action, et ce qui n'a pas été modifié. Si le connecteur Notion manque, le dire dans la réponse.
7. **Bilan interactif** (obligatoire : Baptiste ne lit pas des pages). Écrire une spec JSON (clés et règles en tête de `genere-bilan.py` : `titre`, `titre_court` de 2 à 4 mots, `date`, listes `livre`, `decide`, `attente`, `mots`, `quiz` avec `bonne` = index à partir de 0, `temps`, `pieges`), puis :
   - page versionnée : `python3 "$SKILL/genere-bilan.py" spec.json "$MEM/bilans/AAAA-MM-JJ-sujet.html"` (refusée si le dossier `bilans/` n'est pas à côté d'un `decision-log.md`) ;
   - page à publier : `python3 "$SKILL/genere-bilan.py" --artifact spec.json <scratchpad>/bilan.html`, publiée en **artifact** (republier le même fichier garde l'URL) ;
   - vérifier : `node "$SKILL/teste-bilan.mjs" <bilan.html> <scratchpad>/captures` (onglets au clic et aux flèches, cases, quiz, 390 px sur chaque onglet, thème sombre, 0 erreur JS) ;
   - donner le lien en une ligne.
8. **Commit + push** : `claude-macos-app` → PR en session cloud (D-011) ou commit direct `main` en local (D-006) ; `Tee-es-t` → branche + PR (jamais `main`). Vérifier d'abord que la PR visée n'est pas déjà mergée ; sinon en ouvrir une nouvelle. Messages de commit en français, sans identifiant de modèle.
9. **Tamponner** : `python3 <dossier des hooks>/vive_memoire.py tamponne <session_id>` (la commande exacte, chemin compris, figure dans le message du hook ; l'identifiant est aussi dans `$CLAUDE_CODE_SESSION_ID`). Elle enregistre la synthèse et efface la dette de la session.
10. **Répondre** en 6 lignes maximum : lien du bilan, décisions D-xxx, skills créées/enrichies, ce qui attend Baptiste.

## 3. Règles

- Le code est l'allié : pour toute extraction ou vérification, écrire un script (Python/Node) plutôt que recopier à la main ; le garder dans la skill s'il resservira.
- Rien de mémoire, rien d'inventé : chaque fait vient du transcript, de git, d'un outil ou d'une source citée.
- Jamais de secret, de jeton ou de donnée personnelle dans les fichiers de mémoire.
- Une synthèse courte et juste vaut mieux qu'une longue et vague.
- Si le réseau du conteneur bloque un site utile (WebFetch en `ENOTFOUND`), le noter dans « pièges » et rappeler le réglage : environnement → Modifier → Accès réseau (niveau plus large ou domaine ajouté).
