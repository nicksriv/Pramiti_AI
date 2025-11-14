#!/bin/bash

# Update VPS with Latest Code
# This script pulls the latest changes from GitHub and restarts the service

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       Pramiti AI - VPS Update Script                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if .vps_config exists
if [ ! -f .vps_config ]; then
    echo -e "${YELLOW}VPS configuration not found. Setting up...${NC}"
    echo ""
    read -p "Enter your VPS IP address (e.g., 213.199.48.187): " VPS_IP
    read -p "Enter SSH username (default: root): " SSH_USER
    SSH_USER=${SSH_USER:-root}
    read -p "Enter project directory on VPS (default: ~/Agentic-AI-Organization): " VPS_DIR
    VPS_DIR=${VPS_DIR:-~/Agentic-AI-Organization}
    
    # Save configuration
    cat > .vps_config << EOF
VPS_IP=$VPS_IP
SSH_USER=$SSH_USER
VPS_DIR=$VPS_DIR
EOF
    
    echo -e "${GREEN}✅ Configuration saved to .vps_config${NC}"
else
    # Load existing configuration
    source .vps_config
    echo -e "${CYAN}Using saved configuration:${NC}"
    echo -e "  VPS IP: ${YELLOW}$VPS_IP${NC}"
    echo -e "  SSH User: ${YELLOW}$SSH_USER${NC}"
    echo -e "  Directory: ${YELLOW}$VPS_DIR${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Testing SSH Connection${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSH_USER}@${VPS_IP} "echo ''" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo -e "${YELLOW}Please check:${NC}"
    echo "  1. VPS is running"
    echo "  2. IP address is correct: $VPS_IP"
    echo "  3. SSH key is set up"
    echo ""
    echo "To set up SSH key, run: ./setup_ssh_manual.sh"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Pulling Latest Code from GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~/Agentic-AI-Organization || {
    echo "❌ Project directory not found. Please clone the repository first."
    exit 1
}

echo "📥 Fetching latest changes..."
git fetch origin

echo "🔄 Pulling latest code..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Code updated successfully"
else
    echo "⚠️  Git pull had issues. Attempting to resolve..."
    git stash
    git pull origin main
    echo "✅ Code updated (local changes stashed)"
fi
ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to update code${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Installing/Updating Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~/Agentic-AI-Organization

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    
    echo "📦 Updating dependencies..."
    pip install -r requirements.txt --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies updated"
    else
        echo "⚠️  Some dependencies failed to install"
    fi
else
    echo "⚠️  Virtual environment not found. Installing dependencies globally..."
    pip3 install -r requirements.txt --quiet
fi
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Checking for .env File${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ENV_EXISTS=$(ssh ${SSH_USER}@${VPS_IP} "[ -f ~/Agentic-AI-Organization/.env ] && echo 'yes' || echo 'no'")

if [ "$ENV_EXISTS" == "yes" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo ""
    read -p "Do you want to upload your local .env file? (y/n): " UPLOAD_ENV
    
    if [ "$UPLOAD_ENV" == "y" ]; then
        if [ -f .env ]; then
            echo "📤 Uploading .env file..."
            scp .env ${SSH_USER}@${VPS_IP}:~/Agentic-AI-Organization/.env
            echo -e "${GREEN}✅ .env file uploaded${NC}"
        else
            echo -e "${RED}❌ Local .env file not found${NC}"
            echo "Please create .env file from .env.example"
        fi
    else
        echo -e "${YELLOW}⚠️  Remember to create .env on VPS with credentials${NC}"
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 5: Restarting Application${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~/Agentic-AI-Organization

# Check if running with systemd
if systemctl is-active --quiet pramiti-ai; then
    echo "🔄 Restarting systemd service..."
    sudo systemctl restart pramiti-ai
    sleep 2
    
    if systemctl is-active --quiet pramiti-ai; then
        echo "✅ Service restarted successfully"
        systemctl status pramiti-ai --no-pager -l
    else
        echo "❌ Service failed to start"
        journalctl -u pramiti-ai -n 20 --no-pager
    fi
    
# Check if running with PM2
elif command -v pm2 &> /dev/null && pm2 list | grep -q "api_server"; then
    echo "🔄 Restarting PM2 process..."
    pm2 restart api_server
    sleep 2
    pm2 status api_server
    
# Check for screen session
elif screen -list | grep -q "pramiti"; then
    echo "🔄 Restarting screen session..."
    screen -S pramiti -X quit
    sleep 1
    screen -dmS pramiti bash -c "cd ~/Agentic-AI-Organization && python3 api_server.py"
    echo "✅ Screen session restarted"
    
# Manual process check
else
    # Kill existing process
    if pgrep -f "api_server.py" > /dev/null; then
        echo "🛑 Stopping existing process..."
        pkill -f "api_server.py"
        sleep 2
    fi
    
    # Start new process in background
    echo "🚀 Starting application..."
    nohup python3 api_server.py > /tmp/api_server.log 2>&1 &
    sleep 3
    
    # Check if started
    if pgrep -f "api_server.py" > /dev/null; then
        echo "✅ Application started"
        tail -10 /tmp/api_server.log
    else
        echo "❌ Failed to start application"
        cat /tmp/api_server.log
    fi
fi
ENDSSH

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 6: Verifying Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "🔍 Testing API endpoint..."
sleep 2

# Test the API
RESPONSE=$(ssh ${SSH_USER}@${VPS_IP} "curl -s -o /dev/null -w '%{http_code}' http://localhost:8084/api/v1/connectors 2>/dev/null")

if [ "$RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API is responding (HTTP $RESPONSE)${NC}"
else
    echo -e "${YELLOW}⚠️  API response: HTTP $RESPONSE${NC}"
    echo "Checking logs..."
    ssh ${SSH_USER}@${VPS_IP} "tail -20 /tmp/api_server.log 2>/dev/null || journalctl -u pramiti-ai -n 20 --no-pager"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Update Complete! ✅                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Summary:${NC}"
echo "  • Code updated from GitHub"
echo "  • Dependencies refreshed"
echo "  • Application restarted"
echo "  • VPS IP: $VPS_IP"
echo ""
echo -e "${CYAN}🌐 Access your application:${NC}"
echo "  • API: http://$VPS_IP:8084"
echo "  • Dashboard: http://$VPS_IP:8084/enhanced-dashboard"
echo ""
echo -e "${CYAN}📝 Useful commands:${NC}"
echo "  • Check logs: ssh ${SSH_USER}@${VPS_IP} 'tail -f /tmp/api_server.log'"
echo "  • Check status: ssh ${SSH_USER}@${VPS_IP} 'systemctl status pramiti-ai'"
echo "  • Restart: ./update_vps.sh"
echo ""
