# Multi-Tenant Connector Framework

## Overview

This framework provides complete multi-tenant support for connector management in the Pramiti AI Organization system. Each organization (tenant) can configure their own connectors, and each user within an organization can authorize connectors individually.

## Architecture

### Three-Tier Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Tenant Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tier 1: User Authentication (JWT)                          │
│  ├── User ID                                                │
│  ├── Organization ID                                        │
│  └── Role (super_admin/admin/user)                          │
│      ├── super_admin: Platform-wide access, all orgs        │
│      ├── admin: Tenant admin, single org only               │
│      └── user: Regular user within org                      │
│                                                              │
│  Tier 2: Connector Configuration (Per Org)                  │
│  ├── config/oauth/slack_tenant-a.json                       │
│  ├── config/oauth/slack_tenant-b.json                       │
│  └── config/oauth/microsoft_tenant-a.json                   │
│                                                              │
│  Tier 3: User Tokens (Per Org + User)                       │
│  ├── config/tokens/slack_tenant-a_user123.json              │
│  ├── config/tokens/slack_tenant-a_user456.json              │
│  └── config/tokens/microsoft_tenant-b_user789.json          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Session Manager (`core/session_manager.py`)

Handles JWT-based authentication and multi-tenant session management.

**Features:**
- JWT token generation with org_id + user_id + role
- Token verification and expiration handling
- Organization access control
- Role-based permissions (super_admin/admin/user)
  - **super_admin**: Full platform access, can manage all organizations
  - **admin**: Tenant admin, can manage their organization only
  - **user**: Regular user, basic access within their organization

**Usage:**
```python
from core.session_manager import session_manager

# Create token for user
token = session_manager.create_token(
    user_id="user@example.com",
    org_id="tenant-a",
    role="admin"
)

# Verify token in API endpoint
async def get_current_user(authorization: str = Header(None)):
    return session_manager.get_current_user_from_token(authorization)
```

### 2. Connector Manager (`core/connector_manager.py`)

Manages connector configurations and OAuth tokens with org/user isolation.

**Features:**
- Org-scoped connector configuration storage
- User-scoped OAuth token storage
- Automatic expiration checking
- Query connectors by org or user

**Usage:**
```python
from core.connector_manager import connector_manager

# Save connector config for org
connector_manager.save_connector_config(
    provider="slack",
    org_id="tenant-a",
    config={
        "client_id": "...",
        "client_secret": "...",
        "redirect_uri": "..."
    }
)

# Save user's OAuth token
connector_manager.save_user_token(
    provider="slack",
    org_id="tenant-a",
    user_id="user@example.com",
    token_data={
        "access_token": "xoxp-...",
        "refresh_token": "xoxr-...",
        "expires_in": 3600
    }
)

# Load user's token (with expiration check)
token = connector_manager.load_user_token(
    provider="slack",
    org_id="tenant-a",
    user_id="user@example.com"
)
```

## API Endpoints

### Authentication

#### POST /api/v1/auth/login
```json
Request:
{
  "user_id": "admin@default.com",
  "password": "password"
}

Response:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "admin@default.com",
    "org_id": "default",
    "role": "admin",
    "name": "Default Admin"
  }
}
```

### Connector Setup (Admin Only)

All setup endpoints require `Authorization: Bearer {token}` header.

#### POST /api/v1/oauth/setup/slack
```json
{
  "client_id": "123456789012.1234567890123",
  "client_secret": "abcdef1234567890",
  "org_id": "tenant-a"
}
```

#### POST /api/v1/oauth/setup/jira
```json
{
  "client_id": "YOUR_JIRA_CLIENT_ID",
  "client_secret": "YOUR_SECRET",
  "org_id": "tenant-a"
}
```

#### POST /api/v1/oauth/setup/servicenow
```json
{
  "instance_url": "https://yourinstance.service-now.com",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_SECRET",
  "org_id": "tenant-a"
}
```

#### POST /api/v1/oauth/setup/confluence
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_SECRET",
  "org_id": "tenant-a"
}
```

#### POST /api/v1/oauth/setup/sharepoint
```json
{
  "client_id": "12345678-abcd-1234-5678-123456789abc",
  "client_secret": "YOUR_SECRET",
  "tenant_id": "common",
  "org_id": "tenant-a"
}
```

#### POST /api/v1/oauth/setup/github
```json
{
  "client_id": "Iv1.1234567890abcdef",
  "client_secret": "abcdef1234567890",
  "org_id": "tenant-a"
}
```

### Query Endpoints

#### GET /api/v1/connectors/configured
Returns list of connectors configured for the user's organization.

```json
Response:
{
  "success": true,
  "org_id": "tenant-a",
  "connectors": [
    {
      "provider": "slack",
      "org_id": "tenant-a",
      "configured": true,
      "created_at": "2025-11-21T10:00:00"
    }
  ],
  "total": 1
}
```

#### GET /api/v1/connectors/user/authorized
Returns list of connectors authorized by the current user.

```json
Response:
{
  "success": true,
  "org_id": "tenant-a",
  "user_id": "user@example.com",
  "connectors": [
    {
      "provider": "slack",
      "org_id": "tenant-a",
      "user_id": "user@example.com",
      "authorized": true,
      "expired": false,
      "scopes": ["chat:write", "channels:read"],
      "created_at": "2025-11-21T10:00:00"
    }
  ],
  "total": 1
}
```

## File Structure

```
config/
├── oauth/                          # Org-scoped connector configs
│   ├── slack_tenant-a.json
│   ├── slack_tenant-b.json
│   ├── microsoft_tenant-a.json
│   └── google_tenant-b.json
│
├── tokens/                         # User-scoped OAuth tokens
│   ├── slack_tenant-a_user_at_example_com.json
│   ├── microsoft_tenant-a_admin_at_tenant-a_com.json
│   └── google_tenant-b_user_at_tenant-b_com.json
│
└── users.json                      # User database (demo)

