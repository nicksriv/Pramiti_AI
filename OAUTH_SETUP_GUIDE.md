# Microsoft 365 OAuth 2.0 Setup Guide

## 🎯 Overview

This guide explains how to set up **delegated authentication** (OAuth 2.0 Authorization Code Flow) for Microsoft 365, enabling user-specific operations like email, OneDrive, and calendar access.

## ❓ Why OAuth 2.0?

### The Problem with App-Only Auth
Our previous implementation used **Client Credentials** (app-only authentication), which has limitations:
- ❌ Cannot access `/me` endpoints (user-specific data)
- ❌ Email operations fail with "delegated authentication required"
- ❌ OneDrive operations fail with same error
- ❌ Calendar access not possible

### The Solution: Delegated Auth
**OAuth 2.0 Authorization Code Flow** enables:
- ✅ Full access to user email, OneDrive, calendar
- ✅ User logs in once, tokens are refreshed automatically
- ✅ Better security with user consent
- ✅ Works with all Microsoft Graph APIs

---

## 🏗️ Architecture

### OAuth Flow Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    OAUTH 2.0 FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Your App                                                    │
│     │                                                           │
│     ├─► GET /oauth/authorize/{connector_id}                    │
│     │   (Generate authorization URL)                           │
│     │                                                           │
│  2. User Browser ──► Microsoft Login Page                      │
│     │                (User enters credentials)                 │
│     │                                                           │
│  3. Microsoft ──► Redirect with auth code                      │
│     │                                                           │
│  4. Your App                                                    │
│     │                                                           │
│     ├─► GET /oauth/callback?code=XXX&state=YYY                 │
│     │   (Exchange code for tokens)                             │
│     │                                                           │
│  5. Token Manager                                               │
│     │                                                           │
│     ├─► Save access_token + refresh_token                      │
│     │                                                           │
│  6. Your App ──► Use tokens for API calls                      │
│                                                                 │
│  7. Auto-refresh when token expires                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **OAuth Manager** (`core/oauth_manager.py`)
   - Manages token storage and refresh
   - Generates authorization URLs
   - Exchanges codes for tokens

2. **Connector Implementation** (`core/connector_implementations.py`)
   - Updated authenticate() method
   - Checks for refresh tokens first
   - Falls back to app-only auth if needed

3. **API Endpoints** (`api_server.py`)
   - `/api/v1/oauth/authorize/{connector_id}` - Start flow
   - `/api/v1/oauth/callback` - Handle callback
   - `/api/v1/oauth/status/{connector_id}` - Check status
   - `/api/v1/oauth/tokens/{connector_id}` - Revoke tokens (DELETE)

---

## 🚀 Quick Start

### Option 1: Interactive Setup Script (Recommended)

```bash
python3 setup_oauth.py
```

This script will:
1. Check if API server is running
2. Let you select existing connector or create new one
3. Generate OAuth URL and open browser
4. Guide you through Microsoft login
5. Verify authentication
6. Test email and OneDrive access

### Option 2: Manual Setup

#### Step 1: Ensure API Server is Running

```bash
python3 api_server.py
```

#### Step 2: Create or Get Connector ID

Create new connector:
```bash
curl -X POST http://localhost:8084/api/v1/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Microsoft 365 OAuth",
    "connector_type": "microsoft_teams",
    "auth_config": {
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "tenant_id": "common"
    }
  }'
```

Or list existing:
```bash
curl http://localhost:8084/api/v1/connectors
```

#### Step 3: Generate Authorization URL

```bash
curl http://localhost:8084/api/v1/oauth/authorize/CONNECTOR_ID
```

Response:
```json
{
  "success": true,
  "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...",
  "state": "random_state_string",
  "message": "Please visit the authorization URL to log in"
}
```

#### Step 4: Open URL in Browser

Copy the `authorization_url` and open it in your browser:
1. Log in with your Microsoft account
2. Review permissions:
   - Read and send email
   - Access OneDrive files
   - Manage calendar
   - Create meetings
3. Click "Accept"

#### Step 5: Callback Handling

