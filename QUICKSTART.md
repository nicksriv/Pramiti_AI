# 🚀 Quick Start Guide - Deploy to Contabo

## Option 1: Automated Deployment (Recommended)

**One-command deployment on fresh Ubuntu server:**

```bash
# SSH into your Contabo server
ssh root@your-server-ip

# Download and run the deployment script
curl -sSL https://raw.githubusercontent.com/nicksriv/Pramiti_AI/main/deploy_contabo.sh | bash
```

The script will ask you for:
- OpenAI API Key
- Domain name (optional)
- Admin email
- Admin password

**That's it!** The script handles everything:
- ✅ System updates
- ✅ Python 3.11 installation
- ✅ Dependencies
- ✅ Repository clone
- ✅ Virtual environment
- ✅ Nginx configuration
- ✅ SSL certificate (if domain provided)
- ✅ Firewall setup
- ✅ Admin user creation
- ✅ Automated backups
- ✅ Service monitoring

**Access your application:**
- With domain: `https://your-domain.com`
- Without domain: `http://your-server-ip`

---

## Option 2: Manual Deployment

Follow the detailed guide: [CONTABO_DEPLOYMENT.md](./CONTABO_DEPLOYMENT.md)

---

## After Deployment

### 1. First Login
- Navigate to your application URL
- Log in with admin credentials
- **Change your password immediately!**

### 2. Test Features

**Organization Assistant:**
- As Admin: Ask "How do I set up Microsoft Teams?"
- As User: Ask "What can you help me with?"

**Self-Learning Agent:**
- Log in first (required for tenant isolation)
- As Admin: Ask "How do I configure OAuth?"
- As User: Ask "How do I create a ticket?"

### 3. Configure OAuth (Optional)

If you want Microsoft/Google integrations:

**Microsoft:**
1. Go to Azure Portal: https://portal.azure.com
2. Create App Registration
3. Get Client ID, Client Secret, Tenant ID
4. Update `.env` on server:
   ```bash
   ssh root@your-server-ip
   nano /home/pramiti/Pramiti_AI/.env
   ```
5. Add:
   ```
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_secret
   MICROSOFT_TENANT_ID=your_tenant_id
   ```
6. Restart: `supervisorctl restart pramiti`

**Google:**
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Update `.env` with `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
4. Restart service

### 4. Create Additional Users

```bash
ssh root@your-server-ip
su - pramiti
cd Pramiti_AI
source venv/bin/activate

python3 << EOF
from core.session_manager import SessionManager
sm = SessionManager()

# Create organization admin
sm.create_user(
    user_id="admin@yourcompany.com",
    password="SecurePassword123!",
    org_id="yourcompany",
    role="ADMIN"
)

# Create regular user
sm.create_user(
    user_id="user@yourcompany.com",
    password="UserPassword123!",
    org_id="yourcompany",
    role="USER"
)
EOF
```

---

## Maintenance Commands

### Service Management
```bash
# Check status
supervisorctl status pramiti

# Restart service
supervisorctl restart pramiti

# View logs
tail -f /home/pramiti/Pramiti_AI/logs/access.log
tail -f /home/pramiti/Pramiti_AI/logs/error.log
```

### Updates
```bash
# SSH to server
ssh root@your-server-ip

# Pull latest code
su - pramiti
cd Pramiti_AI
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Restart
exit
supervisorctl restart pramiti
```

### Backups
```bash
# Manual backup
/home/pramiti/backup.sh

# View backups
ls -lh /home/pramiti/backups/

# Restore from backup
tar -xzf /home/pramiti/backups/pramiti_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

### SSL Renewal (Automatic)
```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:8084/health
```

### System Resources
```bash
# Memory usage
free -h

# Disk usage
df -h

# CPU and processes
htop
```

### Application Metrics
- API Docs: `https://your-domain.com/docs`
- Admin Dashboard: `https://your-domain.com`

---

## Troubleshooting

### Service won't start
```bash
# Check logs
tail -50 /home/pramiti/Pramiti_AI/logs/error.log

# Check supervisor
supervisorctl status pramiti

# Restart
supervisorctl restart pramiti
```

### Database errors
```bash
# Check permissions
ls -la /home/pramiti/Pramiti_AI/data/rag/chroma

# Fix permissions
chown -R pramiti:pramiti /home/pramiti/Pramiti_AI/data
```

### High memory usage
```bash
# Check processes
ps aux | grep gunicorn

# Reduce workers in /etc/supervisor/conf.d/pramiti.conf
# Change: -w 4 to -w 2
supervisorctl restart pramiti
```

### 502 Bad Gateway
```bash
# Check if application is running
supervisorctl status pramiti

# Check if port is listening
netstat -tlnp | grep 8084

# Restart both services
supervisorctl restart pramiti
systemctl restart nginx
```

---

## Security Checklist

- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall enabled (UFW)
- [ ] SSH key authentication enabled
- [ ] Default admin password changed
- [ ] Fail2ban installed (optional but recommended)
- [ ] Regular backups configured
- [ ] OpenAI API key secured in .env
- [ ] Secrets directory has 700 permissions
- [ ] Regular security updates enabled

---

## Performance Tuning

### For High Traffic
1. Increase Gunicorn workers:
   ```bash
   nano /etc/supervisor/conf.d/pramiti.conf
   # Change: -w 4 to -w 8 (based on CPU cores)
   ```

2. Enable Nginx caching:
   ```nginx
   # Add to /etc/nginx/sites-available/pramiti
   proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
   ```

3. Add Redis for session caching (see CONTABO_DEPLOYMENT.md)

### For Low Memory Servers
1. Reduce workers: `-w 2`
2. Lower timeout: `--timeout 120`
3. Enable swap space

---

## Next Steps

1. ✅ Deploy to Contabo
2. ✅ Test admin and user workflows
3. ✅ Configure OAuth (if needed)
4. ✅ Create user accounts
5. ✅ Set up monitoring
6. ✅ Configure backups
7. ✅ Add custom domain
8. ✅ Enable SSL
9. ✅ Train team on usage

---

## Support & Documentation

- **Deployment Guide**: [CONTABO_DEPLOYMENT.md](./CONTABO_DEPLOYMENT.md)
- **Role-Based Routing**: [ROLE_BASED_ROUTING.md](./ROLE_BASED_ROUTING.md)
- **Multi-Tenant Security**: [TENANT_ISOLATION.md](./TENANT_ISOLATION.md)
- **System Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Documentation**: `https://your-domain.com/docs`
- **GitHub Issues**: https://github.com/nicksriv/Pramiti_AI/issues

---

## Production Ready! 🎉

Your Pramiti AI system is now:
- ✅ Deployed on Contabo
- ✅ Secured with SSL
- ✅ Role-aware (Admin vs User)
- ✅ Multi-tenant isolated
- ✅ Self-learning with RAG
- ✅ Backed up automatically
- ✅ Monitored and maintained

**Access URL**: `https://your-domain.com`  
**Admin Login**: Use credentials you created during deployment

Enjoy your intelligent, role-aware, multi-tenant AI assistant! 🚀
