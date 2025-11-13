#!/usr/bin/env python3
import requests
import json

API_BASE = "http://localhost:8084/api/v1"
CONNECTOR_ID = "microsoft_teams_7d4eeed3aa02ab27"

print("\n" + "="*80)
print("MICROSOFT 365 EMAIL & ONEDRIVE TEST")
print("="*80 + "\n")

# Test 1: Send Email
print("📧 TEST 1: Sending Email...")
email_data = {
    "to": "nikhilsrivastava@microsoft.com",
    "subject": "Pramiti AI - OAuth 2.0 Integration Success! 🎉",
    "body": """
    <html><body style="font-family: Arial, sans-serif;">
        <h2 style="color: #0078d4;">🎉 OAuth 2.0 Integration Test Successful!</h2>
        <p>This email was sent using delegated authentication via Microsoft 365 OAuth 2.0.</p>
        
        <h3 style="color: #107c10;">✅ Successfully Implemented Features:</h3>
        <ul>
            <li><strong>OAuth 2.0 Authorization Code Flow</strong> with PKCE</li>
            <li><strong>Automatic Token Refresh</strong> (5 min before expiry)</li>
            <li><strong>Email Operations</strong>: Send, Read, Search, Mark as Read</li>
            <li><strong>OneDrive Operations</strong>: List, Upload, Download, Share</li>
            <li><strong>File-based Token Storage</strong> for persistence</li>
        </ul>
        
        <hr style="border: 1px solid #ddd;">
        <p style="color: #666; font-size: 12px;">
            <strong>Technical Details:</strong><br>
            Connector ID: microsoft_teams_7d4eeed3aa02ab27<br>
            Auth Type: Delegated (User Context)<br>
            Timestamp: November 13, 2025<br>
            <br>
            Sent from <strong>Pramiti AI Organization System</strong><br>
            Powered by Microsoft Graph API
        </p>
    </body></html>
    """,
    "is_html": True
}

response = requests.post(f"{API_BASE}/connectors/{CONNECTOR_ID}/send_email", json=email_data)
if response.status_code == 200:
    print("✅ Email sent successfully!")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}\n")

# Test 2: Read Emails
print("📬 TEST 2: Reading Emails...")
response = requests.get(f"{API_BASE}/connectors/{CONNECTOR_ID}/read_emails?limit=10")
if response.status_code == 200:
    result = response.json()
    emails = result.get('emails', [])
    print(f"✅ Found {len(emails)} email(s)")
    for i, email in enumerate(emails[:3], 1):  # Show first 3
        print(f"\n  📧 Email {i}:")
        print(f"     From: {email.get('from', 'Unknown')}")
        print(f"     Subject: {email.get('subject', 'No subject')[:60]}...")
        print(f"     Received: {email.get('received_time', 'Unknown')}")
    if len(emails) > 3:
        print(f"\n  ... and {len(emails) - 3} more emails")
    print()
else:
    print(f"❌ Failed: {response.status_code} - {response.text}\n")

# Test 3: List OneDrive Files
print("📁 TEST 3: Listing OneDrive Files...")
response = requests.get(f"{API_BASE}/connectors/{CONNECTOR_ID}/onedrive/files")
if response.status_code == 200:
    result = response.json()
    files = result.get('files', [])
    print(f"✅ Found {len(files)} item(s) in OneDrive")
    for i, file in enumerate(files[:5], 1):  # Show first 5
        print(f"\n  📄 Item {i}:")
        print(f"     Name: {file.get('name', 'Unknown')}")
        print(f"     Type: {file.get('type', 'Unknown')}")
        if file.get('size'):
            print(f"     Size: {file.get('size')} bytes")
    if len(files) > 5:
        print(f"\n  ... and {len(files) - 5} more items")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
