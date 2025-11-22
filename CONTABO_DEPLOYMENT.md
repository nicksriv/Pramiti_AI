# Contabo Deployment Guide for Pramiti AI

## Prerequisites

- Contabo VPS/Cloud Server (Ubuntu 20.04 or 22.04 recommended)
- Root or sudo access
- Domain name (optional, for production setup)
- OpenAI API key

## Server Specifications Recommendation

**Minimum Requirements:**
- 2 vCPU cores
- 4 GB RAM
- 50 GB SSD storage
- Ubuntu 22.04 LTS

**Recommended for Production:**
- 4 vCPU cores
- 8 GB RAM
- 100 GB SSD storage
- Ubuntu 22.04 LTS

## Deployment Steps

### 1. Connect to Your Contabo Server

```bash
ssh root@your-server-ip
```

### 2. Update System Packages

```bash
apt update && apt upgrade -y
```

### 3. Install Required Dependencies

```bash
# Install Python 3.11
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev

# Install other dependencies
apt install -y git nginx supervisor curl build-essential

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### 4. Create Application User

```bash
# Create a dedicated user for the application
useradd -m -s /bin/bash pramiti
usermod -aG sudo pramiti

# Switch to the pramiti user
su - pramiti
```

### 5. Clone Repository

```bash
cd /home/pramiti
git clone https://github.com/nicksriv/Pramiti_AI.git
cd Pramiti_AI
```

### 6. Set Up Python Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 7. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install chromadb  # For RAG knowledge base
pip install gunicorn  # Production WSGI server
```

### 8. Configure Environment Variables

```bash
# Create .env file
cp .env.example .env  # If you have an example file, otherwise:
nano .env
```

Add the following to `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
PORT=8084
HOST=0.0.0.0

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
JWT_SECRET_KEY=your-jwt-secret-here-generate-with-openssl-rand-hex-32

# Database paths
CHROMA_PERSIST_DIRECTORY=/home/pramiti/Pramiti_AI/data/rag/chroma
CONVERSATIONS_DIR=/home/pramiti/Pramiti_AI/data/rag/conversations

# Optional: OAuth Configuration (configure later)
# MICROSOFT_CLIENT_ID=
# MICROSOFT_CLIENT_SECRET=
# MICROSOFT_TENANT_ID=common
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
```

Generate secure keys:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

### 9. Create Required Directories

```bash
mkdir -p data/rag/chroma
mkdir -p data/rag/conversations
mkdir -p secrets
mkdir -p logs
chmod 700 secrets
```

### 10. Set Up Supervisor (Process Manager)

Exit from pramiti user and switch back to root:
```bash
exit  # Return to root
```

Create supervisor configuration:
```bash
nano /etc/supervisor/conf.d/pramiti.conf
```

Add the following configuration:

```ini
[program:pramiti]
directory=/home/pramiti/Pramiti_AI
command=/home/pramiti/Pramiti_AI/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8084 --timeout 300
user=pramiti
autostart=true
autorestart=true
stderr_logfile=/home/pramiti/Pramiti_AI/logs/error.log
stdout_logfile=/home/pramiti/Pramiti_AI/logs/access.log
environment=PATH="/home/pramiti/Pramiti_AI/venv/bin"
```

