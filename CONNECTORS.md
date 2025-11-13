# Enterprise Connectors Documentation

## Overview

The Agentic AI Organization system includes a comprehensive enterprise connectors framework that enables AI agents to securely integrate with popular business tools like Microsoft Teams, Google Drive, Slack, Jira, and more.

## Architecture

### 3-Layer System

1. **Backend Framework** (`core/connectors.py`)
   - Core connector management and configuration
   - OAuth 2.0 flow handling
   - Rate limiting and security features
   - Support for 14+ standard platforms

2. **Production Implementations** (`core/connector_implementations.py`)
   - Real API integrations (Microsoft Graph API, Google Drive API v3)
   - OAuth token management with automatic refresh
   - Demo mode for testing without real credentials
   - Type-safe methods for reading/writing data

3. **API Layer** (`api_server.py`)
   - RESTful endpoints for connector CRUD operations
   - AI agent integration endpoints
   - Connection testing and authorization flows

4. **Frontend UI** (`web/enhanced-dashboard.html`)
   - Visual connector management interface
   - 3-tab system: Available, Connected, Custom
   - Setup wizard for easy configuration

## Supported Platforms

| Platform | Type | Auth | Capabilities |
|----------|------|------|-------------|
| Microsoft Teams | `microsoft_teams` | OAuth 2.0 | Read/write messages, channels, search |
| Google Drive | `google_drive` | OAuth 2.0 | Read/write files, upload, folders, search |
| Slack | `slack` | OAuth 2.0 | Read/write messages, channels |
| Jira | `jira` | OAuth 2.0 / API Key | Read/write issues, projects |
| ServiceNow | `servicenow` | OAuth 2.0 / Basic | Read/write tickets, incidents |
| Confluence | `confluence` | OAuth 2.0 / API Key | Read/write pages, spaces |
| SharePoint | `sharepoint` | OAuth 2.0 | Read/write documents, lists |
| GitHub | `github` | OAuth 2.0 / API Key | Read/write repos, issues, PRs |
| GitLab | `gitlab` | OAuth 2.0 / API Key | Read/write repos, issues, MRs |
| Salesforce | `salesforce` | OAuth 2.0 | Read/write objects, records |
| Zendesk | `zendesk` | OAuth 2.0 / API Key | Read/write tickets, users |
| OneDrive | `onedrive` | OAuth 2.0 | Read/write files, folders |
| Dropbox | `dropbox` | OAuth 2.0 | Read/write files, folders |
| Custom | `custom` | Any | User-defined |

## Production Setup

### Microsoft Teams Integration

#### 1. Azure AD App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Configure:
   - **Name**: `Agentic AI Teams Connector`
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: `http://localhost:8084/oauth/callback` (development)
4. Click "Register"

#### 2. Configure API Permissions

1. Go to "API permissions" → "Add a permission"
2. Select "Microsoft Graph" → "Application permissions"
3. Add permissions:
   - `Team.ReadBasic.All` - Read team information
   - `Channel.ReadBasic.All` - Read channel information
   - `ChannelMessage.Read.All` - Read channel messages
   - `ChannelMessage.Send` - Send channel messages
4. Click "Grant admin consent"

#### 3. Create Client Secret

