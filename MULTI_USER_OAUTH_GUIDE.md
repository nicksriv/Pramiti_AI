# Multi-User OAuth Setup Guide

## Overview

This system allows **any user in your organization** to authenticate with their own Microsoft 365 or Google Workspace account and access their personal data (email, files, calendar) through the application.

## Architecture

### How It Works

1. **User-Specific Authentication**: Each user logs in with their own credentials
2. **Per-User Token Storage**: Tokens are stored separately for each user
   - Location: `.oauth_tokens/{connector_type}/{user_email}.json`
3. **Organization-Wide Access**: Any user from your organization can authenticate
4. **Automatic Token Management**: Tokens are automatically refreshed before expiry

### Supported Providers

- **Microsoft 365**: Email (Outlook), OneDrive, Calendar, Teams
- **Google Workspace**: Gmail, Google Drive, Google Calendar

## Setup Process

### 1. Configure Azure AD App (Microsoft 365)

```bash
# 1. Go to Azure Portal
https://portal.azure.com

# 2. Navigate to: Azure Active Directory > App registrations
# 3. Create or select your app
# 4. Add these Redirect URIs:
http://localhost:8084/api/v1/oauth/callback/microsoft
https://yourdomain.com/api/v1/oauth/callback/microsoft (for production)

# 5. Add these Delegated Permissions:
- offline_access
- User.Read
- Mail.Read, Mail.ReadWrite, Mail.Send
- Files.Read.All, Files.ReadWrite.All
- Calendars.Read, Calendars.ReadWrite
- OnlineMeetings.ReadWrite

# 6. Grant admin consent for your organization
```

### 2. Configure Google Cloud Project (Google Workspace)

```bash
# 1. Go to Google Cloud Console
https://console.cloud.google.com

# 2. Create or select your project
# 3. Enable these APIs:
- Gmail API
- Google Drive API
- Google Calendar API

# 4. Create OAuth 2.0 Client ID (Web application)
# 5. Add Authorized redirect URIs:
http://localhost:8084/api/v1/oauth/callback/google
https://yourdomain.com/api/v1/oauth/callback/google (for production)

# 6. Add these scopes:
- https://www.googleapis.com/auth/userinfo.email
- https://www.googleapis.com/auth/gmail.readonly
- https://www.googleapis.com/auth/gmail.send
- https://www.googleapis.com/auth/gmail.modify
- https://www.googleapis.com/auth/drive.readonly
- https://www.googleapis.com/auth/drive.file
- https://www.googleapis.com/auth/calendar
- https://www.googleapis.com/auth/calendar.events
```

## API Endpoints

### Start User Authentication

```bash
POST /api/v1/oauth/user/authorize

# Request Body (Microsoft 365):
{
  "user_email": "john.doe@yourcompany.com",
  "connector_type": "microsoft_teams",
  "client_id": "your-azure-client-id",
  "client_secret": "your-azure-client-secret",
  "tenant_id": "your-tenant-id"
}

# Request Body (Google Workspace):
{
  "user_email": "jane.smith@yourcompany.com",
  "connector_type": "google_workspace",
  "client_id": "your-google-client-id.apps.googleusercontent.com",
  "client_secret": "your-google-client-secret"
}

# Response:
{
  "success": true,
  "authorization_url": "https://login.microsoftonline.com/...",
  "state": "random-state-token",
  "user_email": "john.doe@yourcompany.com",
  "connector_type": "microsoft_teams"
}
```

### List Authenticated Users

```bash
GET /api/v1/oauth/users?connector_type=microsoft_teams

# Response:
{
  "connector_type": "microsoft_teams",
  "authenticated_users": [
    "john.doe@yourcompany.com",
    "jane.smith@yourcompany.com",
    "bob.johnson@yourcompany.com"
  ],
  "count": 3
}
```

### Revoke User Access

```bash
DELETE /api/v1/oauth/user/microsoft_teams/john.doe@yourcompany.com

# Response:
{
  "success": true,
  "message": "Tokens revoked for john.doe@yourcompany.com"
}
```

