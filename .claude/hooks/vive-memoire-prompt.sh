#!/bin/bash
# UserPromptSubmit « vive mémoire » : délègue à l'enveloppe commune (mode prompt).
ici=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
exec bash "$ici/vive-memoire-stop.sh" prompt
