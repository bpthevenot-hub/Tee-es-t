---
name: vive-memoire
description: Mémoire vive de fin de discussion — à exécuter automatiquement avant de terminer toute discussion substantielle (le hook Stop le rappelle), ou sur « vive mémoire », « fais le point », « ménage général », « bilan ». Synthétise la session, journalise les décisions, fait grossir les skills/agents/commandes à partir des demandes récurrentes, régénère les ponts vers les autres IA, et publie un bilan interactif ludique. Vaut pour tout modèle et toute session (cloud, desktop, Cursor…).
---

# Vive mémoire

Baptiste (SNB Consulting, consultant IA, travaille seul) veut que **chaque discussion importante laisse une trace exploitable** par la suivante — quel que soit le modèle, l'outil ou la machine — et qu'il n'ait **jamais à redemander** ce qu'il a déjà demandé. Réponses en français, directes.

## 0. Où vit la mémoire

| Quoi | Où | Pourquoi là |
|---|---|---|
| Journal des décisions (append-only, `D-xxx`) | `claude-macos-app/docs/context/decision-log.md` | protocole D-004 : ordre de lecture figé |
| Backlog priorisé | `claude-macos-app/docs/context/next-actions.md` | P0 du haut = tâche courante |
| Chronologie factuelle | `claude-macos-app/docs/context/history.md` | reconstruction SYNC-0002 |
| Reprise Claude / pont ChatGPT | `claude-macos-app/docs/context/claude-handoff.md`, `chatgpt-handoff.md` | pont entre IA |
| **Comptes rendus de session** | `claude-macos-app/docs/context/sessions/AAAA-MM-JJ-sujet.md` | une discussion = un fichier |
| **Candidats skills / agents / commandes** | `claude-macos-app/docs/context/skills-candidats.md` | liste qui grossit, à promouvoir |
| **Bilans interactifs** | `claude-macos-app/docs/context/bilans/AAAA-MM-JJ-sujet.html` + artifact publié | résultat visible, ludique |
| Skills vivantes | `Tee-es-t/.claude/skills/<nom>/SKILL.md` (suivi par git malgré `.gitignore` : `git add -f`) | chargées à chaque session sur le repo |

Si `claude-macos-app` n'est pas dans la session : l'attacher (`add_repo bpthevenot-hub/claude-macos-app`) ; à défaut, écrire la synthèse dans `Tee-es-t/docs/context-miroir/` et le signaler.

## 1. Quand

- **Automatiquement** : le hook Stop (`.claude/hooks/vive-memoire-stop.sh`) bloque la fin de tour d'une discussion substantielle (≥ 4 messages de Baptiste) tant que la synthèse n'a pas été faite, puis toutes les ~8 nouvelles demandes. Il donne l'identifiant de session à tamponner.
- **Sur demande** : « vive mémoire », « fais le point », « bilan », « ménage général ».
- **Jamais** pour une question triviale ou une session sans décision ni livrable.

## 2. Procédure (dans l'ordre, sans sauter d'étape)

1. **Lire** (protocole D-004) : `claude-handoff.md` → `next-actions.md` → 10 dernières entrées de `decision-log.md` → `skills-candidats.md`. Ne rien réécrire de mémoire : tout vient du transcript, de git et des outils.
2. **Compte rendu de session** → `sessions/AAAA-MM-JJ-sujet.md` (≤ 1 page) : Contexte · Ce qui a été livré (liens : PR, URLs, artifacts, fichiers) · Décisions prises (→ D-xxx) · Ce qui reste (→ next-actions) · Ce que Baptiste n'aura plus à redemander · Pièges rencontrés et parades (ex. réseau bloqué, API tronquée, hook).
3. **Journaliser** : chaque décision tranchée → nouvelle entrée `D-xxx` (date, source, statut, contexte, décision, conséquences). Jamais d'effacement ; une décision remplacée est marquée `superseded-by`.
4. **Backlog** : mettre à jour `next-actions.md` (P0 du haut = tâche courante ; cocher ce qui est fait, dater).
5. **Faire grossir les skills** — le cœur de la demande :
   - repérer dans la session ce qui a été demandé **plus d'une fois**, ou ce qui a nécessité une longue explication, ou une procédure que l'on refera (pipeline de build, banc de test, restauration, déploiement, revue) ;
   - l'écrire dans `skills-candidats.md` (nom, déclencheurs, ce qu'elle ferait, preuves : où ça a servi) ;
   - **promouvoir** en skill réelle (`Tee-es-t/.claude/skills/<nom>/SKILL.md`, `git add -f`) dès qu'un candidat a servi 2 fois ou que Baptiste l'a demandé ; enrichir une skill existante plutôt qu'en créer une proche (`chaine-produit`, `atelier-design`, `copilote-freelance`, `auto`, `commercial-agent`…) ;
   - proposer de même des **agents** (`.claude/agents/`) ou des **commandes** quand une tâche est répétitive et bornée ;
   - rappeler à Baptiste qu'une skill utile partout doit aussi être **téléversée dans ses skills claude.ai** (le fichier `SKILL.md` suffit) — on ne peut pas le faire à sa place.
6. **Pont vers les autres IA** : régénérer `claude-handoff.md` (§2 tâches en cours, §3 état des dépôts, §8 prochaines actions) et `chatgpt-handoff.md` (résumé neutre, sans secret, lisible par n'importe quel assistant). Si le connecteur Notion est disponible et que Baptiste l'a demandé, dupliquer le compte rendu dans Notion ; sinon ne rien inventer.
7. **Bilan interactif** (obligatoire — Baptiste ne lit pas des pages) : une page HTML autonome, ludique et scannable en 2 minutes, à partir de `bilan-template.html` : ligne du temps de la session, cartes « livré / décidé / à faire / à ne plus demander », liens cliquables, compteur de skills, et un bloc « ce que tu peux maintenant me demander en un mot ». La sauver dans `bilans/` et la **publier en artifact** (titre court, nom stable) ; donner le lien en une ligne.
8. **Commit + push** : `claude-macos-app` → PR en session cloud (D-011) ou commit direct `main` en local (D-006) ; `Tee-es-t` → branche + PR (jamais `main`). Messages de commit en français, sans identifiant de modèle.
9. **Tamponner** : écrire `<session_id> <nombre de messages>` dans `.claude/.vive-memoire.stamp` du repo courant (valeurs données par le hook) pour que le hook cesse de bloquer.
10. **Répondre** en 6 lignes maximum : lien du bilan, décisions D-xxx, skills créées/enrichies, ce qui attend Baptiste.

## 3. Règles

- Le code est l'allié : pour toute extraction ou vérification, écrire un script (Python/Node) plutôt que recopier à la main ; le garder dans la skill s'il resservira.
- Rien de mémoire, rien d'inventé : chaque fait vient du transcript, de git, d'un outil ou d'une source citée.
- Jamais de secret, de jeton ou de donnée personnelle dans les fichiers de mémoire.
- Une synthèse courte et juste vaut mieux qu'une longue et vague.
- Si le réseau du conteneur bloque un site utile (WebFetch en `ENOTFOUND`), le noter dans « pièges » et rappeler le réglage : environnement → Modifier → Accès réseau (niveau plus large ou domaine ajouté).
