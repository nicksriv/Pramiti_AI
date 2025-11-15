# Setup Assistant Guide for IT Administrators

## Overview

The **Setup Assistant** is an intelligent agent that guides IT administrators through OAuth credential configuration via a conversational chat interface. This enables multi-organization (SaaS) deployments where each customer can have their own OAuth credentials without manual `.env` file editing.

## Features

✅ **Conversational Setup Flow** - Step-by-step credential collection
✅ **Input Validation** - GUID format, email domains, string length checks  
✅ **Session Management** - Resume interrupted setups, cancel anytime
✅ **Multi-Organization Support** - Separate config files per organization
✅ **Automatic .env Updates** - Default organization credentials saved to .env
✅ **Comprehensive Instructions** - Built-in Azure Portal and Google Cloud Console guides
✅ **Both Providers Supported** - Microsoft 365 and Google Workspace

## Quick Start

### Testing the Setup Assistant

1. **Start the API server** (if not already running):
   ```bash
   python3 api_server.py
   ```

2. **Open the dashboard**:
   ```
   http://localhost:8084/enhanced-dashboard
   ```

3. **Start setup by typing one of these commands**:
   - `setup microsoft` - Configure Microsoft 365 OAuth
   - `setup google` - Configure Google Workspace
   - `setup both` - Configure both providers

### Commands Reference

| Command | Description |
|---------|-------------|
| `setup microsoft` | Start Microsoft 365 OAuth configuration |
| `setup google` | Start Google Workspace OAuth configuration |
| `setup both` | Configure both providers sequentially |
| `setup status check` | View configured providers |
| `help` | Show available commands and instructions |
| `cancel` | Cancel current setup session |

## Microsoft 365 OAuth Setup

### Step 1: Start Setup
Type in chat: `setup microsoft`

The agent will display detailed Azure Portal instructions.

### Step 2: Provide Client ID
- Format: GUID (e.g., `12345678-1234-1234-1234-123456789abc`)
- Found in: Azure Portal → App registrations → Application (client) ID
- **Validation**: Must be valid GUID format

