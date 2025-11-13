# Enterprise Connectors - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Start the API Server

```bash
cd /Users/nikhilsrivastava/Documents/GitHub/VSCode/Agentic-AI-Organization
python api_server.py
```

Server runs on: http://localhost:8084

### Step 2: Open Dashboard

Navigate to: http://localhost:8084/enhanced-dashboard.html

Click on "**Connectors**" tab

### Step 3: Create Your First Connector (Demo Mode)

#### Microsoft Teams

```bash
curl -X POST http://localhost:8084/api/v1/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "microsoft_teams",
    "name": "Teams - Demo",
    "description": "Demo Teams connector for testing",
    "auth_config": {
      "client_id": "demo-teams-client-12345",
      "client_secret": "demo-secret-67890",
      "tenant_id": "demo-tenant",
      "redirect_uri": "http://localhost:8084/oauth/callback"
    },
    "permissions": ["read_messages", "write_messages"]
  }'
```

#### Google Drive

```bash
curl -X POST http://localhost:8084/api/v1/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "google_drive",
    "name": "Drive - Demo",
    "description": "Demo Drive connector for testing",
    "auth_config": {
      "client_id": "demo-drive-client-12345",
      "client_secret": "demo-secret-67890",
      "redirect_uri": "http://localhost:8084/oauth/callback"
    },
    "permissions": ["read_files", "write_files", "search"]
  }'
```

### Step 4: Test Connection

In the dashboard:
1. Go to "**Connected**" tab
2. Find your connector
3. Click "**Test**" button
4. Should show: ✅ Connection test successful!

Or via API:

```bash
# Replace {connector_id} with actual ID from creation response
curl -X POST http://localhost:8084/api/v1/connectors/{connector_id}/test
```

### Step 5: Use in AI Agent

```python
# In your AI agent code
from core.agent_connector_integration import AgentConnectorBridge
from core.connectors import connector_manager

# Initialize bridge
bridge = AgentConnectorBridge(connector_manager)

# Send Teams message
bridge.teams_send_message(
    connector_id="microsoft_teams_xxx",
    team_id="your-team-id",
    channel_id="your-channel-id",
    message="Hello from AI!"
)

# List Drive files
files = bridge.drive_list_files(
    connector_id="google_drive_xxx",
    limit=10
)
```

## 🔐 Production Setup (Real Credentials)

### Microsoft Teams

1. **Azure Portal**: https://portal.azure.com
2. **Azure AD** → **App registrations** → **New registration**
3. **API Permissions** → Add:
   - Team.ReadBasic.All
   - Channel.ReadBasic.All
   - ChannelMessage.Read.All
   - ChannelMessage.Send
4. **Grant admin consent**
5. **Certificates & secrets** → Create secret
6. Copy: Client ID, Client Secret, Tenant ID

### Google Drive

1. **Google Cloud Console**: https://console.cloud.google.com
2. Create new project
3. **APIs & Services** → **Library** → Enable "Google Drive API"
4. **Credentials** → **Create OAuth client ID**
5. **Authorized redirect URIs**: http://localhost:8084/oauth/callback
6. Copy: Client ID, Client Secret

## 📊 Dashboard Features

### Available Connectors Tab
- Browse 14+ pre-configured platforms
- See capabilities and auth types
- Click "Setup" to configure

### Connected Tab
- View all active connectors
- Test connections
- Revoke access
- See status (connected/disconnected)

### Custom Integrations Tab
- Create custom connectors
- Support for any API
- Flexible auth options

## 🤖 AI Agent Endpoints

### Teams Operations

**Send Message**
```bash
POST /api/v1/connectors/{id}/teams/send_message
{
  "team_id": "xxx",
  "channel_id": "yyy",
  "message": "Hello!"
}
```

**Get Messages**
```bash
GET /api/v1/connectors/{id}/teams/messages?team_id=xxx&channel_id=yyy&limit=50
```

### Drive Operations

**List Files**
```bash
GET /api/v1/connectors/{id}/drive/files?limit=100
```

**Search Files**
```bash
GET /api/v1/connectors/{id}/drive/files?query=name contains 'report'
```

**Upload File**
```bash
POST /api/v1/connectors/{id}/drive/upload
{
  "file_name": "report.pdf",
  "content": "BASE64_CONTENT",
  "mime_type": "application/pdf"
}
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connector not found after restart | Recreate connector (in-memory storage) |
| Test fails in demo mode | Ensure client_id starts with "demo-" |
| OAuth error | Check redirect_uri matches exactly |
| Permission denied | Verify API permissions granted in cloud console |

## 📖 Full Documentation

See [CONNECTORS.md](./CONNECTORS.md) for complete documentation including:
- Architecture details
- All 14+ supported platforms
- Security features
- Advanced configuration
- API reference
- Production deployment

## 🎯 Common Use Cases

### 1. AI Agent Notifications
```python
# Send alert to Teams when task completes
bridge.teams_send_message(
    connector_id="teams_xxx",
    team_id="team-id",
    channel_id="alerts-channel",
    message="🤖 Task completed: Data analysis finished!"
)
```

### 2. Document Backup
```python
# Backup AI-generated report to Drive
import json
import base64

report_data = {"results": [...]}
content = json.dumps(report_data).encode()

file_id = bridge.drive_upload_file(
    connector_id="drive_xxx",
    file_name=f"ai_report_{datetime.now():%Y%m%d}.json",
    content=content,
    mime_type="application/json"
)
```

### 3. Monitor Team Discussions
```python
# Check for mentions of AI agent
messages = bridge.teams_get_messages(
    connector_id="teams_xxx",
    team_id="team-id",
    channel_id="general",
    limit=20
)

ai_mentions = [
    msg for msg in messages
    if "@AI" in msg.get("body", {}).get("content", "")
]
```

### 4. Search Company Documents
```python
# Find relevant documents for AI analysis
files = bridge.drive_search_files(
    connector_id="drive_xxx",
    query="quarterly financial report 2024"
)

for file in files:
    content = bridge.drive_get_file_content(
        connector_id="drive_xxx",
        file_id=file["id"]
    )
    # Analyze content...
```

## 🌟 Next Steps

1. ✅ Set up demo connectors (5 minutes)
2. ✅ Test in dashboard
3. ✅ Integrate into AI agent code
4. 🔜 Get production credentials
5. 🔜 Deploy to production server
6. 🔜 Add more connector types (Slack, Jira, etc.)

## 💡 Tips

- **Demo Mode**: Perfect for development - uses `demo-` prefix
- **Rate Limits**: 60/min, 1000/hr, 10000/day per connector
- **Security**: OAuth 2.0 with automatic token refresh
- **Testing**: Always test in demo mode first
- **Dashboard**: Use UI for easy setup, API for automation

---

**Need Help?**
- 📚 Full docs: [CONNECTORS.md](./CONNECTORS.md)
- 🔗 API docs: http://localhost:8084/docs
- 🖥️ Dashboard: http://localhost:8084/enhanced-dashboard.html
