#!/usr/bin/env bash
# Run from the repository root after a successful routine and status update.
set -euo pipefail

routine="${1:?Routine requise}"
target_branch="${TARGET_BRANCH:-main}"
case "$routine" in
  morning|followup|weekly_audit) ;;
  *) echo "::error::Routine invalide."; exit 1 ;;
esac

git config user.name "Robot Commercial"
git config user.email "robot@snbbm-consulting.com"
git add -- docs/status.json
if [ -d docs/missions ]; then
  git add -- docs/missions/
fi
if git diff --staged --quiet; then
  echo "Aucun changement a committer."
  exit 0
fi

git commit -m "Robot: mise a jour statut ($routine)"
for attempt in 1 2 3 4; do
  git fetch origin "$target_branch"
  if ! git rebase "origin/$target_branch"; then
    # Abort conflicts before exiting; never leave a rebase in progress or
    # overwrite changes made by another writer.
    if [ -d "$(git rev-parse --git-path rebase-merge)" ] ||
       [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
      git rebase --abort
    fi
    echo "::error::Publication arretee : conflit Git ou fichiers non committes."
    exit 1
  fi
  if git push origin "HEAD:$target_branch"; then
    exit 0
  fi
  if [ "$attempt" -lt 4 ]; then
    echo "Push rejete, nouvelle tentative ($attempt/4)..."
    sleep "$((attempt * 2))"
  fi
done
echo "::error::Impossible de publier apres 4 tentatives. Verifier les droits du token et la protection de branche."
exit 1
