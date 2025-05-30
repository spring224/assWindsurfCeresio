#!/bin/bash

echo "🎯 Preparazione ambiente PyInstaller..."

# Verifica che PyInstaller sia installato
if ! command -v pyinstaller &> /dev/null
then
    echo "❌ PyInstaller non è installato. Installalo con: pip install pyinstaller"
    exit 1
fi

echo "🧼 Pulizia eventuali build precedenti..."
rm -rf build dist main.spec

echo "⚙️ Costruzione app standalone con Cocoa incluso..."
pyinstaller --windowed --onedir main.py

echo ""
echo "✅ App creata nella cartella: dist/main"
echo "➡️ Per avviarla: ./dist/main/main"