Enable and start supervisor:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start pramiti
```

Check status:
```bash
supervisorctl status pramiti
```

### 11. Configure Nginx (Reverse Proxy)

```bash
nano /etc/nginx/sites-available/pramiti
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or server IP

    # Increase client body size for file uploads
    client_max_body_size 50M;

    # Frontend static files
    location / {
        root /home/pramiti/Pramiti_AI/web;
        try_files $uri $uri/ /enhanced-dashboard.html;
        index enhanced-dashboard.html;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # User chat endpoint
    location /user-chat {
        proxy_pass http://127.0.0.1:8084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8084;
        access_log off;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/pramiti /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

### 12. Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

### 13. Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

Follow the prompts to configure SSL. Certbot will automatically update your Nginx configuration.

### 14. Create Default Admin User

```bash
su - pramiti
cd Pramiti_AI
source venv/bin/activate

# Create a Python script to add admin user
python3 << EOF
from core.session_manager import SessionManager

sm = SessionManager()

# Create super admin
sm.create_user(
    user_id="admin@pramiti.ai",
    password="ChangeThisPassword123!",
    org_id="pramiti",
    role="SUPER_ADMIN"
)

print("✅ Super admin created: admin@pramiti.ai")
print("⚠️  IMPORTANT: Change the password after first login!")
EOF
```

### 15. Test the Deployment

```bash
# Check if service is running
supervisorctl status pramiti

# Check logs
tail -f /home/pramiti/Pramiti_AI/logs/access.log
tail -f /home/pramiti/Pramiti_AI/logs/error.log

# Test API endpoint
curl http://localhost:8084/health
```

Access the application:
- If using domain: `http://your-domain.com`
- If using IP: `http://your-server-ip`

## Post-Deployment Configuration

### 1. Update OAuth Redirect URIs

If using OAuth integrations, update redirect URIs in your OAuth apps:
- Microsoft: `https://your-domain.com/api/v1/oauth/callback/microsoft`
- Google: `https://your-domain.com/api/v1/oauth/callback/google`

### 2. Set Up Monitoring

```bash
# Install monitoring tools
apt install -y htop iotop nethogs

# Set up log rotation
nano /etc/logrotate.d/pramiti
```

Add:
```
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
```

### 3. Set Up Automated Backups

```bash
# Create backup script
nano /home/pramiti/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/pramiti/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database and configurations
tar -czf $BACKUP_DIR/pramiti_backup_$DATE.tar.gz \
    /home/pramiti/Pramiti_AI/data \
    /home/pramiti/Pramiti_AI/.env \
    /home/pramiti/Pramiti_AI/config

# Keep only last 7 days of backups
find $BACKUP_DIR -name "pramiti_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/pramiti_backup_$DATE.tar.gz"
```

Make executable and add to cron:
```bash
chmod +x /home/pramiti/backup.sh
crontab -e -u pramiti
```

Add:
```
0 2 * * * /home/pramiti/backup.sh >> /home/pramiti/backups/backup.log 2>&1
```

## Updating the Application

```bash
su - pramiti
cd Pramiti_AI
source venv/bin/activate

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart application
exit  # Back to root
supervisorctl restart pramiti
```

## Troubleshooting

### Application won't start
```bash
# Check logs
tail -f /home/pramiti/Pramiti_AI/logs/error.log

# Check supervisor status
supervisorctl status pramiti

# Restart supervisor
supervisorctl restart pramiti
```

### Database connection issues
```bash
# Check ChromaDB directory permissions
ls -la /home/pramiti/Pramiti_AI/data/rag/chroma
chown -R pramiti:pramiti /home/pramiti/Pramiti_AI/data
```

### High memory usage
```bash
# Check memory usage
free -h
htop

# Reduce number of Gunicorn workers in supervisor config
# Edit: /etc/supervisor/conf.d/pramiti.conf
# Change: -w 4 to -w 2
supervisorctl restart pramiti
```

### SSL certificate renewal
```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

## Security Hardening

### 1. Disable Password Authentication (Use SSH Keys Only)

```bash
nano /etc/ssh/sshd_config
```

Set:
```
PasswordAuthentication no
PermitRootLogin no
```

Restart SSH:
```bash
systemctl restart sshd
```

### 2. Install Fail2Ban

```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Set Up Automatic Security Updates

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 4. Regular Security Audits

```bash
# Check open ports
ss -tulpn

# Check running processes
ps aux | grep python

# Check disk usage
df -h

# Check system logs
journalctl -xe
```

## Performance Optimization

### 1. Enable Redis Caching (Optional)

```bash
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server
```

Add to `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

### 2. Database Optimization

For high-volume deployments, consider:
- Moving ChromaDB to SSD storage
- Increasing ChromaDB cache size
- Using PostgreSQL for session management

## Monitoring Dashboard

Access system metrics:
- Supervisor: `http://your-domain.com:9001` (if enabled)
- Server stats: `htop` (command line)
- Nginx stats: Check `/var/log/nginx/access.log`

## Support

For issues:
1. Check logs: `/home/pramiti/Pramiti_AI/logs/`
2. Review GitHub issues: https://github.com/nicksriv/Pramiti_AI/issues
3. Check API docs: `http://your-domain.com/docs`

## Production Checklist

- [ ] Server hardened (firewall, SSH keys, fail2ban)
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Environment variables configured (.env file)
- [ ] Database directories created with correct permissions
- [ ] Supervisor configured and service running
- [ ] Nginx configured as reverse proxy
- [ ] Default admin user created and password changed
- [ ] Automated backups configured
- [ ] Log rotation configured
- [ ] Monitoring set up
- [ ] OAuth redirect URIs updated (if using OAuth)
- [ ] OpenAI API key configured and tested
- [ ] Domain DNS pointed to server IP
- [ ] Health check endpoint accessible
- [ ] Test both chat interfaces (Organization Assistant, Self-Learning Agent)
- [ ] Verify role-based routing working correctly

## Quick Commands Reference

```bash
# Start/Stop/Restart application
supervisorctl start pramiti
supervisorctl stop pramiti
supervisorctl restart pramiti

# View logs in real-time
tail -f /home/pramiti/Pramiti_AI/logs/access.log
tail -f /home/pramiti/Pramiti_AI/logs/error.log

# Check nginx status
systemctl status nginx
nginx -t  # Test configuration

# Pull updates
cd /home/pramiti/Pramiti_AI && git pull origin main

# Restart everything
supervisorctl restart pramiti && systemctl restart nginx

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux | grep gunicorn
```

---

**Your application is now deployed on Contabo! 🚀**

Access it at: `http://your-server-ip` or `https://your-domain.com`

Login with:
- Username: `admin@pramiti.ai`
- Password: (the one you set during admin user creation)

**Remember to change the default password immediately after first login!**
