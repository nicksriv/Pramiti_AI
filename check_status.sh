#!/bin/bash

# VPS Status Monitor - Quick health check from local machine

if [ ! -f ".vps_config" ]; then
    echo "❌ No VPS configuration found. Run deploy_interactive.sh first."
    exit 1
fi

source .vps_config

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Pramiti AI - VPS Status Monitor                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}VPS: ${VPS_IP}${NC}"
echo ""

# Test SSH connection
if ! ssh -o ConnectTimeout=5 ${SSH_USER}@${VPS_IP} "echo 'connected'" &>/dev/null; then
    echo -e "${RED}❌ Cannot connect to VPS${NC}"
    exit 1
fi

# Get status
ssh ${SSH_USER}@${VPS_IP} << 'ENDSSH'
cd ~/Pramiti_AI 2>/dev/null || { echo "❌ Pramiti_AI not found"; exit 1; }

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Docker Services Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Application Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -f http://localhost:8084/health 2>/dev/null; then
    echo ""
    echo "✅ Application is healthy"
else
    echo "❌ Health check failed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Resource Usage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Memory:"
free -h | grep Mem | awk '{print "  Used: "$3" / "$2" ("$3/$2*100"%)"}'

echo ""
echo "Disk:"
df -h / | tail -1 | awk '{print "  Used: "$3" / "$2" ("$5")"}'

echo ""
echo "Docker:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ Recent Logs (Last 10 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose logs --tail=10 pramiti-ai 2>/dev/null || echo "No logs available"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ENDSSH

echo ""
echo -e "${GREEN}✅ Status check complete${NC}"
echo ""
