# Outlook Email Integration - Quick Start

## ✅ What's Been Added

Your Microsoft Teams connector now has **full Outlook email capabilities**!

### New Email Methods Available:

1. **📧 Send Email** - `send_email()`
   - Send emails with HTML or plain text
   - Support for CC recipients
   - Automatic save to Sent Items

2. **📬 Read Emails** - `read_emails()`
   - Read from any folder (inbox, sent, drafts, etc.)
   - Filter by unread status
   - Customizable message count

3. **🔍 Search Emails** - `search_emails()`
   - Search by subject, sender, keywords
   - Full-text search across mailbox
   - Ranked results

4. **📖 Get Email Details** - `get_email_details()`
   - Full email content including body
   - Attachment information
   - Complete recipient lists

5. **✅ Mark as Read/Unread** - `mark_email_as_read()`
   - Update read status
   - Helps manage inbox

## 🚀 How to Get Started

### Step 1: Add Mail Permissions in Azure AD

You need to add these permissions to your Azure AD app:

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Open: **"Agentic AI Teams Connector"**
4. Click **API permissions** → **+ Add a permission**
5. Select **Microsoft Graph** → **Application permissions**
6. Add these three permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `Mail.Send`
7. Click **✓ Grant admin consent for [Your Organization]**

**📄 Detailed guide:** `ADD_MAIL_PERMISSIONS.md`

### Step 2: Test Email Integration

Your connector is already set up! Just test the new features:

```bash
python3 test_email_connector.py
```

This interactive test script lets you:
- Send test emails
- Read your inbox
- Search for messages
- View email details
- Mark emails as read/unread

### Step 3: Use in Your Code

```python
from core.connector_implementations import get_connector_implementation

# Get your connector
connector = get_connector_implementation(
    "microsoft_teams",
    "microsoft_teams_9672f5016dfe42dc",  # Your connector ID
    auth_config
)

# Send an email
result = connector.send_email(
    to_recipients=["user@example.com"],
    subject="Meeting Tomorrow",
    body="<p>Hi team,</p><p>Meeting at 2pm.</p>",
    is_html=True
)

# Read inbox
emails = connector.read_emails(folder="inbox", top=10)
for email in emails:
    print(f"{email['subject']} from {email['from']}")

# Search emails
results = connector.search_emails(query="project update", top=20)

# Get full email
email = connector.get_email_details(message_id="AAMkAG...")
print(email['body'])
```

### Step 4: Use via API

The new `/execute` endpoint supports all methods:

```bash
# Send email
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "send_email",
    "parameters": {
      "to_recipients": ["user@example.com"],
      "subject": "Test Email",
      "body": "Hello from API!"
    }
  }'

# Read inbox
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "read_emails",
    "parameters": {
      "folder": "inbox",
      "top": 10,
      "unread_only": false
    }
  }'

# Search emails
curl -X POST http://localhost:8084/api/v1/connectors/YOUR_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "search_emails",
    "parameters": {
      "query": "meeting notes",
      "top": 20
    }
  }'
```

## 📚 Available Email Folders

- `inbox` - Inbox
- `sentitems` - Sent Items
- `drafts` - Drafts
- `deleteditems` - Deleted Items
- `junkemail` - Junk Email

## 🎯 Example Use Cases

### 1. Automated Email Response
```python
# Read unread emails
unread = connector.read_emails(folder="inbox", unread_only=True)

for email in unread:
    if "urgent" in email['subject'].lower():
        # Send auto-response
        connector.send_email(
            to_recipients=[email['from']],
            subject=f"Re: {email['subject']}",
            body="Received your urgent email. Will respond shortly."
        )
        # Mark as read
        connector.mark_email_as_read(email['id'], is_read=True)
```

### 2. Email Digest
```python
# Get today's emails
emails = connector.read_emails(folder="inbox", top=50)

# Create summary
digest = "<h2>Today's Email Summary</h2><ul>"
for email in emails[:10]:
    digest += f"<li><b>{email['subject']}</b> from {email['from_name']}</li>"
digest += "</ul>"

# Send digest
connector.send_email(
    to_recipients=["manager@company.com"],
    subject="Daily Email Digest",
    body=digest
)
```

### 3. Email Search & Archive
```python
# Find all emails from specific sender
results = connector.search_emails(query="from:john@company.com")

for email in results:
    # Get full details
    details = connector.get_email_details(email['id'])
    # Process or archive
    if "completed" in details['subject']:
        connector.mark_email_as_read(email['id'], is_read=True)
```

## 🔒 Security Notes

- These are **Application permissions** (access to all mailboxes)
- Appropriate for service accounts and automation
- All API calls are logged
- Credentials encrypted in connector storage

## 📊 What's Next?

1. ✅ **Test email integration** - Run test_email_connector.py
2. 🤖 **Integrate with AI agents** - Add email capabilities to agent chat
3. 📧 **Email automation** - Create workflows for common tasks
4. 📈 **Analytics** - Track email patterns and response times
5. 🔔 **Notifications** - Alert on important emails

## 🆘 Troubleshooting

**"Insufficient privileges" error:**
- Make sure you added Mail.Read, Mail.ReadWrite, Mail.Send
- Ensure admin consent was granted
- Wait 5-10 minutes after granting consent

**"Connector not found" error:**
- Your connector ID is: `microsoft_teams_9672f5016dfe42dc`
- If server restarted, run: `./setup_and_test_teams.sh`

**401 Unauthorized:**
- Access token may have expired
- Connector will auto-refresh on next call

## 📖 Documentation

- **Setup Guide:** `ADD_MAIL_PERMISSIONS.md`
- **Test Script:** `test_email_connector.py`
- **API Reference:** http://localhost:8084/docs

## 🎉 You're All Set!

Your connector now has full email capabilities. Just add the Mail permissions in Azure AD and start testing!

**Current Connector:**
- ID: `microsoft_teams_9672f5016dfe42dc`
- Status: Connected ✅
- Platform: Microsoft Teams + Outlook
- Capabilities: Teams, Meetings, Email

**Commands:**
```bash
# Add permissions (see ADD_MAIL_PERMISSIONS.md)
# Then test:
python3 test_email_connector.py
```
