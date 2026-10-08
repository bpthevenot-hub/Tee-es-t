# Tee-es-t — décision de branches

État observé le 8 octobre 2026. Ces SHA ne sont pas un registre dynamique :
relancer `python3 scripts/audit_branch_topology.py` avant toute décision.
Le script n'écrit que dans un dépôt Git temporaire ; il ne pousse, ne fusionne
et ne supprime rien.

| Dépôt/branche | SHA observé | Constat |
| --- | --- | --- |
| `lfdsss/main` | `9ebdccd5470a` | Original historique, archivé sur GitHub. |
| `bpthevenot-hub/main` | `4d9f1b237206` | Fork direct, 2 commits devant l'original ; derniers changements sur le robot et sa CI. |
| `LFDS31/main` | `3c079bfa9129` | Fork direct, 154 commits derrière ce `main`, aucun commit propre. |
| `LFDS31/chore/synchro-md` | `ebdadb8a74ad` | Un commit propre ajoutant `SYNCHRO.md` sur l'ancienne base. |
| `bpthevenot-hub/claude/e4598f6d...` | `9ebdccd5470a` | Contenue dans `main`, 2 commits derrière. |
| `bpthevenot-hub/copilot/fix-commit-e4598f6d` | `9ebdccd5470a` | Contenue dans `main`, 2 commits derrière. |

Le dépôt privé `snb-cons/Tee-es-t` a son propre historique et son propre
`main` (`1b51c798e60b` lors de la vérification). Il se décrit comme le dépôt
de référence pour StudentFlow. La comparaison inter-dépôts n'a pas pu être
établie par l'API GitHub ; vérifier les ancêtres communs avec deux remotes
authentifiés avant toute opération Git entre eux. Ne pas recopier leurs
workflows ou secrets automatiquement.

Le commit `e4598f6d` du 4 juin 2026 est déjà dans le `main` de ce fork et
dans l'original à `9ebdccd` ; il n'a changé que `docs/status.json`.
Il n'y a rien à cherry-picker pour ce commit. `SYNCHRO.md` présente des
informations du 21 mai 2026 et ne doit pas être fusionné tel quel comme état
actuel. La PR `LFDS31` #34, ouverte vers l'original archivé, doit être réévaluée
avant toute reprise de son contenu.

## Résolution proposée

1. Travailler ici pour les changements propres à ce fork, conformément au
   choix du propriétaire. Pour StudentFlow et les changements propres à
   `snb-cons`, ouvrir une PR séparée dans le dépôt privé.
2. Contribuer par branche issue du `main` du dépôt concerné et PR. Ne pas
   pousser sur `main`. Vérifier les tests, les protections et les déploiements
   avant fusion.
3. Pour chaque branche non contenue dans `main`, examiner les commits et tests
   uniques. Reprendre seulement les changements utiles via PR dédiée.
4. Une fois les décisions enregistrées, demander une validation distincte
   avant de fermer l'ancienne PR, archiver un fork ou supprimer des branches.

Le tableau est une photographie Git, pas une autorisation de fusion. Un SHA
commun ne prouve pas que les comptes GitHub, les secrets et les déploiements
sont synchronisés.

Un changement limité à ces fichiers de gouvernance ne déclenche aucun des
workflows CI filtrés sur les sous-projets. « No jobs were run » sur une PR
documentaire ne valide ni n'invalide les builds. Le fork `bpthevenot-hub`
n'affichait que deux runs dynamiques Claude/Copilot lors de la vérification ;
ne pas interpréter la présence de YAML dans Git comme preuve que son robot,
ses secrets ou ses déploiements sont actifs. Le `main` a reçu deux commits de
CI/robot depuis cette première observation ; vérifier les runs actuels.

## Triage des 16 branches de l'original avec commits non contenus

Triage initial du 27 septembre ; revalider chaque branche avant intégration.
`git cherry` montre des patchs distincts, mais ne prouve ni leur pertinence
actuelle ni l'absence d'une réimplémentation différente. Ce triage est une
file de revue, **pas** une liste de cherry-picks automatiques.

| Priorité | Branches `lfdsss/` | Décision de revue |
| --- | --- | --- |
| Sécurité | `claude/analyze-test-coverage-rzJf6` | Logique de validation `session_id` et neutralisation CSV portée dans la PR brouillon #3 du présent fork ; revoir cette PR avant fusion. |
| Produit | `claude/laposte-larl-tracking-arTIZ` | Évaluer le besoin et les envois externes avant reprise. |
| Produit | `claude/add-claude-documentation-zlT9w` | Séparer CI quiz, StudentFlow et documentation. |
| Produit | `claude/student-job-architecture-lf4FN` | Isoler scraper/SEO/migration et tester la base. |
| Différer | `claude/connect-netlify-integration-cGanV`, `claude/data-collection-component-LqGjM`, `claude/fix-browser-consistency-vL5wk`, `claude/setup-build-scripts-4HdyX` | Revue par sous-projet ; ne pas fusionner une branche entière sur cette base ancienne. |
| Différer | `claude/epic-newton-Q16iK`, `vercel/install-vercel-web-analytics-wmmldd` | Stratégies d'hébergement incompatibles à arbitrer après identification du déploiement réel. |
| Suspendre | `claude/fix-browser-compatibility-zXuli`, `claude/hybrid-strategy-framework-0YH1l`, `claude/improve-conversion-rates-Q5Wjg`, `claude/instagram-agent-automation-u9kd1` | Vérifier consentement, prix et automatisations commerciales avant reprise. |
| Hors réconciliation | `claude/setup-dev-environment-M1wnA`, `claude/youtube-video-extractor-f2XHJ` | Gros périmètre ou fonctionnalité distincte ; décision produit dédiée. |

Risque adjacent constaté pendant la revue : `commercial-agent/update_status.py`
peut écrire des coordonnées HubSpot dans `docs/status.json` sur ce dépôt
public si le robot dispose de ses accès. Vérifier le contenu publié et corriger
ce flux avant d'activer ses secrets ou de relancer la routine. Les correctifs
CI/robot récents doivent être revus séparément de cette cartographie.
