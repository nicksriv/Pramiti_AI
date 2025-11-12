#!/bin/bash

# Quick Setup Script for Pramiti AI Organization

echo "============================================================"
echo "🤖 Pramiti AI Organization - Quick Setup"
echo "============================================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Check if API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo ""
    echo "⚠️  OpenAI API Key not configured!"
    echo ""
    echo "📋 To get your API key:"
    echo "   1. Visit: https://platform.openai.com/api-keys"
    echo "   2. Sign in or create an account"
    echo "   3. Click 'Create new secret key'"
    echo "   4. Copy the key (starts with 'sk-')"
    echo ""
    echo "Would you like to enter your API key now? (y/n)"
    read -r response
    
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo ""
        echo "Enter your OpenAI API key:"
        read -r api_key
        
        # Update .env file
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$api_key/" .env
        else
            # Linux
            sed -i "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$api_key/" .env
        fi
        
        echo "✅ API key configured!"
    else
        echo ""
        echo "📝 You can manually edit .env file and add your key later"
        echo "   Then restart the server with: python3 api_server.py"
    fi
fi

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. Start the server:"
echo "   python3 api_server.py"
echo ""
echo "2. Open the dashboard:"
echo "   http://localhost:8084/openai-dashboard.html"
echo ""
echo "3. Start chatting with AI agents!"
echo ""
echo "📖 For detailed instructions, see: SETUP_GUIDE.md"
echo ""
