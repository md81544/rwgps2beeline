#!/bin/bash
cd "$(dirname "$0")"
if [[ -d venv ]]; then
  . venv/bin/activate
fi
python3 r2b.py $*
if [[ -d venv ]]; then
  deactivate
fi