## Usage Examples

### Example 1: User Authenticates for Email Access

```python
import requests
import webbrowser

# Step 1: Start OAuth flow
response = requests.post(
    "http://localhost:8084/api/v1/oauth/user/authorize",
    json={
        "user_email": "john.doe@company.com",
        "connector_type": "microsoft_teams",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "tenant_id": "your-tenant-id"
    }
)

data = response.json()
auth_url = data["authorization_url"]

# Step 2: User logs in with their Microsoft account
print(f"Please visit: {auth_url}")
webbrowser.open(auth_url)

# Step 3: After user completes login, they can use the application
# The system automatically uses their authenticated session
```

### Example 2: Send Email as Authenticated User

```python
# Once user is authenticated, send email using their account
response = requests.post(
    "http://localhost:8084/api/v1/connectors/{connector_id}/send_email",
    json={
        "user_email": "john.doe@company.com",  # Specify which user
        "to": "recipient@example.com",
        "subject": "Hello from Multi-User OAuth",
        "body": "This email is sent from John's account!",
        "is_html": False
    }
)
```

### Example 3: Access Multiple Users' Calendars

```python
# List all authenticated users
response = requests.get(
    "http://localhost:8084/api/v1/oauth/users?connector_type=microsoft_teams"
)
users = response.json()["authenticated_users"]

# Get calendar events for each user
for user_email in users:
    response = requests.get(
        f"http://localhost:8084/api/v1/connectors/{{connector_id}}/calendar/events",
        params={"user_email": user_email, "limit": 10}
    )
    events = response.json()
    print(f"\nCalendar for {user_email}:")
    for event in events:
        print(f"  - {event['subject']} at {event['start']}")
```

## Security Considerations

### Token Storage

- Tokens are stored in `.oauth_tokens/` directory
- Each user's tokens are in separate files
- File permissions should be restricted (chmod 600)
- **Production**: Use encrypted database storage

### Best Practices

1. **Use HTTPS in production**
2. **Implement rate limiting** to prevent abuse
3. **Log all authentication events** for audit
4. **Set token expiration policies**
5. **Implement user session management**
6. **Add MFA support** where possible

### Token Lifecycle

```
User Login → OAuth Code → Exchange for Tokens → Store Tokens
     ↓              ↓              ↓                   ↓
 Access App    Redirect URI   Access Token      User-specific
                              Refresh Token      Storage
                                   ↓
                          Auto-refresh before expiry
```

## Integration with Agents

### Agent Context with User Identity

```python
# When an agent needs to perform actions, specify the user
class EmailAgent:
    def send_email_as_user(self, user_email: str, recipient: str, message: str):
        """Send email using a specific user's authenticated account"""
        # Get user's access token
        token = multi_user_oauth_manager.get_user_access_token(
            "microsoft_teams", 
            user_email
        )
        
        # Use token to send email via Microsoft Graph API
        # ...
```

## Troubleshooting

### Issue: User can't authenticate

**Solution**: Check that:
1. Redirect URI is correctly configured in Azure AD/Google Cloud
2. User's email matches the organization tenant
3. Required permissions are granted

### Issue: Tokens expired

**Solution**: 
- Tokens auto-refresh 5 minutes before expiry
- If refresh fails, user needs to re-authenticate
- Check that refresh_token is being stored

### Issue: Multiple users, same email

**Solution**:
- System stores one token set per email per connector type
- Last authentication overwrites previous tokens
- For true multi-tenancy, add tenant ID to storage key

## Next Steps

1. **Implement user session management** in frontend
2. **Add user profile display** showing who is authenticated
3. **Create admin dashboard** to view all authenticated users
4. **Add email delegation** (send on behalf of)
5. **Implement shared mailbox** access
6. **Add calendar sharing** between users

## Support

For issues or questions, refer to:
- Microsoft Graph API Docs: https://docs.microsoft.com/en-us/graph/
- Google Workspace API Docs: https://developers.google.com/workspace
