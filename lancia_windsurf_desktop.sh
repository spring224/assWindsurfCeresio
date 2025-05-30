#!/bin/bash

echo "🌊 Avvio Windsurf Desktop con supporto Cocoa..."

cd /Users/giorgiobalzarotti/Documents/SviluppoSW/Python/windsurf_desktop || exit 1
source .venv/bin/activate

export QT_PLUGIN_PATH=$(python -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'plugins'))")

python main.py
