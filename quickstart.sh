#!/bin/bash
# Quick Start Script for Google Docs Proxy VPN
# This script automates the setup process

set -e  # Exit on error

echo "======================================================================"
echo "  🚀 Google Docs Proxy VPN - Quick Start"
echo "======================================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Check if Chrome is installed
echo ""
echo "📋 Checking Chrome/Chromium installation..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✅ Found $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROME_VERSION=$(chromium-browser --version)
    echo "✅ Found $CHROME_VERSION"
elif command -v chromium &> /dev/null; then
    CHROME_VERSION=$(chromium --version)
    echo "✅ Found $CHROME_VERSION"
else
    echo "⚠️  Chrome/Chromium not found. Some features may not work."
    echo "   Install with: sudo apt install chromium-browser"
fi

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ All dependencies installed successfully!"

# Check for client_secrets.json
echo ""
echo "📋 Checking for Google OAuth credentials..."
if [ ! -f "client_secrets.json" ]; then
    echo "⚠️  client_secrets.json not found!"
    echo ""
    echo "📝 To set up Google OAuth:"
    echo "   1. Go to https://console.cloud.google.com"
    echo "   2. Create a new project"
    echo "   3. Enable Google Drive API and Google Docs API"
    echo "   4. Create OAuth 2.0 credentials (Web application)"
    echo "   5. Add redirect URI: http://localhost:5000/oauth2callback"
    echo "   6. Download client_secrets.json and place it in this directory"
    echo ""
    echo "   See SETUP_GUIDE.md for detailed instructions."
else
    echo "✅ client_secrets.json found"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p uploads downloads .config
echo "✅ Directories created"

# Test network connectivity
echo ""
echo "🌐 Testing network connectivity..."
python3 -c "from network_checker import NetworkChecker; checker = NetworkChecker(); status = checker.get_network_status(); print(f'Network Status: {status[\"status\"]}'); print(f'Message: {status[\"message\"]}')"

# Summary
echo ""
echo "======================================================================"
echo "  ✅ Setup Complete!"
echo "======================================================================"
echo ""
echo "🚀 To start the application:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run the app: python3 app_google.py"
echo "   3. Open browser: http://localhost:5000"
echo ""
echo "📖 For detailed instructions, see:"
echo "   - SETUP_GUIDE.md (Complete setup guide)"
echo "   - README_GOOGLE_DOCS.md (Feature documentation)"
echo ""
echo "💡 Next steps:"
if [ ! -f "client_secrets.json" ]; then
    echo "   - Set up Google OAuth (see instructions above)"
fi
echo "   - Configure proxy if needed (Settings page)"
echo "   - Login with Google account"
echo "   - Start browsing and managing files!"
echo ""
echo "======================================================================"
