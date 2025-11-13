# Google Drive Connector Setup

## 🚀 Quick Start

Your interactive setup script is ready! Just run:

```bash
python3 setup_google_drive.py
```

This will guide you through:
1. ✅ Creating Google Cloud project
2. ✅ Enabling Drive API
3. ✅ Configuring OAuth consent screen
4. ✅ Creating OAuth client credentials
5. ✅ Getting refresh token
6. ✅ Creating Drive connector

**Time:** ~10-15 minutes

---

## 📋 What You'll Need

- Google Cloud account (free tier works)
- Browser access to Google Cloud Console
- Terminal access to run the setup script

---

## 🎯 Detailed Steps

The script will walk you through each step, but here's an overview:

### 1. Create Google Cloud Project
- Go to: https://console.cloud.google.com
- Create new project: "Agentic AI Drive Connector"

### 2. Enable Google Drive API
- Navigate to: APIs & Services > Library
- Search for "Google Drive API"
- Click ENABLE

### 3. Configure OAuth Consent Screen
- Go to: OAuth consent screen
- User Type: External
- App name: "Agentic AI Drive Integration"
- Add scopes:
  - `https://www.googleapis.com/auth/drive`
  - `https://www.googleapis.com/auth/drive.file`

### 4. Create OAuth Client
- Go to: Credentials
- Create OAuth client ID
- Type: Web application
- Name: "Agentic AI Drive Client"
- Redirect URI: `http://localhost:8084/oauth/callback`

### 5. Get Refresh Token
- The script will generate an authorization URL
- You'll sign in with Google
- Grant Drive access
- Copy the authorization code from the redirect URL
- Script exchanges it for a refresh token

### 6. Create Connector
- Script saves credentials securely
- Creates Drive connector via API
- Ready to use!

---

## 🧪 Testing

After setup, test your connector:

```bash
python3 test_drive_connector.py
```

This interactive test lets you:
- 📋 List files
- 🔍 Search for files
- ⬆️ Upload files
- 📁 Create folders
- ⬇️ Download files

---

## 💡 Google Drive Methods Available

### List Files
```python
files = connector.list_files(query="mimeType='image/png'", limit=50)
```

### Search Files
```python
results = connector.search_files(query="report")
```

### Upload File
```python
file_id = connector.upload_file(
    file_name="document.pdf",
    content=pdf_bytes,
    mime_type="application/pdf",
    folder_id="optional_folder_id"
)
```

### Create Folder
```python
folder_id = connector.create_folder(
    folder_name="Project Files",
    parent_id="optional_parent_id"
)
```

### Download File
```python
content = connector.get_file_content(file_id="file_id_here")
```

---

## 🌐 Via API

Use the `/execute` endpoint:

```bash
# List files
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list_files",
    "parameters": {
      "limit": 50
    }
  }'

# Upload file
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "upload_file",
    "parameters": {
      "file_name": "test.txt",
      "content": "'$(base64 < test.txt)'",
      "mime_type": "text/plain"
    }
  }'
```

---

## 🔑 Credentials & Security

The setup script saves your credentials to:
- `drive_credentials.txt` - Human-readable format
- `drive_credentials.json` - JSON format for programs

Both files are:
- ✅ Added to `.gitignore` (won't be committed)
- ✅ Stored locally only
- ✅ Used to create connector with refresh token

**Keep these files secure!**

---

## 🎯 Example Use Cases

### 1. Automated Backup
```python
# Backup important files from OneDrive to Google Drive
onedrive_files = ms_connector.list_onedrive_files(folder_path="/Important")

for file in onedrive_files:
    if file['type'] == 'file':
        # Download from OneDrive
        content = requests.get(file['download_url']).content
        
        # Upload to Google Drive
        drive_connector.upload_file(
            file_name=file['name'],
            content=content,
            folder_id=backup_folder_id
        )
```

### 2. Cross-Platform File Sync
```python
# Sync files between OneDrive and Google Drive
def sync_files(source, destination):
    source_files = source.list_files()
    dest_files = destination.list_files()
    
    # Find files in source but not in destination
    for file in source_files:
        if file['name'] not in [f['name'] for f in dest_files]:
            content = source.get_file_content(file['id'])
            destination.upload_file(file['name'], content)
```

### 3. Document Processing
```python
# Find all PDFs, process them, save to Drive
pdfs = drive_connector.search_files(query="*.pdf")

for pdf in pdfs:
    content = drive_connector.get_file_content(pdf['id'])
    # Process PDF
    processed = process_document(content)
    # Upload processed version
    drive_connector.upload_file(
        file_name=f"processed_{pdf['name']}",
        content=processed,
        mime_type="application/pdf"
    )
```

---

## 🆘 Troubleshooting

**"Invalid client" error**
- Check Client ID and Secret are correct
- Verify redirect URI matches exactly: `http://localhost:8084/oauth/callback`

**"Access denied" error**
- Make sure you granted all requested permissions
- Try re-running OAuth flow with `prompt=consent`

**"Refresh token not received"**
- Ensure you included `access_type=offline` in authorization URL
- Use `prompt=consent` to force new token generation
- Script handles this automatically

**"API not enabled"**
- Go to Google Cloud Console
- APIs & Services > Library
- Enable "Google Drive API"

---

## ✅ Complete Integration

After setting up Google Drive, you'll have:

| Service | Capabilities | Connector |
|---------|-------------|-----------|
| **Microsoft Teams** | Messages, channels | Teams connector |
| **Meetings** | Create meetings, join URLs | Teams connector |
| **Outlook Email** | Send, read, search | Teams connector |
| **OneDrive** | Files, folders, sharing | Teams connector |
| **Google Drive** | Files, folders, search | Drive connector |

**2 connectors, 5 cloud services!** 🚀

---

## 📚 Next Steps

1. **Run setup:** `python3 setup_google_drive.py`
2. **Test Drive:** `python3 test_drive_connector.py`
3. **Integrate with agents** - Your AI agents can now:
   - Store files in Drive
   - Retrieve documents
   - Search across both OneDrive and Google Drive
   - Cross-platform file operations

---

## 🎉 You're Building Enterprise-Level Integration!

Your system now supports:
- ✅ Microsoft 365 (10 permissions, 4 services)
- ✅ Google Drive (OAuth 2.0, refresh tokens)
- ✅ RESTful API
- ✅ AI agent integration
- ✅ Secure authentication
- ✅ Production-ready

**Ready to transform how your AI agents work with cloud files!** 🌟
