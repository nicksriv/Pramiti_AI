#!/bin/bash

# Continuous Deployment Helper for Pramiti AI
# Run this script to push updates from local dev to VPS

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Pramiti AI - Continuous Deployment Helper           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Load VPS config if exists
if [ -f ".vps_config" ]; then
    source .vps_config
    echo -e "${GREEN}✅ Loaded VPS configuration${NC}"
else
    echo -e "${YELLOW}Creating VPS configuration...${NC}"
    read -p "VPS IP address: " VPS_IP
    read -p "SSH username (default: root): " SSH_USER
    SSH_USER=${SSH_USER:-root}
    
    # Save config
    cat > .vps_config << EOF
VPS_IP=$VPS_IP
SSH_USER=$SSH_USER
EOF
    echo -e "${GREEN}✅ Configuration saved to .vps_config${NC}"
fi

# Check for changes
echo ""
echo -e "${BLUE}▶ Checking for local changes...${NC}"
if [ -z "$(git status --porcelain)" ]; then 
    echo -e "${YELLOW}⚠️  No local changes detected${NC}"
    read -p "Deploy anyway? (y/n): " DEPLOY_ANYWAY
    if [ "$DEPLOY_ANYWAY" != "y" ]; then
        exit 0
    fi
else
    echo -e "${GREEN}✅ Changes detected${NC}"
    git status --short
fi

# Commit changes
echo ""
echo -e "${BLUE}▶ Committing changes...${NC}"
read -p "Enter commit message (or press Enter for auto-message): " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update deployment $(date '+%Y-%m-%d %H:%M:%S')"
fi

git add .
git commit -m "$COMMIT_MSG" || echo "No changes to commit"

# Push to GitHub
echo ""
echo -e "${BLUE}▶ Pushing to GitHub...${NC}"
git push origin main

echo -e "${GREEN}✅ Changes pushed to GitHub${NC}"

# Deploy to VPS
echo ""
echo -e "${BLUE}▶ Deploying to VPS at ${VPS_IP}...${NC}"
echo ""

ssh -t ${SSH_USER}@${VPS_IP} << 'ENDSSH'
set -e

cd ~/Pramiti_AI

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Pulling latest changes from GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git pull origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Rebuilding Docker images"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose build

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Restarting services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose up -d

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Checking service health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 5
docker-compose ps

echo ""
if curl -f http://localhost:8084/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! Application is healthy."
else
    echo "⚠️  Warning: Health check failed. Viewing recent logs:"
    docker-compose logs --tail=20 pramiti-ai
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Update deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ENDSSH

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ DEPLOYMENT COMPLETE! ✅                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo "   Local:  Changes committed and pushed to GitHub"
echo "   Remote: VPS updated and services restarted"
echo ""
echo -e "${YELLOW}💡 Quick Commands:${NC}"
echo "   View logs:    ssh ${SSH_USER}@${VPS_IP} 'cd Pramiti_AI && docker-compose logs -f'"
echo "   Check status: ssh ${SSH_USER}@${VPS_IP} 'cd Pramiti_AI && docker-compose ps'"
echo "   Restart:      ssh ${SSH_USER}@${VPS_IP} 'cd Pramiti_AI && docker-compose restart'"
echo ""
