#!/bin/bash
# MP-Editor wrapper script

set -e

# Load env
export $(cat ~/.mp-editor/.env | grep -v '^#' | xargs 2>/dev/null || true)

# Activate venv and run
cd ~/.agents/skills/mp-editor
source .venv/bin/activate
python3 -m src.main "$@"
