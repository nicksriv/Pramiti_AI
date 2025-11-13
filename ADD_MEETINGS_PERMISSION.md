# Add OnlineMeetings Permission to Azure AD

Your Teams connector needs additional permission to create meetings.

## Quick Steps

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Azure Active Directory → App registrations
3. **Find**: "Agentic AI Teams Connector"
4. **Click**: API permissions (left sidebar)
5. **Click**: + Add a permission
6. **Select**: Microsoft Graph → Application permissions
7. **Search for**: `OnlineMeetings.ReadWrite.All`
8. **Check the box** next to OnlineMeetings.ReadWrite.All
9. **Click**: Add permissions
10. **IMPORTANT**: Click "Grant admin consent for [Your Organization]"
11. **Confirm**: Click "Yes"

## What This Permission Allows

✅ Create online meetings
✅ Update meeting details
✅ Delete meetings
✅ Get meeting information

## After Adding Permission

Run the test script:
```bash
python3 test_teams_connector.py
```

This will:
- ✅ Check connector status
- ✅ Get your Teams profile
- ✅ List your teams
- ✅ List channels
- ✅ Create a test meeting
- ✅ (Optional) Send a test message

## Expected Permissions (Total: 5)

After adding OnlineMeetings permission, you should have:
1. ✅ Team.ReadBasic.All
2. ✅ Channel.ReadBasic.All
3. ✅ ChannelMessage.Read.All
4. ✅ ChannelMessage.Send
5. ✅ **OnlineMeetings.ReadWrite.All** (NEW)

All should show "Granted for [Your Organization]" status.

---

**Ready to test?** Run: `python3 test_teams_connector.py`
