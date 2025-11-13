# Adding Pending Permissions to Azure AD

Your Teams connector needs additional permissions for **Meetings** and **Email** functionality.

## 📋 Current Status

### ✅ Already Configured:
- Team.ReadBasic.All
- Channel.ReadBasic.All
- ChannelMessage.Read.All
- ChannelMessage.Send

### ⏳ Pending Permissions:

#### For Teams Meetings:
- OnlineMeetings.ReadWrite.All

#### For Outlook Email:
- Mail.Read
- Mail.ReadWrite
- Mail.Send

---

## 🚀 Step-by-Step Setup (5 minutes)

### Step 1: Open Azure Portal

1. Go to **https://portal.azure.com**
2. Sign in with your Azure account
3. Navigate to **Azure Active Directory** (left sidebar)

### Step 2: Find Your App

1. Click on **App registrations** (left menu)
2. Find and click on: **"Agentic AI Teams Connector"**
   - Client ID: `da61b121-5a17-45da-858f-8ae422ba8451`

### Step 3: Add API Permissions

1. In the left menu, click **API permissions**
2. You'll see your current permissions listed
3. Click **+ Add a permission** button

### Step 4: Add Teams Meeting Permission

1. Select **Microsoft Graph**
2. Choose **Application permissions** (NOT Delegated)
3. In the search box, type: `OnlineMeetings`
4. Expand **OnlineMeetings** and check:
   - ✅ **OnlineMeetings.ReadWrite.All**
5. Click **Add permissions**

### Step 5: Add Mail Permissions

1. Click **+ Add a permission** again
2. Select **Microsoft Graph**
3. Choose **Application permissions** (NOT Delegated)
4. In the search box, type: `Mail`
5. Expand **Mail** and check these three:
   - ✅ **Mail.Read**
   - ✅ **Mail.ReadWrite**
   - ✅ **Mail.Send**
6. Click **Add permissions**

### Step 6: Grant Admin Consent

⚠️ **CRITICAL STEP** - Without this, permissions won't work!

1. You'll now see all permissions in the list with "Not granted" status
2. Click the button: **✓ Grant admin consent for [Your Organization Name]**
3. A popup will ask for confirmation - Click **Yes**
4. Wait 5-10 seconds for the page to refresh
5. **Verify**: All permissions should now show:
   - Status: Green checkmark ✅
   - "Granted for [Your Organization]"

---

## ✅ Final Permissions List

After completion, your API permissions should show:

### Microsoft Graph (Application permissions):

| Permission | Type | Status | Purpose |
|------------|------|--------|---------|
| **Team.ReadBasic.All** | Application | ✅ Granted | Read Teams info |
| **Channel.ReadBasic.All** | Application | ✅ Granted | Read channels |
| **ChannelMessage.Read.All** | Application | ✅ Granted | Read messages |
| **ChannelMessage.Send** | Application | ✅ Granted | Send messages |
| **OnlineMeetings.ReadWrite.All** | Application | ✅ Granted | **Create/manage meetings** |
| **Mail.Read** | Application | ✅ Granted | **Read emails** |
| **Mail.ReadWrite** | Application | ✅ Granted | **Read/write emails** |
| **Mail.Send** | Application | ✅ Granted | **Send emails** |

**Total: 8 permissions** - All should have green checkmarks!

---

## 🧪 Testing After Adding Permissions

### Wait Time
⏱️ **Wait 5-10 minutes** after granting consent for permissions to propagate through Microsoft's systems.

### Test Meetings Functionality

```bash
python3 test_teams_connector.py
```

Select option **4** to test meeting creation:
- Enter subject: "Test Meeting"
- Start time: `2025-11-14T14:00:00Z`
- End time: `2025-11-14T15:00:00Z`
- Attendees: your email or press Enter

**Expected Result:** Meeting created successfully with join URL!

### Test Email Functionality

```bash
python3 test_email_connector.py
```

Try these options:
1. **Send test email** - Send to yourself
2. **Read inbox** - View your recent emails
3. **Search emails** - Search for keywords

**Expected Result:** All operations work without "Insufficient privileges" errors!

---

## 📸 Visual Guide

### What You Should See in Azure Portal:

**Before granting consent:**
```
Permission name                    Type          Status
────────────────────────────────────────────────────────
OnlineMeetings.ReadWrite.All      Application   Not granted
Mail.Read                         Application   Not granted
Mail.ReadWrite                    Application   Not granted
Mail.Send                         Application   Not granted
```

**After granting consent (GREEN CHECKMARKS):**
```
Permission name                    Type          Status
────────────────────────────────────────────────────────────────
OnlineMeetings.ReadWrite.All      Application   ✅ Granted for [Org]
Mail.Read                         Application   ✅ Granted for [Org]
Mail.ReadWrite                    Application   ✅ Granted for [Org]
Mail.Send                         Application   ✅ Granted for [Org]
```

---

## 🎯 What Each Permission Does

