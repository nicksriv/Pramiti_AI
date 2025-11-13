#!/bin/bash

# Interactive Contabo VPS Deployment Assistant
# This script helps you deploy Pramiti AI with Docker

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         Pramiti AI - Contabo VPS Deployment             ║"
echo "║              Docker Edition (Interactive)                ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print step headers
print_step() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Get VPS details
print_step "Step 1: VPS Connection Details"
echo ""
read -p "Enter your Contabo VPS IP address: " VPS_IP
read -p "Enter SSH username (default: root): " SSH_USER
SSH_USER=${SSH_USER:-root}

echo ""
echo -e "${YELLOW}Testing SSH connection to ${SSH_USER}@${VPS_IP}...${NC}"

# Test SSH connection
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${SSH_USER}@${VPS_IP} "echo 'Connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful!${NC}"
else
    echo -e "${RED}❌ Cannot connect to VPS. Please check:${NC}"
    echo "   - VPS IP address is correct"
    echo "   - SSH key is set up or password is ready"
    echo "   - VPS is running and accessible"
    exit 1
fi

# Get OpenAI API key
print_step "Step 2: OpenAI API Configuration"
echo ""
echo -e "${YELLOW}You'll need an OpenAI API key for the application.${NC}"
echo "Get one at: https://platform.openai.com/api-keys"
echo ""
read -p "Enter your OpenAI API key: " OPENAI_KEY

# Get domain (optional)
print_step "Step 3: Domain Configuration (Optional)"
echo ""
read -p "Do you have a domain name? (y/n): " HAS_DOMAIN
if [ "$HAS_DOMAIN" = "y" ] || [ "$HAS_DOMAIN" = "Y" ]; then
    read -p "Enter your domain name (e.g., ai.yourdomain.com): " DOMAIN_NAME
else
    DOMAIN_NAME=$VPS_IP
    echo "Using IP address: $DOMAIN_NAME"
fi

# Confirm deployment
print_step "Step 4: Deployment Confirmation"
echo ""
echo "Deployment Configuration:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VPS IP:       $VPS_IP"
echo "  SSH User:     $SSH_USER"
echo "  Domain:       $DOMAIN_NAME"
echo "  OpenAI Key:   ${OPENAI_KEY:0:8}...${OPENAI_KEY: -4}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Proceed with deployment? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Create deployment commands
print_step "Step 5: Deploying to VPS"

echo ""
echo -e "${YELLOW}📦 Connecting to VPS and starting deployment...${NC}"
echo ""

# SSH and run deployment
ssh -t ${SSH_USER}@${VPS_IP} << ENDSSH
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Installing Docker and Docker Compose"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker \$USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Cloning Pramiti AI Repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Clone or update repository
if [ -d "Pramiti_AI" ]; then
    echo "Repository exists, updating..."
    cd Pramiti_AI
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/nicksriv/Pramiti_AI.git
    cd Pramiti_AI
fi

echo "✅ Repository ready"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Configuring Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create .env file
cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=$OPENAI_KEY

# Server Configuration
HOST=0.0.0.0
PORT=8084
ENVIRONMENT=production

# Security
SECRET_KEY=\$(openssl rand -hex 32)
ALLOWED_ORIGINS=http://$DOMAIN_NAME,https://$DOMAIN_NAME,http://$VPS_IP

# Database
POSTGRES_PASSWORD=\$(openssl rand -hex 16)
DATABASE_URL=postgresql://pramiti_user:\${POSTGRES_PASSWORD}@postgres:5432/pramiti_ai

# Redis
REDIS_URL=redis://redis:6379/0
EOF

# Replace placeholders
sed -i "s/\$OPENAI_KEY/$OPENAI_KEY/g" .env
sed -i "s/\$DOMAIN_NAME/$DOMAIN_NAME/g" .env
sed -i "s/\$VPS_IP/$VPS_IP/g" .env

echo "✅ Environment configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Creating Required Directories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p logs data ssl

echo "✅ Directories created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Configuring Firewall"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
echo "y" | sudo ufw enable || true

echo "✅ Firewall configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Building and Starting Docker Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Stop existing containers
docker-compose down 2>/dev/null || true

# Pull images
docker-compose pull

# Build application
docker-compose build

# Start services
docker-compose up -d

echo "✅ Containers started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Waiting for Services to be Ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sleep 15

# Check health
docker-compose ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Testing Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -f http://localhost:8084/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Application may still be starting. Check logs with:"
    echo "   docker-compose logs -f pramiti-ai"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          🎉 DEPLOYMENT SUCCESSFUL! 🎉                    ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Your Pramiti AI Platform is now live!"
echo ""
echo "🌐 Access Points:"
echo "   Dashboard:  http://$DOMAIN_NAME/enhanced-dashboard"
echo "   API Docs:   http://$DOMAIN_NAME/docs"
echo "   Health:     http://$DOMAIN_NAME/health"
echo ""
echo "📚 Useful Commands (run on VPS):"
echo "   cd ~/Pramiti_AI"
echo "   docker-compose ps                 # Check status"
echo "   docker-compose logs -f pramiti-ai # View logs"
echo "   docker-compose restart            # Restart all"
echo "   docker-compose down               # Stop all"
echo "   docker-compose up -d              # Start all"
echo ""
echo "🔒 Next Steps:"
echo "   1. Test the dashboard in your browser"
echo "   2. Setup SSL: sudo certbot --nginx -d $DOMAIN_NAME"
echo "   3. Create your first organization"
echo "   4. Configure backups"
echo ""
echo "📖 Full documentation: ~/Pramiti_AI/DEPLOYMENT_GUIDE.md"
echo ""

ENDSSH

# Local completion message
print_step "Deployment Complete!"
echo ""
echo -e "${GREEN}✅ Your Pramiti AI platform is now running on your Contabo VPS!${NC}"
echo ""
echo "🌐 Access your dashboard at:"
echo -e "${BLUE}   http://${DOMAIN_NAME}/enhanced-dashboard${NC}"
echo ""
echo "📝 To manage your deployment, SSH into your VPS:"
echo -e "${YELLOW}   ssh ${SSH_USER}@${VPS_IP}${NC}"
echo -e "${YELLOW}   cd Pramiti_AI${NC}"
echo ""
echo -e "${GREEN}🎉 Happy deploying!${NC}"