core/
├── session_manager.py              # JWT auth & multi-tenant sessions
└── connector_manager.py            # Connector config & token storage
```

## Demo Users

The system includes demo users for testing:

| Email | Org ID | Role | Password |
|-------|--------|------|----------|
| admin@default.com | default | admin | any |
| user@tenant-a.com | tenant-a | user | any |
| admin@tenant-b.com | tenant-b | admin | any |

**Note:** In development mode, any password is accepted. In production, implement proper bcrypt password hashing.

## Usage Flow

### 1. Admin Configures Connector (One-time per org)

```
1. Admin logs in → receives JWT token
2. Admin goes to Connector Setup page
3. Admin fills in Slack client ID + secret for "tenant-a"
4. POST /api/v1/oauth/setup/slack
5. Config saved to config/oauth/slack_tenant-a.json
```

### 2. User Authorizes Connector (Per user)

```
1. User logs in → receives JWT token
2. User clicks "Authorize Slack"
3. System loads config/oauth/slack_tenant-a.json
4. Redirect to Slack OAuth with tenant-a's client_id
5. Callback receives authorization code
6. Exchange code for access_token
7. Save to config/tokens/slack_tenant-a_user_at_example_com.json
```

### 3. User Uses Connector

```
1. User sends message via Slack connector
2. System loads config/oauth/slack_tenant-a.json (connector config)
3. System loads config/tokens/slack_tenant-a_user_at_example_com.json (user token)
4. Make API call with user's access_token
```

## Security Best Practices

### Token Management
- JWT tokens expire after 24 hours (configurable)
- OAuth access tokens checked for expiration before use
- Refresh tokens used to renew expired access tokens

### Organization Isolation
- Users can only access their own organization's data
- `session_manager.verify_org_access()` enforces this
- Cross-org requests are blocked with HTTP 403

### Role-Based Access Control
- Admin role required for connector setup
- `session_manager.require_admin()` enforces this
- Regular users can only authorize (not configure)

### Secret Storage
- Connector secrets stored in JSON files (for demo)
- Production should use: AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault
- JWT secret should be environment variable, not hardcoded

## Next Steps

### Immediate Enhancements
1. **Implement OAuth Flows** - Add authorize + callback endpoints for each connector
2. **Add Frontend Auth** - Update dashboard to handle login and store JWT token
3. **Token Refresh** - Implement automatic token refresh before expiration
4. **Webhook Support** - Add endpoints for real-time event notifications

### Production Readiness
1. **Password Hashing** - Replace demo auth with bcrypt password verification
2. **Secret Management** - Move to external secret storage (Vault, AWS, Azure)
3. **Database Backend** - Replace JSON files with PostgreSQL/MongoDB
4. **Rate Limiting** - Add per-org/per-user rate limits
5. **Audit Logging** - Log all connector setup and authorization events
6. **Admin UI** - Build org management dashboard for admins

## Supported Connectors

| Connector | Setup Endpoint | OAuth Flow | Status |
|-----------|---------------|------------|--------|
| Microsoft 365 | ✅ /oauth/setup/microsoft | ⏳ Pending | Config only |
| Google Workspace | ✅ /oauth/setup/google | ⏳ Pending | Config only |
| Slack | ✅ /oauth/setup/slack | ⏳ Pending | Config only |
| Jira | ✅ /oauth/setup/jira | ⏳ Pending | Config only |
| ServiceNow | ✅ /oauth/setup/servicenow | ⏳ Pending | Config only |
| Confluence | ✅ /oauth/setup/confluence | ⏳ Pending | Config only |
| SharePoint | ✅ /oauth/setup/sharepoint | ⏳ Pending | Config only |
| GitHub | ✅ /oauth/setup/github | ⏳ Pending | Config only |

**Legend:**
- ✅ Complete
- ⏳ Pending
- ❌ Not started

## Testing

### Test Connector Setup (with curl)

```bash
# 1. Login as admin
curl -X POST http://localhost:8084/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"admin@default.com","password":"test"}'

# Save the token from response

# 2. Setup Slack connector
curl -X POST http://localhost:8084/api/v1/oauth/setup/slack \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -d '{
    "client_id":"123456789012.1234567890123",
    "client_secret":"abcdef1234567890",
    "org_id":"default"
  }'

# 3. Get configured connectors
curl -X GET http://localhost:8084/api/v1/connectors/configured \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE'
```

## Support

For questions or issues with the multi-tenant framework, please check:
- Session Manager: `core/session_manager.py`
- Connector Manager: `core/connector_manager.py`
- API Endpoints: `api_server.py` (search for "OAuth Setup Endpoints")
