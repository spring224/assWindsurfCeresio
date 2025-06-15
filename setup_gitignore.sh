#!/bin/bash

echo "📝 Sovrascrivo il file .gitignore con la versione completa per Windsurf Ceresio"
cat > .gitignore <<EOF
# ========== Python ========== #
__pycache__/
*.pyc
*.pyo
*.pyd
*.db-journal

# ========== Virtual Environment ========== #
.venv/
venv/
env/
*.egg-info/
*.egg

# ========== VS Code ========== #
.vscode/
.history/

# ========== macOS ========== #
.DS_Store
.AppleDouble
.LSOverride
Icon?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ========== Build & Packaging ========== #
build/
dist/
*.spec

# ========== Ricevute & Output ========== #
Ricevute_Noleggi/*.pdf

# ========== File temporanei duplicati ========== #
*Sorgenti Prima Modifica/*copia*
*Sorgenti Prima Modifica/*\ *

# ========== DB editor file ========== #
*.sqbpro
EOF

echo "✅ File .gitignore aggiornato."

echo "📦 Eseguo commit del nuovo .gitignore"
git add .gitignore
git commit -m "Aggiornato .gitignore completo per progetto Windsurf Ceresio"
