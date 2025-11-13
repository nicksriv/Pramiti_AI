# Contabo VPS Deployment Guide

## 🚀 Deploying Agentic AI Organization Platform on Contabo VPS

This guide walks you through deploying the platform on your Contabo VPS for production use.

---

## 📋 Prerequisites

### Contabo VPS Requirements
- **Minimum Specs**: 4 vCPU, 8GB RAM, 50GB SSD
- **Recommended**: 6 vCPU, 16GB RAM, 100GB SSD
- **OS**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- **Access**: SSH root access

### Domain & DNS (Optional but Recommended)
- Domain name (e.g., `ai.yourdomain.com`)
- DNS A record pointing to your Contabo VPS IP

---

## 🔧 Step 1: Initial Server Setup

### 1.1 Connect to Your VPS
```bash
ssh root@YOUR_VPS_IP
```

### 1.2 Update System
```bash
apt update && apt upgrade -y
```

### 1.3 Create Non-Root User
```bash
adduser pramiti
usermod -aG sudo pramiti
su - pramiti
```

### 1.4 Set Up Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🐍 Step 2: Install Python & Dependencies

### 2.1 Install Python 3.11+
```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y git curl wget build-essential
```

### 2.2 Install Nginx (Web Server)
```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 2.3 Install Supervisor (Process Manager)
```bash
sudo apt install -y supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

---

## 📥 Step 3: Clone & Setup Application

### 3.1 Clone Repository
```bash
cd /home/pramiti
git clone https://github.com/nicksriv/Pramiti_AI.git
cd Pramiti_AI
```

### 3.2 Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Configure Environment
```bash
cp .env.example .env
nano .env
```

**Edit `.env` file:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8084
ENVIRONMENT=production

# Security (generate strong keys)
SECRET_KEY=your_secret_key_here_use_openssl_rand_hex_32
ALLOWED_ORIGINS=https://yourdomain.com,https://ai.yourdomain.com

# Database (if using PostgreSQL in future)
# DATABASE_URL=postgresql://user:password@localhost/pramiti_ai
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔧 Step 4: Configure Supervisor (Process Manager)

### 4.1 Create Supervisor Config
```bash
sudo nano /etc/supervisor/conf.d/pramiti-ai.conf
```

**Add this configuration:**
```ini
[program:pramiti-ai]
directory=/home/pramiti/Pramiti_AI
command=/home/pramiti/Pramiti_AI/venv/bin/python3 api_server.py
user=pramiti
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pramiti-ai/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/home/pramiti/Pramiti_AI/venv/bin"

[program:pramiti-ai-worker]
directory=/home/pramiti/Pramiti_AI
command=/home/pramiti/Pramiti_AI/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8084 --workers 4
user=pramiti
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pramiti-ai/worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/home/pramiti/Pramiti_AI/venv/bin"
```

### 4.2 Create Log Directory
```bash
sudo mkdir -p /var/log/pramiti-ai
sudo chown pramiti:pramiti /var/log/pramiti-ai
```

### 4.3 Update & Start Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
sudo supervisorctl status
```

---

## 🌐 Step 5: Configure Nginx (Reverse Proxy)

### 5.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/pramiti-ai
```

**Add this configuration:**
```nginx
upstream pramiti_backend {
    server 127.0.0.1:8084;
    keepalive 64;
}

server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;  # Replace with your domain or VPS IP
    
    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;
    
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
        alias /home/pramiti/Pramiti_AI/web/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://pramiti_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://pramiti_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
    
    # Main application
    location / {
        proxy_pass http://pramiti_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://pramiti_backend/health;
        access_log off;
    }
}
```

### 5.2 Enable Site & Test
```bash
sudo ln -s /etc/nginx/sites-available/pramiti-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 Step 6: SSL Certificate (HTTPS) with Let's Encrypt

### 6.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter email for urgent renewal notices
- Agree to terms of service
- Choose to redirect HTTP to HTTPS (recommended)

### 6.3 Auto-Renewal Setup
```bash
sudo certbot renew --dry-run
```

The auto-renewal cron job is automatically set up.

---

## 🗄️ Step 7: Optional - PostgreSQL Database Setup

### 7.1 Install PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 7.2 Create Database & User
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE pramiti_ai;
CREATE USER pramiti_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pramiti_ai TO pramiti_user;
\q
```

### 7.3 Update .env File
```bash
nano /home/pramiti/Pramiti_AI/.env
```

Add:
```bash
DATABASE_URL=postgresql://pramiti_user:your_secure_password@localhost/pramiti_ai
```

### 7.4 Restart Application
```bash
sudo supervisorctl restart pramiti-ai-worker
```

---

## 📊 Step 8: Monitoring & Logging

### 8.1 View Application Logs
```bash
# Real-time logs
sudo tail -f /var/log/pramiti-ai/app.log

# Nginx access logs
sudo tail -f /var/log/nginx/pramiti-ai-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/pramiti-ai-error.log
```

### 8.2 Check Application Status
```bash
sudo supervisorctl status pramiti-ai-worker
```

### 8.3 Restart Application
```bash
sudo supervisorctl restart pramiti-ai-worker
```

