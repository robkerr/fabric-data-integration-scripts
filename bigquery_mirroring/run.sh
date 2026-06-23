#!/usr/bin/env bash
# Run setup_bigquery_mirror.py inside the local virtual environment.
#
# Usage:
#   ./run.sh [args...]
#
# Examples:
#   ./run.sh mirroring.yaml
#   ./run.sh mirroring.yaml --status
#   ./run.sh mirroring.yaml --stop
#   ./run.sh --list-connections --filter BigQuery
#   ./run.sh --list-mirrored-databases --workspace <WORKSPACE_ID>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install --quiet -r "${SCRIPT_DIR}/requirements.txt"
fi

"${VENV_DIR}/bin/python" "${SCRIPT_DIR}/setup_bigquery_mirror.py" "$@"
