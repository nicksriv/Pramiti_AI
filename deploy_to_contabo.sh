#!/bin/bash

# Local script to deploy Pramiti AI to Contabo server
# This script runs on your local machine and connects to Contabo via SSH

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Pramiti AI - Contabo Deployment Helper"
echo "=========================================="
echo ""

# Read OpenAI key from local .env file
if [ -f ".env" ]; then
    OPENAI_KEY=$(grep "OPENAI_API_KEY=" .env | cut -d '=' -f2)
    echo -e "${GREEN}✓${NC} Found OpenAI API key in .env"
else
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

# Get server details
read -p "Contabo Server IP: " SERVER_IP
read -p "Domain name (optional, press Enter to skip): " DOMAIN_NAME
read -p "Admin email (default: admin@pramiti.ai): " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@pramiti.ai}
read -sp "Admin password: " ADMIN_PASSWORD
echo ""

if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}✗${NC} Server IP is required!"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo -e "${RED}✗${NC} Admin password is required!"
    exit 1
fi

echo ""
echo -e "${YELLOW}Connecting to Contabo server...${NC}"

# Create remote deployment script
REMOTE_SCRIPT=$(cat <<'SCRIPT_EOF'
#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

echo "Starting non-interactive deployment..."

# Update system
echo "Updating system..."
apt update && apt upgrade -y
print_success "System updated"

# Install dependencies
echo "Installing dependencies..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev git nginx supervisor curl build-essential
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
print_success "Dependencies installed"

# Create user
if ! id "pramiti" &>/dev/null; then
    useradd -m -s /bin/bash pramiti
    print_success "User created"
else
    print_warning "User already exists"
fi

# Clone/update repository
cd /home/pramiti
if [ -d "Pramiti_AI" ]; then
    cd Pramiti_AI
    sudo -u pramiti git pull origin main
    print_success "Repository updated"
else
    sudo -u pramiti git clone https://github.com/nicksriv/Pramiti_AI.git
    cd Pramiti_AI
    print_success "Repository cloned"
fi

# Setup Python environment
sudo -u pramiti python3.11 -m venv venv
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install --upgrade pip
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install -r requirements.txt
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install chromadb gunicorn
print_success "Python environment ready"

# Generate keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Create .env file
cat > /home/pramiti/Pramiti_AI/.env << ENV_EOF
OPENAI_API_KEY=__OPENAI_KEY__
PORT=8084
HOST=0.0.0.0
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
CHROMA_PERSIST_DIRECTORY=/home/pramiti/Pramiti_AI/data/rag/chroma
CONVERSATIONS_DIR=/home/pramiti/Pramiti_AI/data/rag/conversations
ENV_EOF

chown pramiti:pramiti /home/pramiti/Pramiti_AI/.env
chmod 600 /home/pramiti/Pramiti_AI/.env
print_success "Environment configured"

# Create directories
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/data/rag/chroma
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/data/rag/conversations
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/secrets
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/logs
sudo -u pramiti mkdir -p /home/pramiti/backups
chmod 700 /home/pramiti/Pramiti_AI/secrets
print_success "Directories created"

# Configure Supervisor
cat > /etc/supervisor/conf.d/pramiti.conf << SUPER_EOF
[program:pramiti]
directory=/home/pramiti/Pramiti_AI
command=/home/pramiti/Pramiti_AI/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8084 --timeout 300
user=pramiti
autostart=true
autorestart=true
stderr_logfile=/home/pramiti/Pramiti_AI/logs/error.log
stdout_logfile=/home/pramiti/Pramiti_AI/logs/access.log
environment=PATH="/home/pramiti/Pramiti_AI/venv/bin"
SUPER_EOF

supervisorctl reread
supervisorctl update
supervisorctl start pramiti
print_success "Supervisor configured"

# Configure Nginx
SERVER_NAME="__SERVER_NAME__"

cat > /etc/nginx/sites-available/pramiti << NGINX_EOF
server {
    listen 80;
    server_name ${SERVER_NAME};
    client_max_body_size 50M;

    location / {
        root /home/pramiti/Pramiti_AI/web;
        try_files \$uri \$uri/ /enhanced-dashboard.html;
        index enhanced-dashboard.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /user-chat {
        proxy_pass http://127.0.0.1:8084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /health {
        proxy_pass http://127.0.0.1:8084;
        access_log off;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/pramiti /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
print_success "Nginx configured"

# Configure firewall
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

# Create admin user
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/python3 << PYTHON_EOF
import sys
sys.path.insert(0, '/home/pramiti/Pramiti_AI')
from core.session_manager import SessionManager

sm = SessionManager()
try:
    sm.create_user(
        user_id="__ADMIN_EMAIL__",
        password="__ADMIN_PASSWORD__",
        org_id="pramiti",
        role="SUPER_ADMIN"
    )
    print("✓ Admin user created")
except Exception as e:
    print(f"Note: {e}")
PYTHON_EOF

print_success "Admin user configured"

# Setup SSL if domain provided
DOMAIN_SETUP="__DOMAIN_NAME__"
if [ ! -z "$DOMAIN_SETUP" ] && [ "$DOMAIN_SETUP" != "_" ]; then
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN_SETUP --non-interactive --agree-tos --email __ADMIN_EMAIL__ --redirect
    print_success "SSL configured"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "=================================="
echo "🎉 Deployment Complete!"
echo "=================================="
echo ""
if [ ! -z "$DOMAIN_SETUP" ] && [ "$DOMAIN_SETUP" != "_" ]; then
    echo "Access: https://$DOMAIN_SETUP"
else
    echo "Access: http://$SERVER_IP"
fi
echo "Admin: __ADMIN_EMAIL__"
echo ""
SCRIPT_EOF
)

# Replace placeholders in remote script
REMOTE_SCRIPT="${REMOTE_SCRIPT//__OPENAI_KEY__/$OPENAI_KEY}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__ADMIN_EMAIL__/$ADMIN_EMAIL}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__ADMIN_PASSWORD__/$ADMIN_PASSWORD}"

if [ -z "$DOMAIN_NAME" ]; then
    REMOTE_SCRIPT="${REMOTE_SCRIPT//__SERVER_NAME__/_}"
    REMOTE_SCRIPT="${REMOTE_SCRIPT//__DOMAIN_NAME__/}"
else
    REMOTE_SCRIPT="${REMOTE_SCRIPT//__SERVER_NAME__/$DOMAIN_NAME}"
    REMOTE_SCRIPT="${REMOTE_SCRIPT//__DOMAIN_NAME__/$DOMAIN_NAME}"
fi

# Execute on remote server
echo "$REMOTE_SCRIPT" | ssh root@$SERVER_IP 'bash -s'

echo ""
echo -e "${GREEN}✓${NC} Deployment completed successfully!"
echo ""
if [ -z "$DOMAIN_NAME" ]; then
    echo "Access your application at: http://$SERVER_IP"
else
    echo "Access your application at: https://$DOMAIN_NAME"
fi
echo "Login with: $ADMIN_EMAIL"
echo ""
