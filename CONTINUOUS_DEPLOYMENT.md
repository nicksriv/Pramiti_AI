# Continuous Deployment Workflow for Pramiti AI

This guide covers the complete workflow for deploying and continuously updating your Pramiti AI platform on Contabo VPS using Docker.

## 🚀 Quick Start

### Initial Deployment (One-Time Setup)

```bash
# Run the interactive deployment script
./deploy_interactive.sh
```

**What it does:**
- ✅ Tests SSH connection to your VPS
- ✅ Collects OpenAI API key and domain info
- ✅ Installs Docker and Docker Compose on VPS
- ✅ Clones the repository
- ✅ Configures environment variables
- ✅ Sets up firewall rules
- ✅ Builds and starts all services
- ✅ Verifies deployment health

**Time Required:** 10-15 minutes

---

## 🔄 Continuous Updates

### Making Changes and Deploying

```bash
# 1. Make your changes locally in VS Code
# 2. Run the update script
./update_deployment.sh
```

**What it does:**
- ✅ Commits your local changes
- ✅ Pushes to GitHub
- ✅ Pulls changes on VPS
- ✅ Rebuilds Docker images
- ✅ Restarts services with zero downtime
- ✅ Verifies health

**Time Required:** 2-3 minutes

---

## 📋 Development Workflow

### Recommended Workflow

```bash
# 1. Work on your local machine
code .  # Open VS Code

# 2. Test locally
python3 api_server.py
# Visit http://localhost:8084/enhanced-dashboard

# 3. When ready, deploy updates
./update_deployment.sh
```

### Git Workflow

```bash
# Create a feature branch (optional)
git checkout -b feature/new-enhancement

# Make changes...

# Commit changes
git add .
git commit -m "Add new enhancement"

# Deploy to production
git checkout main
git merge feature/new-enhancement
./update_deployment.sh
```

---

## 🐳 Docker Architecture

### Services Running on VPS

| Service | Port | Purpose |
|---------|------|---------|
| **pramiti-ai** | 8084 | Main application (FastAPI) |
| **postgres** | 5432 | Database (PostgreSQL 15) |
| **redis** | 6379 | Cache & session storage |
| **nginx** | 80, 443 | Reverse proxy & SSL |

### Container Health Checks

```bash
# Check all services
ssh user@vps-ip 'cd Pramiti_AI && docker-compose ps'

# Check specific service
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs pramiti-ai'
```

---

## 🛠️ Management Commands

### On Your Local Machine

```bash
# Deploy initial setup
./deploy_interactive.sh

# Push updates
./update_deployment.sh

# Quick commit and push
git add . && git commit -m "Update" && git push origin main
```

### On Your VPS (via SSH)

```bash
# SSH into VPS
ssh user@vps-ip
cd Pramiti_AI

# View all services
docker-compose ps

# View logs (live)
docker-compose logs -f pramiti-ai

# View logs (last 100 lines)
docker-compose logs --tail=100 pramiti-ai

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart pramiti-ai

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Rebuild and restart
docker-compose up -d --build

# View resource usage
docker stats

# Clean up old images
docker system prune -a
```

---

## 📊 Monitoring & Logs

### Application Logs

```bash
# Real-time logs
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs -f pramiti-ai'

# Last 50 lines
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs --tail=50 pramiti-ai'

# Search logs
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs pramiti-ai | grep ERROR'
```

### Database Logs

```bash
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs postgres'
```

### Nginx Logs

```bash
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs nginx'
```

### System Resources

```bash
# Container stats
ssh user@vps-ip 'docker stats --no-stream'

# Disk usage
ssh user@vps-ip 'df -h'

# Memory usage
ssh user@vps-ip 'free -h'
```

---

## 🔧 Configuration Updates

### Update Environment Variables

```bash
# SSH into VPS
ssh user@vps-ip
cd Pramiti_AI

# Edit .env file
nano .env

# Restart to apply changes
docker-compose restart
```

### Update OpenAI API Key

```bash
# On VPS
cd Pramiti_AI
sed -i 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=sk-your-new-key/' .env
docker-compose restart pramiti-ai
```

### Add New Environment Variables

```bash
# On VPS
cd Pramiti_AI
echo "NEW_VARIABLE=value" >> .env
docker-compose restart
```

---

## 🗄️ Database Management

### Backup Database

```bash
# On VPS
cd Pramiti_AI
docker-compose exec postgres pg_dump -U pramiti_user pramiti_ai > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# On VPS
cd Pramiti_AI
cat backup_20241113.sql | docker-compose exec -T postgres psql -U pramiti_user pramiti_ai
```

