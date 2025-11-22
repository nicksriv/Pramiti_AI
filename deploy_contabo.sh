#!/bin/bash

# Pramiti AI - Contabo Quick Deploy Script
# This script automates the deployment process on a fresh Ubuntu server

set -e  # Exit on error

echo "🚀 Starting Pramiti AI Deployment..."
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Get configuration from user
echo ""
echo "Please provide the following information:"
read -p "OpenAI API Key: " OPENAI_KEY
read -p "Domain name (or press Enter to use IP): " DOMAIN_NAME
read -p "Admin email (default: admin@pramiti.ai): " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@pramiti.ai}
read -sp "Admin password: " ADMIN_PASSWORD
echo ""

if [ -z "$OPENAI_KEY" ]; then
    print_error "OpenAI API Key is required!"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    print_error "Admin password is required!"
    exit 1
fi

# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

print_success "Configuration collected"

# Step 1: Update system
echo ""
echo "Step 1: Updating system packages..."
apt update && apt upgrade -y
print_success "System updated"

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev git nginx supervisor curl build-essential
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
print_success "Dependencies installed"

# Step 3: Create application user
echo ""
echo "Step 3: Creating application user..."
if id "pramiti" &>/dev/null; then
    print_warning "User 'pramiti' already exists, skipping..."
else
    useradd -m -s /bin/bash pramiti
    print_success "User 'pramiti' created"
fi

# Step 4: Clone repository
echo ""
echo "Step 4: Cloning repository..."
cd /home/pramiti
if [ -d "Pramiti_AI" ]; then
    print_warning "Directory already exists, pulling latest changes..."
    cd Pramiti_AI
    sudo -u pramiti git pull origin main
else
    sudo -u pramiti git clone https://github.com/nicksriv/Pramiti_AI.git
    cd Pramiti_AI
fi
print_success "Repository ready"

# Step 5: Set up Python virtual environment
echo ""
echo "Step 5: Setting up Python virtual environment..."
sudo -u pramiti python3.11 -m venv venv
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install --upgrade pip
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install -r requirements.txt
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/pip install chromadb gunicorn
print_success "Python environment ready"

# Step 6: Configure environment variables
echo ""
echo "Step 6: Configuring environment variables..."
cat > /home/pramiti/Pramiti_AI/.env << EOF
# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_KEY}

# Server Configuration
PORT=8084
HOST=0.0.0.0

# Security
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Database paths
CHROMA_PERSIST_DIRECTORY=/home/pramiti/Pramiti_AI/data/rag/chroma
CONVERSATIONS_DIR=/home/pramiti/Pramiti_AI/data/rag/conversations

# OAuth Configuration (configure later if needed)
# MICROSOFT_CLIENT_ID=
# MICROSOFT_CLIENT_SECRET=
# MICROSOFT_TENANT_ID=common
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
EOF

chown pramiti:pramiti /home/pramiti/Pramiti_AI/.env
chmod 600 /home/pramiti/Pramiti_AI/.env
print_success "Environment configured"

# Step 7: Create required directories
echo ""
echo "Step 7: Creating required directories..."
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/data/rag/chroma
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/data/rag/conversations
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/secrets
sudo -u pramiti mkdir -p /home/pramiti/Pramiti_AI/logs
sudo -u pramiti mkdir -p /home/pramiti/backups
chmod 700 /home/pramiti/Pramiti_AI/secrets
print_success "Directories created"

# Step 8: Set up Supervisor
echo ""
echo "Step 8: Configuring Supervisor..."
cat > /etc/supervisor/conf.d/pramiti.conf << EOF
[program:pramiti]
directory=/home/pramiti/Pramiti_AI
command=/home/pramiti/Pramiti_AI/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8084 --timeout 300
user=pramiti
autostart=true
autorestart=true
stderr_logfile=/home/pramiti/Pramiti_AI/logs/error.log
stdout_logfile=/home/pramiti/Pramiti_AI/logs/access.log
environment=PATH="/home/pramiti/Pramiti_AI/venv/bin"
EOF

supervisorctl reread
supervisorctl update
supervisorctl start pramiti
print_success "Supervisor configured and service started"

# Step 9: Configure Nginx
echo ""
echo "Step 9: Configuring Nginx..."

if [ -z "$DOMAIN_NAME" ]; then
    SERVER_NAME="_"
    print_warning "No domain provided, using IP address"
