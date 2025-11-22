# Enterprise Security Configuration Guide
**Production Deployment Checklist for Pramiti AI**

## 🎯 Overview

This guide provides step-by-step instructions for deploying Pramiti AI with enterprise-grade security suitable for large organizations. Follow ALL steps before production deployment.

---

## 📋 Pre-Deployment Checklist

### ✅ Phase 1: Infrastructure Security (CRITICAL)

#### 1.1 Secrets Management Setup

**Choose ONE secrets backend:**

**Option A: AWS Secrets Manager** (Recommended for AWS deployments)
```bash
# Install AWS CLI
pip install awscli boto3

# Configure AWS credentials
aws configure

# Create secrets
aws secretsmanager create-secret \
    --name pramiti-ai/production/jwt-secret \
    --secret-string "$(openssl rand -base64 64)"

aws secretsmanager create-secret \
    --name pramiti-ai/production/encryption-master-key \
    --secret-string "$(openssl rand -base64 64)"

# Set environment variables
export SECRETS_BACKEND=aws
export AWS_REGION=us-east-1
```

**Option B: HashiCorp Vault** (Recommended for on-premises)
```bash
# Install Vault
brew install vault  # macOS
# OR
sudo apt-get install vault  # Linux

# Start Vault server
vault server -dev  # Development
# For production: https://learn.hashicorp.com/vault/getting-started/deploy

# Set environment variables
export SECRETS_BACKEND=vault
export VAULT_ADDR=https://vault.yourcompany.com
export VAULT_TOKEN=your-vault-token

# Create secrets
vault kv put secret/pramiti-ai/jwt-secret value="$(openssl rand -base64 64)"
vault kv put secret/pramiti-ai/encryption-key value="$(openssl rand -base64 64)"
```

**Option C: Azure Key Vault** (Recommended for Azure deployments)
```bash
# Install Azure CLI
pip install azure-cli azure-keyvault-secrets azure-identity

# Login to Azure
az login

# Create Key Vault
az keyvault create \
    --name pramiti-ai-vault \
    --resource-group your-resource-group \
    --location eastus

# Add secrets
az keyvault secret set \
    --vault-name pramiti-ai-vault \
    --name jwt-secret-key \
    --value "$(openssl rand -base64 64)"

# Set environment variables
export SECRETS_BACKEND=azure
export AZURE_VAULT_URL=https://pramiti-ai-vault.vault.azure.net/
```

#### 1.2 Database Security

**PostgreSQL with SSL**
```bash
# Enable SSL in postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/root.crt'

# Create encrypted user
CREATE USER pramiti_user WITH ENCRYPTED PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE pramiti_ai TO pramiti_user;

# Connection string with SSL
export DATABASE_URL="postgresql://pramiti_user:password@localhost/pramiti_ai?sslmode=verify-full"
```

**MongoDB with Authentication**
```bash
# Enable auth in mongod.conf
security:
  authorization: enabled

# Create admin user
use admin
db.createUser({
  user: "pramiti_admin",
  pwd: "strong-password-here",
  roles: [{role: "readWriteAnyDatabase", db: "admin"}]
})

# Connection string
export MONGO_URI="mongodb://pramiti_admin:password@localhost:27017/pramiti_ai?authSource=admin&ssl=true"
```

#### 1.3 TLS/SSL Certificate Setup

**Option A: Let's Encrypt (Free)**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourcompany.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Option B: Commercial Certificate**
```bash
# Generate CSR
openssl req -new -newkey rsa:4096 -nodes \
    -keyout yourcompany.key -out yourcompany.csr

# Submit CSR to certificate authority (DigiCert, Sectigo, etc.)
# Download signed certificate and intermediate certificates

# Install certificate in nginx/apache/load balancer
```

### ✅ Phase 2: Application Security Configuration

#### 2.1 Environment Variables

Create `.env.production` (NEVER commit to git):

```bash
# ==================== ENVIRONMENT ====================
ENVIRONMENT=production
DEBUG=false

# ==================== SECRETS BACKEND ====================
SECRETS_BACKEND=aws  # or vault, azure, local
AWS_REGION=us-east-1
# VAULT_ADDR=https://vault.yourcompany.com
# VAULT_TOKEN=xxx
# AZURE_VAULT_URL=https://your-vault.vault.azure.net/

# ==================== MASTER ENCRYPTION ====================
# CRITICAL: Set unique password for production
MASTER_ENCRYPTION_PASSWORD=your-super-secure-64-char-password-here-change-this

# ==================== DATABASE ====================
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=verify-full
MONGO_URI=mongodb://user:pass@host:27017/db?authSource=admin&ssl=true
REDIS_URL=rediss://user:pass@host:6379/0  # Note: rediss with SSL

# ==================== API KEYS (stored in secrets manager) ====================
# These should NOT be in .env - use secrets manager
# OPENAI_API_KEY will be retrieved from secrets manager

# ==================== SECURITY ====================
ENABLE_SIEM=true
SECURITY_LOG_DIR=/var/log/pramiti-ai/security
AUDIT_LOG_SALT=your-unique-salt-for-audit-logs

# ==================== RATE LIMITING ====================
RATE_LIMIT_ENABLED=true
REDIS_RATE_LIMIT_URL=rediss://host:6379/1

# ==================== CORS ====================
ALLOWED_ORIGINS=https://app.yourcompany.com,https://admin.yourcompany.com
# NEVER use * in production!

# ==================== SESSION ====================
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict

# ==================== MONITORING ====================
SENTRY_DSN=https://xxx@sentry.io/xxx
PROMETHEUS_ENABLED=true

# ==================== BACKUP ====================
BACKUP_ENCRYPTION_KEY=your-backup-encryption-key
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
```

