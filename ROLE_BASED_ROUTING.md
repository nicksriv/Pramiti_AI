# Role-Based Routing for Organization Assistant

## Overview
The Organization Assistant now provides **context-aware routing** based on user roles, ensuring that admins get technical setup guidance while regular users get usage instructions.

## Routing Logic

### For ADMIN / SUPER_ADMIN Users

When an admin asks about **Microsoft, Google, Slack, OAuth, or any integration**, they will be routed to the **Setup Assistant** which provides:

✅ **Technical Configuration Steps:**
- Client ID and Client Secret setup
- Tenant ID configuration
- API Key permissions
- OAuth application registration
- Redirect URI configuration
- Azure Portal / Google Cloud Console navigation
- Environment variable setup
- Integration-specific credentials

**Example Admin Queries That Trigger Setup Assistant:**
- "How do I set up Microsoft Teams integration?"
- "I want to configure Google Workspace"
- "Help me integrate Slack"
- "How to enable Office 365 authentication?"
- "Configure Azure OAuth for my organization"

### For Regular USER Role

Regular users asking about integrations will get:
- General usage instructions
- How to use features (not configure them)
- End-user focused guidance
- OAuth connection flow for personal accounts (via OAuth Assistant)

**Example User Queries:**
- "How do I connect my Microsoft account?" → OAuth Assistant (user-level connection)
- "What can this system do?" → General Agent (features overview)
- "I need to report an incident" → ITSM Agent

## Technical Implementation

### Backend Changes

**1. Updated ChatMessage Model** (`api_server.py` line 74)
```python
class ChatMessage(BaseModel):
    agent_id: Optional[str] = None
    message: str
    user_id: str = "user"
    session_id: Optional[str] = None
    role: Optional[str] = None      # NEW: User role for routing
    org_id: Optional[str] = None    # NEW: Organization context
```

**2. Role-Aware Routing Logic** (`api_server.py` line 1122)

The routing now checks:
1. **Active Setup Session** (highest priority) - continues existing setup flow
2. **Admin + Integration Keywords** - routes to Setup Assistant for technical guidance
   - Integration keywords: microsoft, google, slack, jira, azure, teams, oauth, etc.
   - Setup intent: "set up", "configure", "install", "integrate", "connect", "enable"
3. **Explicit Technical Keywords** - routes to Setup Assistant (any role)
   - "client id", "client secret", "tenant id", "api key", "credentials"
4. **User-Level OAuth** - routes to OAuth Assistant (regular users only)
   - "connect my account", "link my account", "authorize access"
5. **General Queries** - routes to General Agent

### Frontend Changes

**Updated User-Chat Request** (`enhanced-dashboard.html` line ~5644)

The frontend now sends user role information when available:
```javascript
const user = getAuthUser();
const requestBody = {
    message: message,
    user_id: user ? user.user_id : 'dashboard-user',
    agent_id: 'userbot',
    session_id: `userbot-${Date.now()}`
};

// Add role and org_id if user is logged in
if (user) {
    requestBody.role = user.role;
    requestBody.org_id = user.org_id;
}
```

## Usage Examples

### Admin User Experience

**Query:** "How do I set up Microsoft Teams integration?"

**Response from Setup Assistant:**
```
🔧 Microsoft Teams Integration Setup

To integrate Microsoft Teams, you'll need to configure OAuth credentials:

1. **Azure Portal Setup:**
   - Go to https://portal.azure.com
   - Navigate to "Azure Active Directory" → "App registrations"
   - Click "New registration"
   - Name: "Pramiti AI - Teams Integration"
   - Redirect URI: http://localhost:8084/api/v1/oauth/callback/microsoft

2. **Get Credentials:**
   - Copy "Application (client) ID" → This is MICROSOFT_CLIENT_ID
   - Go to "Certificates & secrets" → New client secret
   - Copy the secret value → This is MICROSOFT_CLIENT_SECRET
   - Your Tenant ID is in the Overview section

3. **Configure Permissions:**
   - Go to "API permissions"
   - Add Microsoft Graph permissions:
     - User.Read
     - Mail.Read
     - Calendars.Read
     - Team.ReadBasic.All

4. **Update .env File:**
   ```
   MICROSOFT_CLIENT_ID=your_application_id
   MICROSOFT_CLIENT_SECRET=your_secret_value
   MICROSOFT_TENANT_ID=your_tenant_id
   ```

5. **Restart Server:**
   ```bash
   pkill -f api_server.py
   python3 api_server.py
   ```

Would you like step-by-step guidance through any of these steps?
```

### Regular User Experience

**Query:** "How do I connect my Microsoft account?"

**Response from OAuth Assistant:**
```
📧 Connect Your Microsoft Account

I can help you connect your Microsoft account to access your emails, calendar, and files.

Click the link below to authenticate:
[Connect Microsoft Account] → Redirects to OAuth flow

After authentication, you'll be able to:
- Access your Outlook emails
- View your calendar
- Sync OneDrive files
- Collaborate in Teams

Would you like me to generate the authentication link?
```

## Routing Decision Matrix

| User Role | Query Type | Keywords Present | Routes To |
|-----------|-----------|------------------|-----------|
| ADMIN | Integration Setup | microsoft, setup | **Setup Assistant** (Technical) |
| ADMIN | Explicit Config | client id, tenant id | **Setup Assistant** (Technical) |
| USER | Personal Connection | connect my account | **OAuth Assistant** (User Flow) |
| USER | General Question | what can you do | **General Agent** |
| ANY | Active Session | N/A | **Setup Assistant** (Continue) |

## Benefits

✅ **Contextual Guidance**: Right information for the right user  
✅ **Security**: Admins handle credentials, users handle their own auth  
✅ **Efficiency**: No more generic responses for technical questions  
✅ **Better UX**: Role-appropriate language and instructions  
✅ **Tenant Isolation**: Org-specific setup guidance when org_id is provided

## Testing

**Test as Admin:**
```bash
# Login as admin
curl -X POST http://localhost:8084/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@tenant-a.com", "password": "admin123"}'

# Get token and use in chat
curl -X POST http://localhost:8084/user-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I set up Microsoft integration?",
    "user_id": "admin@tenant-a.com",
    "role": "ADMIN",
    "org_id": "tenant-a"
  }'
```

**Expected:** Detailed technical setup instructions

**Test as Regular User:**
```bash
curl -X POST http://localhost:8084/user-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I connect my Microsoft account?",
    "user_id": "user@tenant-a.com",
    "role": "USER",
    "org_id": "tenant-a"
  }'
```

**Expected:** User-friendly OAuth connection flow

## Future Enhancements

- [ ] Track which integrations are already configured per tenant
- [ ] Provide tenant-specific setup status
- [ ] Link to organization's existing OAuth apps
- [ ] Integration health monitoring
- [ ] Role-based permission requirements in responses
