# Credentials Setup Guide

This guide explains how to set up OAuth credentials for Microsoft 365 and Google Workspace integration.

## Environment Variables

Create a `.env` file in the project root with your credentials. Use `.env.example` as a template:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials.

## Microsoft 365 / Azure AD Setup

### 1. Register Application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: Your App Name (e.g., "Agentic AI Organization")
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: 
     - Platform: Web
     - URI: `http://localhost:8084/api/v1/oauth/callback/microsoft`
5. Click **Register**

### 2. Get Client ID and Tenant ID

After registration:
- **Application (client) ID** → Copy to `MICROSOFT_CLIENT_ID` in `.env`
- **Directory (tenant) ID** → Copy to `MICROSOFT_TENANT_ID` in `.env`

### 3. Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Description: "OAuth Client Secret"
4. Expires: Choose duration (24 months recommended)
5. Click **Add**
6. **Copy the VALUE immediately** → Save to `MICROSOFT_CLIENT_SECRET` in `.env`
   - ⚠️ **Important**: Copy the VALUE, not the Secret ID
   - You won't be able to see it again!

### 4. Configure API Permissions

Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**

Add these permissions:
- `offline_access` - Maintain access to data you have given it access to
- `User.Read` - Sign in and read user profile
- `Mail.Read` - Read user mail
- `Mail.ReadWrite` - Read and write access to user mail
- `Mail.Send` - Send mail as a user
- `Files.Read.All` - Read all files that user can access
- `Files.ReadWrite.All` - Read and write all files that user can access
- `Calendars.Read` - Read user calendars
- `Calendars.ReadWrite` - Read and write user calendars
- `OnlineMeetings.ReadWrite` - Read and create user's online meetings

Click **Grant admin consent** for your organization.

### 5. Update .env File

```env
MICROSOFT_CLIENT_ID=your-application-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret-value
MICROSOFT_TENANT_ID=your-directory-tenant-id
```

## Google Workspace Setup

### 1. Create Project in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API

### 2. Configure OAuth Consent Screen

1. Go to **OAuth consent screen**
2. Choose **Internal** (for workspace) or **External**
3. Fill in required fields:
   - App name
   - User support email
   - Developer contact email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/calendar`

### 3. Create OAuth Client ID

1. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
2. Application type: **Web application**
3. Name: Your App Name
4. Authorized redirect URIs:
   - `http://localhost:8084/api/v1/oauth/callback/google`
5. Click **Create**
6. Download the JSON or copy:
   - **Client ID** → `GOOGLE_CLIENT_ID` in `.env`
   - **Client Secret** → `GOOGLE_CLIENT_SECRET` in `.env`

### 4. Update .env File

```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Security Best Practices

### Never Commit Secrets

Ensure your `.gitignore` includes:
```
.env
.env.local
.env.production
.oauth_tokens/
.vps_config
```

### Rotate Secrets Regularly

- Microsoft: Rotate client secrets every 6-24 months
- Google: Rotate OAuth credentials if compromised
- Update `.env` file when rotating

### Use Different Credentials for Environments

- **Development**: Use test credentials
- **Production**: Use separate, more restricted credentials
- **Testing**: Use dedicated test accounts

## Loading Environment Variables

The application automatically loads environment variables from `.env` using `python-dotenv`.

Install if needed:
```bash
pip install python-dotenv
```

In your code:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Access credentials
client_id = os.getenv("MICROSOFT_CLIENT_ID")
client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
tenant_id = os.getenv("MICROSOFT_TENANT_ID")
```

## Troubleshooting

### "Invalid client secret"
- Make sure you copied the SECRET VALUE, not the Secret ID
- Check for extra spaces or newlines
- Secret might have expired - create a new one

### "Unauthorized client"
- Verify redirect URI matches exactly (including http/https)
- Check API permissions are granted
- Admin consent may be required

### "Access denied"
- User hasn't consented to permissions
- Check if permissions are enabled in Azure AD/Google Console
- Verify tenant/workspace settings allow OAuth apps

## Verification

Test your credentials setup:

```bash
# Start the API server
python3 api_server.py

# Test OAuth flow through chat
curl -X POST http://localhost:8084/user-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Connect Outlook for test@yourcompany.com", "user_id": "test"}'
```

You should receive an authorization URL in the response.

## Next Steps

After configuring credentials:
1. Test Microsoft 365 authentication
2. Test Google Workspace authentication (if configured)
3. Configure production environment variables
4. Set up HTTPS for production redirect URIs
5. Update redirect URIs in Azure/Google for production domain

## Support

For issues:
- Azure AD: [Microsoft Documentation](https://docs.microsoft.com/azure/active-directory/)
- Google Workspace: [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
