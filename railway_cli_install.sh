#!/bin/bash
# Railway CLI Installation and Verification Script

echo "🚀 Railway CLI Installation & Verification Tool"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running in CI environment
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    print_status "Running in CI environment"
    CI_MODE=true
else
    print_status "Running in local environment"
    CI_MODE=false
fi

# Method 1: Try npm installation (most reliable)
install_via_npm() {
    print_status "Attempting Railway CLI installation via npm..."

    if command -v npm &> /dev/null; then
        if npm install -g @railway/cli; then
            print_status "Railway CLI installed successfully via npm"
            return 0
        else
            print_warning "npm installation failed"
            return 1
        fi
    else
        print_warning "npm not found, skipping npm installation"
        return 1
    fi
}

# Method 2: Download from GitHub releases
install_via_github() {
    print_status "Attempting Railway CLI installation via GitHub releases..."

    RAILWAY_VERSION="v3.17.1"
    TEMP_DIR=$(mktemp -d)

    # Try multiple download URLs
    urls=(
        "https://github.com/railwayapp/cli/releases/download/${RAILWAY_VERSION}/railway-linux-amd64"
        "https://github.com/railwayapp/cli/releases/download/${RAILWAY_VERSION}/railway_linux_amd64"
        "https://github.com/railwayapp/cli/releases/download/${RAILWAY_VERSION}/railway_linux_amd64.tar.gz"
    )

    for url in "${urls[@]}"; do
        print_status "Trying download from: $url"

        if curl -L -o "$TEMP_DIR/railway" "$url" 2>/dev/null; then
            # Check if downloaded file is valid
            if [ -f "$TEMP_DIR/railway" ] && [ -s "$TEMP_DIR/railway" ]; then
                # Check if it's not an HTML error page
                if ! head -n 1 "$TEMP_DIR/railway" | grep -q "Not Found\|404\|HTML"; then
                    print_status "Download successful"

                    # Extract if it's a tar.gz
                    if file "$TEMP_DIR/railway" | grep -q "gzip compressed"; then
                        tar -xzf "$TEMP_DIR/railway" -C "$TEMP_DIR"
                        find "$TEMP_DIR" -name "railway" -type f -executable | head -n 1 | xargs -I {} mv {} "$TEMP_DIR/railway"
                    fi

                    # Make executable and move to PATH
                    chmod +x "$TEMP_DIR/railway"

                    if [ "$CI_MODE" = true ]; then
                        sudo mv "$TEMP_DIR/railway" /usr/local/bin/railway
                    else
                        mv "$TEMP_DIR/railway" /usr/local/bin/railway 2>/dev/null || sudo mv "$TEMP_DIR/railway" /usr/local/bin/railway
                    fi

                    rm -rf "$TEMP_DIR"
                    return 0
                else
                    print_warning "Downloaded file appears to be an error page"
                fi
            fi
        fi
    done

    rm -rf "$TEMP_DIR"
    print_error "All GitHub download methods failed"
    return 1
}

# Method 3: Use package manager (apt/yum/brew)
install_via_package_manager() {
    print_status "Attempting Railway CLI installation via package manager..."

    if command -v apt &> /dev/null; then
        print_status "Using apt package manager"
        curl -fsSL https://railway.app/install.sh | sh
        return $?
    elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
        print_status "Using yum/dnf package manager"
        curl -fsSL https://railway.app/install.sh | sh
        return $?
    elif command -v brew &> /dev/null; then
        print_status "Using Homebrew"
        brew install railway
        return $?
    else
        print_warning "No suitable package manager found"
        return 1
    fi
}

# Main installation logic
main_installation() {
    # Check if Railway CLI is already installed
    if command -v railway &> /dev/null; then
        print_status "Railway CLI is already installed"
        railway --version
        return 0
    fi

    # Try installation methods in order of preference
    if install_via_npm; then
        return 0
    fi

    if install_via_github; then
        return 0
    fi

    if install_via_package_manager; then
        return 0
    fi

    print_error "All installation methods failed"
    return 1
}

# Verification function
verify_installation() {
    print_status "Verifying Railway CLI installation..."

    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found in PATH"
        return 1
    fi

    print_status "Railway CLI found at: $(which railway)"

    if railway --version 2>/dev/null || railway version 2>/dev/null; then
        print_status "Railway CLI version check successful"
    else
        print_warning "Railway CLI version check failed, but binary exists"
    fi

    return 0
}

# Authentication check
check_authentication() {
    if [ -n "$RAILWAY_TOKEN" ]; then
        print_status "RAILWAY_TOKEN environment variable is set"

        if railway login --token "$RAILWAY_TOKEN" 2>/dev/null; then
            print_status "Railway authentication successful"
            return 0
        else
            print_error "Railway authentication failed"
            return 1
        fi
    else
        print_warning "RAILWAY_TOKEN environment variable is not set"
        print_status "You can set it with: export RAILWAY_TOKEN=your_token_here"
        return 1
    fi
}

# Main execution
main() {
    echo ""

    if main_installation; then
        echo ""
        if verify_installation; then
            echo ""
            if [ -n "$RAILWAY_TOKEN" ]; then
                check_authentication
            else
                print_warning "Skipping authentication check (no RAILWAY_TOKEN provided)"
            fi

            echo ""
            print_status "Railway CLI setup completed successfully!"
            echo ""
            print_status "You can now use: railway --help"
            return 0
        fi
    fi

    echo ""
    print_error "Railway CLI setup failed"
    echo ""
    print_status "Troubleshooting tips:"
    echo "  1. Check your internet connection"
    echo "  2. Verify you have sudo permissions (for CI)"
    echo "  3. Try running the script again"
    echo "  4. Check Railway CLI GitHub releases for manual download"
    return 1
}

# Run main function
main "$@"
