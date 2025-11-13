# 🚀 Quick Deployment Reference - Contabo VPS

## One-Command Deployment Options

### Option 1: Traditional VPS Setup (Recommended)
```bash
# On your Contabo VPS, run:
git clone https://github.com/nicksriv/Pramiti_AI.git
cd Pramiti_AI
./deploy_vps.sh
```

### Option 2: Docker Deployment (Easier)
```bash
# On your Contabo VPS, run:
git clone https://github.com/nicksriv/Pramiti_AI.git
cd Pramiti_AI
./deploy_docker.sh
```

---

## 📝 Pre-Deployment Checklist

- [ ] Contabo VPS with Ubuntu 22.04/24.04 LTS
- [ ] SSH access to VPS (root or sudo user)
- [ ] OpenAI API key ready
- [ ] Domain name (optional but recommended)
- [ ] DNS A record pointing to VPS IP (if using domain)

---

## 🔑 Initial VPS Setup

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Create non-root user (if not exists)
adduser pramiti
usermod -aG sudo pramiti
su - pramiti

# Clone repository
git clone https://github.com/nicksriv/Pramiti_AI.git
cd Pramiti_AI
```

---

## ⚡ Quick Start Commands

### After Deployment - Edit Configuration
```bash
# Edit environment file
nano .env

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-actual-key-here

# Save and restart
sudo supervisorctl restart pramiti-ai-worker
# OR for Docker:
docker-compose restart pramiti-ai
```

### Check Status
```bash
# Traditional deployment
sudo supervisorctl status

# Docker deployment
docker-compose ps
```

### View Logs
```bash
# Traditional deployment
sudo tail -f /var/log/pramiti-ai/app.log

# Docker deployment
docker-compose logs -f pramiti-ai
```

### Access Application
```bash
# Get your VPS IP
curl ifconfig.me

# Then visit in browser:
http://YOUR_VPS_IP/enhanced-dashboard
```

---

## 🔒 Setup HTTPS (After Initial Deployment)

```bash
# Install Certbot (if not already installed)
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts and choose to redirect HTTP to HTTPS
```

---

## 🛠️ Common Management Commands

### Application Control
```bash
# Start
sudo supervisorctl start pramiti-ai-worker

# Stop
sudo supervisorctl stop pramiti-ai-worker

# Restart
sudo supervisorctl restart pramiti-ai-worker

# Status
sudo supervisorctl status
```

### Nginx Control
```bash
# Test configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx
```

### View Logs
```bash
# Application logs
sudo tail -f /var/log/pramiti-ai/app.log

# Nginx access logs
sudo tail -f /var/log/nginx/pramiti-ai-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/pramiti-ai-error.log
```

---

## 🔄 Update Application

```bash
cd /home/pramiti/Pramiti_AI
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart pramiti-ai-worker
```

---

## 🆘 Troubleshooting

### Application won't start
```bash
# Check logs
sudo tail -100 /var/log/pramiti-ai/app.log

# Check if port is in use
sudo netstat -tulpn | grep 8084

# Restart supervisor
sudo systemctl restart supervisor
```

### 502 Bad Gateway
```bash
# Check application status
sudo supervisorctl status pramiti-ai-worker

# Restart application
sudo supervisorctl restart pramiti-ai-worker

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Can't connect to application
```bash
# Check firewall
sudo ufw status

# Open ports if needed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## 📊 Monitoring

### Check System Resources
```bash
# Memory usage
free -h

# Disk space
df -h

# CPU usage
top

# Application processes
ps aux | grep python
```

### Health Check
```bash
# Check API health
curl http://localhost:8084/health

# Check if listening
sudo netstat -tulpn | grep 8084
```

---

## 🔐 Security Checklist

- [ ] Changed default passwords
- [ ] Disabled root SSH login
- [ ] Enabled UFW firewall
- [ ] SSL certificate installed
- [ ] Regular backups configured
- [ ] .env file permissions restricted (chmod 600)
- [ ] Fail2ban installed and configured

---

## 📁 Important File Locations

```
/home/pramiti/Pramiti_AI/          - Application directory
/home/pramiti/Pramiti_AI/.env      - Configuration file
/var/log/pramiti-ai/               - Application logs
/var/log/nginx/                    - Nginx logs
/etc/nginx/sites-available/        - Nginx configuration
/etc/supervisor/conf.d/            - Supervisor configuration
```

---

## 🎯 Access Points

After deployment, your application will be available at:

- **Main Dashboard**: `http://YOUR_IP/enhanced-dashboard`
- **API Docs**: `http://YOUR_IP/docs`
- **Health Check**: `http://YOUR_IP/health`
- **WebSocket**: `ws://YOUR_IP/ws`

With SSL:
- **Main Dashboard**: `https://yourdomain.com/enhanced-dashboard`
- **API Docs**: `https://yourdomain.com/docs`

---

## 📞 Support Resources

- **Full Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Architecture Diagram**: `ARCHITECTURE_DIAGRAM.md`
- **API Documentation**: `API_INTEGRATION_GUIDE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`

---

## 🔄 Backup Command

```bash
# Create backup
cd /home/pramiti
tar -czf pramiti-backup-$(date +%Y%m%d).tar.gz Pramiti_AI

# Restore from backup
tar -xzf pramiti-backup-YYYYMMDD.tar.gz
```

---

**Last Updated**: November 13, 2025  
**Version**: 1.0