### Access Database Console

```bash
# On VPS
cd Pramiti_AI
docker-compose exec postgres psql -U pramiti_user pramiti_ai
```

---

## 🔒 SSL Setup (Optional)

### Using Let's Encrypt

```bash
# On VPS
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

### Manual Certificate

```bash
# Place certificates in ssl/ directory
cd Pramiti_AI
mkdir -p ssl
# Copy your cert.pem and key.pem to ssl/
# Update docker-compose.yml nginx volumes
docker-compose restart nginx
```

---

## 🚨 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs pramiti-ai

# Check all services
docker-compose ps

# Rebuild completely
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Health Check Failing

```bash
# Test manually
curl http://localhost:8084/health

# Check application logs
docker-compose logs --tail=100 pramiti-ai

# Restart service
docker-compose restart pramiti-ai
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a --volumes

# Check disk usage
df -h
du -sh /var/lib/docker
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/Pramiti_AI

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Port Already in Use

```bash
# Find process using port 8084
sudo lsof -i :8084

# Kill process
sudo kill -9 <PID>

# Or stop conflicting container
docker-compose down
```

---

## 🎯 Best Practices

### Development

1. **Test Locally First**
   ```bash
   python3 api_server.py
   # Test at http://localhost:8084
   ```

2. **Use Feature Branches**
   ```bash
   git checkout -b feature/my-enhancement
   # Make changes...
   git checkout main
   git merge feature/my-enhancement
   ```

3. **Commit Often**
   ```bash
   git add .
   git commit -m "Clear, descriptive message"
   ```

### Deployment

1. **Deploy During Low Traffic**
   - Early morning or late night

2. **Monitor After Deployment**
   ```bash
   docker-compose logs -f pramiti-ai
   ```

3. **Keep Backups**
   ```bash
   # Weekly database backup
   docker-compose exec postgres pg_dump -U pramiti_user pramiti_ai > backup_$(date +%Y%m%d).sql
   ```

4. **Update Dependencies Regularly**
   ```bash
   # On local machine
   pip install --upgrade -r requirements.txt
   pip freeze > requirements.txt
   ./update_deployment.sh
   ```

### Security

1. **Rotate Secrets Regularly**
   ```bash
   # Generate new secret
   openssl rand -hex 32
   # Update .env on VPS
   ```

2. **Keep Docker Updated**
   ```bash
   sudo apt update
   sudo apt upgrade docker-ce docker-ce-cli containerd.io
   ```

3. **Monitor Logs for Anomalies**
   ```bash
   docker-compose logs pramiti-ai | grep -i error
   ```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# In docker-compose.yml
services:
  pramiti-ai:
    deploy:
      replicas: 3
    # Load balancer will be needed
```

### Vertical Scaling

```yaml
# Increase resources in docker-compose.yml
services:
  pramiti-ai:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 🔗 Quick Reference

### Essential URLs

- **Dashboard:** `http://your-vps-ip/enhanced-dashboard`
- **API Docs:** `http://your-vps-ip/docs`
- **Health Check:** `http://your-vps-ip/health`
- **GitHub Repo:** `https://github.com/nicksriv/Pramiti_AI`

### One-Line Commands

```bash
# Deploy updates from local
./update_deployment.sh

# View live logs
ssh user@vps-ip 'cd Pramiti_AI && docker-compose logs -f'

# Restart services
ssh user@vps-ip 'cd Pramiti_AI && docker-compose restart'

# Check health
ssh user@vps-ip 'curl http://localhost:8084/health'

# Backup database
ssh user@vps-ip 'cd Pramiti_AI && docker-compose exec postgres pg_dump -U pramiti_user pramiti_ai > backup.sql'
```

---

## 📞 Support

### Common Issues

1. **Can't access dashboard**
   - Check firewall: `sudo ufw status`
   - Check services: `docker-compose ps`
   - Check logs: `docker-compose logs nginx`

2. **OpenAI errors**
   - Verify API key in `.env`
   - Check API quota on OpenAI dashboard
   - View logs: `docker-compose logs pramiti-ai | grep OpenAI`

3. **Database connection errors**
   - Check postgres: `docker-compose ps postgres`
   - Check connection: `docker-compose exec postgres pg_isready`
   - Restart: `docker-compose restart postgres pramiti-ai`

---

## 🎉 Summary

**Initial Deployment:**
```bash
./deploy_interactive.sh
```

**Continuous Updates:**
```bash
./update_deployment.sh
```

**That's it!** Your deployment workflow is now fully automated. Make changes locally, run the update script, and your changes are live in minutes! 🚀
