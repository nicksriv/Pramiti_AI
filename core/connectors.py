"""
Enterprise Connectors Module
Manages integrations with standard enterprise tools and custom connectors
Implements OAuth 2.0, API key auth, and custom authentication protocols
"""

from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import secrets
from abc import ABC, abstractmethod

class ConnectorType(Enum):
    """Types of available connectors"""
    MICROSOFT_TEAMS = "microsoft_teams"
    SLACK = "slack"
    GOOGLE_DRIVE = "google_drive"
    GOOGLE_WORKSPACE = "google_workspace"
    JIRA = "jira"
    SERVICENOW = "servicenow"
    ZENDESK = "zendesk"
    CONFLUENCE = "confluence"
    SHAREPOINT = "sharepoint"
    ONEDRIVE = "onedrive"
    DROPBOX = "dropbox"
    GITHUB = "github"
    GITLAB = "gitlab"
    SALESFORCE = "salesforce"
    CUSTOM = "custom"

class AuthType(Enum):
    """Authentication types"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    CUSTOM = "custom"

class ConnectorStatus(Enum):
    """Connector connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING_AUTH = "pending_auth"
    EXPIRED = "expired"

class PermissionScope(Enum):
    """Permission scopes for connectors"""
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"

@dataclass
class ConnectorConfig:
    """Configuration for a connector"""
    connector_id: str
    connector_type: ConnectorType
    name: str
    description: str
    auth_type: AuthType
    status: ConnectorStatus = ConnectorStatus.DISCONNECTED
    
    # Authentication details
    auth_config: Dict[str, Any] = field(default_factory=dict)
    
    # Permissions and scopes
    permissions: List[str] = field(default_factory=list)
    scope: PermissionScope = PermissionScope.READ_WRITE
    
    # Connector metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    
    # Rate limiting
    rate_limit: Dict[str, int] = field(default_factory=lambda: {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
    })
    
    # Custom fields for flexibility
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    # Tenant isolation
    tenant_id: Optional[str] = None
    
    # Encryption key for sensitive data
    encryption_key: Optional[str] = None

@dataclass
class OAuthConfig:
    """OAuth 2.0 configuration"""
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    redirect_uri: str
    scope: List[str]
    state: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

@dataclass
class ConnectorCapabilities:
    """Capabilities supported by a connector"""
    read_files: bool = False
    write_files: bool = False
    read_messages: bool = False
    send_messages: bool = False
    create_tickets: bool = False
    update_tickets: bool = False
    read_calendar: bool = False
    write_calendar: bool = False
    search: bool = False
    webhooks: bool = False
    real_time_sync: bool = False
    custom_actions: List[str] = field(default_factory=list)

class BaseConnector(ABC):
    """Base class for all connectors"""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.capabilities = self.get_capabilities()
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ConnectorCapabilities:
        """Get connector capabilities"""
        pass
    
    @abstractmethod
    def revoke_access(self) -> bool:
        """Revoke access and disconnect"""
        pass
    
    def validate_permissions(self, required_permission: str) -> bool:
        """Validate if connector has required permission"""
        return required_permission in self.config.permissions
    
    def update_status(self, status: ConnectorStatus):
        """Update connector status"""
        self.config.status = status
        self.config.updated_at = datetime.now()

# Predefined connector configurations
STANDARD_CONNECTORS = {
    ConnectorType.MICROSOFT_TEAMS: {
        "name": "Microsoft Teams",
        "description": "Integrate with Microsoft Teams for messaging and collaboration",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "scope": ["User.Read", "Chat.Read", "Chat.ReadWrite", "Files.Read", "Files.ReadWrite"]
        },
        "capabilities": {
            "read_messages": True,
            "send_messages": True,
            "read_files": True,
            "write_files": True,
            "webhooks": True
        },
        "icon": "teams-icon.svg",
        "documentation_url": "https://docs.microsoft.com/en-us/graph/teams-concept-overview"
    },
    
    ConnectorType.SLACK: {
        "name": "Slack",
        "description": "Connect to Slack workspaces for team communication",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://slack.com/oauth/v2/authorize",
            "token_url": "https://slack.com/api/oauth.v2.access",
            "scope": ["channels:read", "channels:write", "chat:write", "files:read", "files:write"]
        },
        "capabilities": {
            "read_messages": True,
            "send_messages": True,
            "read_files": True,
            "write_files": True,
            "webhooks": True,
            "real_time_sync": True
        },
        "icon": "slack-icon.svg",
        "documentation_url": "https://api.slack.com/docs"
    },
    
    ConnectorType.GOOGLE_DRIVE: {
        "name": "Google Drive",
        "description": "Access and manage files in Google Drive",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scope": ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.readonly"]
        },
        "capabilities": {
            "read_files": True,
            "write_files": True,
            "search": True
        },
        "icon": "google-drive-icon.svg",
        "documentation_url": "https://developers.google.com/drive/api/guides/about-sdk"
    },
    
    ConnectorType.JIRA: {
        "name": "Jira",
        "description": "Manage issues and projects in Atlassian Jira",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://auth.atlassian.com/authorize",
            "token_url": "https://auth.atlassian.com/oauth/token",
            "scope": ["read:jira-work", "write:jira-work", "read:jira-user"]
        },
        "capabilities": {
            "create_tickets": True,
            "update_tickets": True,
            "search": True,
            "webhooks": True
        },
        "icon": "jira-icon.svg",
        "documentation_url": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/"
    },
    
    ConnectorType.SERVICENOW: {
        "name": "ServiceNow",
        "description": "Integrate with ServiceNow ITSM platform",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://{instance}.service-now.com/oauth_auth.do",
            "token_url": "https://{instance}.service-now.com/oauth_token.do",
            "scope": ["useraccount"]
        },
        "capabilities": {
            "create_tickets": True,
            "update_tickets": True,
            "read_messages": True,
            "search": True,
            "webhooks": True
        },
        "icon": "servicenow-icon.svg",
        "documentation_url": "https://docs.servicenow.com/bundle/tokyo-platform-security/page/administer/security/concept/c_OAuthApplications.html"
    },
    
    ConnectorType.CONFLUENCE: {
        "name": "Confluence",
        "description": "Access and manage Confluence documentation",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://auth.atlassian.com/authorize",
            "token_url": "https://auth.atlassian.com/oauth/token",
            "scope": ["read:confluence-content.all", "write:confluence-content"]
        },
        "capabilities": {
            "read_files": True,
            "write_files": True,
            "search": True
        },
        "icon": "confluence-icon.svg",
        "documentation_url": "https://developer.atlassian.com/cloud/confluence/rest/v2/intro/"
    },
    
    ConnectorType.SHAREPOINT: {
        "name": "SharePoint",
        "description": "Connect to Microsoft SharePoint for document management",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "scope": ["Sites.Read.All", "Sites.ReadWrite.All"]
        },
        "capabilities": {
            "read_files": True,
            "write_files": True,
            "search": True
        },
        "icon": "sharepoint-icon.svg",
        "documentation_url": "https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/sharepoint-add-ins"
    },
    
    ConnectorType.GITHUB: {
        "name": "GitHub",
        "description": "Integrate with GitHub repositories and issues",
        "auth_type": AuthType.OAUTH2,
        "oauth_config": {
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "scope": ["repo", "read:org", "write:repo_hook"]
        },
        "capabilities": {
            "read_files": True,
            "write_files": True,
            "create_tickets": True,
            "update_tickets": True,
            "webhooks": True
        },
        "icon": "github-icon.svg",
        "documentation_url": "https://docs.github.com/en/rest"
    }
}