#### 2.2 Install Security Dependencies

```bash
# Install all security packages
pip install -r requirements-security.txt

# Verify installation
python -c "import bcrypt, jwt, cryptography; print('✅ Security packages installed')"

# Run security checks
safety check --full-report
bandit -r core/ api/ -f json -o security-report.json
```

#### 2.3 Initialize Secrets

```bash
# Run initialization script
python scripts/init_production_secrets.py

# This will:
# 1. Generate JWT secret key
# 2. Generate encryption keys
# 3. Store in chosen secrets backend
# 4. Create encrypted directories
```

### ✅ Phase 3: Network Security

#### 3.1 Firewall Configuration

**AWS Security Groups**
```bash
# API Server (port 8084)
Inbound: TCP 443 from Load Balancer Security Group
Outbound: TCP 443 to 0.0.0.0/0 (HTTPS only)

# Database (PostgreSQL - port 5432)
Inbound: TCP 5432 from API Server Security Group ONLY
Outbound: None

# Redis (port 6379)
Inbound: TCP 6379 from API Server Security Group ONLY
Outbound: None
```

**Linux iptables**
```bash
# Allow HTTPS only
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8084 -j DROP  # Block direct access
sudo iptables -A INPUT -j DROP  # Drop all other traffic

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### 3.2 Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/pramiti-ai`:

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

upstream pramiti_backend {
    server 127.0.0.1:8084 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourcompany.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Hide nginx version
    server_tokens off;

    # Request size limits
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # Logging
    access_log /var/log/nginx/pramiti-access.log;
    error_log /var/log/nginx/pramiti-error.log warn;

    # Rate limiting for login endpoint
    location /api/v1/auth/login {
        limit_req zone=login_limit burst=10 nodelay;
        proxy_pass http://pramiti_backend;
        include proxy_params;
    }

    # Rate limiting for API endpoints
    location /api/ {
        limit_req zone=api_limit burst=200 nodelay;
        proxy_pass http://pramiti_backend;
        include proxy_params;

        # Additional proxy headers
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }

    # Static files (if serving frontend)
    location /static/ {
        alias /var/www/pramiti-ai/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourcompany.com;
    return 301 https://$server_name$request_uri;
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/pramiti-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### ✅ Phase 4: Application Hardening

#### 4.1 Update api_server.py

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

# Use secure imports
from core.session_manager_secure import session_manager
from core.connector_manager_secure import secure_connector_manager
from core.security_audit import security_audit, SecurityEventType

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Pramiti AI API",
    version="1.0.0",
    docs_url=None if os.getenv('ENVIRONMENT') == 'production' else "/docs",  # Disable in prod
    redoc_url=None if os.getenv('ENVIRONMENT') == 'production' else "/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Trusted hosts (prevent host header injection)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv('ALLOWED_HOSTS', 'api.yourcompany.com').split(',')
)

# CORS - restrictive in production
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if os.getenv('ENVIRONMENT') == 'production' and not allowed_origins:
    raise ValueError("ALLOWED_ORIGINS must be set in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Total-Count"],
    max_age=3600
)

# Health check (no auth required)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": os.getenv('ENVIRONMENT', 'unknown')}

