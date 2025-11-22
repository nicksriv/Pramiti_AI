"""
Multi-tenant Connector Manager for Pramiti AI Organization

Handles connector configuration and token storage with org/user isolation.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException


class ConnectorManager:
    """Manages connector configurations and tokens with multi-tenant support"""
    
    def __init__(self, config_dir: str = "config/oauth", token_dir: str = "config/tokens"):
        """
        Initialize connector manager
        
        Args:
            config_dir: Directory for org-scoped connector configs
            token_dir: Directory for user-scoped access tokens
        """
        self.config_dir = Path(config_dir)
        self.token_dir = Path(token_dir)
        
        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.token_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== CONFIG MANAGEMENT ====================
    
    def save_connector_config(
        self, 
        provider: str, 
        org_id: str, 
        config: Dict[str, Any]
    ) -> str:
        """
        Save connector configuration for an organization
        
        Args:
            provider: Connector provider (microsoft, google, slack, etc.)
            org_id: Organization ID
            config: Configuration dict (client_id, client_secret, etc.)
            
        Returns:
            Path to saved config file
        """
        config_file = self.config_dir / f"{provider}_{org_id}.json"
        
        # Add metadata
        config_data = {
            "provider": provider,
            "org_id": org_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **config
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return str(config_file)
    
    def load_connector_config(self, provider: str, org_id: str) -> Dict[str, Any]:
        """
        Load connector configuration for an organization
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            
        Returns:
            Configuration dict
            
        Raises:
            HTTPException: If config not found
        """
        config_file = self.config_dir / f"{provider}_{org_id}.json"
        
        if not config_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"{provider.title()} connector not configured for organization {org_id}"
            )
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def get_configured_connectors(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get list of configured connectors for an organization
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of connector configurations
        """
        configs = []
        
        for config_file in self.config_dir.glob(f"*_{org_id}.json"):
            with open(config_file, 'r') as f:
                config = json.load(f)
                configs.append({
                    "provider": config.get("provider"),
                    "org_id": config.get("org_id"),
                    "configured": True,
                    "created_at": config.get("created_at")
                })
        
        return configs
    
    def delete_connector_config(self, provider: str, org_id: str):
        """
        Delete connector configuration for an organization
        
        Args:
            provider: Connector provider
            org_id: Organization ID
        """
        config_file = self.config_dir / f"{provider}_{org_id}.json"
        
        if config_file.exists():
            config_file.unlink()
    
    # ==================== TOKEN MANAGEMENT ====================
    
    def save_user_token(
        self,
        provider: str,
        org_id: str,
        user_id: str,
        token_data: Dict[str, Any]
    ) -> str:
        """
        Save OAuth access token for a user
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            user_id: User ID
            token_data: Token dict (access_token, refresh_token, expires_in, etc.)
            
        Returns:
            Path to saved token file
        """
        # Sanitize user_id for filename (replace @ and special chars)
        safe_user_id = user_id.replace('@', '_at_').replace('.', '_')
        token_file = self.token_dir / f"{provider}_{org_id}_{safe_user_id}.json"
        
        # Calculate expiry if not provided
        expires_at = token_data.get('expires_at')
        if not expires_at and token_data.get('expires_in'):
            expires_at = (datetime.utcnow() + timedelta(seconds=token_data['expires_in'])).isoformat()
        
        token_info = {
            "provider": provider,
            "org_id": org_id,
            "user_id": user_id,
            "access_token": token_data.get('access_token'),
            "refresh_token": token_data.get('refresh_token'),
            "token_type": token_data.get('token_type', 'Bearer'),
            "expires_at": expires_at,
            "scopes": token_data.get('scope', '').split() if isinstance(token_data.get('scope'), str) else token_data.get('scopes', []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_info, f, indent=2)
        
        return str(token_file)
    
    def load_user_token(self, provider: str, org_id: str, user_id: str) -> Dict[str, Any]:
        """
        Load OAuth access token for a user
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            user_id: User ID
            
        Returns:
            Token dict
            
        Raises:
            HTTPException: If token not found or expired
        """
        safe_user_id = user_id.replace('@', '_at_').replace('.', '_')
        token_file = self.token_dir / f"{provider}_{org_id}_{safe_user_id}.json"
        
        if not token_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No {provider} authorization found for user {user_id} in org {org_id}. Please authorize first."
            )
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        # Check if token is expired
        if token_data.get('expires_at'):
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.utcnow() >= expires_at:
                raise HTTPException(
                    status_code=401,
                    detail=f"{provider.title()} token expired. Please re-authorize."
                )
        
        return token_data
    
    def get_user_connectors(self, org_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get list of connectors authorized by a user
        
        Args:
            org_id: Organization ID
            user_id: User ID
            
        Returns:
            List of authorized connectors with token info
        """
        safe_user_id = user_id.replace('@', '_at_').replace('.', '_')
        connectors = []
        
        for token_file in self.token_dir.glob(f"*_{org_id}_{safe_user_id}.json"):
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                
                # Check expiry
                is_expired = False
                if token_data.get('expires_at'):
                    expires_at = datetime.fromisoformat(token_data['expires_at'])
                    is_expired = datetime.utcnow() >= expires_at
                
                connectors.append({
                    "provider": token_data.get("provider"),
                    "org_id": token_data.get("org_id"),
                    "user_id": token_data.get("user_id"),
                    "authorized": True,
                    "expired": is_expired,
                    "scopes": token_data.get("scopes", []),
                    "created_at": token_data.get("created_at")
                })
        
        return connectors
    
    def delete_user_token(self, provider: str, org_id: str, user_id: str):
        """
        Delete OAuth token for a user (revoke access)
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            user_id: User ID
        """
        safe_user_id = user_id.replace('@', '_at_').replace('.', '_')
        token_file = self.token_dir / f"{provider}_{org_id}_{safe_user_id}.json"
        
        if token_file.exists():
            token_file.unlink()
    
    def is_connector_configured(self, provider: str, org_id: str) -> bool:
        """
        Check if connector is configured for an organization
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            
        Returns:
            True if configured, False otherwise
        """
        config_file = self.config_dir / f"{provider}_{org_id}.json"
        return config_file.exists()
    
    def is_user_authorized(self, provider: str, org_id: str, user_id: str) -> bool:
        """
        Check if user has authorized a connector
        
        Args:
            provider: Connector provider
            org_id: Organization ID
            user_id: User ID
            
        Returns:
            True if authorized and token valid, False otherwise
        """
        try:
            token_data = self.load_user_token(provider, org_id, user_id)
            return True
        except HTTPException:
            return False


# Global connector manager instance
connector_manager = ConnectorManager()