### Step 3: Provide Client Secret
- Format: String (minimum 10 characters)
- Found in: Azure Portal → Certificates & secrets → Client secrets → Value
- **Important**: Copy secret value immediately when created (won't show again)

### Step 4: Provide Tenant ID
- Format: GUID or "common"
- Found in: Azure Portal → App registrations → Directory (tenant) ID
- **Validation**: Must be valid GUID or "common" for multi-tenant

### What Happens Next
- Config saved to: `config/oauth/microsoft_{org_id}.json`
- If org_id is "default", "main", or "admin": `.env` file is also updated
- Success message with test instructions displayed

## Google Workspace OAuth Setup

### Step 1: Start Setup
Type in chat: `setup google`

The agent will display detailed Google Cloud Console instructions.

### Step 2: Provide Client ID
- Format: `*.apps.googleusercontent.com`
- Found in: Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs
- **Validation**: Must end with `.apps.googleusercontent.com`

### Step 3: Provide Client Secret
- Format: String (minimum 10 characters)
- Found in: Google Cloud Console → Credentials → Client secret
- **Validation**: Minimum length check

### What Happens Next
- Config saved to: `config/oauth/google_{org_id}.json`
- If org_id is "default", "main", or "admin": `.env` file is also updated
- Success message with test instructions displayed

## Configuration File Structure

### Microsoft Configuration
```json
{
  "provider": "microsoft",
  "client_id": "12345678-1234-1234-1234-123456789abc",
  "client_secret": "your_secret_value",
  "tenant_id": "87654321-4321-4321-4321-cba987654321",
  "redirect_uri": "http://localhost:8084/api/v1/oauth/callback/microsoft"
}
```

### Google Configuration
```json
{
  "provider": "google",
  "client_id": "123456789-abc.apps.googleusercontent.com",
  "client_secret": "GOCSPX-your_secret",
  "redirect_uri": "http://localhost:8084/api/v1/oauth/callback/google"
}
```

## Multi-Organization Support

### How It Works

1. **Organization ID**: Each setup session uses the `user_id` as the organization identifier
2. **Separate Configs**: Each org gets its own JSON file: `config/oauth/{provider}_{org_id}.json`
3. **Default Organization**: If `org_id` is "default", "main", or "admin", credentials are also saved to `.env`

### Example: 3 Organizations

```
config/oauth/
├── microsoft_acme-corp.json
├── microsoft_globex.json
├── google_acme-corp.json
└── google_globex.json
```

Each organization can have their own OAuth credentials without conflicts.

## Validation Features

### Microsoft Client ID Validation
- ✅ Must be valid GUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- ✅ All lowercase or uppercase accepted
- ❌ Rejects invalid formats with helpful error message

### Google Client ID Validation
- ✅ Must end with `.apps.googleusercontent.com`
- ❌ Rejects other domains or formats

### Client Secret Validation
- ✅ Minimum 10 characters
- ❌ Rejects short or empty values

### Tenant ID Validation (Microsoft)
- ✅ Valid GUID format
- ✅ "common" for multi-tenant apps
- ❌ Rejects invalid formats

## Testing the Setup

### Complete Flow Test (Microsoft)

```bash
# Step 1: Start setup
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "setup microsoft", "user_id": "test-org"}'

# Step 2: Provide Client ID
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "12345678-abcd-1234-ef00-123456789abc", "user_id": "test-org"}'

# Step 3: Provide Client Secret
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "MY_SECRET_VALUE_ABC123456789", "user_id": "test-org"}'

# Step 4: Provide Tenant ID
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "87654321-dcba-4321-ba00-cba987654321", "user_id": "test-org"}'

# Verify config was created
cat config/oauth/microsoft_test-org.json
```

### Complete Flow Test (Google)

```bash
# Step 1: Start setup
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "setup google", "user_id": "test-org"}'

# Step 2: Provide Client ID
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "123456789-abc.apps.googleusercontent.com", "user_id": "test-org"}'

# Step 3: Provide Client Secret
curl -X POST 'http://localhost:8084/user-chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "GOCSPX-MySecretValue123456", "user_id": "test-org"}'

# Verify config was created
cat config/oauth/google_test-org.json
```

## Session Management

### Active Sessions
- Sessions are stored in memory: `setup_assistant.setup_sessions`
- Each session tracks: provider, current step, collected data, user_id
- Sessions persist across messages until completion or cancellation

### Cancel Setup
Type: `cancel` at any point during setup to abort and clear the session

### Resume Setup
If you close the dashboard and return, type the setup command again to start fresh (old sessions don't persist across server restarts)

## Integration with API Routing

The Setup Assistant uses **session-aware routing** in `/user-chat` endpoint:

1. **Check Active Session** (Highest Priority)
   - If user has active setup session → Route to Setup Assistant
   - Enables multi-step credential collection

2. **Check Setup Keywords**
   - Keywords: `setup`, `configure`, `install`, `credentials`, `client id`, `oauth setup`, etc.
   - Routes to Setup Assistant for new setups

3. **Check OAuth Keywords**
   - Keywords: `login`, `authenticate`, `connect`, `microsoft`, `google`, etc.
   - Routes to OAuth Assistant for end-user authentication

## Troubleshooting

### "Invalid Client ID format" Error
- **Cause**: Client ID doesn't match expected GUID format
- **Solution**: Copy exact Client ID from Azure Portal (Application ID)
- **Format**: Must be `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### "Invalid Client ID" (Google)
- **Cause**: Client ID doesn't end with `.apps.googleusercontent.com`
- **Solution**: Copy exact Client ID from Google Cloud Console
- **Format**: Must be `{numbers}-{hash}.apps.googleusercontent.com`

### Config File Not Created
- **Cause**: Setup not completed (server restarted or process interrupted)
- **Solution**: Complete all 3 steps (Microsoft) or 2 steps (Google)
- **Verify**: Check `config/oauth/` directory for JSON files

### .env Not Updated
- **Cause**: Organization ID is not "default", "main", or "admin"
- **Solution**: Use org_id "default" when testing, or manually copy from JSON config
- **Note**: This is by design for multi-tenant support

### Routing to Wrong Agent
- **Cause**: Message doesn't contain setup keywords
- **Solution**: Include words like "setup", "configure", "oauth", "credentials"
- **Example**: Instead of "status", use "setup status check"

## Next Steps

### For Production Deployment

1. **Update OAuth Endpoints** to load org-specific credentials:
   ```python
   def load_oauth_credentials(org_id: str, provider: str):
       config_file = f"config/oauth/{provider}_{org_id}.json"
       if os.path.exists(config_file):
           with open(config_file) as f:
               return json.load(f)
       # Fallback to .env
       return {...}
   ```

2. **Add Organization Context** to chat:
   - Update `ChatMessage` model with `org_id` field
   - Dashboard sends org identifier with each message
   - OAuth endpoints use org-specific credentials

3. **Deploy to VPS**:
   ```bash
   git add agents/setup_assistant_agent.py api_server.py
   git commit -m "feat: Add Setup Assistant for multi-org OAuth setup"
   git push origin main
   
   ssh root@213.199.48.187
   cd ~/Pramiti_AI
   git pull
   docker-compose down pramiti-ai
   docker-compose build pramiti-ai
   docker-compose up -d pramiti-ai
   ```

4. **Create IT Admin Documentation**:
   - Step-by-step Azure Portal guide with screenshots
   - Google Cloud Console setup guide
   - Required permissions and API enablement
   - Redirect URI configuration

## Architecture

### Agent Hierarchy

```
Setup Assistant (IT Admins)
├── Configure OAuth credentials
├── Multi-organization support
└── Session management

OAuth Assistant (End Users)
├── Authenticate with configured providers
└── Generate authorization URLs

ITSM Agents (End Users)
├── Incident Management
├── Problem Analysis
└── Change Management
```

### Data Flow

```
1. IT Admin → "setup microsoft" → Setup Assistant
2. Setup Assistant → Collect credentials → Validate format
3. Setup Assistant → Save to config/oauth/microsoft_{org_id}.json
4. Setup Assistant → Update .env (if default org)
5. End User → "connect outlook" → OAuth Assistant
6. OAuth Assistant → Load credentials from config → Generate OAuth URL
7. End User → Click URL → Azure login → Callback → Token stored
```

## Summary

The Setup Assistant provides a **conversational, self-service OAuth configuration system** that:

✅ Eliminates manual .env editing
✅ Supports multiple organizations (SaaS model)
✅ Validates all inputs with helpful error messages
✅ Provides comprehensive setup instructions
✅ Handles both Microsoft 365 and Google Workspace
✅ Persists sessions across messages
✅ Integrates seamlessly with existing OAuth Assistant

**Ready to use!** Just type `setup microsoft` or `setup google` in the chat to get started.
