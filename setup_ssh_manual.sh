#!/bin/bash

# Alternative SSH Key Setup - Copy/Paste Method
# Use this if ssh-copy-id has connection issues

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         SSH Key Setup - Alternative Method                  ║
║            (Copy/Paste via VPS Console)                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}This method uses your VPS control panel's web console${NC}"
echo -e "${CYAN}to avoid SSH connection issues.${NC}"
echo ""

# Check for SSH key
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${YELLOW}No SSH key found. Generating one...${NC}"
    ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}✅ SSH key created${NC}"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Copy Your Public Key${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Your SSH public key (already copied to clipboard):"
echo ""
echo -e "${YELLOW}"
cat ~/.ssh/id_rsa.pub
echo -e "${NC}"
echo ""

# Copy to clipboard
if command -v pbcopy &> /dev/null; then
    cat ~/.ssh/id_rsa.pub | pbcopy
    echo -e "${GREEN}✅ Key copied to clipboard!${NC}"
elif command -v xclip &> /dev/null; then
    cat ~/.ssh/id_rsa.pub | xclip -selection clipboard
    echo -e "${GREEN}✅ Key copied to clipboard!${NC}"
else
    echo -e "${YELLOW}⚠️  Please manually copy the key above${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Add Key to VPS via Console${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Follow these steps:"
echo ""
echo -e "${CYAN}1.${NC} Go to your Contabo control panel:"
echo "   https://my.contabo.com/"
echo ""
echo -e "${CYAN}2.${NC} Find your VPS (213.199.48.187)"
echo ""
echo -e "${CYAN}3.${NC} Click on 'VNC' or 'Console' to open web terminal"
echo ""
echo -e "${CYAN}4.${NC} Log in with username: ${YELLOW}nicksriv${NC} and your password"
echo ""
echo -e "${CYAN}5.${NC} Run these commands in the console:"
echo ""
echo -e "${YELLOW}   mkdir -p ~/.ssh${NC}"
echo -e "${YELLOW}   chmod 700 ~/.ssh${NC}"
echo -e "${YELLOW}   nano ~/.ssh/authorized_keys${NC}"
echo ""
echo -e "${CYAN}6.${NC} Paste your public key (from clipboard or above)"
echo ""
echo -e "${CYAN}7.${NC} Press: ${YELLOW}Ctrl+O${NC} (save), ${YELLOW}Enter${NC}, then ${YELLOW}Ctrl+X${NC} (exit)"
echo ""
echo -e "${CYAN}8.${NC} Set correct permissions:"
echo ""
echo -e "${YELLOW}   chmod 600 ~/.ssh/authorized_keys${NC}"
echo ""
echo -e "${CYAN}9.${NC} Verify the key was added:"
echo ""
echo -e "${YELLOW}   cat ~/.ssh/authorized_keys${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Test Connection${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Press Enter when you've completed the steps above..."

echo ""
echo "Testing SSH connection..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 nicksriv@213.199.48.187 "echo 'Success!'" 2>/dev/null; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ SSH KEY AUTHENTICATION WORKING! ✅              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Save config
    cat > .vps_config << EOF
VPS_IP=213.199.48.187
SSH_USER=nicksriv
EOF
    
    echo -e "${GREEN}✅ VPS configuration saved${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. Deploy: ${YELLOW}./deploy_interactive.sh${NC}"
    echo "  2. Or menu: ${YELLOW}./deploy_menu.sh${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Connection test inconclusive${NC}"
    echo ""
    echo "Try manual test:"
    echo -e "${YELLOW}  ssh nicksriv@213.199.48.187${NC}"
    echo ""
    echo "If it asks for password, double-check Step 2 above."
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