class ConnectorManager:
    """Manages all connector instances and operations"""
    
    def __init__(self):
        self.connectors: Dict[str, ConnectorConfig] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_connector(self, connector_type: ConnectorType, name: str, 
                        auth_config: Dict[str, Any], tenant_id: Optional[str] = None) -> ConnectorConfig:
        """Create a new connector instance"""
        connector_id = f"{connector_type.value}_{secrets.token_hex(8)}"
        
        standard_config = STANDARD_CONNECTORS.get(connector_type, {})
        
        config = ConnectorConfig(
            connector_id=connector_id,
            connector_type=connector_type,
            name=name,
            description=standard_config.get("description", ""),
            auth_type=AuthType(standard_config.get("auth_type", AuthType.OAUTH2.value)),
            auth_config=auth_config,
            tenant_id=tenant_id
        )
        
        self.connectors[connector_id] = config
        return config
    
    def get_connector(self, connector_id: str) -> Optional[ConnectorConfig]:
        """Get connector by ID"""
        return self.connectors.get(connector_id)
    
    def list_connectors(self, tenant_id: Optional[str] = None) -> List[ConnectorConfig]:
        """List all connectors for a tenant"""
        if tenant_id:
            return [c for c in self.connectors.values() if c.tenant_id == tenant_id]
        return list(self.connectors.values())
    
    def delete_connector(self, connector_id: str) -> bool:
        """Delete a connector"""
        if connector_id in self.connectors:
            del self.connectors[connector_id]
            return True
        return False
    
    def get_standard_connectors(self) -> Dict[ConnectorType, Dict[str, Any]]:
        """Get list of available standard connectors"""
        return STANDARD_CONNECTORS
    
    def initiate_oauth_flow(self, connector_id: str) -> Dict[str, Any]:
        """Initiate OAuth 2.0 authorization flow"""
        config = self.get_connector(connector_id)
        if not config:
            raise ValueError(f"Connector {connector_id} not found")
        
        if config.auth_type != AuthType.OAUTH2:
            raise ValueError(f"Connector {connector_id} does not use OAuth 2.0")
        
        standard_config = STANDARD_CONNECTORS.get(config.connector_type, {})
        oauth_config = standard_config.get("oauth_config", {})
        
        state = secrets.token_urlsafe(32)
        
        # Store state for verification
        self.active_sessions[state] = {
            "connector_id": connector_id,
            "timestamp": datetime.now(),
            "type": "oauth_flow"
        }
        
        return {
            "authorization_url": oauth_config.get("authorization_url"),
            "client_id": config.auth_config.get("client_id"),
            "redirect_uri": config.auth_config.get("redirect_uri"),
            "scope": " ".join(oauth_config.get("scope", [])),
            "state": state
        }
    
    def validate_webhook_signature(self, connector_id: str, payload: str, 
                                   signature: str) -> bool:
        """Validate webhook signature"""
        config = self.get_connector(connector_id)
        if not config:
            return False
        
        webhook_secret = config.auth_config.get("webhook_secret")
        if not webhook_secret:
            return False
        
        expected_signature = hashlib.sha256(
            f"{webhook_secret}{payload}".encode()
        ).hexdigest()
        
        return secrets.compare_digest(signature, expected_signature)

# Global connector manager instance
connector_manager = ConnectorManager()
