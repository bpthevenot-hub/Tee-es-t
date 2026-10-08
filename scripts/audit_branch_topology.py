#!/usr/bin/env python3
"""Compare Tee-es-t refs without changing any configured repository or remote.

Fetches into a disposable bare repository, never pushes or deletes branches.
Requires only Python 3 and Git. Run from any working directory.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORIES = {
    "bpthevenot-hub": "https://github.com/bpthevenot-hub/Tee-es-t.git",
    "lfdsss": "https://github.com/lfdsss/Tee-es-t.git",
    "LFDS31": "https://github.com/LFDS31/Tee-es-t.git",
}
BASE = "refs/remotes/bpthevenot-hub/main"
COMMIT_TO_CHECK = "e4598f6dffcaffd14cbce61d6b0b0c59ecb64712"


def git(directory: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--git-dir", str(directory), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def compare(directory: Path, base: str, other: str) -> tuple[str, str, str]:
    common = git(directory, "merge-base", base, other, check=False)
    if common.returncode:
        return ("?", "?", "historique sans ancêtre commun")
    counts = git(directory, "rev-list", "--left-right", "--count", f"{base}...{other}")
    behind, ahead = counts.stdout.strip().split()
    if behind == ahead == "0":
        status = "identique"
    elif ahead == "0":
        status = "contenue dans la base"
    elif behind == "0":
        status = "en avance sur la base"
    else:
        status = "divergente"
    return behind, ahead, status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", choices=tuple(REPOSITORIES), default="bpthevenot-hub",
        help="dépôt dont le main sert de point de comparaison (non une décision de propriété)",
    )
    args = parser.parse_args()

    try:
        with tempfile.TemporaryDirectory(prefix="tee-es-t-audit-") as temporary:
            directory = Path(temporary) / "audit.git"
            subprocess.run(["git", "init", "--bare", "--quiet", str(directory)], check=True)
            for name, url in REPOSITORIES.items():
                # A ref namespace per repository prevents collisions between branch names.
                git(
                    directory, "fetch", "--quiet", "--no-tags", url,
                    f"+refs/heads/*:refs/remotes/{name}/*",
                )

            base = f"refs/remotes/{args.base}/main"
            git(directory, "rev-parse", "--verify", base)
            rows = git(
                directory, "for-each-ref", "--sort=refname",
                "--format=%(refname)%09%(objectname)", "refs/remotes",
            ).stdout.splitlines()
            print(f"# Tee-es-t — comparaison avec {args.base}/main\n")
            print("Lecture seule sur GitHub ; seuls des objets temporaires locaux sont créés. ")
            print("Les nombres indiquent les commits absents de la branche / absents de la base.\n")
            print("| Branche | SHA | Retard | Avance | État |")
            print("| --- | --- | ---: | ---: | --- |")
            for row in rows:
                ref, sha = row.split("\t")
                behind, ahead, status = compare(directory, base, ref)
                name = ref.removeprefix("refs/remotes/")
                print(f"| `{name}` | `{sha[:12]}` | {behind} | {ahead} | {status} |")

            print(f"\nCommit {COMMIT_TO_CHECK[:12]} contenu dans :")
            for name in REPOSITORIES:
                ref = f"refs/remotes/{name}/main"
                result = git(directory, "merge-base", "--is-ancestor", COMMIT_TO_CHECK, ref, check=False)
                print(f"- `{name}/main` : {'oui' if result.returncode == 0 else 'non'}")
            print("\nCe diagnostic ne décide ni du dépôt canonique ni d'une fusion/suppression.")
    except (OSError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            # No credential-bearing command line or remote URL in the error message.
            print(f"Échec Git (code {error.returncode}) : {error.stderr.strip()}", file=sys.stderr)
        else:
            print(f"Échec local : {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