### OnlineMeetings.ReadWrite.All
- ✅ Create Teams meetings programmatically
- ✅ Get meeting join URLs
- ✅ Add attendees to meetings
- ✅ Update meeting details
- ✅ Delete meetings
- 🤖 **Use Case:** AI agent schedules meetings on your behalf

### Mail.Read
- ✅ Read emails from all mailboxes
- ✅ Access inbox, sent items, drafts
- ✅ Get email metadata (subject, sender, date)
- ✅ Read email bodies
- 🤖 **Use Case:** AI agent monitors inbox for important messages

### Mail.ReadWrite
- ✅ Everything in Mail.Read
- ✅ Mark emails as read/unread
- ✅ Move emails between folders
- ✅ Delete emails
- ✅ Update email properties
- 🤖 **Use Case:** AI agent organizes your inbox

### Mail.Send
- ✅ Send emails as any user
- ✅ Send with attachments
- ✅ Send HTML emails
- ✅ Add CC/BCC recipients
- 🤖 **Use Case:** AI agent sends automated responses

---

## 🔒 Security Considerations

### Application Permissions vs Delegated

You're using **Application permissions** which means:

✅ **Pros:**
- Works without user sign-in
- Perfect for automation/background jobs
- AI agents can work 24/7

⚠️ **Important:**
- Access to **ALL** users' data in your organization
- Requires **admin consent**
- Should only be used by trusted applications

### Best Practices:
1. ✅ Only grant permissions you actually need
2. ✅ Regularly audit who has access
3. ✅ Keep client secret secure (already in .gitignore)
4. ✅ Monitor API usage through Azure portal
5. ✅ Review audit logs periodically

---

## 🆘 Troubleshooting

### "Insufficient privileges to complete the operation"

**Cause:** Admin consent not granted or not propagated yet

**Solution:**
1. Verify green checkmarks in Azure Portal
2. Wait 5-10 minutes
3. Restart your connector:
   ```bash
   ./setup_and_test_teams.sh
   ```

### "The application does not have permission..."

**Cause:** Wrong permission type (Delegated instead of Application)

**Solution:**
1. Go to Azure Portal → API permissions
2. Remove delegated permissions
3. Add Application permissions
4. Grant admin consent

### "Access denied"

**Cause:** Permission not in the list or typo in permission name

**Solution:**
1. Double-check permission names exactly as listed above
2. Make sure you selected "Application permissions"
3. Remove and re-add if needed

### "401 Unauthorized"

**Cause:** Access token expired

**Solution:**
1. Connector auto-refreshes tokens
2. Or manually recreate: `./setup_and_test_teams.sh`

---

## ✅ Verification Checklist

After adding permissions, verify:

- [ ] All 8 permissions show in Azure Portal
- [ ] All have green checkmarks ✅
- [ ] Status says "Granted for [Your Organization]"
- [ ] Type shows "Application" (not Delegated)
- [ ] Waited 5-10 minutes after granting
- [ ] Ran test scripts successfully
- [ ] No "Insufficient privileges" errors

---

## 🎉 Once Complete

After adding permissions, you can:

### Test Meetings:
```bash
python3 test_teams_connector.py
# Select option 4 to create a meeting
```

### Test Email:
```bash
python3 test_email_connector.py
# Test all email features
```

### Use in Code:
```python
# Create meeting
meeting = connector.create_online_meeting(
    subject="Team Sync",
    start_time="2025-11-14T10:00:00Z",
    end_time="2025-11-14T11:00:00Z",
    attendees=["team@company.com"]
)
print(f"Join URL: {meeting['join_url']}")

# Send email
connector.send_email(
    to_recipients=["user@company.com"],
    subject="Meeting Scheduled",
    body=f"<p>Meeting link: {meeting['join_url']}</p>"
)

# Read inbox
emails = connector.read_emails(folder="inbox", top=10)
```

---

## 📚 Additional Resources

- [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [OnlineMeetings API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting)
- [Mail API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [Application vs Delegated Permissions](https://learn.microsoft.com/en-us/graph/auth/auth-concepts#microsoft-graph-permissions)

---

## 🚀 Quick Start Command

After adding permissions:

```bash
# Test everything
python3 test_teams_connector.py    # Tests Teams + Meetings
python3 test_email_connector.py    # Tests Email

# Or recreate connector first
./setup_and_test_teams.sh
```

---

## 📞 Your App Details (for reference)

- **App Name:** Agentic AI Teams Connector
- **Client ID:** `da61b121-5a17-45da-858f-8ae422ba8451`
- **Tenant ID:** `2058f753-f5f8-4567-b3d8-0754be452611`
- **Connector ID:** `microsoft_teams_9672f5016dfe42dc`
- **Azure Portal:** https://portal.azure.com

---

## ✨ Summary

**Add 4 permissions:**
1. OnlineMeetings.ReadWrite.All
2. Mail.Read
3. Mail.ReadWrite
4. Mail.Send

**Type:** Application permissions  
**Admin Consent:** Required ✅  
**Time:** ~5 minutes  
**Result:** Full Teams + Email capabilities! 🚀
