#!/bin/bash

# Quick Deployment Script for Contabo VPS
# Run this script on your VPS after cloning the repository

set -e

echo "🚀 Pramiti AI - Contabo VPS Deployment Script"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run this script as root${NC}"
    echo "   Run as: ./deploy_vps.sh"
    exit 1
fi

echo -e "${GREEN}✅ Starting deployment...${NC}"
echo ""

# Step 1: Update system
echo "📦 Step 1/10: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install dependencies
echo "📦 Step 2/10: Installing system dependencies..."
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget \
    build-essential nginx supervisor postgresql postgresql-contrib \
    certbot python3-certbot-nginx fail2ban

# Step 3: Create virtual environment
echo "🐍 Step 3/10: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate

# Step 4: Install Python dependencies
echo "📚 Step 4/10: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Configure environment
echo "⚙️  Step 5/10: Configuring environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
        echo "   Especially set: OPENAI_API_KEY, SECRET_KEY, ALLOWED_ORIGINS"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Step 6: Create log directory
echo "📁 Step 6/10: Creating log directories..."
sudo mkdir -p /var/log/pramiti-ai
sudo chown $USER:$USER /var/log/pramiti-ai

# Step 7: Configure Supervisor
echo "🔧 Step 7/10: Configuring Supervisor..."
SUPERVISOR_CONF="/etc/supervisor/conf.d/pramiti-ai.conf"
if [ ! -f "$SUPERVISOR_CONF" ]; then
    sudo tee $SUPERVISOR_CONF > /dev/null <<EOF
[program:pramiti-ai-worker]
directory=$(pwd)
command=$(pwd)/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8084 --workers 4
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pramiti-ai/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="$(pwd)/venv/bin"
EOF
    echo -e "${GREEN}✅ Supervisor configuration created${NC}"
else
    echo -e "${YELLOW}⚠️  Supervisor configuration already exists${NC}"
fi

# Step 8: Configure Nginx
echo "🌐 Step 8/10: Configuring Nginx..."
read -p "Enter your domain name (or press Enter to use IP address): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    DOMAIN_NAME=$(curl -s ifconfig.me)
    echo "Using IP address: $DOMAIN_NAME"
fi

NGINX_CONF="/etc/nginx/sites-available/pramiti-ai"
if [ ! -f "$NGINX_CONF" ]; then
    sudo tee $NGINX_CONF > /dev/null <<EOF
upstream pramiti_backend {
    server 127.0.0.1:8084;
    keepalive 64;
}

server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    client_max_body_size 50M;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logs
    access_log /var/log/nginx/pramiti-ai-access.log;
    error_log /var/log/nginx/pramiti-ai-error.log;
    
    # Static files
    location /web/ {
        alias $(pwd)/web/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://pramiti_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://pramiti_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
    
    # Main application
    location / {
        proxy_pass http://pramiti_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://pramiti_backend/health;
        access_log off;
    }
}
EOF
    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
    echo -e "${GREEN}✅ Nginx configuration created${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx configuration already exists${NC}"
fi

# Step 9: Test and reload services
echo "🔄 Step 9/10: Starting services..."
sudo nginx -t
sudo systemctl reload nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all

# Step 10: Configure firewall
echo "🔒 Step 10/10: Configuring firewall..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow OpenSSH
sudo ufw --force enable

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit configuration file:"
echo "   nano .env"
echo "   Set OPENAI_API_KEY and other settings"
echo ""
echo "2. Restart the application:"
echo "   sudo supervisorctl restart pramiti-ai-worker"
echo ""
echo "3. Check application status:"
echo "   sudo supervisorctl status"
echo ""
echo "4. View logs:"
echo "   sudo tail -f /var/log/pramiti-ai/app.log"
echo ""
echo "5. Access your application:"
echo "   http://$DOMAIN_NAME/enhanced-dashboard"
echo ""
echo "6. (Optional) Setup SSL certificate:"
echo "   sudo certbot --nginx -d $DOMAIN_NAME"
echo ""
echo "7. Check health endpoint:"
echo "   curl http://$DOMAIN_NAME/health"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "   - Edit .env file with your actual API keys"
echo "   - Setup SSL certificate for HTTPS"
echo "   - Configure database if needed"
echo "   - Setup backups"
echo ""
echo "📚 Full documentation: DEPLOYMENT_GUIDE.md"
echo ""
