#!/usr/bin/env bash
set -euo pipefail
if ! command -v cygpath >/dev/null 2>&1 || [[ -z "${LOCALAPPDATA:-}" ]]; then
    echo 'Abra este comando no Git Bash do Windows.' >&2
    exit 1
fi
launcher="$(cygpath -u "$LOCALAPPDATA")/JarvisDevin/bin/jarvis-devin"
if [[ ! -f "$launcher" ]]; then
    echo 'Instale primeiro: bash Instalar.sh' >&2
    exit 1
fi
exec bash "$launcher" "$@"