1. Go to "Certificates & secrets" → "New client secret"
2. Description: `Agentic AI Connector Secret`
3. Expires: 24 months
4. Click "Add"
5. **Copy the secret value immediately** (you won't see it again)

#### 4. Get Configuration Values

From your app registration:
- **Client ID**: Found on Overview page
- **Client Secret**: Created in previous step
- **Tenant ID**: Found on Overview page

#### 5. Create Connector

```bash
curl -X POST http://localhost:8084/api/v1/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "microsoft_teams",
    "name": "Microsoft Teams - Production",
    "description": "Production Teams integration",
    "auth_config": {
      "client_id": "YOUR_CLIENT_ID_HERE",
      "client_secret": "YOUR_CLIENT_SECRET_HERE",
      "tenant_id": "YOUR_TENANT_ID_HERE",
      "redirect_uri": "http://localhost:8084/oauth/callback"
    },
    "permissions": ["read_messages", "write_messages", "read_channels"]
  }'
```

### Google Drive Integration

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Project name: `Agentic AI Drive Connector`
4. Click "Create"

#### 2. Enable Google Drive API

1. Navigate to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click "Enable"

#### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted:
   - User type: Internal (for organization) or External (for testing)
   - App name: `Agentic AI Connector`
   - Scopes: Add `https://www.googleapis.com/auth/drive`
4. Application type: Web application
5. Name: `Agentic AI Drive Client`
6. Authorized redirect URIs: `http://localhost:8084/oauth/callback`
7. Click "Create"

#### 4. Get Configuration Values

From your OAuth 2.0 Client:
- **Client ID**: Displayed after creation
- **Client Secret**: Displayed after creation

#### 5. Create Connector

```bash
curl -X POST http://localhost:8084/api/v1/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "google_drive",
    "name": "Google Drive - Production",
    "description": "Production Drive integration",
    "auth_config": {
      "client_id": "YOUR_CLIENT_ID_HERE",
      "client_secret": "YOUR_CLIENT_SECRET_HERE",
      "redirect_uri": "http://localhost:8084/oauth/callback"
    },
    "permissions": ["read_files", "write_files", "search"]
  }'
```

## Testing Connectors

### Demo Mode

Both Microsoft Teams and Google Drive connectors support demo mode for testing without real credentials:

- Use client_id starting with `demo-` (e.g., `demo-teams-client-id-12345`)
- Returns simulated data for all API calls
- Perfect for development and testing

### Test Connection

```bash
# Test Teams connector
curl -X POST http://localhost:8084/api/v1/connectors/{connector_id}/test

# Expected response:
{
  "success": true,
  "connector_id": "microsoft_teams_xxx",
  "status": "connected",
  "message": "Connection test successful",
  "details": {
    "response_time_ms": 150,
    "authenticated": true,
    "permissions_valid": true,
    "test_result": {
      "success": true,
      "message": "Connection test successful (demo mode)",
      "service": "Microsoft Teams",
      "api_version": "v1.0"
    }
  }
}
```

## AI Agent Integration

### Available Endpoints

#### Microsoft Teams

**Send Message**
```bash
POST /api/v1/connectors/{connector_id}/teams/send_message
Content-Type: application/json

{
  "team_id": "team-12345",
  "channel_id": "channel-67890",
  "message": "Hello from AI Agent!"
}
```

**Get Messages**
```bash
GET /api/v1/connectors/{connector_id}/teams/messages?team_id=team-12345&channel_id=channel-67890&limit=50
```

#### Google Drive

**List Files**
```bash
GET /api/v1/connectors/{connector_id}/drive/files?query=name contains 'report'&limit=100
```

**Upload File**
```bash
POST /api/v1/connectors/{connector_id}/drive/upload
Content-Type: application/json

{
  "file_name": "report.pdf",
  "content": "BASE64_ENCODED_CONTENT",
  "mime_type": "application/pdf",
  "folder_id": "optional-folder-id"
}
```

### Python Integration Example

```python
from core.agent_connector_integration import AgentConnectorBridge

# Initialize bridge
bridge = AgentConnectorBridge(connector_manager)

# Send Teams notification
bridge.teams_send_message(
    connector_id="microsoft_teams_xxx",
    team_id="team-12345",
    channel_id="channel-67890",
    message="🤖 AI Agent Update: Task completed successfully!"
)

# Search Drive files
files = bridge.drive_search_files(
    connector_id="google_drive_xxx",
    query="quarterly report"
)

# Upload backup to Drive
file_id = bridge.drive_upload_file(
    connector_id="google_drive_xxx",
    file_name="ai_backup_20240115.json",
    content=backup_data,
    mime_type="application/json"
)
```

## Security Features

### Authentication
- **OAuth 2.0**: Industry-standard authorization framework
- **Token Management**: Automatic token refresh
- **Secure Storage**: Encrypted auth credentials (production)

### Rate Limiting
- **Per-minute**: 60 requests
- **Per-hour**: 1,000 requests
- **Per-day**: 10,000 requests

### Data Protection
- **HTTPS**: All production traffic encrypted
- **Webhook Validation**: HMAC signature verification
- **Multi-tenant Isolation**: Separate credentials per connector

## API Reference

### Connector Management

**List Available Connectors**
```bash
GET /api/v1/connectors/available
```

**List Configured Connectors**
```bash
GET /api/v1/connectors
```

**Create Connector**
```bash
POST /api/v1/connectors
Content-Type: application/json

{
  "connector_type": "microsoft_teams",
  "name": "Teams Connector",
  "description": "Primary Teams integration",
  "auth_config": { ... },
  "permissions": ["read_messages", "write_messages"]
}
```

**Get Connector**
```bash
GET /api/v1/connectors/{connector_id}
```

**Update Connector**
```bash
PUT /api/v1/connectors/{connector_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "permissions": ["read_messages"]
}
```

**Delete Connector**
```bash
DELETE /api/v1/connectors/{connector_id}
```

**Test Connection**
```bash
POST /api/v1/connectors/{connector_id}/test
```

**Initiate OAuth Flow**
```bash
POST /api/v1/connectors/{connector_id}/authorize
```

**Revoke Access**
```bash
POST /api/v1/connectors/{connector_id}/revoke
```

**Get Permissions**
```bash
GET /api/v1/connectors/{connector_id}/permissions
```

## Troubleshooting

### Common Issues

**Error: "Connector not found"**
- Connector was lost after server restart (in-memory storage)
- Solution: Recreate connector using POST /api/v1/connectors
- Future: Database persistence will solve this

**Error: "Invalid Teams connector"**
- Wrong connector type or connector_id
- Solution: Verify connector type with GET /api/v1/connectors

**Error: "Failed to initialize connector"**
- Missing auth_config or invalid credentials
- Solution: Check client_id, client_secret, tenant_id

**Demo Mode Not Working**
- Client ID doesn't start with "demo-"
- Solution: Use `demo-teams-client-id-12345` format

### Production OAuth Flow

For production connectors with real credentials:

1. Create connector with real client_id/secret
2. Call `/authorize` endpoint to get authorization URL
3. Redirect user to authorization URL
4. User grants permissions
5. OAuth provider redirects back with auth code
6. Backend exchanges code for access token
7. Token stored in connector auth_config
8. Test connection to verify

## Roadmap

### Phase 1 (Complete) ✅
- Core connector framework
- Microsoft Teams and Google Drive implementations
- API endpoints for connector management
- Frontend UI integration
- Demo mode for testing

### Phase 2 (Current)
- Production credential support
- Real OAuth flows
- AI agent integration endpoints
- Documentation

### Phase 3 (Planned)
- Database persistence
- More connector implementations (Slack, Jira, etc.)
- Advanced search capabilities
- Webhook support
- Rate limit management UI

### Phase 4 (Future)
- Enterprise features (SSO, SAML)
- Audit logging
- Advanced permissions management
- Connector marketplace
- Custom connector SDK

## Support

For issues or questions:
1. Check this documentation
2. Review API docs at http://localhost:8084/docs
3. Check connector status in dashboard
4. Review server logs for error details

## License

Copyright © 2024 Agentic AI Organization. All rights reserved.
