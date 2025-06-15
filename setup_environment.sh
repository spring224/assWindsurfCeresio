!/bin/bash

echo "📦 Creazione ambiente virtuale .venv"
python3 -m venv .venv

echo "✅ Attivazione ambiente virtuale"
source .venv/bin/activate

echo "⬆️ Aggiornamento pip"
pip install --upgrade pip

echo "📂 Installazione pacchetti da requirements.txt"
pip install -r requirements.txt

echo "✅ Ambiente configurato correttamente!"
