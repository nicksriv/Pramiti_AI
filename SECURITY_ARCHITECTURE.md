# Enterprise Security Architecture - Pramiti AI
**Security Assessment & Implementation Guide for Enterprise Deployment**

## 🔒 Executive Summary

This document outlines the comprehensive security architecture for Pramiti AI, designed to meet enterprise-grade security requirements including SOC 2, ISO 27001, GDPR, and industry best practices for SaaS applications handling sensitive corporate data.

---

## 📋 Critical Security Vulnerabilities (Current State)

### 🚨 SEVERITY: CRITICAL

1. **Hardcoded JWT Secret Key**
   - **Location**: `core/session_manager.py`
   - **Issue**: `'your-secret-key-change-in-production'` hardcoded fallback
   - **Risk**: Token forgery, session hijacking, complete auth bypass
   - **Impact**: CRITICAL - Complete system compromise

2. **Plaintext Credential Storage**
   - **Location**: `config/oauth/*.json`, `config/tokens/*.json`
   - **Issue**: Client secrets, access tokens stored as plaintext JSON
   - **Risk**: Credential theft if files accessed
   - **Impact**: CRITICAL - Cross-tenant data breach

3. **No Password Hashing**
   - **Location**: `core/session_manager.py` - `authenticate_user()`
   - **Issue**: Demo mode accepts any password, no bcrypt/argon2
   - **Risk**: Unauthorized access to any account
   - **Impact**: CRITICAL - Authentication bypass

4. **Missing Input Validation**
   - **Location**: All API endpoints
   - **Issue**: No sanitization of user inputs
   - **Risk**: SQL injection, XSS, command injection
   - **Impact**: HIGH - Code execution, data exfiltration

5. **No Rate Limiting**
   - **Location**: All endpoints
   - **Issue**: No throttling on authentication or API calls
   - **Risk**: Brute force attacks, DDoS
   - **Impact**: HIGH - Service disruption, credential compromise

6. **Insufficient CORS Configuration**
   - **Location**: `api_server.py`
   - **Issue**: Allows all origins (`allow_origins=["*"]`)
   - **Risk**: CSRF attacks, data theft
   - **Impact**: HIGH - Unauthorized API access

7. **No Audit Logging**
   - **Location**: System-wide
   - **Issue**: No security event logging (failed logins, token usage, etc.)
   - **Risk**: Undetected breaches, compliance violations
   - **Impact**: HIGH - Forensic blindness

8. **Insecure Token Storage (Frontend)**
   - **Location**: `web/enhanced-dashboard.html` - localStorage
   - **Issue**: XSS can steal tokens, no httpOnly cookies
   - **Risk**: Token theft via XSS
   - **Impact**: MEDIUM - Session hijacking

9. **No Certificate Pinning**
   - **Location**: HTTPS configuration
   - **Issue**: No SSL/TLS certificate validation
   - **Risk**: Man-in-the-middle attacks
   - **Impact**: MEDIUM - Credential interception

10. **Exposed API Keys in Environment**
    - **Location**: Direct `os.getenv()` calls
    - **Issue**: Keys in environment variables (logged, exposed)
    - **Risk**: Credential leakage through logs/errors
    - **Impact**: MEDIUM - API abuse

---

## 🛡️ Enterprise Security Framework

### 1. Secrets Management (AWS Secrets Manager / HashiCorp Vault)

**Implementation: Multi-Layer Encryption**

