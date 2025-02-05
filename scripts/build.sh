#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist/ build/

# Install dependencies if needed
poetry install

# Create single file executable
echo -e "${YELLOW}Building executable...${NC}"
poetry run pyinstaller src/cli.py \
    --name nimbasms \
    --onefile \
    --clean \
    --add-data "src/core:core" \
    --add-data "src/commands:commands" \
    --add-data "src/config:config" \
    --add-data "src/utils:utils" \
    --hidden-import typer \
    --hidden-import rich \
    --hidden-import httpx

# Check if build was successful
if [ -f "dist/nimbasms" ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo -e "Executable created at: dist/nimbasms"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi