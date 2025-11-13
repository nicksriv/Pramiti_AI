#!/bin/bash

# SSH Key Setup Helper for Contabo VPS
# This script helps you set up SSH key authentication

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              SSH Key Setup for Contabo VPS                  ║
║            Passwordless Authentication Guide                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}This script will help you set up SSH key authentication${NC}"
echo -e "${CYAN}so you can deploy without entering passwords.${NC}"
echo ""

# Step 1: Check for existing SSH key
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Checking for existing SSH key${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${GREEN}✅ SSH key found: ~/.ssh/id_rsa.pub${NC}"
    echo ""
    echo "Your public key:"
    echo -e "${YELLOW}$(cat ~/.ssh/id_rsa.pub)${NC}"
    echo ""
    read -p "Use this existing key? (y/n): " USE_EXISTING
    
    if [ "$USE_EXISTING" = "y" ] || [ "$USE_EXISTING" = "Y" ]; then
        SSH_KEY_PATH="$HOME/.ssh/id_rsa.pub"
    else
        CREATE_NEW=true
    fi
else
    echo -e "${YELLOW}⚠️  No SSH key found${NC}"
    CREATE_NEW=true
fi

# Step 2: Create new SSH key if needed
if [ "$CREATE_NEW" = true ]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Step 2: Creating new SSH key${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    read -p "Enter your email for the SSH key: " EMAIL
    
    echo "Generating new SSH key..."
    ssh-keygen -t rsa -b 4096 -C "$EMAIL" -f ~/.ssh/id_rsa -N ""
    
    echo -e "${GREEN}✅ SSH key created successfully!${NC}"
    SSH_KEY_PATH="$HOME/.ssh/id_rsa.pub"
    
    echo ""
    echo "Your new public key:"
    echo -e "${YELLOW}$(cat ~/.ssh/id_rsa.pub)${NC}"
fi

# Step 3: Get VPS details
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: VPS Connection Details${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Enter your VPS IP address: " VPS_IP
read -p "Enter SSH username (default: nicksriv): " SSH_USER
SSH_USER=${SSH_USER:-nicksriv}

# Step 4: Copy SSH key to VPS
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Copying SSH key to VPS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}You'll need to enter your VPS password one last time.${NC}"
echo ""

# Try ssh-copy-id first (macOS might not have it)
if command -v ssh-copy-id &> /dev/null; then
    echo "Using ssh-copy-id..."
    ssh-copy-id -i "$SSH_KEY_PATH" ${SSH_USER}@${VPS_IP}
else
    echo "ssh-copy-id not found, using manual method..."
    echo ""
    echo -e "${YELLOW}Please enter your VPS password when prompted:${NC}"
    
    # Manual method
    cat "$SSH_KEY_PATH" | ssh ${SSH_USER}@${VPS_IP} "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
fi

# Step 5: Test connection
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 5: Testing SSH connection${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Testing passwordless connection..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 ${SSH_USER}@${VPS_IP} "echo 'SSH key authentication successful!'" 2>/dev/null; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║          ✅ SSH KEY SETUP SUCCESSFUL! ✅                    ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}You can now SSH without password:${NC}"
    echo -e "${YELLOW}  ssh ${SSH_USER}@${VPS_IP}${NC}"
    echo ""
    
    # Save VPS config
    cat > .vps_config << EOF
VPS_IP=$VPS_IP
SSH_USER=$SSH_USER
EOF
    
    echo -e "${GREEN}✅ VPS configuration saved to .vps_config${NC}"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Next Steps:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1. Deploy your application:"
    echo -e "   ${YELLOW}./deploy_interactive.sh${NC}"
    echo ""
    echo "2. Or use the menu:"
    echo -e "   ${YELLOW}./deploy_menu.sh${NC}"
    echo ""
    echo -e "${GREEN}🎉 You're all set for passwordless deployment!${NC}"
    echo ""
else
    echo -e "${RED}❌ SSH key authentication failed${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check VPS permissions:"
    echo -e "   ${YELLOW}ssh ${SSH_USER}@${VPS_IP} 'chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'${NC}"
    echo ""
    echo "2. Check if key is in authorized_keys:"
    echo -e "   ${YELLOW}ssh ${SSH_USER}@${VPS_IP} 'cat ~/.ssh/authorized_keys'${NC}"
    echo ""
    echo "3. Try manual connection:"
    echo -e "   ${YELLOW}ssh -v ${SSH_USER}@${VPS_IP}${NC}"
    echo ""
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
