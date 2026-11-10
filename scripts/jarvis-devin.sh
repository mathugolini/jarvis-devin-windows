#!/usr/bin/env bash
# jarvis-devin managed launcher
set -euo pipefail

if ! command -v cygpath >/dev/null 2>&1; then
    echo 'Este comando requer o Git Bash do Git for Windows.' >&2
    exit 1
fi
bin_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -f "$bin_dir/runtime-python.txt" || ! -f "$bin_dir/runtime-data.txt" ]]; then
    echo 'Instalacao incompleta. Execute bash Instalar.sh novamente.' >&2
    exit 1
fi
IFS= read -r runtime < "$bin_dir/runtime-python.txt"
IFS= read -r data_dir < "$bin_dir/runtime-data.txt"
runtime="${runtime%$'\r'}"
data_dir="${data_dir%$'\r'}"
runtime="$(cygpath -u "$runtime")"
app_file="$(cygpath -w "$bin_dir/../app/jarvis.py")"
export JARVIS_DEVIN_HOME="$data_dir" PYTHONUTF8=1 PYTHONIOENCODING=utf-8
if [[ -n "${LOCALAPPDATA:-}" ]]; then
    export PATH="$(cygpath -u "$LOCALAPPDATA")/devin/cli/bin:$PATH"
fi

# Convert only documented filesystem arguments. Preserve the request literally.
args=()
action="${1:-}"
position=0
path_next=0
for arg in "$@"; do
    if (( path_next )); then
        args+=("$(cygpath -w "$arg")")
        path_next=0
    elif [[ "$arg" == --projeto || "$arg" == --modelo ]]; then
        args+=("$arg")
        path_next=1
    elif [[ "$arg" == --projeto=* || "$arg" == --modelo=* ]]; then
        args+=("${arg%%=*}=$(cygpath -w "${arg#*=}")")
    elif (( position == 1 )) && [[ "$action" == projeto || "$action" == transcrever ]]; then
        args+=("$(cygpath -w "$arg")")
    else
        args+=("$arg")
    fi
    position=$((position + 1))
done

# Git Bash/mintty needs a Windows console for msvcrt and the Devin interface.
# The bridge is automatic; no separate PowerShell session is opened.
if [[ -t 0 && -t 1 ]]; then
    if command -v winpty >/dev/null 2>&1; then
        export MSYS2_ARG_CONV_EXCL='*'
        exec winpty -- "$runtime" -u "$app_file" "${args[@]}"
    fi
    if ! "$runtime" -c 'import sys; sys.exit(0 if sys.stdin.isatty() else 1)'; then
        echo 'O terminal precisa do winpty incluido no Git for Windows. Atualize o Git ou abra o Git Bash no Windows Terminal.' >&2
        exit 1
    fi
fi
export MSYS2_ARG_CONV_EXCL='*'
exec "$runtime" -u "$app_file" "${args[@]}"
