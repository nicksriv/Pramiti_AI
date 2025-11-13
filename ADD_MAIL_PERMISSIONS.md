# Adding Outlook Mail Permissions to Azure AD

Your Teams connector now has email capabilities! Follow these steps to add the required Microsoft Graph Mail API permissions.

## Required Permissions

You need to add these **Application permissions** to your Azure AD app:

1. **Mail.Read** - Read mail in all mailboxes
2. **Mail.ReadWrite** - Read and write mail in all mailboxes  
3. **Mail.Send** - Send mail as any user

## Step-by-Step Guide

### 1. Go to Azure Portal
- Open https://portal.azure.com
- Navigate to **Azure Active Directory** → **App registrations**
- Find your app: **"Agentic AI Teams Connector"**

### 2. Add API Permissions
1. Click on **API permissions** in the left menu
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions** (not Delegated)
5. Search for and add these permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `Mail.Send`

### 3. Grant Admin Consent
1. After adding the permissions, you'll see them in the list
2. Click **✓ Grant admin consent for [Your Organization]**
3. Confirm by clicking **Yes**
4. Wait for the status to show green checkmarks

### 4. Verify Permissions
Your permissions list should now include:

**Current Permissions:**
- ✅ Team.ReadBasic.All
- ✅ Channel.ReadBasic.All
- ✅ ChannelMessage.Read.All
- ✅ ChannelMessage.Send

**New Permissions:**
- ✅ Mail.Read
- ✅ Mail.ReadWrite
- ✅ Mail.Send

**Optional (for calendar features):**
- Calendars.Read
- Calendars.ReadWrite

## Testing Email Functionality

Once permissions are added, you can test with:

```bash
python3 test_email_connector.py
```

This will let you:
- 📧 Send emails
- 📬 Read inbox messages
- 🔍 Search emails
- 📖 Get email details
- ✅ Mark emails as read/unread

## API Methods Available

### Send Email
```python
connector.send_email(
    to_recipients=["user@example.com"],
    subject="Test Email",
    body="<h1>Hello!</h1><p>This is a test.</p>",
    cc_recipients=["cc@example.com"],  # Optional
    is_html=True
)
```

### Read Emails
```python
# Get latest 10 emails from inbox
emails = connector.read_emails(folder="inbox", top=10)

# Get only unread emails
unread = connector.read_emails(folder="inbox", unread_only=True)

# Check sent items
sent = connector.read_emails(folder="sentitems", top=5)
```

### Search Emails
```python
results = connector.search_emails(query="meeting notes", top=20)
```

### Get Email Details
```python
email = connector.get_email_details(message_id="AAMkAG...")
# Returns full email with body, attachments, etc.
```

### Mark as Read
```python
connector.mark_email_as_read(message_id="AAMkAG...", is_read=True)
```

## Available Mail Folders

- `inbox` - Inbox
- `sentitems` - Sent Items
- `drafts` - Drafts
- `deleteditems` - Deleted Items
- `junkemail` - Junk Email

## Security Note

⚠️ **Important**: These are **Application permissions** which give access to ALL users' mailboxes in your organization. This is appropriate for service accounts and automation scenarios.

For user-specific access (only the signed-in user's mailbox), you would need **Delegated permissions** instead:
- Mail.Read
- Mail.ReadWrite
- Mail.Send

## Troubleshooting

**Error: "Insufficient privileges"**
- Make sure admin consent was granted
- Wait 5-10 minutes after granting consent
- Try refreshing the access token

**Error: "Access denied"**
- Verify the correct permissions are added
- Check that they're **Application** permissions, not Delegated
- Ensure admin consent shows green checkmarks

**401 Unauthorized**
- Access token might be expired
- Connector will auto-refresh on next API call
- Or manually recreate the connector

## Next Steps

After adding permissions:

1. ✅ Test email sending
2. ✅ Test reading inbox
3. ✅ Test search functionality
4. 🔄 Integrate with agent chat interface
5. 📝 Set up email automation workflows

## Resources

- [Microsoft Graph Mail API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [Mail permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference#mail-permissions)
