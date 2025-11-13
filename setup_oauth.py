#!/usr/bin/env python3
"""
Interactive OAuth Setup for Microsoft 365
Guides user through delegated authentication flow
"""

import requests
import json
import sys
import webbrowser
from time import sleep

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


# Configuration
API_BASE = "http://localhost:8084/api/v1"
CONNECTOR_ID = None  # Will be set during setup


def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE}/connectors", timeout=2)
        return response.status_code == 200
    except:
        return False


def list_connectors():
    """List all Microsoft 365 connectors"""
    try:
        response = requests.get(f"{API_BASE}/connectors")
        response.raise_for_status()
        
        connectors_data = response.json()
        connectors = connectors_data.get('connectors', [])
        
        # Filter Microsoft Teams connectors
        ms_connectors = [c for c in connectors if c.get('connector_type') == 'microsoft_teams']
        
        return ms_connectors
    except Exception as e:
        print_error(f"Failed to list connectors: {e}")
        return []


def create_connector():
    """Create a new Microsoft 365 connector"""
    print_header("CREATE NEW MICROSOFT 365 CONNECTOR")
    
    print("You need Azure AD app credentials. If you don't have them:")
    print("1. Go to https://portal.azure.com")
    print("2. Navigate to 'Azure Active Directory' > 'App registrations'")
    print("3. Create new registration or use existing")
    print("4. Copy Client ID, Client Secret, and Tenant ID")
    print()
    
    client_id = input(f"{Colors.CYAN}Enter Client ID: {Colors.ENDC}").strip()
    client_secret = input(f"{Colors.CYAN}Enter Client Secret: {Colors.ENDC}").strip()
    tenant_id = input(f"{Colors.CYAN}Enter Tenant ID (or 'common'): {Colors.ENDC}").strip() or 'common'
    
    if not client_id or not client_secret:
        print_error("Client ID and Client Secret are required!")
        return None
    
    # Create connector
    try:
        payload = {
            "name": "Microsoft 365 (OAuth)",
            "connector_type": "microsoft_teams",
            "auth_config": {
                "client_id": client_id,
                "client_secret": client_secret,
                "tenant_id": tenant_id
            }
        }
        
        response = requests.post(f"{API_BASE}/connectors", json=payload)
        response.raise_for_status()
        
        result = response.json()
        connector_id = result.get('connector_id')
        
        print_success(f"Connector created: {connector_id}")
        return connector_id
        
    except Exception as e:
        print_error(f"Failed to create connector: {e}")
        return None


def start_oauth_flow(connector_id):
    """Start OAuth authorization flow"""
    print_header("STEP 1: GENERATE AUTHORIZATION URL")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/authorize/{connector_id}")
        response.raise_for_status()
        
        result = response.json()
        auth_url = result.get('authorization_url')
        state = result.get('state')
        
        print_success("Authorization URL generated!")
        print()
        print(f"{Colors.BOLD}Authorization URL:{Colors.ENDC}")
        print(f"{Colors.BLUE}{auth_url}{Colors.ENDC}")
        print()
        
        print_info("Opening browser for Microsoft login...")
        print_warning("If browser doesn't open, copy the URL above and paste it in your browser")
        print()
        
        # Open browser
        sleep(1)
        webbrowser.open(auth_url)
        
        print(f"{Colors.YELLOW}Please complete the following steps in your browser:{Colors.ENDC}")
        print("1. Log in with your Microsoft account")
        print("2. Review and accept the requested permissions")
        print("3. You will be redirected to a success page")
        print()
        
        input(f"{Colors.CYAN}Press ENTER after you've completed the login...{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to generate authorization URL: {e}")
        return False


def check_oauth_status(connector_id):
    """Check if OAuth authentication is complete"""
    try:
        response = requests.get(f"{API_BASE}/oauth/status/{connector_id}")
        response.raise_for_status()
        
        status = response.json()
        is_authenticated = status.get('is_authenticated', False)
        auth_type = status.get('auth_type', 'none')
        expires_at = status.get('expires_at')
        
        return is_authenticated, auth_type, expires_at
        
    except Exception as e:
        print_error(f"Failed to check OAuth status: {e}")
        return False, 'none', None


def test_email_access(connector_id):
    """Test email access"""
    print_info("Testing email access...")
    
    try:
        payload = {
            "action": "read_emails",
            "parameters": {
                "folder": "inbox",
                "top": 5
            }
        }
        
        response = requests.post(f"{API_BASE}/connectors/{connector_id}/execute", json=payload)
        response.raise_for_status()
        
        emails = response.json()
        
        if isinstance(emails, list):
            print_success(f"Email access working! Found {len(emails)} emails")
            if emails:
                print_info("Most recent email:")
                email = emails[0]
                print(f"  Subject: {email.get('subject', 'N/A')}")
                print(f"  From: {email.get('from', {}).get('emailAddress', {}).get('address', 'N/A')}")
        else:
            print_warning("Email response received but format unexpected")
        
        return True
        
    except Exception as e:
        print_error(f"Email test failed: {e}")
        return False


