#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current version from pyproject.toml
CURRENT_VERSION=$(poetry version -s)

# Get the new version from command line argument or prompt
if [ -z "$1" ]; then
    read -p "Enter new version (current: $CURRENT_VERSION): " NEW_VERSION
else
    NEW_VERSION=$1
fi

# Validate version format
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Invalid version format. Please use semantic versioning (e.g., 1.0.0)${NC}"
    exit 1
fi

echo -e "${YELLOW}Preparing release v$NEW_VERSION...${NC}"

# Update version in pyproject.toml
poetry version $NEW_VERSION

# Create git tag
git add pyproject.toml
git commit -m "release: version $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

echo -e "${GREEN}Release v$NEW_VERSION prepared!${NC}"
echo -e "${YELLOW}To publish the release:${NC}"
echo "1. Push the commit: git push origin main"
echo "2. Push the tag: git push origin v$NEW_VERSION"
echo "3. GitHub Actions will automatically build and create the release"