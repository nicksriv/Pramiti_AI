#!/bin/bash

# Initial VPS Setup - Clone Repository and Configure
# Run this first before update_vps.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       Pramiti AI - Initial VPS Setup                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Load or create VPS config
if [ ! -f .vps_config ]; then
    echo -e "${YELLOW}Setting up VPS configuration...${NC}"
    echo ""
    read -p "Enter your VPS IP address (e.g., 213.199.48.187): " VPS_IP
    read -p "Enter SSH username (default: root): " SSH_USER
    SSH_USER=${SSH_USER:-root}
    
    cat > .vps_config << EOF
VPS_IP=$VPS_IP
SSH_USER=$SSH_USER
VPS_DIR=~/Agentic-AI-Organization
EOF
    
    echo -e "${GREEN}✅ Configuration saved${NC}"
else
    source .vps_config
    echo -e "${CYAN}Using saved configuration:${NC}"
    echo -e "  VPS IP: ${YELLOW}$VPS_IP${NC}"
    echo -e "  SSH User: ${YELLOW}$SSH_USER${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Testing SSH Connection${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSH_USER}@${VPS_IP} "echo ''" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo -e "${YELLOW}Please set up SSH access first using: ./setup_ssh_manual.sh${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Installing Required Packages${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
echo "📦 Updating package list..."
sudo apt-get update -qq

echo "📦 Installing Git, Python, and pip..."
sudo apt-get install -y -qq git python3 python3-pip python3-venv

echo "✅ Packages installed"
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Cloning Repository from GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~

# Remove old directory if exists
if [ -d "Agentic-AI-Organization" ]; then
    echo "🗑️  Removing old directory..."
    rm -rf Agentic-AI-Organization
fi

echo "📥 Cloning repository..."
git clone https://github.com/nicksriv/Pramiti_AI.git Agentic-AI-Organization

if [ $? -eq 0 ]; then
    echo "✅ Repository cloned successfully"
    cd Agentic-AI-Organization
    echo "📁 Current directory: $(pwd)"
    echo "📊 Files cloned: $(ls -1 | wc -l) items"
else
    echo "❌ Failed to clone repository"
    exit 1
fi
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Setting Up Python Virtual Environment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~/Agentic-AI-Organization

echo "🐍 Creating virtual environment..."
python3 -m venv venv

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

echo "✅ Virtual environment ready"
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 5: Setting Up Environment Variables${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f .env ]; then
    echo -e "${CYAN}Found local .env file. Uploading to VPS...${NC}"
    scp .env ${SSH_USER}@${VPS_IP}:~/Agentic-AI-Organization/.env
    echo -e "${GREEN}✅ .env file uploaded${NC}"
else
    echo -e "${YELLOW}⚠️  No local .env file found${NC}"
    echo ""
    read -p "Do you want to create .env on VPS now? (y/n): " CREATE_ENV
    
    if [ "$CREATE_ENV" == "y" ]; then
        echo ""
        echo -e "${CYAN}Enter your credentials:${NC}"
        read -p "Microsoft Client ID: " MS_CLIENT_ID
        read -p "Microsoft Client Secret: " MS_CLIENT_SECRET
        read -p "Microsoft Tenant ID: " MS_TENANT_ID
        
        ssh ${SSH_USER}@${VPS_IP} << EOF
cd ~/Agentic-AI-Organization
cat > .env << ENVEOF
# Microsoft 365 OAuth Credentials
MICROSOFT_CLIENT_ID=$MS_CLIENT_ID
MICROSOFT_CLIENT_SECRET=$MS_CLIENT_SECRET
MICROSOFT_TENANT_ID=$MS_TENANT_ID

# Google Workspace OAuth Credentials
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8084
ENVEOF
EOF
        echo -e "${GREEN}✅ .env file created on VPS${NC}"
    else
        echo -e "${YELLOW}⚠️  Remember to create .env file manually${NC}"
        ssh ${SSH_USER}@${VPS_IP} "cd ~/Agentic-AI-Organization && cp .env.example .env"
        echo -e "${YELLOW}Template .env created. Edit it with your credentials later.${NC}"
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 6: Creating Systemd Service${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
echo "📝 Creating systemd service file..."

sudo tee /etc/systemd/system/pramiti-ai.service > /dev/null << EOF
[Unit]
Description=Pramiti AI - Agentic Organization System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Agentic-AI-Organization
Environment="PATH=/root/Agentic-AI-Organization/venv/bin"
ExecStart=/root/Agentic-AI-Organization/venv/bin/python3 api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "✅ Enabling service to start on boot..."
sudo systemctl enable pramiti-ai

echo "✅ Systemd service created"
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 7: Starting Application${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
echo "🚀 Starting Pramiti AI service..."
sudo systemctl start pramiti-ai

sleep 3

if systemctl is-active --quiet pramiti-ai; then
    echo "✅ Service started successfully"
    systemctl status pramiti-ai --no-pager -l
else
    echo "❌ Service failed to start"
    echo "Checking logs..."
    journalctl -u pramiti-ai -n 30 --no-pager
fi
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 8: Configuring Firewall${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
echo "🔥 Configuring UFW firewall..."

# Enable UFW if not already enabled
if ! sudo ufw status | grep -q "Status: active"; then
    sudo ufw --force enable
fi

# Allow SSH
sudo ufw allow OpenSSH

# Allow application port
sudo ufw allow 8084/tcp

echo "✅ Firewall configured"
sudo ufw status numbered
ENDSSH

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Initial Setup Complete! ✅                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Summary:${NC}"
echo "  ✅ Repository cloned from GitHub"
echo "  ✅ Python virtual environment created"
echo "  ✅ Dependencies installed"
echo "  ✅ Environment variables configured"
echo "  ✅ Systemd service created and started"
echo "  ✅ Firewall configured"
echo ""
echo -e "${CYAN}🌐 Access your application:${NC}"
echo "  • API: http://$VPS_IP:8084"
echo "  • Dashboard: http://$VPS_IP:8084/enhanced-dashboard"
echo "  • OpenAI Dashboard: http://$VPS_IP:8084/openai-dashboard"
echo ""
echo -e "${CYAN}📝 Useful commands:${NC}"
echo "  • Check status: ssh ${SSH_USER}@${VPS_IP} 'systemctl status pramiti-ai'"
echo "  • View logs: ssh ${SSH_USER}@${VPS_IP} 'journalctl -u pramiti-ai -f'"
echo "  • Restart: ssh ${SSH_USER}@${VPS_IP} 'sudo systemctl restart pramiti-ai'"
echo "  • Update code: ./update_vps.sh"
echo ""
echo -e "${YELLOW}📌 Next steps:${NC}"
echo "  1. Verify .env file has your OAuth credentials"
echo "  2. Update Azure redirect URI to http://$VPS_IP:8084/api/v1/oauth/callback/microsoft"
echo "  3. Test the application by visiting the dashboard"
echo "  4. Use ./update_vps.sh for future updates"
echo ""
