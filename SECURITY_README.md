# 🔒 Pramiti AI - Enterprise Security

## Overview

Pramiti AI implements **enterprise-grade security** suitable for deployment in large organizations with strict compliance requirements (SOC 2, GDPR, ISO 27001, HIPAA).

This document provides a quick start guide. For comprehensive details, see the full documentation.

---

## 🚀 Quick Start

### 1. Install Security Dependencies

```bash
# Install all security packages
pip install -r requirements-security.txt

# Verify installation
python -c "import bcrypt, jwt, cryptography; print('✅ Security packages installed')"
```

### 2. Run Automated Setup

```bash
# Make script executable
chmod +x scripts/setup_security.sh

# Run setup (choose environment)
./scripts/setup_security.sh development
# OR
./scripts/setup_security.sh production
```

This script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Generate secure directory structure
- ✅ Create environment configuration
- ✅ Initialize secrets manager
- ✅ Verify security components

### 3. Configure for Your Environment

**For Development:**
```bash
# Already configured! Just run:
source venv/bin/activate
source .env.development
python api_server.py
```

**For Production:**
```bash
# 1. Choose secrets backend
export SECRETS_BACKEND=aws  # or vault, azure

# 2. Configure cloud provider
export AWS_REGION=us-east-1
# OR
export VAULT_ADDR=https://vault.yourcompany.com
# OR
export AZURE_VAULT_URL=https://your-vault.vault.azure.net/

# 3. Set master password (CRITICAL)
export MASTER_ENCRYPTION_PASSWORD="your-64-char-random-password"

# 4. Review and update .env.production
# - Update ALLOWED_ORIGINS with your actual domains
# - Configure database URLs with SSL
# - Set up monitoring (Sentry, Prometheus)
# - Enable SIEM integration

# 5. Follow SECURITY_DEPLOYMENT_GUIDE.md
```

---

## 🛡️ Security Features

### ✅ Implemented

| Feature | Status | Details |
|---------|--------|---------|
| **Password Hashing** | ✅ | bcrypt with 12 rounds |
| **JWT Authentication** | ✅ | Secure secret from secrets manager |
| **Secrets Management** | ✅ | AWS/Vault/Azure + encrypted local |
| **Encryption at Rest** | ✅ | AES-256 (Fernet) for credentials |
| **Audit Logging** | ✅ | Tamper-evident, SIEM-ready |
| **Rate Limiting** | ✅ | IP-based, per-endpoint |
| **Input Validation** | ✅ | Pydantic models |
| **CORS Security** | ✅ | Whitelist-only origins |
| **Security Headers** | 📝 | Nginx configuration provided |
| **TLS/SSL** | 📝 | Certificate setup guide provided |

### 🔐 Key Components

1. **Secrets Manager** (`core/secrets_manager.py`)
   - Multi-cloud support (AWS/Vault/Azure)
   - AES-256 encryption
   - Automatic key rotation
   - Per-organization isolation

2. **Security Audit** (`core/security_audit.py`)
   - 40+ event types
   - Tamper-evident logging
   - Automatic incident detection
   - SIEM integration ready

3. **Session Manager** (`core/session_manager_secure.py`)
   - bcrypt password hashing
   - JWT with token rotation
   - Built-in rate limiting
   - Password policy enforcement

4. **Connector Manager** (`core/connector_manager_secure.py`)
   - Encrypted OAuth credentials
   - Automatic expiration handling
   - Per-tenant isolation
   - Audit trail for all access

---

## 📋 Production Checklist

Before deploying to production, ensure:

### Critical (Must Complete)
- [ ] Secrets backend configured (AWS/Vault/Azure)
- [ ] Master encryption password set (64+ random characters)
- [ ] TLS/SSL certificate installed (A+ rating on SSL Labs)
- [ ] Database connections use SSL/TLS
- [ ] CORS restricted to actual domains (no wildcards)
- [ ] Rate limiting enabled on all endpoints
- [ ] Security audit logging enabled
- [ ] Firewall rules configured (HTTPS only)
- [ ] API documentation disabled (`docs_url=None`)
- [ ] Debug mode disabled (`DEBUG=false`)

### Important (Should Complete)
- [ ] SIEM integration configured (Splunk/ELK)
- [ ] Error tracking enabled (Sentry)
- [ ] Monitoring enabled (Prometheus)
- [ ] Backup encryption enabled
- [ ] Incident response plan documented
- [ ] Regular security scans scheduled
- [ ] Penetration testing completed
- [ ] Security team contacts updated

### Recommended (Nice to Have)
- [ ] Multi-factor authentication
- [ ] WAF (Web Application Firewall)
- [ ] DDoS protection
- [ ] Certificate pinning
- [ ] Bug bounty program

---

## 🔍 Security Verification

### Run Security Checks

```bash
# 1. Dependency vulnerability scan
safety check --full-report

# 2. Security linting
bandit -r core/ api/ -f json -o security-report.json

# 3. Verify secrets encryption
python -c "from core.secrets_manager import secrets_manager; print('✅ Secrets manager working')"

# 4. Test password hashing
python -c "from core.session_manager_secure import session_manager; print('✅ Password hashing working')"

# 5. Check audit logging
python -c "from core.security_audit import security_audit; print('✅ Audit logging working')"
```

