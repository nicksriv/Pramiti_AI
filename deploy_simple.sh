#!/bin/bash

# Simple Docker Deployment for Contabo
# Uses existing .env file and deploys via Docker Compose

set -e

echo "🐳 Pramiti AI - Docker Deployment to Contabo"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get configuration
read -p "Contabo Server IP or Domain: " SERVER
read -p "Deploy with SSL? (y/n): " USE_SSL

if [ -z "$SERVER" ]; then
    echo -e "${RED}✗${NC} Server address is required!"
    exit 1
fi

# Check if .env exists locally
if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found local .env file"

# Check SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ssh root@$SERVER "echo '✓ SSH connection successful'"; then
    echo -e "${GREEN}✓${NC} Connected to server"
else
    echo -e "${RED}✗${NC} Cannot connect to server"
    exit 1
fi

# Install Docker on remote server if needed
echo -e "${YELLOW}Checking Docker on remote server...${NC}"
ssh root@$SERVER << 'ENDSSH'
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✓ Docker installed"
else
    echo "✓ Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✓ Docker Compose installed"
else
    echo "✓ Docker Compose already installed"
fi
ENDSSH

# Create deployment directory on server
echo -e "${YELLOW}Creating deployment directory...${NC}"
ssh root@$SERVER "mkdir -p /opt/pramiti-ai && mkdir -p /opt/pramiti-ai/{data,logs,secrets,ssl,config}"

# Copy files to server
echo -e "${YELLOW}Copying files to server...${NC}"
scp -r \
    .env \
    Dockerfile \
    docker-compose.yml \
    nginx.conf \
    requirements.txt \
    api_server.py \
    core/ \
    agents/ \
    web/ \
    config/ \
    root@$SERVER:/opt/pramiti-ai/

echo -e "${GREEN}✓${NC} Files copied"

# Setup SSL if requested
if [ "$USE_SSL" = "y" ] || [ "$USE_SSL" = "Y" ]; then
    echo -e "${YELLOW}Setting up SSL with Let's Encrypt...${NC}"
    ssh root@$SERVER << ENDSSH
cd /opt/pramiti-ai
apt-get update
apt-get install -y certbot
certbot certonly --standalone -d $SERVER --non-interactive --agree-tos --email admin@$SERVER
cp /etc/letsencrypt/live/$SERVER/fullchain.pem ssl/
cp /etc/letsencrypt/live/$SERVER/privkey.pem ssl/

# Update nginx.conf for SSL
sed -i 's/#     listen 443/    listen 443/g' nginx.conf
sed -i 's/#     server_name/    server_name/g' nginx.conf
sed -i "s/yourdomain.com/$SERVER/g" nginx.conf
sed -i 's/#     ssl_certificate/    ssl_certificate/g' nginx.conf
sed -i 's/#     ssl_/    ssl_/g' nginx.conf
sed -i 's/# }/}/g' nginx.conf
ENDSSH
    echo -e "${GREEN}✓${NC} SSL configured"
fi

# Deploy with Docker Compose
echo -e "${YELLOW}Deploying with Docker Compose...${NC}"
ssh root@$SERVER << 'ENDSSH'
cd /opt/pramiti-ai

# Pull and build
docker-compose pull
docker-compose build

# Stop existing containers
docker-compose down 2>/dev/null || true

# Start services
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 15

# Show status
docker-compose ps
ENDSSH

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$USE_SSL" = "y" ] || [ "$USE_SSL" = "Y" ]; then
    echo "🌐 Access your application at: https://$SERVER"
else
    echo "🌐 Access your application at: http://$SERVER"
fi

echo ""
echo "📊 View logs:"
echo "   ssh root@$SERVER 'cd /opt/pramiti-ai && docker-compose logs -f'"
echo ""
echo "🔄 Restart services:"
echo "   ssh root@$SERVER 'cd /opt/pramiti-ai && docker-compose restart'"
echo ""
echo "🛑 Stop services:"
echo "   ssh root@$SERVER 'cd /opt/pramiti-ai && docker-compose stop'"
echo ""

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
sleep 5
if [ "$USE_SSL" = "y" ] || [ "$USE_SSL" = "Y" ]; then
    HEALTH_URL="https://$SERVER/health"
else
    HEALTH_URL="http://$SERVER/health"
fi

if curl -f -s "$HEALTH_URL" > /dev/null; then
    echo -e "${GREEN}✓${NC} Application is healthy!"
else
    echo -e "${YELLOW}⚠${NC} Health check pending... give it a minute to start up"
fi

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
