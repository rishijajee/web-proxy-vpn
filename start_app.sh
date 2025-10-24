#!/bin/bash
# Simple script to start the Google Docs Proxy VPN app

echo "🚀 Starting Google Docs Proxy VPN..."
echo ""

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./quickstart.sh first to set up the app."
    exit 1
fi

# Start the app using virtual environment
echo "✓ Found virtual environment"
echo "✓ Starting app on http://localhost:5000"
echo ""
echo "📌 IMPORTANT REMINDERS:"
echo "   1. To access Google Docs, click 'Login with Google' on dashboard"
echo "   2. Don't try to login via screenshot - it won't work!"
echo "   3. Read GOOGLE_DOCS_WORKFLOW.md for detailed instructions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

./venv/bin/python3 app_google.py
