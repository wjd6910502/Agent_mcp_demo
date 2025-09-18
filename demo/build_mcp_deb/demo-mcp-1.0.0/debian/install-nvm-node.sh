#!/bin/bash

# NVM and Node.js installation script for demo-mcp package
# This script installs NVM and Node.js from the bundled source_pkg files

set -e

# Configuration
NVM_VERSION="0.39.7"
NODE_VERSION="v22.16.0"
INSTALL_DIR="/usr/share/demo-mcp"
NVM_DIR="/opt/nvm"
NODE_DIR="/opt/node"

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

log_info "Starting NVM and Node.js installation..."

# Create installation directories
log_info "Creating installation directories..."
mkdir -p "$NVM_DIR"
mkdir -p "$NODE_DIR"

# Extract and install NVM
log_info "Installing NVM..."
cd "$INSTALL_DIR/source_pkg"
if [ -f "nvm-${NVM_VERSION}.zip" ]; then
    unzip -q "nvm-${NVM_VERSION}.zip" -d /tmp/
    cp -r /tmp/nvm-${NVM_VERSION}/* "$NVM_DIR/"
    chmod +x "$NVM_DIR/nvm.sh"
    chmod +x "$NVM_DIR/nvm-exec"
    #chmod +x "$NVM_DIR/nvm"
    log_info "NVM installed successfully"
else
    log_error "NVM source package not found: nvm-${NVM_VERSION}.zip"
    exit 1
fi

# Extract and install Node.js
log_info "Installing Node.js..."
if [ -f "node-${NODE_VERSION}-linux-x64.tar.xz" ]; then
    tar -xf "node-${NODE_VERSION}-linux-x64.tar.xz" -C /tmp/
    cp -r /tmp/node-${NODE_VERSION}-linux-x64/* "$NODE_DIR/"
    chmod +x "$NODE_DIR/bin/node"
    chmod +x "$NODE_DIR/bin/npm"
    chmod +x "$NODE_DIR/bin/npx"
    log_info "Node.js installed successfully"
else
    log_error "Node.js source package not found: node-${NODE_VERSION}-linux-x64.tar.xz"
    exit 1
fi

# Create symlinks
log_info "Creating symlinks..."
ln -sf "$NODE_DIR/bin/node" /usr/local/bin/node
ln -sf "$NODE_DIR/bin/npm" /usr/local/bin/npm
ln -sf "$NODE_DIR/bin/npx" /usr/local/bin/npx

# Set up NVM environment
log_info "Setting up NVM environment..."
cat > /etc/profile.d/nvm.sh << EOF
# NVM configuration
export NVM_DIR="$NVM_DIR"
export PATH="$NODE_DIR/bin:\$PATH"

# Source NVM
[ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh"
[ -s "\$NVM_DIR/bash_completion" ] && \. "\$NVM_DIR/bash_completion"

# Set default Node.js version
export PATH="$NODE_DIR/bin:\$PATH"
EOF

# Set proper permissions
chmod 644 /etc/profile.d/nvm.sh

# Verify installation
#log_info "Verifying installation..."
#if [ -x "/usr/local/bin/node"]; then
#    NODE_VERSION_INSTALLED=$("/usr/local/bin/node" --version)
#    log_info "Node.js version: $NODE_VERSION_INSTALLED"
#else
#    log_error "Node.js installation verification failed"
#    exit 1
#fi

#if [-x "/usr/local/bin/npm"]; then
#    NPM_VERSION_INSTALLED=$("/usr/local/bin/npm" --version)
#    log_info "NPM version: $NPM_VERSION_INSTALLED"
#else
#    log_error "NPM installation verification failed"
#    exit 1
#fi

log_info "NVM and Node.js installation completed successfully!"

# Clean up temporary files
rm -rf /tmp/nvm-${NVM_VERSION}
rm -rf /tmp/node-${NODE_VERSION}-linux-x64

log_info "Installation cleanup completed" 
