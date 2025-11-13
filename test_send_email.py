#!/usr/bin/env python3
"""Test sending email via Microsoft 365 OAuth"""

import requests
import json

API_BASE = "http://localhost:8084/api/v1"
CONNECTOR_ID = "microsoft_teams_285b4ada6b2c5eca"

def test_send_email():
    """Test sending an email"""
    print("\n" + "="*80)
    print("TESTING EMAIL SEND".center(80))
    print("="*80 + "\n")
    
    # Prepare email data
    email_data = {
        "to": "nikhilsrivastava@microsoft.com",  # Sending to yourself
        "subject": "Test Email from Pramiti AI - OAuth Success!",
        "body": """
        <html>
        <body>
            <h2>🎉 OAuth 2.0 Integration Test Successful!</h2>
            <p>This email was sent using delegated authentication via Microsoft 365 OAuth 2.0.</p>
            
            <h3>✅ Successfully Implemented:</h3>
            <ul>
                <li>OAuth 2.0 Authorization Code Flow</li>
                <li>Automatic token refresh</li>
                <li>Email sending with delegated permissions</li>
                <li>OneDrive file access</li>
            </ul>
            
            <p><strong>Connector ID:</strong> microsoft_teams_285b4ada6b2c5eca</p>
            <p><strong>Auth Type:</strong> Delegated (User context)</p>
            <p><strong>Timestamp:</strong> November 13, 2025</p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent from Pramiti AI Organization System<br>
                Powered by Microsoft Graph API
            </p>
        </body>
        </html>
        """,
        "is_html": True
    }
    
    # Send email
    print(f"📧 Sending test email to: {email_data['to']}")
    print(f"📝 Subject: {email_data['subject']}\n")
    
    response = requests.post(
        f"{API_BASE}/connectors/{CONNECTOR_ID}/send_email",
        json=email_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Email sent successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"❌ Failed to send email")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_read_emails():
    """Test reading emails"""
    print("\n" + "="*80)
    print("TESTING EMAIL READ".center(80))
    print("="*80 + "\n")
    
    print("📬 Reading last 5 emails from inbox...\n")
    
    response = requests.get(
        f"{API_BASE}/connectors/{CONNECTOR_ID}/read_emails",
        params={"limit": 5}
    )
    
    if response.status_code == 200:
        result = response.json()
        emails = result.get('emails', [])
        
        print(f"✅ Found {len(emails)} email(s)")
        
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Email {i}:")
            print(f"   From: {email.get('from', 'Unknown')}")
            print(f"   Subject: {email.get('subject', 'No subject')}")
            print(f"   Received: {email.get('received_time', 'Unknown')}")
            print(f"   Has attachments: {email.get('has_attachments', False)}")
        
        return True
    else:
        print(f"❌ Failed to read emails")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MICROSOFT 365 EMAIL FUNCTIONALITY TEST".center(80))
    print("="*80)
    
    # Test sending email
    send_success = test_send_email()
    
    # Wait a moment, then read emails
    if send_success:
        import time
        print("\n⏳ Waiting 3 seconds for email to be delivered...")
        time.sleep(3)
    
    # Test reading emails
    read_success = test_read_emails()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY".center(80))
    print("="*80)
    print(f"Send Email: {'✅ PASSED' if send_success else '❌ FAILED'}")
    print(f"Read Emails: {'✅ PASSED' if read_success else '❌ FAILED'}")
    print("="*80 + "\n")
