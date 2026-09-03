#!/bin/bash

# ============================================================================
# Script: boostrap.sh
# Purpose: Downloads and installs UV - An extremely fast Python package and project manager, written in Rust.
# Usage: ./boostrap.sh
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script configuration
INSTALL_URL="https://astral.sh/uv/install.sh"

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo ""
    echo "========================================"
    echo "UV Installer"
    echo "========================================"
    echo ""
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

check_dependencies() {
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed on this system."
        echo "Please install curl and try again."
        echo "Alternatively, follow the installation instructions for UV at"
        echo "https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
}

run_installer() {
    echo ""
    echo "Executing installation script..."
    echo ""

    if curl -LsSf "$INSTALL_URL" | sh; then
        echo ""
        print_success "Installation completed successfully."
        return 0
    else
        local exit_code=$?
        echo ""
        print_error "The installation script failed with exit code $exit_code."
        echo "Alternatively, follow the installation instructions for UV at"
        echo "https://docs.astral.sh/uv/getting-started/installation/"
        return $exit_code
    fi
}

# ============================================================================
# Main execution
# ============================================================================

main() {
    print_header
    check_dependencies
    run_installer

    echo ""
    read -p "Installation complete, press ENTER to close..."
}

# Run main function
main "$@"