After you accept, Microsoft redirects to:
```
http://localhost:8084/api/v1/oauth/callback?code=XXX&state=YYY
```

The server automatically:
- Validates the state parameter
- Exchanges code for tokens
- Saves access_token and refresh_token
- Updates connector status to CONNECTED
- Shows success page

#### Step 6: Verify Authentication

```bash
curl http://localhost:8084/api/v1/oauth/status/CONNECTOR_ID
```

Response:
```json
{
  "connector_id": "microsoft_teams_abc123",
  "has_tokens": true,
  "is_authenticated": true,
  "expires_at": "2025-11-14T14:30:00",
  "auth_type": "delegated"
}
```

---

## 🔐 Azure AD Configuration

### Required Settings

1. **Redirect URI**
   - Go to Azure Portal > App registrations > Your app
   - Authentication > Add platform > Web
   - Redirect URI: `http://localhost:8084/api/v1/oauth/callback`
   - Click "Configure"

2. **API Permissions** (Delegated)
   - Microsoft Graph > Delegated permissions
   - Add these permissions:
     - `offline_access` (required for refresh token)
     - `User.Read`
     - `Mail.Read`
     - `Mail.ReadWrite`
     - `Mail.Send`
     - `Files.Read.All`
     - `Files.ReadWrite.All`
     - `Calendars.Read`
     - `Calendars.ReadWrite`
     - `OnlineMeetings.ReadWrite`
   - Click "Grant admin consent"

3. **Token Configuration**
   - Optional claims not required
   - Default settings work fine

### Security Best Practices

- ✅ Use `state` parameter for CSRF protection
- ✅ Store tokens securely (currently in `.oauth_tokens/`)
- ✅ Refresh tokens automatically before expiry
- ✅ Use HTTPS in production
- ✅ Implement token encryption for production

---

## 📁 Token Storage

### Location
Tokens are stored in `.oauth_tokens/` directory:
```
.oauth_tokens/
  ├── microsoft_teams_abc123.json
  └── microsoft_teams_xyz789.json
```

### Token File Format
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJub...",
  "refresh_token": "0.AXsA...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "Mail.Read Mail.Send Files.Read.All...",
  "saved_at": "2025-11-13T19:30:00.123456",
  "expires_at": "2025-11-13T20:30:00.123456"
}
```

### Token Lifecycle

1. **Access Token** (1 hour lifespan)
   - Used for API requests
   - Automatically refreshed 5 minutes before expiry

2. **Refresh Token** (90 days lifespan)
   - Used to get new access tokens
   - Doesn't expire as long as it's used regularly
   - Rotated on each refresh (new refresh token returned)

---

## 🧪 Testing

### Test Email Access

```bash
python3 test_email_connector.py
```

Or manually:
```bash
curl -X POST http://localhost:8084/api/v1/connectors/CONNECTOR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "read_emails",
    "parameters": {"folder": "inbox", "top": 5}
  }'
```

### Test OneDrive Access

```bash
python3 test_onedrive_connector.py
```

Or manually:
```bash
curl -X POST http://localhost:8084/api/v1/connectors/CONNECTOR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list_onedrive_files",
    "parameters": {"top": 10}
  }'
```

### Check Authentication Status

```bash
curl http://localhost:8084/api/v1/oauth/status/CONNECTOR_ID
```

---

## 🔄 Token Refresh Flow

### Automatic Refresh

The connector automatically refreshes tokens when:
- Access token expires (within 5 minutes of expiry)
- API call fails with 401 Unauthorized

### Manual Refresh

Tokens are refreshed automatically, but you can trigger re-authentication:

```bash
# Delete tokens (requires re-authentication)
curl -X DELETE http://localhost:8084/api/v1/oauth/tokens/CONNECTOR_ID

# Re-run OAuth flow
curl http://localhost:8084/api/v1/oauth/authorize/CONNECTOR_ID
```

---

## 🐛 Troubleshooting

### Problem: "Connector not found"

**Solution**: Ensure API server is running and connector exists
```bash
curl http://localhost:8084/api/v1/connectors
```

### Problem: "Invalid redirect URI"

**Solution**: Add redirect URI in Azure AD
- Go to Azure Portal > App registrations
- Authentication > Add platform > Web
- Add: `http://localhost:8084/api/v1/oauth/callback`

