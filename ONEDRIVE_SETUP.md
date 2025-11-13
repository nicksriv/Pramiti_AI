# OneDrive Integration - Setup & Testing

## ✅ OneDrive Capabilities Added!

Your Microsoft Teams connector now includes **full OneDrive file management**:

### 🗂️ Available OneDrive Methods:

1. **📁 `list_onedrive_files()`** - List files/folders, search across OneDrive
2. **⬇️ `download_onedrive_file()`** - Get download URLs for files
3. **⬆️ `upload_onedrive_file()`** - Upload files to OneDrive
4. **📂 `create_onedrive_folder()`** - Create new folders
5. **🗑️ `delete_onedrive_item()`** - Delete files/folders
6. **🔗 `share_onedrive_file()`** - Create sharing links

---

## 🔑 Required Permissions

You need to add OneDrive permissions to your existing Azure AD app.

### Add These Permissions:

Go to **Azure Portal** → **App registrations** → **"Agentic AI Teams Connector"** → **API permissions**

Add these **Application permissions**:

1. **Files.Read.All** - Read files in all site collections
2. **Files.ReadWrite.All** - Read and write files in all site collections

### Step-by-Step:

1. Click **+ Add a permission**
2. Select **Microsoft Graph**
3. Choose **Application permissions**
4. Search for `Files`
5. Check:
   - ✅ **Files.Read.All**
   - ✅ **Files.ReadWrite.All**
6. Click **Add permissions**
7. **Click "✓ Grant admin consent"** ⚠️ CRITICAL!
8. Verify green checkmarks ✅

---

## ✅ Complete Permissions List

After adding OneDrive permissions, you should have **10 total permissions**:

| Permission | Purpose | Status |
|------------|---------|--------|
| Team.ReadBasic.All | Teams | ✅ |
| Channel.ReadBasic.All | Channels | ✅ |
| ChannelMessage.Read.All | Messages | ✅ |
| ChannelMessage.Send | Send messages | ✅ |
| OnlineMeetings.ReadWrite.All | Meetings | ✅ |
| Mail.Read | Email | ✅ |
| Mail.ReadWrite | Email | ✅ |
| Mail.Send | Email | ✅ |
| **Files.Read.All** | **OneDrive** | **⏳ ADD** |
| **Files.ReadWrite.All** | **OneDrive** | **⏳ ADD** |

---

## 🧪 Testing OneDrive

Once permissions are added:

```bash
python3 test_onedrive_connector.py
```

This interactive test lets you:
- 📋 List files and folders
- 🔍 Search for files
- ⬆️ Upload test files
- 📂 Create folders
- ⬇️ Download files
- 🔗 Create sharing links
- 🗑️ Delete items

---

## 💡 Usage Examples

### List Files in Root
```python
files = connector.list_onedrive_files()
for file in files:
    print(f"{file['name']} ({file['type']}) - {file['size']} bytes")
```

### List Files in Specific Folder
```python
files = connector.list_onedrive_files(folder_path="/Documents")
```

### Search OneDrive
```python
results = connector.list_onedrive_files(search_query="report")
```

### Upload File
```python
with open("report.pdf", "rb") as f:
    content = f.read()

result = connector.upload_onedrive_file(
    file_name="Q4_Report.pdf",
    content=content,
    folder_path="/Documents"
)
print(f"Uploaded: {result['web_url']}")
```

### Create Folder
```python
folder = connector.create_onedrive_folder(
    folder_name="Project Files",
    parent_path="/Documents"
)
```

### Download File
```python
file_info = connector.download_onedrive_file(file_id="ABC123...")
# Use file_info['download_url'] to download
```

### Share File
```python
share_link = connector.share_onedrive_file(
    item_id="ABC123...",
    share_type="view"  # or "edit"
)
print(f"Share link: {share_link['link']}")
```

### Delete File
```python
success = connector.delete_onedrive_item(item_id="ABC123...")
```

---

## 🌐 Via API

Use the `/execute` endpoint:

### List Files
```bash
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list_onedrive_files",
    "parameters": {
      "folder_path": "/Documents",
      "top": 50
    }
  }'
```

### Upload File
```bash
# Content must be base64 encoded
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "upload_onedrive_file",
    "parameters": {
      "file_name": "test.txt",
      "content": "'$(base64 < test.txt)'",
      "folder_path": "/Documents"
    }
  }'
```

### Search Files
```bash
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list_onedrive_files",
    "parameters": {
      "search_query": "meeting notes"
    }
  }'
```

---

## 🎯 Use Cases

### 1. Automated File Organization
```python
# List all files in root
files = connector.list_onedrive_files()

# Create folders by file type
connector.create_onedrive_folder("PDFs")
connector.create_onedrive_folder("Images")

# Move files (upload to new location, delete old)
for file in files:
    if file['name'].endswith('.pdf'):
        # Download and re-upload to PDFs folder
        content = requests.get(file['download_url']).content
        connector.upload_onedrive_file(
            file_name=file['name'],
            content=content,
            folder_path="/PDFs"
        )
```

### 2. Backup System
```python
# Backup important files
files = connector.list_onedrive_files(folder_path="/Important")

backup_folder = connector.create_onedrive_folder("Backup_2025_11_13")

for file in files:
    if file['type'] == 'file':
        # Create backup
        content = requests.get(file['download_url']).content
        connector.upload_onedrive_file(
            file_name=file['name'],
            content=content,
            folder_path=f"/{backup_folder['name']}"
        )
```

### 3. Share Reports Automatically
```python
# Find latest report
reports = connector.list_onedrive_files(
    folder_path="/Reports",
    search_query="Q4"
)

if reports:
    latest = reports[0]
    # Create share link
    share_link = connector.share_onedrive_file(
        item_id=latest['id'],
        share_type="view"
    )
    
    # Send email with link
    connector.send_email(
        to_recipients=["team@company.com"],
        subject="Q4 Report Available",
        body=f"<p>View the Q4 report here: {share_link['link']}</p>"
    )
```

---

## 🔒 Security Notes

- **Application permissions** = Access to all users' OneDrive files
- Appropriate for service accounts and automation
- All operations are audited by Microsoft
- Files are stored in Microsoft's secure cloud

---

## 🆘 Troubleshooting

**"Insufficient privileges"**
- Add Files.Read.All and Files.ReadWrite.All
- Grant admin consent
- Wait 5-10 minutes

**"Item not found"**
- Check file/folder paths start with "/"
- Verify item ID is correct
- Ensure file exists in OneDrive

**"Access denied"**
- Verify permissions have green checkmarks
- Check admin consent was granted
- Try recreating connector

---

## 📊 Your Complete Connector

After adding OneDrive permissions, your connector has:

### ✅ Teams
- Read teams/channels
- Send messages
- Search messages

### ✅ Meetings
- Create online meetings
- Get join URLs
- Add attendees

### ✅ Email (Outlook)
- Send emails
- Read inbox
- Search emails
- Mark as read/unread

### ✅ OneDrive
- List/search files
- Upload/download
- Create folders
- Share files
- Delete items

**All integrated into ONE connector!** 🚀

---

## 🎉 Next Steps

1. **Add permissions** (Files.Read.All, Files.ReadWrite.All)
2. **Grant admin consent**
3. **Test OneDrive**: `python3 test_onedrive_connector.py`
4. **Test everything together** with your AI agents!

Your connector is now a **complete Microsoft 365 integration** with Teams, Meetings, Email, and OneDrive! 🎊
