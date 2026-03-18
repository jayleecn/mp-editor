#!/bin/bash
# MP-Editor Skill - Run script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load environment from ~/.mp-editor/.env if exists
if [ -f "$HOME/.mp-editor/.env" ]; then
    export $(cat "$HOME/.mp-editor/.env" | grep -v '^#' | xargs)
fi

# Run the main Python module
python3 -m src.main "$@"
