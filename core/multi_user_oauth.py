"""
Multi-User OAuth Manager
Supports multiple users authenticating with their own accounts for organization-wide access
"""

import os
import json
import secrets
import requests
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class MultiUserOAuthManager:
    """
    Manages OAuth tokens for multiple users across an organization
    
    Architecture:
    - Tokens stored per user (email) per connector
    - Each user authenticates with their own Microsoft/Google account
    - Tokens stored in: .oauth_tokens/{connector_type}/{user_email}.json
    - Supports Microsoft 365 and Google Workspace
    """
    
    def __init__(self, storage_dir: str = ".oauth_tokens"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.user_tokens: Dict[str, Dict[str, Dict[str, Any]]] = {}  # {connector_type: {user_email: token_data}}
        self.pending_auth: Dict[str, Dict[str, str]] = {}  # {state: {user_email, connector_type}}
        self._load_all_tokens()
    
    def _get_user_token_file(self, connector_type: str, user_email: str) -> Path:
        """Get token file path for a specific user"""
        connector_dir = self.storage_dir / connector_type
        connector_dir.mkdir(exist_ok=True)
        # Sanitize email for filename
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        return connector_dir / f"{safe_email}.json"
    
    def _load_all_tokens(self):
        """Load all stored user tokens"""
        for connector_dir in self.storage_dir.iterdir():
            if connector_dir.is_dir():
                connector_type = connector_dir.name
                self.user_tokens[connector_type] = {}
                
                for token_file in connector_dir.glob("*.json"):
                    try:
                        with open(token_file, 'r') as f:
                            token_data = json.load(f)
                            user_email = token_data.get('user_email')
                            if user_email:
                                self.user_tokens[connector_type][user_email] = token_data
                                logger.info(f"Loaded tokens for {user_email} ({connector_type})")
                    except Exception as e:
                        logger.error(f"Failed to load token file {token_file}: {e}")
    
    def save_user_tokens(self, 
                        connector_type: str,
                        user_email: str, 
                        token_data: Dict[str, Any]):
        """
        Save OAuth tokens for a specific user
        
        Args:
            connector_type: Type of connector (microsoft_teams, google_workspace, etc.)
            user_email: User's email address
            token_data: OAuth token data (access_token, refresh_token, etc.)
        """
        try:
            # Add metadata
            token_data['user_email'] = user_email
            token_data['connector_type'] = connector_type
            token_data['saved_at'] = datetime.now().isoformat()
            
            if 'expires_in' in token_data:
                expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
                token_data['expires_at'] = expiry.isoformat()
            
            # Save to memory
            if connector_type not in self.user_tokens:
                self.user_tokens[connector_type] = {}
            self.user_tokens[connector_type][user_email] = token_data
            
            # Save to disk
            token_file = self._get_user_token_file(connector_type, user_email)
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            logger.info(f"Saved tokens for user: {user_email} ({connector_type})")
        except Exception as e:
            logger.error(f"Failed to save tokens for {user_email}: {e}")
            raise
    
    def get_user_tokens(self, 
                       connector_type: str,
                       user_email: str) -> Optional[Dict[str, Any]]:
        """Get tokens for a specific user"""
        return self.user_tokens.get(connector_type, {}).get(user_email)
    
    def get_user_access_token(self, 
                             connector_type: str,
                             user_email: str) -> Optional[str]:
        """
        Get valid access token for user, refreshing if needed
        
        Returns:
            Valid access token or None if expired/not found
        """
        token_data = self.get_user_tokens(connector_type, user_email)
        if not token_data:
            return None
        
        # Check if token is expired
        if 'expires_at' in token_data:
            expiry = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() >= expiry - timedelta(minutes=5):
                logger.info(f"Token expired for {user_email}, needs refresh")
                return None
        
        return token_data.get('access_token')
    
    def has_user_refresh_token(self, 
                               connector_type: str,
                               user_email: str) -> bool:
        """Check if user has a refresh token"""
        token_data = self.get_user_tokens(connector_type, user_email)
        return token_data and 'refresh_token' in token_data
    
    def delete_user_tokens(self, 
                          connector_type: str,
                          user_email: str):
        """Delete tokens for a specific user"""
        if connector_type in self.user_tokens:
            if user_email in self.user_tokens[connector_type]:
                del self.user_tokens[connector_type][user_email]
        
        token_file = self._get_user_token_file(connector_type, user_email)
        if token_file.exists():
            token_file.unlink()
            logger.info(f"Deleted tokens for user: {user_email}")
    
    def list_authenticated_users(self, connector_type: str) -> List[str]:
        """Get list of all authenticated users for a connector type"""
        return list(self.user_tokens.get(connector_type, {}).keys())
    
    def start_user_auth_flow(self, 
                            connector_type: str,
                            user_email: str,
                            state: str):
        """Register a pending authentication flow for a user"""
        self.pending_auth[state] = {
            'user_email': user_email,
            'connector_type': connector_type,
            'started_at': datetime.now().isoformat()
        }
    
    def complete_user_auth_flow(self, state: str) -> Optional[Tuple[str, str]]:
        """
        Complete authentication flow and get user details
        
        Returns:
            Tuple of (user_email, connector_type) or None if invalid state
        """
        auth_data = self.pending_auth.get(state)
        if not auth_data:
            return None
        
        # Clean up
        del self.pending_auth[state]
        
        return auth_data['user_email'], auth_data['connector_type']


class MicrosoftOAuthFlow:
    """Handles Microsoft 365 OAuth 2.0 Authorization Code Flow with multi-user support"""
    
    AUTHORIZE_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    DEFAULT_SCOPES = [
        "offline_access",  # Refresh token
        "User.Read",  # Read user profile
        "Mail.Read", "Mail.ReadWrite", "Mail.Send",  # Email
        "Files.Read.All", "Files.ReadWrite.All",  # OneDrive
        "Calendars.Read", "Calendars.ReadWrite",  # Calendar
        "OnlineMeetings.ReadWrite",  # Teams meetings
    ]
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 tenant_id: str = "common",
                 redirect_uri: str = "http://localhost:8084/api/v1/oauth/callback/microsoft"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, 
                             user_email: str,
                             scopes: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for a specific user
        
        Args:
            user_email: Email of the user who will authenticate
            scopes: List of permission scopes
        
        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'response_mode': 'query',
            'scope': ' '.join(scopes),
            'state': state,
            'prompt': 'consent',
            'login_hint': user_email,  # Pre-fill the login with user's email
        }
        
        auth_url = self.AUTHORIZE_URL.format(tenant_id=self.tenant_id)
        full_url = f"{auth_url}?{urlencode(params)}"
        
        logger.info(f"Generated authorization URL for user: {user_email}")
        return full_url, state
    
    def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for tokens"""
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
            logger.info("Successfully exchanged code for tokens")
            return token_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
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
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            return None


class GoogleOAuthFlow:
    """Handles Google Workspace OAuth 2.0 Authorization Code Flow with multi-user support"""
    
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",  # User profile
        "https://www.googleapis.com/auth/gmail.readonly",  # Read Gmail
        "https://www.googleapis.com/auth/gmail.send",  # Send Gmail
        "https://www.googleapis.com/auth/gmail.modify",  # Modify Gmail
        "https://www.googleapis.com/auth/drive.readonly",  # Read Drive
        "https://www.googleapis.com/auth/drive.file",  # Manage Drive files
        "https://www.googleapis.com/auth/calendar",  # Calendar access
        "https://www.googleapis.com/auth/calendar.events",  # Calendar events
    ]
    
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str = "http://localhost:8084/api/v1/oauth/callback/google"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self,
                             user_email: str,
                             scopes: Optional[List[str]] = None) -> Tuple[str, str]:
        """Generate OAuth authorization URL for a specific user"""
        state = secrets.token_urlsafe(32)
        
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'state': state,
            'access_type': 'offline',  # Get refresh token
            'prompt': 'consent',  # Force consent to ensure refresh token
            'login_hint': user_email,  # Pre-fill with user's email
        }
        
        full_url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"
        logger.info(f"Generated Google authorization URL for user: {user_email}")
        return full_url, state
    
    def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for tokens"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        try:
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            token_data = response.json()
            logger.info("Successfully exchanged Google code for tokens")
            return token_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange Google code for tokens: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh Google token: {e}")
            return None


# Global multi-user OAuth manager
multi_user_oauth_manager = MultiUserOAuthManager()
