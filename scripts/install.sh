#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="/usr/local/bin"
TEMP_DIR="/tmp/nimbasms-cli"

# Print banner
echo "╔═══════════════════════════════════════╗"
echo "║       Nimba SMS CLI Installer         ║"
echo "╚═══════════════════════════════════════╝"

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Convert architecture names
case $ARCH in
    x86_64)  ARCH="amd64" ;;
    arm64)   ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

# Set binary name based on OS
case $OS in
    darwin)
        BINARY_NAME="nimbasms-darwin-${ARCH}"
        ;;
    linux)
        BINARY_NAME="nimbasms-linux-${ARCH}"
        ;;
    *)
        echo -e "${RED}Unsupported operating system: $OS${NC}"
        exit 1
        ;;
esac

# Create temp directory
mkdir -p $TEMP_DIR
cd $TEMP_DIR

echo -e "${YELLOW}Downloading Nimba SMS CLI...${NC}"
RELEASE_URL="https://github.com/nimbasms/nimbasms-cli/releases/latest/download/${BINARY_NAME}"

if ! curl -L --progress-bar $RELEASE_URL -o nimbasms; then
    echo -e "${RED}Failed to download CLI binary${NC}"
    exit 1
fi

# Make binary executable
chmod +x nimbasms

# Create installation directory if it doesn't exist
sudo mkdir -p $INSTALL_DIR

# Move binary to installation directory
sudo mv nimbasms $INSTALL_DIR/

# Clean up
cd ..
rm -rf $TEMP_DIR

echo -e "${GREEN}Nimba SMS CLI has been installed successfully!${NC}"
echo -e "${YELLOW}You can now use the 'nimbasms' command.${NC}"
echo -e "${YELLOW}Try 'nimbasms --help' for usage information.${NC}"