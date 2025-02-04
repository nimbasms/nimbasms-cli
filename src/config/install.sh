#!/bin/bash
set -e

# URL de téléchargement de l'exécutable
BINARY_URL="https://github.com/nimbasms/nimbasms-cli/releases/download/v0.1.0/nimbasms-cli"

# Emplacement temporaire pour le téléchargement
TMP_PATH="/tmp/nimbasms-cli"

# Répertoire d'installation (assurez-vous qu'il est dans le PATH, ici /usr/local/bin)
INSTALL_DIR="/usr/local/bin"

echo "Téléchargement de nimbasms-cli depuis $BINARY_URL ..."
curl -L -o "$TMP_PATH" "$BINARY_URL"

echo "Rendre l'exécutable..."
chmod +x "$TMP_PATH"

echo "Déplacement de nimbasms-cli vers $INSTALL_DIR (cela peut nécessiter sudo)..."
sudo mv "$TMP_PATH" "$INSTALL_DIR/nimbasms-cli"

echo "Installation terminée !"
echo "Vous pouvez lancer l'application en tapant 'nimbasms help' dans votre terminal."