#!/usr/bin/env bash
set -euo pipefail
if ! command -v cygpath >/dev/null 2>&1; then
    echo 'Abra este instalador no Git Bash do Windows.' >&2
    exit 1
fi
package_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
installer="$(cygpath -w "$package_dir/scripts/install.ps1")"
command_args=(powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File "$installer" "$@")
if [[ -t 0 && -t 1 ]] && command -v winpty >/dev/null 2>&1; then
    winpty -- "${command_args[@]}"
else
    "${command_args[@]}"
fi
echo
echo 'Pronto. Para usar nesta mesma aba, execute:'
echo 'export PATH="$(cygpath -u "$LOCALAPPDATA")/JarvisDevin/bin:$PATH"'
echo 'jarvis-devin'
