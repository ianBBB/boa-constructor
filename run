#!/bin/bash

# ============================================================================
# Script: run.sh
# Purpose:
# Usage: ./run.sh
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

PROGRAM="Boa.py"

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo ""
    echo "========================================"
    echo "Launching Boa Constructor"
    echo "========================================"
    echo ""
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

run_program() {
    echo ""
    echo "Executing installation script..."
    echo ""

    if uv run $PROGRAM; then
        echo ""
        print_success "Installation completed successfully."
        return 0
    else
        local exit_code=$?
        echo ""
        print_error "The installation script failed with exit code $exit_code."
        return $exit_code
    fi
}

# ============================================================================
# Main execution
# ============================================================================

main() {
    print_header
    run_program
}

# Run main function
main "$@"
