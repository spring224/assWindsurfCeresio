#!/bin/bash

# Titolo visivo
echo "🚀 Avvio deploy su Git..."

# Aggiunge tutte le modifiche
git add .

# Commit con timestamp
git commit -m "Aggiornamento automatico $(date '+%Y-%m-%d %H:%M:%S')"

# Push verso il remote
git push

echo "✅ Deploy completato con successo!"