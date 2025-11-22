"""
Multi-tenant Session Management for Pramiti AI Organization

Handles user authentication, JWT token generation, and org-scoped sessions.
"""

import os
import jwt
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import HTTPException, Request, Header


class SessionManager:
    """Manages user sessions with multi-tenant support"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize session manager
        
        Args:
            secret_key: JWT secret key (defaults to env variable or generated)
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24
        
        # User database (in production, use real DB)
        self.users_db = self._load_users_db()
    
    def _load_users_db(self) -> Dict[str, Dict[str, Any]]:
        """Load user database from file (or use in-memory for demo)"""
        users_file = Path('config/users.json')
        
        if users_file.exists():
            with open(users_file, 'r') as f:
                return json.load(f)
        
        # Demo users for development
        return {
            "admin@default.com": {
                "user_id": "admin@default.com",
                "org_id": "default",
                "role": "admin",
                "name": "Default Admin",
                "password_hash": "demo_hash"  # In production: use bcrypt
            },
            "user@tenant-a.com": {
                "user_id": "user@tenant-a.com",
                "org_id": "tenant-a",
                "role": "user",
                "name": "Tenant A User",
                "password_hash": "demo_hash"
            },
            "admin@tenant-b.com": {
                "user_id": "admin@tenant-b.com",
                "org_id": "tenant-b",
                "role": "admin",
                "name": "Tenant B Admin",
                "password_hash": "demo_hash"
            }
        }
    
    def create_token(self, user_id: str, org_id: str, role: str = "user") -> str:
        """
        Create JWT token for user
        
        Args:
            user_id: User email or ID
            org_id: Organization/tenant ID
            role: User role (admin, user, etc.)
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload with user_id, org_id, role
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user (demo implementation)
        
        Args:
            user_id: User email
            password: User password
            
        Returns:
            User info if authenticated, None otherwise
        """
        user = self.users_db.get(user_id)
        
        if not user:
            return None
        
        # In production: use bcrypt.checkpw()
        # For demo: accept any password
        return {
            "user_id": user["user_id"],
            "org_id": user["org_id"],
            "role": user["role"],
            "name": user["name"]
        }
    
    def get_current_user_from_token(self, authorization: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract current user from Authorization header
        
        Args:
            authorization: Authorization header value (Bearer {token})
            
        Returns:
            User info dict with user_id, org_id, role
            
        Raises:
            HTTPException: If token is missing or invalid
        """
        if not authorization:
            # For development: return default user
            return {
                "user_id": "admin@default.com",
                "org_id": "default",
                "role": "admin"
            }
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        return self.verify_token(token)
    
    def require_admin(self, user: Dict[str, Any]):
        """
        Verify user has admin or super_admin role
        
        Args:
            user: User info dict
            
        Raises:
            HTTPException: If user is not admin or super_admin
        """
        if user.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin role required")
    
    def require_super_admin(self, user: Dict[str, Any]):
        """
        Verify user has super_admin role
        
        Args:
            user: User info dict
            
        Raises:
            HTTPException: If user is not super_admin
        """
        if user.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Super admin role required")
    
    def verify_org_access(self, user: Dict[str, Any], org_id: str):
        """
        Verify user has access to specified org
        Super admins have access to all orgs
        
        Args:
            user: User info dict
            org_id: Target organization ID
            
        Raises:
            HTTPException: If user doesn't have access to org
        """
        # Super admins can access any org
        if user.get("role") == "super_admin":
            return
            
        if user.get("org_id") != org_id:
            raise HTTPException(
                status_code=403, 
                detail=f"User does not have access to organization {org_id}"
            )


# Global session manager instance
session_manager = SessionManager()
