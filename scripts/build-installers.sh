#!/bin/bash

# Build Installers Script for Retail Gateway Platform
# This script builds Windows and Linux installer packages

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Building Retail Gateway Platform Installers${NC}"
echo "============================================================"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALLER_DIR="$PROJECT_ROOT/apps/installer"
DEPLOYMENT_DIR="$PROJECT_ROOT/apps/gateway-service/deployment"

echo -e "${YELLOW}📁 Project Root: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}📁 Installer Directory: $INSTALLER_DIR${NC}"
echo -e "${YELLOW}📁 Deployment Directory: $DEPLOYMENT_DIR${NC}"

# Check if deployment directory exists
if [ ! -d "$DEPLOYMENT_DIR" ]; then
    echo -e "${RED}❌ Deployment directory not found: $DEPLOYMENT_DIR${NC}"
    exit 1
fi

# Create installer directories if they don't exist
mkdir -p "$INSTALLER_DIR/packages/windows"
mkdir -p "$INSTALLER_DIR/packages/linux"
mkdir -p "$INSTALLER_DIR/configs"
mkdir -p "$INSTALLER_DIR/scripts"

echo -e "${YELLOW}📦 Building Windows Installer...${NC}"
cd "$DEPLOYMENT_DIR"
python windows_installer.py

echo -e "${YELLOW}📦 Building Linux Installer...${NC}"
python linux_package_installer.py

echo -e "${YELLOW}📋 Copying installer packages...${NC}"
# Copy Windows installers
if [ -d "$DEPLOYMENT_DIR/dist/windows" ]; then
    cp "$DEPLOYMENT_DIR/dist/windows"/*.zip "$INSTALLER_DIR/packages/windows/" 2>/dev/null || true
    echo -e "${GREEN}✅ Windows installers copied${NC}"
else
    echo -e "${RED}⚠️ No Windows installers found${NC}"
fi

# Copy Linux installers
if [ -d "$DEPLOYMENT_DIR/dist/linux" ]; then
    cp "$DEPLOYMENT_DIR/dist/linux"/*.tar.gz "$INSTALLER_DIR/packages/linux/" 2>/dev/null || true
    echo -e "${GREEN}✅ Linux installers copied${NC}"
else
    echo -e "${RED}⚠️ No Linux installers found${NC}"
fi

# Update metadata with actual file sizes and checksums
echo -e "${YELLOW}📊 Updating metadata...${NC}"

# Update Windows metadata
if [ -f "$INSTALLER_DIR/packages/windows/metadata.json" ]; then
    # Get file size and checksum for Windows installer
    WINDOWS_FILE=$(ls "$INSTALLER_DIR/packages/windows"/*.zip 2>/dev/null | head -1)
    if [ -n "$WINDOWS_FILE" ]; then
        WINDOWS_SIZE=$(stat -f%z "$WINDOWS_FILE" 2>/dev/null || stat -c%s "$WINDOWS_FILE" 2>/dev/null || echo "0")
        WINDOWS_CHECKSUM=$(shasum -a 256 "$WINDOWS_FILE" 2>/dev/null | cut -d' ' -f1 || echo "")
        
        # Update metadata (this is a simple approach - in production, use jq)
        sed -i.bak "s/\"size\": 0/\"size\": $WINDOWS_SIZE/g" "$INSTALLER_DIR/packages/windows/metadata.json"
        sed -i.bak "s/\"checksum\": \"\"/\"checksum\": \"$WINDOWS_CHECKSUM\"/g" "$INSTALLER_DIR/packages/windows/metadata.json"
        rm -f "$INSTALLER_DIR/packages/windows/metadata.json.bak"
    fi
fi

# Update Linux metadata
if [ -f "$INSTALLER_DIR/packages/linux/metadata.json" ]; then
    # Get file sizes and checksums for Linux installers
    for file in "$INSTALLER_DIR/packages/linux"/*.tar.gz; do
        if [ -f "$file" ]; then
            SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            CHECKSUM=$(shasum -a 256 "$file" 2>/dev/null | cut -d' ' -f1 || echo "")
            FILENAME=$(basename "$file")
            
            # Update metadata for this file
            sed -i.bak "s/\"size\": 0/\"size\": $SIZE/g" "$INSTALLER_DIR/packages/linux/metadata.json"
            sed -i.bak "s/\"checksum\": \"\"/\"checksum\": \"$CHECKSUM\"/g" "$INSTALLER_DIR/packages/linux/metadata.json"
        fi
    done
    rm -f "$INSTALLER_DIR/packages/linux/metadata.json.bak"
fi

echo -e "${GREEN}✅ Metadata updated${NC}"

# List created installers
echo -e "${GREEN}📋 Created Installers:${NC}"
echo "Windows:"
ls -la "$INSTALLER_DIR/packages/windows/" 2>/dev/null || echo "  No Windows installers found"
echo "Linux:"
ls -la "$INSTALLER_DIR/packages/linux/" 2>/dev/null || echo "  No Linux installers found"

echo -e "${GREEN}🎉 Installer build completed successfully!${NC}"
echo -e "${YELLOW}📁 Installers are available in: $INSTALLER_DIR/packages/${NC}"
