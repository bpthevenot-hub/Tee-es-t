#!/usr/bin/env bash
# Verify the presence of the secrets required by the commercial robot.
# Never fails on missing configuration: writes `config_ready=true|false` to
# $GITHUB_OUTPUT so the workflow skips the routine gracefully. The secrets
# stay deactivated on this public fork until the status publication leak
# documented in BRANCHES.md is fixed; the cron must stay green meanwhile.
set -euo pipefail

missing=()
for key in ANTHROPIC_API_KEY HUBSPOT_API_KEY; do
  value="${!key:-}"
  if [[ -z "${value//[[:space:]]/}" ]]; then
    missing+=("$key")
    echo "::warning::Secret requis manquant ou vide : $key."
  fi
done

secrets_url="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/settings/secrets/actions"
if (( ${#missing[@]} > 0 )); then
  {
    printf '## Robot suspendu : configuration incomplete\n\n'
    printf 'Secrets requis non disponibles pour ce workflow :\n\n'
    printf -- '- `%s`\n' "${missing[@]}"
    printf '\n[Configurer les secrets Actions de ce depot](%s).\n\n' "$secrets_url"
    printf 'Ajouter les cles sous ces noms exacts dans le depot qui execute le workflow.\n'
    printf 'Si elles sont stockees dans un environnement GitHub, le job doit utiliser cet environnement.\n\n'
    printf "Ne pas activer les secrets avant d'avoir corrige le flux de publication decrit dans BRANCHES.md.\n"
    printf 'Puis lancer ce workflow depuis la branche par defaut avec `configuration_only` coche.\n'
  } >> "$GITHUB_STEP_SUMMARY"
  echo "::notice::Robot suspendu : secrets manquants (${missing[*]}). Voir $secrets_url"
  echo "config_ready=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

{
  printf '## Configuration presente\n\n'
  printf 'Les deux secrets requis sont disponibles. Ce controle verifie leur presence, pas leur validite API.\n'
} >> "$GITHUB_STEP_SUMMARY"
echo "config_ready=true" >> "$GITHUB_OUTPUT"