# Secured login endpoint with rate limiting
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    # Get client IP
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent')
    
    # Authenticate
    user = session_manager.authenticate_user(
        credentials.user_id,
        credentials.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create tokens
    access_token = session_manager.create_token(
        user['user_id'],
        user['org_id'],
        user['role'],
        token_type='access'
    )
    
    refresh_token = session_manager.create_token(
        user['user_id'],
        user['org_id'],
        user['role'],
        token_type='refresh'
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }
```

### ✅ Phase 5: Monitoring & Alerting

#### 5.1 Sentry Integration (Error Tracking)

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Add to api_server.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if os.getenv('ENVIRONMENT') == 'production':
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('ENVIRONMENT'),
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,
        integrations=[FastApiIntegration()]
    )
```

#### 5.2 Security Monitoring Dashboard

**Splunk/ELK Integration:**
```python
# In core/security_audit.py, update _send_to_siem():
import requests

def _send_to_siem(self, event_data: Dict):
    """Send to Splunk HEC"""
    splunk_url = os.getenv('SPLUNK_HEC_URL')
    splunk_token = os.getenv('SPLUNK_HEC_TOKEN')
    
    if splunk_url and splunk_token:
        requests.post(
            f"{splunk_url}/services/collector/event",
            headers={'Authorization': f'Splunk {splunk_token}'},
            json={"event": event_data},
            verify=True
        )
```

#### 5.3 Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
login_attempts = Counter('login_attempts_total', 'Total login attempts', ['status'])
api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
response_time = Histogram('response_time_seconds', 'Response time in seconds')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### ✅ Phase 6: Compliance & Auditing

#### 6.1 Enable Comprehensive Audit Logging

All security events are automatically logged. To query:

```python
from core.security_audit import security_audit, SecurityEventType
from datetime import datetime, timedelta

# Query failed logins in last 24 hours
events = security_audit.query_events(
    start_date=datetime.utcnow() - timedelta(days=1),
    event_types=[SecurityEventType.LOGIN_FAILED],
    severity="WARNING"
)

# Export for compliance reporting
import json
with open('security_audit_report.json', 'w') as f:
    json.dump(events, f, indent=2)
```

#### 6.2 GDPR Compliance

```python
# Add data deletion endpoint
@app.delete("/api/v1/users/{user_id}/data")
async def delete_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """GDPR Right to Erasure (Article 17)"""
    # Verify user can delete this data
    session_manager.require_super_admin(current_user)
    
    # Delete user data
    # - Remove from users database
    # - Delete connector tokens
    # - Anonymize logs
    # - Remove from backups
    
    security_audit.log_event(
        SecurityEventType.DATA_DELETED,
        user_id=current_user['user_id'],
        details={"deleted_user": user_id, "reason": "GDPR request"},
        severity="WARNING"
    )
    
    return {"status": "deleted"}
```

### ✅ Phase 7: Penetration Testing

Before production, run:

```bash
# 1. OWASP ZAP (Web Application Security Scanner)
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://api.yourcompany.com

# 2. SQLMap (SQL Injection Testing)
sqlmap -u "https://api.yourcompany.com/api/v1/endpoint" --batch

# 3. Nuclei (Vulnerability Scanner)
nuclei -u https://api.yourcompany.com -t vulnerabilities/

# 4. SSL Labs Test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=api.yourcompany.com
```

---

## 🚨 Critical Production Checklist

Before going live, verify:

- [ ] All secrets stored in secrets manager (not .env files)
- [ ] HTTPS/TLS enabled with valid certificate (A+ rating on SSL Labs)
- [ ] Database connections use SSL/TLS
- [ ] CORS restricted to specific origins (no wildcards)
- [ ] Rate limiting enabled on all endpoints
- [ ] Password hashing with bcrypt (12 rounds minimum)
- [ ] JWT tokens use secure secret (64+ random chars)
- [ ] All credentials encrypted at rest (Fernet AES-256)
- [ ] Security audit logging enabled
- [ ] SIEM integration configured (Splunk/ELK)
- [ ] Error tracking enabled (Sentry)
- [ ] API documentation disabled in production
- [ ] Debug mode disabled
- [ ] Firewall rules configured (whitelist only)
- [ ] Reverse proxy with security headers (nginx)
- [ ] Regular security scans scheduled
- [ ] Backup encryption enabled
- [ ] Incident response plan documented
- [ ] Security team contact information updated
- [ ] Compliance requirements met (SOC 2, GDPR, etc.)

---

## 📞 Security Incident Response

If a security incident is detected:

1. **Immediate Actions:**
   ```bash
   # Revoke all JWT tokens
   python scripts/revoke_all_tokens.py
   
   # Lock affected accounts
   python scripts/lock_accounts.py --user-ids affected_users.txt
   
   # Enable maintenance mode
   export MAINTENANCE_MODE=true
   ```

2. **Investigation:**
   - Review security audit logs
   - Check SIEM alerts
   - Analyze access patterns
   - Identify breach scope

3. **Notification:**
   - Alert security team
   - Notify affected users (if GDPR applies)
   - Report to relevant authorities (if required)

4. **Remediation:**
   - Patch vulnerabilities
   - Rotate all secrets
   - Update security rules
   - Conduct post-mortem

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
- [SOC 2 Compliance Guide](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome)
- [GDPR Compliance](https://gdpr.eu/)

---

## ✅ Final Verification

Run comprehensive security check:

```bash
# Execute security verification script
python scripts/verify_production_security.py

# Expected output:
# ✅ Secrets management configured
# ✅ Database encryption enabled
# ✅ TLS/SSL certificates valid
# ✅ Rate limiting active
# ✅ Audit logging functional
# ✅ CORS properly configured
# ✅ Password hashing enabled
# ✅ Token encryption verified
# ✅ All security dependencies installed
# 
# 🎉 System ready for production deployment
```

---

**REMEMBER: Security is an ongoing process, not a one-time setup. Schedule regular security audits, keep dependencies updated, and monitor for threats continuously.**
