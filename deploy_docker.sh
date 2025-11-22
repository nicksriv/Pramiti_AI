#!/bin/bash

# Docker Deployment Script for Contabo VPS
# Quick containerized deployment using Docker Compose

set -e

echo "🐳 Pramiti AI - Docker Deployment"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env <<EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8084
ENVIRONMENT=production

# Security (auto-generated secure keys)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# ChromaDB and RAG
CHROMA_PERSIST_DIRECTORY=/app/data/rag/chroma
CONVERSATIONS_DIR=/app/data/rag/conversations

# OAuth Configuration (optional)
# MICROSOFT_CLIENT_ID=
# MICROSOFT_CLIENT_SECRET=
# MICROSOFT_TENANT_ID=common
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
EOF
    echo -e "${RED}⚠️  Please edit .env file and set your OPENAI_API_KEY${NC}"
    echo "   nano .env"
    read -p "Press Enter after editing .env file..."
else
    echo -e "${GREEN}✅ Found existing .env file${NC}"
fi

# Create required directories
mkdir -p logs data ssl

# Pull images
echo -e "${GREEN}📥 Pulling Docker images...${NC}"
docker-compose pull

# Build application
echo -e "${GREEN}🔨 Building application...${NC}"
docker-compose build

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check health
echo -e "${GREEN}🏥 Checking service health...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Docker Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📋 Service Status:"
docker-compose ps
echo ""
echo "🌐 Access your application:"
echo "   http://$(curl -s ifconfig.me)/enhanced-dashboard"
echo ""
echo "📊 Useful Commands:"
echo "   View logs:          docker-compose logs -f pramiti-ai"
echo "   Restart services:   docker-compose restart"
echo "   Stop services:      docker-compose stop"
echo "   Remove services:    docker-compose down"
echo ""
echo "🔒 To setup SSL:"
echo "   1. Install certbot on host"
echo "   2. Run: sudo certbot certonly --standalone -d yourdomain.com"
echo "   3. Copy certificates to ./ssl directory"
echo "   4. Update nginx configuration"
echo ""