### Problem: "Consent required"

**Solution**: Grant admin consent in Azure AD
- API permissions > Grant admin consent for [Your Org]

### Problem: "/me request is only valid with delegated authentication"

**Solution**: Complete OAuth flow to get delegated tokens
```bash
python3 setup_oauth.py
```

### Problem: "Token expired"

**Solution**: Tokens auto-refresh, but if refresh fails:
```bash
# Delete old tokens
curl -X DELETE http://localhost:8084/api/v1/oauth/tokens/CONNECTOR_ID

# Re-authenticate
python3 setup_oauth.py
```

---

## 📊 Comparison: App-Only vs Delegated

| Feature | App-Only (Client Credentials) | Delegated (OAuth 2.0) |
|---------|------------------------------|----------------------|
| User Login | ❌ Not required | ✅ Required (one-time) |
| Email Access | ❌ Requires `/users/{email}` | ✅ Works with `/me` |
| OneDrive Access | ❌ Requires `/users/{email}` | ✅ Works with `/me` |
| Calendar Access | ❌ Requires `/users/{email}` | ✅ Works with `/me` |
| User Consent | ❌ Admin consent only | ✅ User grants permissions |
| Token Refresh | ✅ Automatic | ✅ Automatic |
| Complexity | ✅ Simple | ⚠️ More complex |
| Best For | Admin operations | User-specific operations |

---

## 🎯 Next Steps

1. ✅ **Set up OAuth** with `python3 setup_oauth.py`
2. ✅ **Test email** with `python3 test_email_connector.py`
3. ✅ **Test OneDrive** with `python3 test_onedrive_connector.py`
4. 🔄 **Implement Calendar** methods (create_event, read_events, etc.)
5. 🔄 **Implement Meetings** methods (create_meeting, etc.)
6. 🔄 **Add to production** with database persistence

---

## 📚 API Reference

### Generate Authorization URL

```http
GET /api/v1/oauth/authorize/{connector_id}
```

Response:
```json
{
  "success": true,
  "authorization_url": "https://login.microsoftonline.com/...",
  "state": "random_string",
  "message": "Please visit the authorization URL..."
}
```

### OAuth Callback

```http
GET /api/v1/oauth/callback?code={code}&state={state}
```

Returns HTML success/error page

### Check OAuth Status

```http
GET /api/v1/oauth/status/{connector_id}
```

Response:
```json
{
  "connector_id": "microsoft_teams_abc123",
  "has_tokens": true,
  "is_authenticated": true,
  "expires_at": "2025-11-14T14:30:00",
  "auth_type": "delegated"
}
```

### Revoke Tokens

```http
DELETE /api/v1/oauth/tokens/{connector_id}
```

Response:
```json
{
  "success": true,
  "message": "OAuth tokens revoked successfully"
}
```

---

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**
   - OAuth requires HTTPS in production
   - Update redirect URI to `https://your-domain.com/api/v1/oauth/callback`

2. **Encrypt Tokens**
   - Add encryption layer in `OAuthTokenManager`
   - Use environment variables for encryption keys

3. **Database Storage**
   - Move from file storage to database
   - Implement proper access controls

4. **Rate Limiting**
   - Add rate limiting to OAuth endpoints
   - Prevent abuse of token refresh

5. **Audit Logging**
   - Log all OAuth events
   - Monitor for suspicious activity

---

## 💡 Tips

- **Refresh Token Lifespan**: Refresh tokens last 90 days if used regularly
- **Concurrent Sessions**: Each connector can have its own user authentication
- **Multi-User**: Create separate connectors for different users
- **Token Rotation**: Refresh tokens are automatically rotated on use
- **Offline Access**: `offline_access` scope is required for refresh tokens

---

## 📞 Support

For issues or questions:
1. Check logs in API server output
2. Verify Azure AD configuration
3. Test with `setup_oauth.py` script
4. Check token files in `.oauth_tokens/` directory

---

**🎉 You're now ready to use Microsoft 365 with full delegated authentication!**
