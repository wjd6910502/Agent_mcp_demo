#!/bin/bash

# UV installation script for demo-mcp package
# This script installs UV from the bundled source_pkg files

set -e

# Configuration
UV_VERSION="latest"
INSTALL_DIR="/usr/share/demo-mcp"
UV_DIR="/opt/uv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

log_info "Starting UV installation..."

# Create installation directory
log_info "Creating installation directory..."
mkdir -p "$UV_DIR"

# Extract and install UV
log_info "Installing UV..."
cd "$INSTALL_DIR/source_pkg"
if [ -f "uv-x86_64-unknown-linux-gnu.tar.gz" ]; then
    tar -xzf "uv-x86_64-unknown-linux-gnu.tar.gz" -C /tmp/
    
    # Find the uv binary in the extracted directory
    UV_BINARY=$(find /tmp/uv-x86_64-unknown-linux-gnu -name "uv" -type f -executable | head -n 1)
    
    if [ -n "$UV_BINARY" ]; then
        cp "$UV_BINARY" "$UV_DIR/uv"
        chmod +x "$UV_DIR/uv"
	cp "$UV_BINARY" "$UV_DIR/uvx"
	chmod +x "$UV_DIR/uvx"
        log_info "UV binary installed successfully"
    else
        log_error "UV binary not found in extracted archive"
        exit 1
    fi
else
    log_error "UV source package not found: uv-x86_64-unknown-linux-gnu.tar.gz"
    exit 1
fi

# Create symlink
log_info "Creating symlink..."
ln -sf "$UV_DIR/uv" /usr/local/bin/uv
ln -sf "$UV_DIR/uvx" /usr/local/bin/uvx

log_info "UV installation completed successfully!"

# Clean up temporary files
rm -rf /tmp/uv-*

log_info "Installation cleanup completed" 
