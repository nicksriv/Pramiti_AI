#!/bin/bash

# ============================================================================
# Pramiti AI - Enterprise Security Setup Script
# ============================================================================
# This script installs and configures enterprise-grade security features
# 
# Usage:
#   chmod +x scripts/setup_security.sh
#   ./scripts/setup_security.sh [environment]
#
# Arguments:
#   environment: development | staging | production (default: development)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}Pramiti AI - Enterprise Security Setup${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${GREEN}Environment:${NC} $ENVIRONMENT"
echo -e "${GREEN}Project Root:${NC} $PROJECT_ROOT"
echo ""

# Step 1: Check Python version
echo -e "${BLUE}[1/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${RED}❌ Python 3.9+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Step 2: Create virtual environment (if not exists)
echo -e "${BLUE}[2/8] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Step 3: Upgrade pip
echo -e "${BLUE}[3/8] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"

# Step 4: Install security dependencies
echo -e "${BLUE}[4/8] Installing security dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"
pip install -r requirements-security.txt
echo -e "${GREEN}✅ Security dependencies installed${NC}"

# Step 5: Create directory structure
echo -e "${BLUE}[5/8] Creating secure directory structure...${NC}"

# Create directories
mkdir -p logs/security
mkdir -p secrets/global
mkdir -p config/oauth_encrypted
mkdir -p config/tokens_encrypted

# Create .gitignore files
cat > secrets/.gitignore << EOF
*
!.gitignore
EOF

cat > config/oauth_encrypted/.gitignore << EOF
*
!.gitignore
EOF

cat > config/tokens_encrypted/.gitignore << EOF
*
!.gitignore
EOF

cat > logs/.gitignore << EOF
*.log
!.gitignore
EOF

echo -e "${GREEN}✅ Directory structure created${NC}"

# Step 6: Generate environment file
echo -e "${BLUE}[6/8] Generating environment configuration...${NC}"

ENV_FILE=".env.${ENVIRONMENT}"

if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  $ENV_FILE already exists. Creating backup...${NC}"
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Generate random secrets
JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')
ENCRYPTION_PASSWORD=$(openssl rand -base64 64 | tr -d '\n')
AUDIT_SALT=$(openssl rand -base64 32 | tr -d '\n')

cat > "$ENV_FILE" << EOF
# ============================================================================
# Pramiti AI - Security Configuration ($ENVIRONMENT)
# Generated: $(date)
# ============================================================================