else
    SERVER_NAME="$DOMAIN_NAME"
    print_success "Using domain: $DOMAIN_NAME"
fi

cat > /etc/nginx/sites-available/pramiti << EOF
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
EOF

ln -sf /etc/nginx/sites-available/pramiti /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
print_success "Nginx configured"

# Step 10: Configure firewall
echo ""
echo "Step 10: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

# Step 11: Create admin user
echo ""
echo "Step 11: Creating admin user..."
sudo -u pramiti /home/pramiti/Pramiti_AI/venv/bin/python3 << EOF
import sys
sys.path.insert(0, '/home/pramiti/Pramiti_AI')
from core.session_manager import SessionManager

sm = SessionManager()
try:
    sm.create_user(
        user_id="${ADMIN_EMAIL}",
        password="${ADMIN_PASSWORD}",
        org_id="pramiti",
        role="SUPER_ADMIN"
    )
    print("✓ Admin user created successfully")
except Exception as e:
    print(f"Note: {e}")
EOF
print_success "Admin user configured"

# Step 12: Set up SSL (if domain provided)
if [ ! -z "$DOMAIN_NAME" ]; then
    echo ""
    echo "Step 12: Setting up SSL certificate..."
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $ADMIN_EMAIL --redirect
    print_success "SSL certificate installed"
else
    print_warning "Skipping SSL setup (no domain provided)"
fi

# Step 13: Set up log rotation
echo ""
echo "Setting up log rotation..."
cat > /etc/logrotate.d/pramiti << EOF
/home/pramiti/Pramiti_AI/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 pramiti pramiti
    sharedscripts
    postrotate
        supervisorctl restart pramiti > /dev/null
    endscript
}
EOF
print_success "Log rotation configured"

# Step 14: Create backup script
echo ""
echo "Creating backup script..."
cat > /home/pramiti/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/pramiti/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/pramiti_backup_$DATE.tar.gz \
    /home/pramiti/Pramiti_AI/data \
    /home/pramiti/Pramiti_AI/.env \
    /home/pramiti/Pramiti_AI/config 2>/dev/null

find $BACKUP_DIR -name "pramiti_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/pramiti_backup_$DATE.tar.gz"
EOF

chmod +x /home/pramiti/backup.sh
chown pramiti:pramiti /home/pramiti/backup.sh

# Add to crontab
(sudo -u pramiti crontab -l 2>/dev/null; echo "0 2 * * * /home/pramiti/backup.sh >> /home/pramiti/backups/backup.log 2>&1") | sudo -u pramiti crontab -
print_success "Backup script configured"

# Final checks
echo ""
echo "=================================="
echo "Running final checks..."
echo "=================================="

# Check if service is running
if supervisorctl status pramiti | grep -q RUNNING; then
    print_success "Pramiti service is running"
else
    print_error "Pramiti service is not running!"
    echo "Check logs: tail -f /home/pramiti/Pramiti_AI/logs/error.log"
fi

# Check if Nginx is running
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running"
else
    print_error "Nginx is not running!"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

# Print summary
echo ""
echo "=================================="
echo "🎉 Deployment Complete!"
echo "=================================="
echo ""
echo "Access your application:"
if [ -z "$DOMAIN_NAME" ]; then
    echo "  URL: http://${SERVER_IP}"
else
    echo "  URL: https://${DOMAIN_NAME}"
fi
echo ""
echo "Admin Login:"
echo "  Email: ${ADMIN_EMAIL}"
echo "  Password: [the password you entered]"
echo ""
echo "Important Files:"
echo "  Logs: /home/pramiti/Pramiti_AI/logs/"
echo "  Config: /home/pramiti/Pramiti_AI/.env"
echo "  Backups: /home/pramiti/backups/"
echo ""
echo "Useful Commands:"
echo "  Service status: supervisorctl status pramiti"
echo "  Restart service: supervisorctl restart pramiti"
echo "  View logs: tail -f /home/pramiti/Pramiti_AI/logs/access.log"
echo "  Pull updates: cd /home/pramiti/Pramiti_AI && git pull origin main"
echo ""
echo "Next Steps:"
echo "  1. Log in and change your admin password"
echo "  2. Configure OAuth if needed (Microsoft, Google)"
echo "  3. Set up additional users and organizations"
echo "  4. Review security settings"
echo ""
print_success "Deployment script completed!"
echo ""