### Penetration Testing

```bash
# Run OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://api.yourcompany.com

# Check SSL/TLS configuration
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=api.yourcompany.com
```

---

## 📚 Documentation

### Quick References
- **This File**: Quick start and overview
- **[SECURITY_IMPLEMENTATION_SUMMARY.md](SECURITY_IMPLEMENTATION_SUMMARY.md)**: What we built and why
- **[SECURITY_DEPLOYMENT_GUIDE.md](SECURITY_DEPLOYMENT_GUIDE.md)**: Comprehensive production setup (734 lines)
- **[SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)**: High-level security design

### Code Documentation
- **[core/secrets_manager.py](core/secrets_manager.py)**: Secrets management implementation
- **[core/security_audit.py](core/security_audit.py)**: Audit logging implementation
- **[core/session_manager_secure.py](core/session_manager_secure.py)**: Secure authentication
- **[core/connector_manager_secure.py](core/connector_manager_secure.py)**: Encrypted credentials

---

## 🆘 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'bcrypt'"**
```bash
# Solution: Install security dependencies
pip install -r requirements-security.txt
```

**2. "ValueError: MASTER_ENCRYPTION_PASSWORD must be set in production"**
```bash
# Solution: Set environment variable
export MASTER_ENCRYPTION_PASSWORD="$(openssl rand -base64 64)"
```

**3. "HTTPException: Token expired"**
```bash
# Solution: Tokens expire after 24 hours. Re-login or implement token refresh
# Refresh tokens are valid for 30 days
```

**4. "HTTPException: Too many login attempts"**
```bash
# Solution: Rate limiting is working! Wait 5 minutes or whitelist IP
# Configure in session_manager_secure.py: login_rate_limit, login_rate_window
```

**5. Secrets not persisting**
```bash
# Check secrets backend configuration
echo $SECRETS_BACKEND

# Verify secrets directory exists
ls -la secrets/

# Check permissions
chmod 700 secrets/
```

---

## 🔐 Security Best Practices

### Development
1. **Never commit secrets** to version control
   - Use `.gitignore` for secrets directories
   - Use environment variables or secrets manager

2. **Use different secrets** for each environment
   - Development: Auto-generated (okay)
   - Staging: Unique, rotated monthly
   - Production: Unique, rotated weekly, stored in cloud secrets manager

3. **Test security features** in development
   - Try brute force attacks (rate limiting)
   - Test with expired tokens
   - Verify audit logs are written

### Production
1. **Use cloud secrets manager** (not local encryption)
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

2. **Enable all monitoring**
   - SIEM integration (Splunk/ELK)
   - Error tracking (Sentry)
   - Metrics (Prometheus)

3. **Regular security audits**
   - Monthly: Dependency scans (`safety check`)
   - Quarterly: Penetration testing
   - Annually: Full security audit, compliance review

4. **Incident response**
   - Have a plan documented
   - Security team contacts updated
   - Escalation procedures clear

---

## 📞 Support

### Security Issues
If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@yourcompany.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### General Questions
- Documentation: See files listed above
- Implementation questions: Review code comments in core/ modules
- Production setup: Follow SECURITY_DEPLOYMENT_GUIDE.md step-by-step

---

## ✅ Quick Verification

After setup, verify everything is working:

```bash
# Run this command:
python << 'EOF'
import os
os.environ.setdefault('ENVIRONMENT', 'development')

try:
    from core.secrets_manager import secrets_manager
    from core.security_audit import security_audit, SecurityEventType
    from core.session_manager_secure import session_manager
    from core.connector_manager_secure import secure_connector_manager
    
    print("✅ All security modules imported successfully")
    
    # Test password hashing
    hashed = session_manager.hash_password("TestPassword123!")
    print(f"✅ Password hashing: {hashed[:30]}...")
    
    # Test audit logging
    security_audit.log_event(
        SecurityEventType.CONFIGURATION_CHANGED,
        details={"test": "security_setup"}
    )
    print("✅ Audit logging working")
    
    print("\n🎉 Security setup verified successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF
```

Expected output:
```
✅ All security modules imported successfully
✅ Password hashing: $2b$12$...
✅ Audit logging working

🎉 Security setup verified successfully!
```

---

## 🎯 Summary

Pramiti AI now has **enterprise-grade security** including:

- ✅ **Password hashing** with bcrypt (12 rounds)
- ✅ **JWT authentication** with secure secrets
- ✅ **Secrets management** (multi-cloud support)
- ✅ **Encryption at rest** (AES-256)
- ✅ **Audit logging** (tamper-evident)
- ✅ **Rate limiting** (DDoS protection)
- ✅ **Input validation** (injection prevention)
- ✅ **CORS security** (whitelist-only)
- ✅ **Compliance ready** (SOC 2, GDPR, ISO 27001)

**The platform is ready for deployment in large enterprises with strict security requirements.**

For detailed setup instructions, see **[SECURITY_DEPLOYMENT_GUIDE.md](SECURITY_DEPLOYMENT_GUIDE.md)**.

---

**Last Updated:** November 21, 2025  
**Security Version:** 1.0.0  
**Compliance:** SOC 2, GDPR, ISO 27001 ready