# Environment
ENVIRONMENT=$ENVIRONMENT
DEBUG=$([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false")

# Secrets Backend
# Options: aws, vault, azure, local
SECRETS_BACKEND=local

# Master Encryption Password
# CRITICAL: Change this in production and store in secrets manager
MASTER_ENCRYPTION_PASSWORD=$ENCRYPTION_PASSWORD

# JWT Configuration (will be stored in secrets manager)
JWT_SECRET_KEY=$JWT_SECRET

# Security Logging
SECURITY_LOG_DIR=logs/security
AUDIT_LOG_SALT=$AUDIT_SALT
ENABLE_SIEM=false

# Rate Limiting
RATE_LIMIT_ENABLED=true

# CORS Configuration
# PRODUCTION: Replace with your actual domains
ALLOWED_ORIGINS=$([ "$ENVIRONMENT" = "production" ] && echo "https://app.yourcompany.com" || echo "http://localhost:3000,http://localhost:8084")
ALLOWED_HOSTS=$([ "$ENVIRONMENT" = "production" ] && echo "api.yourcompany.com" || echo "localhost")

# Database (configure with SSL in production)
DATABASE_URL=postgresql://user:pass@localhost:5432/pramiti_ai
MONGO_URI=mongodb://localhost:27017/pramiti_ai
REDIS_URL=redis://localhost:6379/0

# Session Configuration
SESSION_COOKIE_SECURE=$([ "$ENVIRONMENT" = "production" ] && echo "true" || echo "false")
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict

# Monitoring (configure in production)
# SENTRY_DSN=
# PROMETHEUS_ENABLED=false

# Cloud Provider Secrets (if using)
# AWS_REGION=us-east-1
# VAULT_ADDR=
# VAULT_TOKEN=
# AZURE_VAULT_URL=

EOF

echo -e "${GREEN}✅ Environment file created: $ENV_FILE${NC}"

if [ "$ENVIRONMENT" != "development" ]; then
    echo -e "${RED}⚠️  IMPORTANT: Review and update $ENV_FILE with production values!${NC}"
fi

# Step 7: Initialize secrets manager
echo -e "${BLUE}[7/8] Initializing secrets manager...${NC}"

python3 << EOF
import os
os.environ['ENVIRONMENT'] = '$ENVIRONMENT'
os.environ['MASTER_ENCRYPTION_PASSWORD'] = '$ENCRYPTION_PASSWORD'

try:
    from core.secrets_manager import secrets_manager
    
    # Store JWT secret
    secrets_manager.set_secret('jwt_secret_key', '$JWT_SECRET')
    
    print("✅ Secrets manager initialized")
except Exception as e:
    print(f"⚠️  Failed to initialize secrets: {e}")
EOF

# Step 8: Run security verification
echo -e "${BLUE}[8/8] Running security verification...${NC}"

python3 << 'EOF'
import os
import sys

def verify_security():
    """Verify security components are properly installed"""
    checks = []
    
    # Check 1: bcrypt
    try:
        import bcrypt
        checks.append(("bcrypt (password hashing)", True, None))
    except ImportError as e:
        checks.append(("bcrypt (password hashing)", False, str(e)))
    
    # Check 2: PyJWT
    try:
        import jwt
        checks.append(("PyJWT (token management)", True, None))
    except ImportError as e:
        checks.append(("PyJWT (token management)", False, str(e)))
    
    # Check 3: cryptography
    try:
        from cryptography.fernet import Fernet
        checks.append(("cryptography (encryption)", True, None))
    except ImportError as e:
        checks.append(("cryptography (encryption)", False, str(e)))
    
    # Check 4: Security modules
    try:
        from core.secrets_manager import secrets_manager
        checks.append(("Secrets Manager", True, None))
    except ImportError as e:
        checks.append(("Secrets Manager", False, str(e)))
    
    try:
        from core.security_audit import security_audit
        checks.append(("Security Audit Logger", True, None))
    except ImportError as e:
        checks.append(("Security Audit Logger", False, str(e)))
    
    # Check 5: Directory structure
    required_dirs = [
        'logs/security',
        'secrets/global',
        'config/oauth_encrypted',
        'config/tokens_encrypted'
    ]
    
    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        checks.append((f"Directory: {dir_path}", exists, None if exists else "Not found"))
    
    # Print results
    all_passed = True
    for name, passed, error in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if error:
            print(f"   Error: {error}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = verify_security()
    sys.exit(0 if success else 1)
EOF

VERIFICATION_RESULT=$?

echo ""
echo -e "${BLUE}============================================================================${NC}"

if [ $VERIFICATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 Security setup completed successfully!${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo -e "  1. Review and update ${ENV_FILE}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "  2. ${RED}CRITICAL:${NC} Configure secrets backend (AWS/Vault/Azure)"
        echo -e "  3. ${RED}CRITICAL:${NC} Set up TLS/SSL certificates"
        echo -e "  4. Configure CORS with actual domain names"
        echo -e "  5. Set up database with SSL/TLS"
        echo -e "  6. Enable SIEM integration"
        echo -e "  7. Configure monitoring (Sentry, Prometheus)"
        echo -e "  8. Run penetration tests"
    else
        echo -e "  2. Activate virtual environment: source venv/bin/activate"
        echo -e "  3. Load environment: source ${ENV_FILE}"
        echo -e "  4. Start server: python api_server.py"
    fi
    
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  - Security Architecture: SECURITY_ARCHITECTURE.md"
    echo -e "  - Deployment Guide: SECURITY_DEPLOYMENT_GUIDE.md"
    echo -e "  - Implementation Summary: SECURITY_IMPLEMENTATION_SUMMARY.md"
else
    echo -e "${RED}❌ Security setup encountered errors${NC}"
    echo -e "Please review the output above and fix any issues."
    exit 1
fi

echo -e "${BLUE}============================================================================${NC}"
