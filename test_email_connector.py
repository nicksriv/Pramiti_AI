#!/usr/bin/env python3
"""
Interactive test script for Microsoft Outlook Email integration via Teams connector.
Tests email sending, reading, searching, and management capabilities.
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE = "http://localhost:8084/api/v1"

# Set your connector ID here (from setup_and_test_teams.sh output)
CONNECTOR_ID = "microsoft_teams_833476c52e87e4ac"

# Color codes for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{CYAN}ℹ️  {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def test_connector_status():
    """Check if connector exists and is connected"""
    print_header("STEP 1: Check Connector Status")
    
    try:
        response = requests.get(f"{API_BASE}/connectors/{CONNECTOR_ID}")
        
        if response.status_code == 200:
            connector = response.json()
            print(f"Connector ID: {CYAN}{connector.get('id')}{RESET}")
            print(f"Platform: {CYAN}{connector.get('platform')}{RESET}")
            print(f"Status: {CYAN}{connector.get('status')}{RESET}")
            
            if connector.get('status') == 'connected':
                print_success("Connector is connected and ready!")
                return True
            else:
                print_error(f"Connector status is: {connector.get('status')}")
                return False
        else:
            print_error(f"Failed to get connector: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"Error checking connector status: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_test_email():
    """Send a test email"""
    print_header("STEP 2: Send Test Email")
    
    print_info("Let's send a test email via Outlook")
    
    # Get recipient email
    to_email = input(f"\n{CYAN}Enter recipient email address: {RESET}").strip()
    if not to_email:
        print_warning("No email provided, skipping send test")
        return
    
    # Get subject
    subject = input(f"{CYAN}Enter subject (default: 'Test Email from Agentic AI'): {RESET}").strip()
    if not subject:
        subject = "Test Email from Agentic AI"
    
    # Get body
    print(f"{CYAN}Enter email body (HTML supported, press Enter twice when done):{RESET}")
    body_lines = []
    while True:
        line = input()
        if line == "" and (not body_lines or body_lines[-1] == ""):
            break
        body_lines.append(line)
    
    body = "\n".join(body_lines[:-1]) if body_lines else "<p>This is a test email sent from the Agentic AI system.</p>"
    
    # Add CC (optional)
    cc_input = input(f"\n{CYAN}Enter CC email (optional, press Enter to skip): {RESET}").strip()
    cc_list = [cc_input] if cc_input else None
    
    # HTML or plain text
    use_html = input(f"{CYAN}Send as HTML? (y/n, default: y): {RESET}").strip().lower() != 'n'
    
    try:
        print_info(f"Sending email to {to_email}...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "send_email",
                "parameters": {
                    "to_recipients": [to_email],
                    "subject": subject,
                    "body": body,
                    "cc_recipients": cc_list,
                    "is_html": use_html
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Email sent successfully!")
                print(f"Subject: {result.get('subject')}")
                print(f"To: {', '.join(result.get('to', []))}")
            else:
                print_error(f"Failed to send email: {result.get('error')}")
                print(f"Details: {result.get('details')}")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()


def read_inbox():
    """Read emails from inbox"""
    print_header("STEP 3: Read Inbox")
    
    # Get parameters
    count = input(f"{CYAN}How many emails to read? (default: 10): {RESET}").strip()
    count = int(count) if count.isdigit() else 10
    
    unread_only = input(f"{CYAN}Only show unread emails? (y/n, default: n): {RESET}").strip().lower() == 'y'
    
    folder = input(f"{CYAN}Folder (inbox/sentitems/drafts, default: inbox): {RESET}").strip().lower()
    folder = folder if folder in ['inbox', 'sentitems', 'drafts', 'deleteditems', 'junkemail'] else 'inbox'
    
    try:
        print_info(f"Reading {count} emails from {folder}{'(unread only)' if unread_only else ''}...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "read_emails",
                "parameters": {
                    "folder": folder,
                    "top": count,
                    "unread_only": unread_only
                }
            }
        )
        
        if response.status_code == 200:
            emails = response.json()
            
            if not emails:
                print_warning("No emails found")
                return
            
            print_success(f"Found {len(emails)} email(s)")
            print("\n" + "─" * 80)
            
            for i, email in enumerate(emails, 1):
                print(f"\n{BOLD}Email #{i}{RESET}")
                print(f"  From: {CYAN}{email.get('from_name')} <{email.get('from')}>{RESET}")
                print(f"  Subject: {BOLD}{email.get('subject')}{RESET}")
                print(f"  Received: {email.get('received')}")
                print(f"  Preview: {email.get('preview')[:100]}...")
                print(f"  Read: {GREEN if email.get('is_read') else YELLOW}{'Yes' if email.get('is_read') else 'No'}{RESET}")
                if email.get('has_attachments'):
                    print(f"  📎 Has attachments")
                print(f"  ID: {email.get('id')[:20]}...")
                
            print("\n" + "─" * 80)
            
            # Ask if user wants to view details of any email
            view_detail = input(f"\n{CYAN}View details of an email? (enter number or press Enter to skip): {RESET}").strip()
            if view_detail.isdigit() and 1 <= int(view_detail) <= len(emails):
                selected_email = emails[int(view_detail) - 1]
                get_email_details(selected_email['id'])
            
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error reading emails: {str(e)}")
        import traceback
        traceback.print_exc()


def search_emails():
    """Search for emails"""
    print_header("STEP 4: Search Emails")
    
    query = input(f"{CYAN}Enter search query (subject, sender, or keywords): {RESET}").strip()
    if not query:
        print_warning("No query provided, skipping search")
        return
    
    count = input(f"{CYAN}How many results? (default: 20): {RESET}").strip()
    count = int(count) if count.isdigit() else 20
    
    try:
        print_info(f"Searching for '{query}'...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "search_emails",
                "parameters": {
                    "query": query,
                    "top": count
                }
            }
        )
        
        if response.status_code == 200:
            emails = response.json()
            
            if not emails:
                print_warning(f"No emails found matching '{query}'")
                return
            
            print_success(f"Found {len(emails)} matching email(s)")
            print("\n" + "─" * 80)
            
            for i, email in enumerate(emails, 1):
                print(f"\n{BOLD}Result #{i}{RESET}")
                print(f"  From: {CYAN}{email.get('from_name')} <{email.get('from')}>{RESET}")
                print(f"  Subject: {BOLD}{email.get('subject')}{RESET}")
                print(f"  Received: {email.get('received')}")
                print(f"  Preview: {email.get('preview')[:100]}...")
                print(f"  ID: {email.get('id')[:20]}...")
                
            print("\n" + "─" * 80)
            
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error searching emails: {str(e)}")
        import traceback
        traceback.print_exc()


def get_email_details(message_id=None):
    """Get full details of an email"""
    print_header("STEP 5: Get Email Details")
    
    if not message_id:
        message_id = input(f"{CYAN}Enter message ID: {RESET}").strip()
        if not message_id:
            print_warning("No message ID provided, skipping")
            return
    
    try:
        print_info(f"Fetching email details...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "get_email_details",
                "parameters": {
                    "message_id": message_id
                }
            }
        )
        
        if response.status_code == 200:
            email = response.json()
            
            if not email:
                print_error("Email not found")
                return
            
            print_success("Email details retrieved")
            print("\n" + "═" * 80)
            print(f"{BOLD}Subject:{RESET} {email.get('subject')}")
            print(f"\n{BOLD}From:{RESET} {email.get('from', {}).get('name')} <{email.get('from', {}).get('address')}>")
            
            print(f"\n{BOLD}To:{RESET}")
            for recipient in email.get('to_recipients', []):
                print(f"  - {recipient.get('name')} <{recipient.get('address')}>")
            
            if email.get('cc_recipients'):
                print(f"\n{BOLD}CC:{RESET}")
                for recipient in email.get('cc_recipients', []):
                    print(f"  - {recipient.get('name')} <{recipient.get('address')}>")
            
            print(f"\n{BOLD}Received:{RESET} {email.get('received')}")
            print(f"{BOLD}Read Status:{RESET} {GREEN if email.get('is_read') else YELLOW}{'Read' if email.get('is_read') else 'Unread'}{RESET}")
            
            if email.get('has_attachments'):
                print(f"{BOLD}Attachments:{RESET} Yes (📎)")
            
            print(f"\n{BOLD}Body ({email.get('body_type')}):{RESET}")
            print("─" * 80)
            body = email.get('body', '')
            # Show first 500 characters of body
            print(body[:500] + ("..." if len(body) > 500 else ""))
            print("─" * 80)
            print("═" * 80)
            
            # Ask if user wants to mark as read/unread
            mark = input(f"\n{CYAN}Mark this email as read? (y/n/skip): {RESET}").strip().lower()
            if mark == 'y':
                mark_email_as_read(message_id, True)
            elif mark == 'n':
                mark_email_as_read(message_id, False)
            
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error getting email details: {str(e)}")
        import traceback
        traceback.print_exc()


def mark_email_as_read(message_id=None, is_read=True):
    """Mark an email as read or unread"""
    
    if not message_id:
        message_id = input(f"{CYAN}Enter message ID: {RESET}").strip()
        if not message_id:
            print_warning("No message ID provided, skipping")
            return
        
        is_read_input = input(f"{CYAN}Mark as read? (y/n, default: y): {RESET}").strip().lower()
        is_read = is_read_input != 'n'
    
    try:
        print_info(f"Marking email as {'read' if is_read else 'unread'}...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "mark_email_as_read",
                "parameters": {
                    "message_id": message_id,
                    "is_read": is_read
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print_success(f"Email marked as {'read' if is_read else 'unread'}")
            else:
                print_error("Failed to mark email")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error marking email: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test flow"""
    print(f"{BOLD}{CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                  MICROSOFT OUTLOOK EMAIL CONNECTOR TEST                  ║")
    print("║                      Testing Email Integration                            ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info(f"Using connector: {CONNECTOR_ID}")
    print_warning("Make sure you've added Mail API permissions in Azure AD!")
    print_info("See ADD_MAIL_PERMISSIONS.md for setup instructions\n")
    
    # Test 1: Check connector status
    if not test_connector_status():
        print_error("Connector is not ready. Please check setup.")
        return
    
    input(f"\n{YELLOW}Press Enter to continue to email tests...{RESET}")
    
    # Main test loop
    while True:
        print_header("EMAIL TEST MENU")
        print(f"{CYAN}1.{RESET} Send test email")
        print(f"{CYAN}2.{RESET} Read inbox")
        print(f"{CYAN}3.{RESET} Search emails")
        print(f"{CYAN}4.{RESET} Get email details")
        print(f"{CYAN}5.{RESET} Mark email as read/unread")
        print(f"{CYAN}6.{RESET} Exit")
        
        choice = input(f"\n{CYAN}Select option (1-6): {RESET}").strip()
        
        if choice == '1':
            send_test_email()
        elif choice == '2':
            read_inbox()
        elif choice == '3':
            search_emails()
        elif choice == '4':
            get_email_details()
        elif choice == '5':
            mark_email_as_read()
        elif choice == '6':
            print_success("Goodbye!")
            break
        else:
            print_warning("Invalid option, please select 1-6")
        
        input(f"\n{YELLOW}Press Enter to continue...{RESET}")
    
    print_header("TEST COMPLETE")
    print_success("All email tests completed!")
    print_info("Next steps:")
    print("  1. ✅ Email sending and reading working")
    print("  2. 🔄 Integrate with agent chat interface")
    print("  3. 📝 Set up email automation workflows")
    print("  4. 📊 Add email analytics and reporting")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
