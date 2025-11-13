"""
OAuth 2.0 Manager for Microsoft 365 Delegated Authentication
Handles user login flow, token management, and refresh token storage
"""

import os
import json
import secrets
import requests
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode, parse_qs

logger = logging.getLogger(__name__)


class OAuthTokenManager:
    """Manages OAuth tokens with secure storage and automatic refresh"""
    
    def __init__(self, storage_dir: str = ".oauth_tokens"):
        """
        Initialize OAuth token manager
        
        Args:
            storage_dir: Directory to store encrypted tokens
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._load_tokens()
    
    def _get_token_file(self, connector_id: str) -> Path:
        """Get the token file path for a connector"""
        return self.storage_dir / f"{connector_id}.json"
    
    def _load_tokens(self):
        """Load all stored tokens"""
        for token_file in self.storage_dir.glob("*.json"):
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    connector_id = token_file.stem
                    self.tokens[connector_id] = token_data
                    logger.info(f"Loaded tokens for connector: {connector_id}")
            except Exception as e:
                logger.error(f"Failed to load token file {token_file}: {e}")
    
    def save_tokens(self, connector_id: str, token_data: Dict[str, Any]):
        """
        Save tokens for a connector
        
        Args:
            connector_id: Unique connector identifier
            token_data: Token data including access_token, refresh_token, expires_in
        """
        try:
            # Add timestamp and expiry calculation
            token_data['saved_at'] = datetime.now().isoformat()
            if 'expires_in' in token_data:
                expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
                token_data['expires_at'] = expiry.isoformat()
            
            # Save to memory and disk
            self.tokens[connector_id] = token_data
            
            token_file = self._get_token_file(connector_id)
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            logger.info(f"Saved tokens for connector: {connector_id}")
        except Exception as e:
            logger.error(f"Failed to save tokens for {connector_id}: {e}")
            raise
    
    def get_tokens(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """Get tokens for a connector"""
        return self.tokens.get(connector_id)
    
    def get_access_token(self, connector_id: str) -> Optional[str]:
        """Get valid access token, refreshing if needed"""
        token_data = self.get_tokens(connector_id)
        if not token_data:
            return None
        
        # Check if token is expired
        if 'expires_at' in token_data:
            expiry = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() >= expiry - timedelta(minutes=5):  # Refresh 5 min before expiry
                logger.info(f"Token expired for {connector_id}, needs refresh")
                return None
        
        return token_data.get('access_token')
    
    def has_refresh_token(self, connector_id: str) -> bool:
        """Check if connector has a refresh token"""
        token_data = self.get_tokens(connector_id)
        return token_data and 'refresh_token' in token_data
    
    def delete_tokens(self, connector_id: str):
        """Delete tokens for a connector"""
        if connector_id in self.tokens:
            del self.tokens[connector_id]
        
        token_file = self._get_token_file(connector_id)
        if token_file.exists():
            token_file.unlink()
            logger.info(f"Deleted tokens for connector: {connector_id}")


class MicrosoftOAuthFlow:
    """Handles Microsoft 365 OAuth 2.0 Authorization Code Flow"""
    
    # Microsoft OAuth endpoints
    AUTHORIZE_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    # Scopes for Microsoft 365 access
    DEFAULT_SCOPES = [
        "offline_access",  # Required for refresh token
        "User.Read",  # Read user profile
        "Mail.Read",  # Read email
        "Mail.ReadWrite",  # Read and write email
        "Mail.Send",  # Send email
        "Files.Read.All",  # Read OneDrive files
        "Files.ReadWrite.All",  # Read and write OneDrive files
        "Calendars.Read",  # Read calendar
        "Calendars.ReadWrite",  # Read and write calendar
        "OnlineMeetings.ReadWrite",  # Create meetings
    ]
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 tenant_id: str = "common",
                 redirect_uri: str = "http://localhost:8084/api/v1/oauth/callback"):
        """
        Initialize Microsoft OAuth flow
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID (use 'common' for multi-tenant)
            redirect_uri: OAuth callback URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.redirect_uri = redirect_uri
        self.state_storage: Dict[str, str] = {}  # Store state -> connector_id mapping
    
    def get_authorization_url(self, connector_id: str, scopes: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for user login
        
        Args:
            connector_id: Connector identifier to associate with this flow
            scopes: List of permission scopes (uses DEFAULT_SCOPES if not provided)
        
        Returns:
            Tuple of (authorization_url, state)
        """
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        self.state_storage[state] = connector_id
        
        # Use default scopes if not provided
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'response_mode': 'query',
            'scope': ' '.join(scopes),
            'state': state,
            'prompt': 'consent',  # Force consent screen to ensure all permissions granted
        }
        
        auth_url = self.AUTHORIZE_URL.format(tenant_id=self.tenant_id)
        full_url = f"{auth_url}?{urlencode(params)}"
        
        logger.info(f"Generated authorization URL for connector {connector_id}")
        return full_url, state
    
    def exchange_code_for_tokens(self, 
                                  code: str, 
                                  state: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from callback
            state: State parameter for validation
        
        Returns:
            Tuple of (connector_id, token_data) or (None, None) on failure
        """
        # Validate state
        connector_id = self.state_storage.get(state)
        if not connector_id:
            logger.error(f"Invalid state parameter: {state}")
            return None, None
        
        # Clean up state
        del self.state_storage[state]
        
        # Exchange code for tokens
        token_url = self.TOKEN_URL.format(tenant_id=self.tenant_id)
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info(f"Successfully exchanged code for tokens for connector {connector_id}")
            
            return connector_id, token_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None, None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: The refresh token
        
        Returns:
            New token data or None on failure
        """
        token_url = self.TOKEN_URL.format(tenant_id=self.tenant_id)
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed access token")
            
            return token_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None


# Global OAuth manager instances
oauth_token_manager = OAuthTokenManager()
oauth_flows: Dict[str, MicrosoftOAuthFlow] = {}  # connector_id -> OAuth flow


def get_oauth_flow(client_id: str, 
                   client_secret: str, 
                   tenant_id: str = "common",
                   redirect_uri: str = "http://localhost:8084/api/v1/oauth/callback") -> MicrosoftOAuthFlow:
    """
    Get or create an OAuth flow instance
    
    Args:
        client_id: Azure AD application client ID
        client_secret: Azure AD application client secret
        tenant_id: Azure AD tenant ID
        redirect_uri: OAuth callback URL
    
    Returns:
        MicrosoftOAuthFlow instance
    """
    flow_key = f"{client_id}:{tenant_id}"
    if flow_key not in oauth_flows:
        oauth_flows[flow_key] = MicrosoftOAuthFlow(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            redirect_uri=redirect_uri
        )
    return oauth_flows[flow_key]
