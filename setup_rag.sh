#!/bin/bash
# RAG System Setup Script
# Installs and configures the RAG (Retrieval-Augmented Generation) system

set -e  # Exit on any error

echo "======================================================================"
echo "RAG SYSTEM SETUP"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  WARNING: No virtual environment detected"
    echo "   It's recommended to use a virtual environment."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Install RAG dependencies
echo "Installing RAG dependencies..."
pip install chromadb==0.4.22 openai==1.7.2 tiktoken==0.5.2
echo "✓ ChromaDB, OpenAI, and Tiktoken installed"
echo ""

# Check for OpenAI API key
if [ -f .env ]; then
    if grep -q "OPENAI_API_KEY=" .env; then
        echo "✓ OPENAI_API_KEY found in .env file"
    else
        echo "⚠️  OPENAI_API_KEY not found in .env file"
        echo ""
        read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_KEY
        if [ ! -z "$OPENAI_KEY" ]; then
            echo "OPENAI_API_KEY=$OPENAI_KEY" >> .env
            echo "✓ OPENAI_API_KEY added to .env"
        else
            echo "⚠️  Skipped. You'll need to add it manually later."
        fi
    fi
else
    echo "⚠️  .env file not found"
    echo ""
    read -p "Create .env file with OpenAI API key? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " OPENAI_KEY
        echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
        echo "✓ .env file created"
    else
        echo "⚠️  You'll need to create .env file manually"
    fi
fi
echo ""

# Create data directories
echo "Creating RAG data directories..."
mkdir -p data/rag/chromadb
mkdir -p data/rag/conversations
mkdir -p data/rag/feedback
echo "✓ Directories created:"
echo "  - data/rag/chromadb (vector database)"
echo "  - data/rag/conversations (conversation history)"
echo "  - data/rag/feedback (user feedback)"
echo ""

# Test ChromaDB installation
echo "Testing ChromaDB installation..."
python3 -c "import chromadb; print('✓ ChromaDB import successful')" 2>/dev/null || {
    echo "✗ ChromaDB import failed"
    exit 1
}
echo ""

# Test OpenAI installation
echo "Testing OpenAI installation..."
python3 -c "import openai; print('✓ OpenAI import successful')" 2>/dev/null || {
    echo "✗ OpenAI import failed"
    exit 1
}
echo ""

# Run quick test
echo "Running RAG system quick test..."
echo ""
python3 test_rag_system.py

echo ""
echo "======================================================================"
echo "✓ RAG SYSTEM SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "  1. Ensure OPENAI_API_KEY is set in .env file"
echo "  2. Start the API server: python api_server.py"
echo "  3. Open RAG chat interface: http://localhost:8084/static/rag-chat-interface.html"
echo "  4. Chat with the AI and provide feedback with 👍/👎 buttons"
echo ""
echo "Documentation:"
echo "  - RAG System Guide: docs/RAG_SYSTEM.md"
echo "  - Security Guide: docs/SECURITY_IMPLEMENTATION.md"
echo ""
