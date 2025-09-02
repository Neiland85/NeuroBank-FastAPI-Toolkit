#!/bin/bash
# Vercel CLI Installation and Configuration Script

echo "🚀 Vercel CLI Setup for NeuroBank FastAPI"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running in CI environment
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    print_status "Running in CI environment"
    CI_MODE=true
else
    print_status "Running in local environment"
    CI_MODE=false
fi

# Install Vercel CLI
install_vercel_cli() {
    print_status "Installing Vercel CLI..."

    if command -v vercel &> /dev/null; then
        print_status "Vercel CLI is already installed"
        vercel --version
        return 0
    fi

    if command -v npm &> /dev/null; then
        if npm install -g vercel; then
            print_status "Vercel CLI installed successfully via npm"
            vercel --version
            return 0
        else
            print_error "Failed to install Vercel CLI via npm"
            return 1
        fi
    else
        print_error "npm not found. Please install Node.js and npm first"
        return 1
    fi
}

# Authenticate with Vercel
authenticate_vercel() {
    print_status "Authenticating with Vercel..."

    if [ -n "$VERCEL_TOKEN" ]; then
        print_info "Using VERCEL_TOKEN from environment"

        if vercel login --token "$VERCEL_TOKEN"; then
            print_status "Successfully authenticated with Vercel using token"
            return 0
        else
            print_error "Failed to authenticate with Vercel token"
            return 1
        fi
    else
        print_warning "No VERCEL_TOKEN found in environment"
        print_info "You can set it with: export VERCEL_TOKEN=your_token_here"
        print_info "Or run: vercel login (for interactive login)"

        if [ "$CI_MODE" = false ]; then
            read -p "Do you want to login interactively? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if vercel login; then
                    print_status "Successfully authenticated with Vercel"
                    return 0
                else
                    print_error "Interactive login failed"
                    return 1
                fi
            fi
        fi

        return 1
    fi
}

# Setup Vercel project
setup_project() {
    print_status "Setting up Vercel project..."

    # Check if vercel.json exists
    if [ ! -f "vercel.json" ]; then
        print_error "vercel.json not found in current directory"
        return 1
    fi

    # Link or create project
    if [ -n "$VERCEL_ORG_ID" ] && [ -n "$VERCEL_PROJECT_ID" ]; then
        print_info "Linking to existing project..."
        if vercel link --project "$VERCEL_PROJECT_ID" --org "$VERCEL_ORG_ID" --yes; then
            print_status "Successfully linked to Vercel project"
            return 0
        else
            print_warning "Failed to link to existing project, trying to create new one"
        fi
    fi

    # Try to link automatically
    if vercel link --yes 2>/dev/null; then
        print_status "Successfully linked to Vercel project"
        return 0
    else
        print_warning "Could not link to existing project"
        print_info "You may need to create a project manually or set VERCEL_ORG_ID and VERCEL_PROJECT_ID"
        return 1
    fi
}

# Test deployment
test_deployment() {
    print_status "Testing Vercel deployment..."

    if vercel --prod --yes; then
        print_status "Deployment test successful"

        # Get deployment URL
        sleep 5
        DEPLOYMENT_URL=$(vercel ls 2>/dev/null | grep "https://" | head -n 1 | awk '{print $2}' || echo "")

        if [ -n "$DEPLOYMENT_URL" ]; then
            print_status "Deployment URL: $DEPLOYMENT_URL"

            # Test health endpoint
            if curl -f -s "$DEPLOYMENT_URL/api/health" > /dev/null 2>&1; then
                print_status "Health check passed!"
            else
                print_warning "Health check failed"
            fi
        else
            print_warning "Could not retrieve deployment URL"
        fi

        return 0
    else
        print_error "Deployment test failed"
        return 1
    fi
}

# Main execution
main() {
    echo ""

    if install_vercel_cli; then
        echo ""
        if authenticate_vercel; then
            echo ""
            setup_project
            echo ""

            if [ "$CI_MODE" = false ]; then
                read -p "Do you want to test deployment? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    test_deployment
                fi
            fi

            echo ""
            print_status "Vercel setup completed!"
            echo ""
            print_info "Useful commands:"
            echo "  vercel --help          # Show all commands"
            echo "  vercel ls              # List deployments"
            echo "  vercel logs            # View deployment logs"
            echo "  vercel env ls          # List environment variables"
            return 0
        fi
    fi

    echo ""
    print_error "Vercel setup failed"
    echo ""
    print_info "Troubleshooting:"
    echo "  1. Make sure you have Node.js and npm installed"
    echo "  2. Check your internet connection"
    echo "  3. Verify your Vercel token is valid"
    echo "  4. Try running: vercel login (for interactive setup)"
    return 1
}

# Show usage if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Vercel Setup Script for NeuroBank FastAPI"
    echo ""
    echo "Usage:"
    echo "  ./vercel_setup.sh              # Run setup interactively"
    echo "  VERCEL_TOKEN=xxx ./vercel_setup.sh    # Run with token"
    echo "  ./vercel_setup.sh --help       # Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  VERCEL_TOKEN     # Vercel authentication token"
    echo "  VERCEL_ORG_ID    # Vercel organization ID (optional)"
    echo "  VERCEL_PROJECT_ID # Vercel project ID (optional)"
    exit 0
fi

# Run main function
main "$@"
