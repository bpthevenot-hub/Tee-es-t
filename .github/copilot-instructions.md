# Contribuer à Tee-es-t avec Copilot

Lire `CLAUDE.md` à la racine puis les consignes du sous-projet concerné.
Ce dépôt public est `bpthevenot-hub/Tee-es-t`. Le dépôt privé
`snb-cons/Tee-es-t` et les dépôts clients ont leurs propres branches et secrets.
Ne pas les synchroniser par simple ressemblance de nom. La mémoire privée
reste dans `claude-macos-app/docs/context/`, jamais dans ce dépôt public.

Pour un échec CI, partir du dernier run du SHA courant : lire le job et ses
journaux, reproduire la cause, appliquer un correctif ciblé, exécuter le test
pertinent puis vérifier la CI du nouveau SHA. Ne jamais déclarer une revue
Copilot, un test, une fusion ou un déploiement réussis sans preuve disponible.
Une revue bloquée par quota reste une limite à signaler.

Commandes selon le périmètre :
- Agent commercial : `cd commercial-agent && python -m pytest -q` après
  installation de `requirements-dev.txt`. Les tests restent sans accès aux API.
- Relève : `cd releve/site && npm ci && npm run build`.
- Mémoire : `python3 .claude/hooks/test_fork_concurrency.py` puis
  `python3 .claude/hooks/teste_vive_memoire.py`. Tester sur un runner disposant
  d'une vue cohérente de ses processus, Linux et macOS étant les cibles.

Le robot commercial est manuel depuis la décision du propriétaire du
13 octobre 2026 : ne pas réactiver de cron en résolvant un conflit.
Pour les dépendances, garder manifestes et lockfiles cohérents ; valider une
montée majeure et sa compatibilité avec la version Node/Python de la CI.
Pour les accès, ne jamais mettre de secret ou de jeton prospect dans le code,
les journaux ou les exemples. Tester les refus d'accès autant que les succès.

Travailler sur une branche et une PR, conserver l'historique et vérifier le
SHA avant fusion. Une fusion demandée dans la conversation reste soumise aux
règles du dépôt et aux défauts de sécurité non résolus.

Méthode : [cookbook GitHub Copilot](https://docs.github.com/fr/enterprise-cloud@latest/copilot/tutorials/copilot-cookbook),
recettes diagnostic CI, triage, sécurité et mises à jour des dépendances.