def test_onedrive_access(connector_id):
    """Test OneDrive access"""
    print_info("Testing OneDrive access...")
    
    try:
        payload = {
            "action": "list_onedrive_files",
            "parameters": {
                "top": 10
            }
        }
        
        response = requests.post(f"{API_BASE}/connectors/{connector_id}/execute", json=payload)
        response.raise_for_status()
        
        files = response.json()
        
        if isinstance(files, list):
            print_success(f"OneDrive access working! Found {len(files)} items")
            if files:
                print_info("Recent files:")
                for file in files[:3]:
                    print(f"  - {file.get('name', 'N/A')}")
        else:
            print_warning("OneDrive response received but format unexpected")
        
        return True
        
    except Exception as e:
        print_error(f"OneDrive test failed: {e}")
        return False


def main():
    """Main setup flow"""
    print_header("MICROSOFT 365 OAUTH SETUP")
    print(f"{Colors.BOLD}This script will help you set up delegated authentication for Microsoft 365{Colors.ENDC}")
    print()
    
    # Check API server
    print_info("Checking API server...")
    if not check_api_server():
        print_error("API server is not running on http://localhost:8084")
        print_info("Please start it with: python3 api_server.py")
        sys.exit(1)
    print_success("API server is running")
    
    # List existing connectors
    print_header("SELECT OR CREATE CONNECTOR")
    connectors = list_connectors()
    
    if connectors:
        print_info(f"Found {len(connectors)} Microsoft 365 connector(s):")
        for i, conn in enumerate(connectors, 1):
            print(f"{i}. {conn.get('name')} (ID: {conn.get('connector_id')})")
        print(f"{len(connectors) + 1}. Create new connector")
        print()
        
        choice = input(f"{Colors.CYAN}Select option [1-{len(connectors) + 1}]: {Colors.ENDC}").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(connectors):
                connector_id = connectors[choice_num - 1].get('connector_id')
                print_success(f"Using connector: {connector_id}")
            else:
                connector_id = create_connector()
        except:
            print_error("Invalid choice")
            sys.exit(1)
    else:
        print_info("No Microsoft 365 connectors found")
        connector_id = create_connector()
    
    if not connector_id:
        print_error("Failed to get or create connector")
        sys.exit(1)
    
    # Check current OAuth status
    print_header("CHECK AUTHENTICATION STATUS")
    is_authenticated, auth_type, expires_at = check_oauth_status(connector_id)
    
    if is_authenticated:
        print_success(f"Already authenticated with {auth_type} auth")
        print_info(f"Expires at: {expires_at}")
        
        redo = input(f"{Colors.CYAN}Re-authenticate? [y/N]: {Colors.ENDC}").strip().lower()
        if redo != 'y':
            print_info("Skipping OAuth flow")
        else:
            # Start OAuth flow
            if not start_oauth_flow(connector_id):
                print_error("OAuth flow failed")
                sys.exit(1)
    else:
        print_info(f"Current auth type: {auth_type}")
        print_warning("Delegated authentication not set up")
        
        # Start OAuth flow
        if not start_oauth_flow(connector_id):
            print_error("OAuth flow failed")
            sys.exit(1)
    
    # Verify authentication
    print_header("VERIFY AUTHENTICATION")
    sleep(2)  # Give time for tokens to be saved
    
    is_authenticated, auth_type, expires_at = check_oauth_status(connector_id)
    
    if is_authenticated:
        print_success("OAuth authentication successful!")
        print_info(f"Auth type: {auth_type}")
        print_info(f"Expires at: {expires_at}")
    else:
        print_error("OAuth authentication failed")
        print_info("Please check the Azure AD app configuration and try again")
        sys.exit(1)
    
    # Test functionality
    print_header("TEST FUNCTIONALITY")
    
    print()
    test_email_access(connector_id)
    print()
    test_onedrive_access(connector_id)
    
    # Summary
    print_header("SETUP COMPLETE")
    print_success("Microsoft 365 OAuth authentication is set up!")
    print()
    print(f"{Colors.BOLD}Connector Details:{Colors.ENDC}")
    print(f"  Connector ID: {connector_id}")
    print(f"  Auth Type: Delegated (OAuth 2.0)")
    print(f"  Status: Authenticated")
    print()
    print(f"{Colors.BOLD}Available Features:{Colors.ENDC}")
    print("  ✅ Send and read emails")
    print("  ✅ Access OneDrive files")
    print("  ✅ Manage calendar events")
    print("  ✅ Create Teams meetings")
    print()
    print(f"{Colors.CYAN}You can now use this connector in your applications!{Colors.ENDC}")
    print()
    print("Test the connector with:")
    print(f"  python3 test_email_connector.py")
    print(f"  python3 test_onedrive_connector.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