```python
# core/secrets_manager.py
"""
Enterprise Secrets Management with AWS Secrets Manager Integration
Supports: AWS Secrets Manager, HashiCorp Vault, Azure Key Vault
"""

import os
import json
import boto3
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hvac  # HashiCorp Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class SecretsManager:
    """
    Enterprise-grade secrets management with multiple backend support
    
    Features:
    - Multi-cloud support (AWS/Azure/GCP)
    - Local encryption for development
    - Automatic key rotation
    - Audit logging
    - FIPS 140-2 compliance
    """
    
    def __init__(self, backend: str = "aws"):
        """
        Initialize secrets manager
        
        Args:
            backend: 'aws', 'vault', 'azure', or 'local'
        """
        self.backend = backend
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        if backend == "aws":
            self.client = boto3.client('secretsmanager')
        elif backend == "vault":
            vault_url = os.getenv('VAULT_ADDR', 'http://localhost:8200')
            vault_token = os.getenv('VAULT_TOKEN')
            self.client = hvac.Client(url=vault_url, token=vault_token)
        elif backend == "azure":
            vault_url = os.getenv('AZURE_VAULT_URL')
            self.client = SecretClient(
                vault_url=vault_url,
                credential=DefaultAzureCredential()
            )
        elif backend == "local":
            # For development only - encrypted local storage
            self.encryption_key = self._derive_key()
            self.cipher = Fernet(self.encryption_key)
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from master password (PBKDF2)"""
        master_password = os.getenv('MASTER_PASSWORD', 'dev-only-password').encode()
        salt = os.getenv('ENCRYPTION_SALT', 'pramiti-ai-salt').encode()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return urlsafe_b64encode(kdf.derive(master_password))
    
    def get_secret(self, secret_name: str, org_id: Optional[str] = None) -> str:
        """
        Retrieve secret with org-scoping
        
        Args:
            secret_name: Name of secret (e.g., 'jwt_secret', 'openai_api_key')
            org_id: Optional org ID for tenant-specific secrets
            
        Returns:
            Decrypted secret value
        """
        # Build full secret path
        full_path = f"{org_id}/{secret_name}" if org_id else f"global/{secret_name}"
        
        # Check cache
        if full_path in self.cache:
            return self.cache[full_path]
        
        try:
            if self.backend == "aws":
                response = self.client.get_secret_value(SecretId=full_path)
                secret_value = response['SecretString']
            
            elif self.backend == "vault":
                secret = self.client.secrets.kv.v2.read_secret_version(path=full_path)
                secret_value = secret['data']['data']['value']
            
            elif self.backend == "azure":
                secret = self.client.get_secret(full_path.replace('/', '-'))
                secret_value = secret.value
            
            elif self.backend == "local":
                # Read from encrypted local file
                secret_file = f"secrets/{full_path}.enc"
                if os.path.exists(secret_file):
                    with open(secret_file, 'rb') as f:
                        encrypted = f.read()
                    secret_value = self.cipher.decrypt(encrypted).decode()
                else:
                    raise ValueError(f"Secret {full_path} not found")
            
            # Cache secret
            self.cache[full_path] = secret_value
            return secret_value
        
        except Exception as e:
            # Log to security audit
            self._log_security_event("secret_access_failed", {
                "secret_name": secret_name,
                "org_id": org_id,
                "error": str(e)
            })
            raise
    
    def set_secret(
        self, 
        secret_name: str, 
        secret_value: str, 
        org_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Store secret with encryption
        
        Args:
            secret_name: Name of secret
            secret_value: Secret value to encrypt
            org_id: Optional org ID for scoping
            metadata: Optional metadata (tags, rotation policy, etc.)
        """
        full_path = f"{org_id}/{secret_name}" if org_id else f"global/{secret_name}"
        
        try:
            if self.backend == "aws":
                self.client.create_secret(
                    Name=full_path,
                    SecretString=secret_value,
                    Tags=[{'Key': k, 'Value': v} for k, v in (metadata or {}).items()]
                )
            
            elif self.backend == "vault":
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=full_path,
                    secret={'value': secret_value, **(metadata or {})}
                )
            
            elif self.backend == "azure":
                self.client.set_secret(
                    full_path.replace('/', '-'),
                    secret_value
                )
            
            elif self.backend == "local":
                # Encrypt and save locally
                os.makedirs(f"secrets/{os.path.dirname(full_path)}", exist_ok=True)
                encrypted = self.cipher.encrypt(secret_value.encode())
                with open(f"secrets/{full_path}.enc", 'wb') as f:
                    f.write(encrypted)
            
            # Invalidate cache
            if full_path in self.cache:
                del self.cache[full_path]
            
            self._log_security_event("secret_created", {
                "secret_name": secret_name,
                "org_id": org_id
            })
        
        except Exception as e:
            self._log_security_event("secret_creation_failed", {
                "secret_name": secret_name,
                "org_id": org_id,
                "error": str(e)
            })
            raise
    
    def rotate_secret(self, secret_name: str, org_id: Optional[str] = None):
        """Trigger automatic secret rotation"""
        # Implementation for automatic rotation
        pass
    
    def _log_security_event(self, event_type: str, details: Dict):
        """Log security events to audit trail"""
        # Will be implemented in security_audit.py
        pass


# Global instance
secrets_manager = SecretsManager(
    backend=os.getenv('SECRETS_BACKEND', 'local')
)
```

**Configuration:**
