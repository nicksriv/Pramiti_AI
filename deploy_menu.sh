#!/bin/bash

# Pramiti AI - Deployment Helper Menu

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
║              Pramiti AI - Deployment Helper                 ║
║                   Quick Command Menu                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DEPLOYMENT COMMANDS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}1.${NC} Initial VPS Deployment (First time only)"
echo -e "   ${CYAN}Command:${NC} ./deploy_interactive.sh"
echo -e "   ${CYAN}Time:${NC} 10-15 minutes"
echo -e "   ${CYAN}What it does:${NC} Full setup on your VPS with Docker"
echo ""
echo -e "${YELLOW}2.${NC} Update Deployment (After making changes)"
echo -e "   ${CYAN}Command:${NC} ./update_deployment.sh"
echo -e "   ${CYAN}Time:${NC} 2-3 minutes"
echo -e "   ${CYAN}What it does:${NC} Commits, pushes, and deploys updates to VPS"
echo ""
echo -e "${YELLOW}3.${NC} Check VPS Status"
echo -e "   ${CYAN}Command:${NC} ./check_status.sh"
echo -e "   ${CYAN}Time:${NC} 10 seconds"
echo -e "   ${CYAN}What it does:${NC} Shows health, logs, and resource usage"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  LOCAL TESTING${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}4.${NC} Start Local Server"
echo -e "   ${CYAN}Command:${NC} python3 api_server.py"
echo -e "   ${CYAN}Access:${NC} http://localhost:8084/enhanced-dashboard"
echo ""
echo -e "${YELLOW}5.${NC} Kill Local Server"
echo -e "   ${CYAN}Command:${NC} lsof -ti:8084 | xargs kill -9"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  GIT OPERATIONS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}6.${NC} Quick Commit and Push"
echo -e "   ${CYAN}Command:${NC} git add . && git commit -m \"Your message\" && git push"
echo ""
echo -e "${YELLOW}7.${NC} Check Git Status"
echo -e "   ${CYAN}Command:${NC} git status"
echo ""
echo -e "${YELLOW}8.${NC} View Recent Commits"
echo -e "   ${CYAN}Command:${NC} git log --oneline -10"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  VPS MANAGEMENT (Via SSH)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}9.${NC} View Live Logs"
echo -e "   ${CYAN}Command:${NC} ssh user@vps 'cd Pramiti_AI && docker-compose logs -f'"
echo ""
echo -e "${YELLOW}10.${NC} Restart Services"
echo -e "   ${CYAN}Command:${NC} ssh user@vps 'cd Pramiti_AI && docker-compose restart'"
echo ""
echo -e "${YELLOW}11.${NC} Check Service Status"
echo -e "   ${CYAN}Command:${NC} ssh user@vps 'cd Pramiti_AI && docker-compose ps'"
echo ""
echo -e "${YELLOW}12.${NC} View Last 50 Log Lines"
echo -e "   ${CYAN}Command:${NC} ssh user@vps 'cd Pramiti_AI && docker-compose logs --tail=50'"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DOCUMENTATION${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📚 Available Guides:${NC}"
echo ""
echo "  • DOCKER_DEPLOYMENT_README.md - Start here! Quick guide"
echo "  • CONTINUOUS_DEPLOYMENT.md - Complete workflow guide"
echo "  • DEPLOYMENT_GUIDE.md - Detailed technical manual"
echo "  • QUICK_DEPLOY.md - Quick reference commands"
echo "  • CONTABO_DEPLOYMENT_SUMMARY.md - Overview"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  QUICK ACTIONS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if VPS is configured
if [ -f ".vps_config" ]; then
    source .vps_config
    echo -e "${GREEN}✅ VPS Configured: ${VPS_IP}${NC}"
    echo ""
    
    echo "What would you like to do?"
    echo ""
    echo "  [1] Deploy/Update to VPS"
    echo "  [2] Check VPS Status"
    echo "  [3] Test Locally"
    echo "  [4] View VPS Logs"
    echo "  [5] Open Documentation"
    echo "  [Q] Quit"
    echo ""
    read -p "Enter choice: " choice
    
    case $choice in
        1)
            echo ""
            echo "Starting deployment..."
            ./update_deployment.sh
            ;;
        2)
            echo ""
            echo "Checking VPS status..."
            ./check_status.sh
            ;;
        3)
            echo ""
            echo "Starting local server..."
            echo "Access at: http://localhost:8084/enhanced-dashboard"
            python3 api_server.py
            ;;
        4)
            echo ""
            echo "Connecting to VPS logs..."
            ssh ${SSH_USER}@${VPS_IP} 'cd Pramiti_AI && docker-compose logs -f pramiti-ai'
            ;;
        5)
            echo ""
            echo "Opening documentation..."
            if command -v code &> /dev/null; then
                code DOCKER_DEPLOYMENT_README.md
            else
                cat DOCKER_DEPLOYMENT_README.md
            fi
            ;;
        [Qq])
            echo "Goodbye!"
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
else
    echo -e "${YELLOW}⚠️  VPS Not Configured Yet${NC}"
    echo ""
    echo -e "To get started, run: ${CYAN}./deploy_interactive.sh${NC}"
    echo ""
    echo -e "This will:"
    echo "  1. Connect to your VPS"
    echo "  2. Install Docker"
    echo "  3. Deploy the application"
    echo "  4. Configure everything"
    echo ""
    read -p "Run deployment now? (y/n): " run_deploy
    
    if [ "$run_deploy" = "y" ] || [ "$run_deploy" = "Y" ]; then
        ./deploy_interactive.sh
    fi
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
