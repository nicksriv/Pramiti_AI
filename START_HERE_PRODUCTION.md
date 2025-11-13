# 🚀 Production Credentials Setup - Quick Guide

## Three Ways to Set Up Real Credentials

### 🎯 Option 1: Interactive Wizard (Easiest)

```bash
python3 setup_production_connectors.py
```

The wizard will:
- ✅ Guide you step-by-step
- ✅ Show you exactly what to copy from Azure/Google Cloud
- ✅ Create connectors automatically
- ✅ Test connections
- ✅ Provide connector IDs

### 📖 Option 2: Follow Detailed Guide

See **PRODUCTION_CREDENTIALS_SETUP.md** for:
- Screenshot-by-screenshot instructions
- Exact steps for Azure AD and Google Cloud
- Troubleshooting tips
- Security best practices

### 🖥️ Option 3: Use Dashboard UI

1. Open: http://localhost:8084/enhanced-dashboard.html
2. Click **Connectors** tab
3. Go to **Available Connectors**
4. Click **Setup** on Microsoft Teams or Google Drive
5. Enter your credentials
6. Click **Create Connector**

---

## 📋 What You Need

### Microsoft Teams
From Azure Portal (portal.azure.com):
1. **Client ID** (Application ID)
2. **Client Secret** (from Certificates & secrets)
3. **Tenant ID** (Directory ID)

**Time**: ~10 minutes  
**Cost**: Free

### Google Drive
From Google Cloud Console (console.cloud.google.com):
1. **Client ID** (OAuth 2.0 client)
2. **Client Secret** (OAuth 2.0 client)

**Time**: ~10 minutes  
**Cost**: Free

---

## 🎬 Getting Started

### Step 1: Start API Server (if not running)

```bash
python3 api_server.py
```

Verify: http://localhost:8084/enhanced-dashboard.html

### Step 2: Choose Your Path

**For Microsoft Teams**:
```bash
# Interactive wizard
python3 setup_production_connectors.py

# Or follow the guide in PRODUCTION_CREDENTIALS_SETUP.md
```

**For Google Drive**:
```bash
# Interactive wizard
python3 setup_production_connectors.py

# Or follow the guide in PRODUCTION_CREDENTIALS_SETUP.md
```

### Step 3: Get Credentials

#### Microsoft Teams (Azure Portal)
1. Go to: https://portal.azure.com
2. Azure Active Directory → App registrations → New registration
3. Name: `Agentic AI Teams Connector`
4. Redirect URI: `http://localhost:8084/oauth/callback`
5. Create → Copy Client ID and Tenant ID
6. Certificates & secrets → New secret → Copy value
7. API permissions → Add Microsoft Graph permissions:
   - Team.ReadBasic.All
   - Channel.ReadBasic.All
   - ChannelMessage.Read.All
   - ChannelMessage.Send
8. Grant admin consent

#### Google Drive (Google Cloud)
1. Go to: https://console.cloud.google.com
2. Create new project: `Agentic AI Drive Connector`
3. Enable Google Drive API
4. Create OAuth consent screen
5. Create OAuth client ID (Web application)
6. Redirect URI: `http://localhost:8084/oauth/callback`
7. Copy Client ID and Client Secret

### Step 4: Enter Credentials

Run the wizard and follow prompts:
```bash
python3 setup_production_connectors.py
```

Or use the dashboard at: http://localhost:8084/enhanced-dashboard.html

### Step 5: Test & Use

The wizard will test your connection automatically!

You'll get a **Connector ID** like:
- `microsoft_teams_abc123def456`
- `google_drive_xyz789abc123`

Use this ID in your AI agent code.

---

## 🧪 Quick Test

After setup, test your connector:

```bash
# Replace {connector_id} with your actual ID
curl -X POST http://localhost:8084/api/v1/connectors/{connector_id}/test
```

**Success Response**:
```json
{
  "success": true,
  "status": "connected",
  "message": "Connection test successful",
  "test_result": {
    "service": "Microsoft Teams",
    "api_version": "v1.0"
  }
}
```

If you see `"demo mode"` in the message, you're still using demo credentials!

---

## 💻 Using in AI Agent Code

Once you have your connector ID:

```python
from core.agent_connector_integration import AgentConnectorBridge
from core.connectors import connector_manager

# Initialize bridge
bridge = AgentConnectorBridge(connector_manager)

# Send Teams message
bridge.teams_send_message(
    connector_id="microsoft_teams_abc123def456",  # Your connector ID
    team_id="19:xxx@thread.tacv2",               # From Teams URL
    channel_id="19:yyy@thread.tacv2",            # From Teams URL
    message="🤖 Hello from production API!"
)

# List Drive files
files = bridge.drive_list_files(
    connector_id="google_drive_xyz789abc123",    # Your connector ID
    limit=10
)
print(f"Found {len(files)} files")
```

---

## 📚 Documentation

### Quick References
- **This Guide**: START_HERE.md (you are here!)
- **Setup Guide**: PRODUCTION_CREDENTIALS_SETUP.md
- **Full Documentation**: CONNECTORS.md
- **Quick Start**: CONNECTORS_QUICKSTART.md

### Live Resources
- **Dashboard**: http://localhost:8084/enhanced-dashboard.html
- **API Docs**: http://localhost:8084/docs
- **Connected Tab**: View all your connectors

---

## 🆘 Troubleshooting

### "Cannot connect to API server"
```bash
# Start the server
python3 api_server.py
```

### "Connection test shows demo mode"
- Your client_id starts with "demo-"
- Enter real credentials from Azure/Google Cloud

### "Permission denied" errors
- **Teams**: Ensure admin consent was granted in Azure
- **Drive**: Verify OAuth consent screen is configured

### "Connector not found" after restart
- Connectors are in-memory (reset on restart)
- Re-create them or add database persistence

---

## ✅ Success Checklist

- [ ] API server is running
- [ ] Ran setup wizard OR
- [ ] Followed manual setup guide OR
- [ ] Used dashboard UI
- [ ] Created connector(s)
- [ ] Tested connection (shows production, not demo)
- [ ] Got connector ID(s)
- [ ] Can view in dashboard Connected tab
- [ ] Ready to use in AI agent code!

---

## 🎉 You're Ready!

Once your connectors show "connected" status (not demo mode):

✅ **AI agents can now**:
- Send/read Microsoft Teams messages
- Upload/download Google Drive files
- Search across both platforms
- Access real production data

🚀 **Next Steps**:
1. Integrate connectors into your AI agent workflows
2. Set up more connector types (Slack, Jira, etc.)
3. Build automation workflows
4. Monitor usage in dashboard

---

**Questions?** Check:
- PRODUCTION_CREDENTIALS_SETUP.md (detailed guide)
- CONNECTORS.md (full documentation)
- http://localhost:8084/docs (API reference)

**Ready to start?** → `python3 setup_production_connectors.py`