---

## 🔄 Step 9: Deployment & Updates

### 9.1 Create Deployment Script
```bash
nano /home/pramiti/Pramiti_AI/deploy.sh
chmod +x /home/pramiti/Pramiti_AI/deploy.sh
```

**Add this content:**
```bash
#!/bin/bash

# Deployment script for Pramiti AI

set -e

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /home/pramiti/Pramiti_AI

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Restart application
echo "🔄 Restarting application..."
sudo supervisorctl restart pramiti-ai-worker

# Check status
echo "✅ Checking application status..."
sudo supervisorctl status pramiti-ai-worker

echo "🎉 Deployment completed successfully!"
```

### 9.2 Deploy Updates
```bash
cd /home/pramiti/Pramiti_AI
./deploy.sh
```

---

## 🔐 Step 10: Security Hardening

### 10.1 Setup Fail2Ban (Brute Force Protection)
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 10.2 Configure SSH Security
```bash
sudo nano /etc/ssh/sshd_config
```

Update:
```bash
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### 10.3 Enable Automatic Security Updates
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 📈 Step 11: Performance Optimization

### 11.1 Configure Uvicorn Workers
Edit supervisor config to match your CPU cores:
```bash
sudo nano /etc/supervisor/conf.d/pramiti-ai.conf
```

Update workers (use number of CPU cores):
```ini
command=/home/pramiti/Pramiti_AI/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8084 --workers 4
```

### 11.2 Enable Nginx Caching
```bash
sudo nano /etc/nginx/nginx.conf
```

Add in http block:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=pramiti_cache:10m max_size=100m inactive=60m use_temp_path=off;
```

### 11.3 Optimize PostgreSQL (if using)
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Adjust based on your RAM:
```conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
```

---

## 🧪 Step 12: Testing Deployment

### 12.1 Test API
```bash
curl http://YOUR_VPS_IP/health
curl http://YOUR_VPS_IP/api/v1/agents
```

### 12.2 Test WebSocket
Visit in browser:
```
http://YOUR_VPS_IP/enhanced-dashboard
```

### 12.3 Test SSL (after setup)
```bash
curl -I https://yourdomain.com
```

---

## 📋 Quick Reference Commands

### Application Management
```bash
# Start application
sudo supervisorctl start pramiti-ai-worker

# Stop application
sudo supervisorctl stop pramiti-ai-worker

# Restart application
sudo supervisorctl restart pramiti-ai-worker

# Check status
sudo supervisorctl status

# View logs
sudo tail -f /var/log/pramiti-ai/app.log
```

### Nginx Management
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### System Monitoring
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top

# Check running processes
ps aux | grep python
```

---

## 🆘 Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo tail -100 /var/log/pramiti-ai/app.log

# Check supervisor status
sudo supervisorctl status

# Restart supervisor
sudo systemctl restart supervisor
```

### 502 Bad Gateway Error
```bash
# Check if application is running
sudo supervisorctl status pramiti-ai-worker

# Check application is listening on port
sudo netstat -tulpn | grep 8084

# Restart application
sudo supervisorctl restart pramiti-ai-worker
```

### SSL Certificate Issues
```bash
# Test certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check Nginx configuration
sudo nginx -t
```

### High Memory Usage
```bash
# Check memory
free -h

# Restart application
sudo supervisorctl restart pramiti-ai-worker

# Reduce worker count if needed
sudo nano /etc/supervisor/conf.d/pramiti-ai.conf
```

---

## 🔄 Backup Strategy

### 12.1 Create Backup Script
```bash
nano /home/pramiti/backup.sh
chmod +x /home/pramiti/backup.sh
```

**Content:**
```bash
#!/bin/bash

BACKUP_DIR="/home/pramiti/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/pramiti-ai-$DATE.tar.gz /home/pramiti/Pramiti_AI

# Backup database (if using PostgreSQL)
# sudo -u postgres pg_dump pramiti_ai > $BACKUP_DIR/db-$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "pramiti-ai-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 12.2 Schedule Daily Backups
```bash
crontab -e
```

Add:
```bash
0 2 * * * /home/pramiti/backup.sh >> /var/log/pramiti-backup.log 2>&1
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Weekly**: Check logs for errors
- **Monthly**: Update system packages
- **Quarterly**: Review and optimize database
- **As needed**: Deploy application updates

### Monitoring Checklist
- [ ] Application responds on /health endpoint
- [ ] Dashboard accessible via browser
- [ ] SSL certificate valid and auto-renewing
- [ ] Disk space > 20% free
- [ ] Memory usage < 80%
- [ ] No critical errors in logs

---

## 🎯 Post-Deployment

Your application should now be accessible at:
- **HTTP**: http://YOUR_VPS_IP/enhanced-dashboard
- **HTTPS** (after SSL): https://yourdomain.com/enhanced-dashboard

### Default Access
- Main Dashboard: `/enhanced-dashboard`
- API Documentation: `/docs`
- Health Check: `/health`

---

**Deployment Version**: 1.0  
**Last Updated**: November 13, 2025  
**For Support**: Check logs and documentation
