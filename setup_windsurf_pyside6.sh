#!/bin/bash

echo "🔧 Vai nella cartella del progetto"
cd /Users/giorgiobalzarotti/Documents/SviluppoSW/Python/windsurf_desktop || exit 1

echo "🗑️ Elimino eventuale ambiente virtuale esistente..."
rm -rf .venv

echo "🧱 Creo nuovo venv con Python 3.12..."
/opt/homebrew/Cellar/python@3.12/3.12.10_1/bin/python3.12 -m venv .venv

echo "✅ Attivo venv..."
source .venv/bin/activate

echo "🔍 Verifico versione Python attiva:"
python --version

echo "⬆️ Aggiorno pip e setuptools..."
pip install --upgrade pip setuptools

echo "📦 Installo PySide6 versione stabile (6.6.1)..."
pip install PySide6==6.6.1

echo "🚀 Avvio applicazione..."
python main.py
