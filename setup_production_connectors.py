#!/usr/bin/env python3
"""
Production Connector Setup Script
Guides users through setting up real credentials for Microsoft Teams and Google Drive
"""

import sys
import json
import requests
from typing import Dict, Optional

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

API_BASE = "http://localhost:8084"


def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{ENDC}")
    print(f"{BOLD}{BLUE}{text.center(80)}{ENDC}")
    print(f"{BOLD}{BLUE}{'=' * 80}{ENDC}\n")


def print_step(num: int, text: str):
    print(f"\n{BOLD}{GREEN}Step {num}: {text}{ENDC}")


def print_info(text: str):
    print(f"{YELLOW}ℹ️  {text}{ENDC}")


def print_success(text: str):
    print(f"{GREEN}✅ {text}{ENDC}")


def print_error(text: str):
    print(f"{RED}❌ {text}{ENDC}")


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def confirm(prompt: str) -> bool:
    """Ask for yes/no confirmation"""
    response = get_input(f"{prompt} (y/n)", "n").lower()
    return response in ['y', 'yes']


def setup_microsoft_teams() -> Optional[Dict]:
    """Guide user through Microsoft Teams setup"""
    print_header("Microsoft Teams Production Setup")
    
    print_info("You need an Azure AD application with Microsoft Graph API permissions.")
    print_info("If you haven't created one yet, follow these steps:\n")
    
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations → New registration")
    print("3. Configure:")
    print("   - Name: Agentic AI Teams Connector")
    print("   - Account types: Accounts in this organizational directory only")
    print("   - Redirect URI: http://localhost:8084/oauth/callback")
    print("\n4. After creation, go to 'API permissions' → Add permission")
    print("   - Microsoft Graph → Application permissions")
    print("   - Add these permissions:")
    print("     • Team.ReadBasic.All")
    print("     • Channel.ReadBasic.All")
    print("     • ChannelMessage.Read.All")
    print("     • ChannelMessage.Send")
    print("   - Click 'Grant admin consent'")
    print("\n5. Go to 'Certificates & secrets' → New client secret")
    print("   - Description: Agentic AI Connector Secret")
    print("   - Expires: 24 months")
    print("   - Copy the secret value immediately!\n")
    
    if not confirm("Have you completed the Azure AD setup?"):
        print_info("Please complete the Azure AD setup first, then run this script again.")
        return None
    
    print_step(1, "Enter your Azure AD credentials")
    
    client_id = get_input("Client ID (from App registration Overview page)")
    if not client_id:
        print_error("Client ID is required")
        return None
    
    client_secret = get_input("Client Secret (from Certificates & secrets)")
    if not client_secret:
        print_error("Client Secret is required")
        return None
    
    tenant_id = get_input("Tenant ID (from App registration Overview page)")
    if not tenant_id:
        print_error("Tenant ID is required")
        return None
    
    redirect_uri = get_input("Redirect URI", "http://localhost:8084/oauth/callback")
    
    print_step(2, "Choose permissions")
    print("Available permissions:")
    print("  1. read_messages - Read Teams messages")
    print("  2. write_messages - Send Teams messages")
    print("  3. read_channels - Read channel information")
    print("  4. manage_teams - Manage team settings")
    
    permissions = []
    if confirm("Enable read_messages?"):
        permissions.append("read_messages")
    if confirm("Enable write_messages?"):
        permissions.append("write_messages")
    if confirm("Enable read_channels?"):
        permissions.append("read_channels")
    if confirm("Enable manage_teams?"):
        permissions.append("manage_teams")
    
    if not permissions:
        print_error("At least one permission is required")
        return None
    
    connector_name = get_input("Connector name", "Microsoft Teams - Production")
    connector_desc = get_input("Connector description", "Production Microsoft Teams integration")
    
    return {
        "connector_type": "microsoft_teams",
        "name": connector_name,
        "description": connector_desc,
        "auth_config": {
            "client_id": client_id,
            "client_secret": client_secret,
            "tenant_id": tenant_id,
            "redirect_uri": redirect_uri
        },
        "permissions": permissions
    }


def setup_google_drive() -> Optional[Dict]:
    """Guide user through Google Drive setup"""
    print_header("Google Drive Production Setup")
    
    print_info("You need a Google Cloud project with Drive API enabled.")
    print_info("If you haven't created one yet, follow these steps:\n")
    
    print("1. Go to: https://console.cloud.google.com")
    print("2. Create a new project:")
    print("   - Click 'Select a project' → 'New Project'")
    print("   - Project name: Agentic AI Drive Connector")
    print("   - Click 'Create'")
    print("\n3. Enable Google Drive API:")
    print("   - Navigate to 'APIs & Services' → 'Library'")
    print("   - Search for 'Google Drive API'")
    print("   - Click 'Enable'")
    print("\n4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' → 'Credentials'")
    print("   - Configure consent screen if prompted:")
    print("     • User type: Internal (for organization) or External (for testing)")
    print("     • App name: Agentic AI Connector")
    print("     • Add scope: https://www.googleapis.com/auth/drive")
    print("   - Click 'Create Credentials' → 'OAuth client ID'")
    print("   - Application type: Web application")
    print("   - Name: Agentic AI Drive Client")
    print("   - Authorized redirect URIs: http://localhost:8084/oauth/callback")
    print("   - Click 'Create'")
    print("   - Copy Client ID and Client Secret\n")
    
    if not confirm("Have you completed the Google Cloud setup?"):
        print_info("Please complete the Google Cloud setup first, then run this script again.")
        return None
    
    print_step(1, "Enter your Google Cloud credentials")
    
    client_id = get_input("Client ID (from OAuth 2.0 Client)")
    if not client_id:
        print_error("Client ID is required")
        return None
    
    client_secret = get_input("Client Secret (from OAuth 2.0 Client)")
    if not client_secret:
        print_error("Client Secret is required")
        return None
    
    redirect_uri = get_input("Redirect URI", "http://localhost:8084/oauth/callback")
    
    print_step(2, "Choose permissions")
    print("Available permissions:")
    print("  1. read_files - Read files from Drive")
    print("  2. write_files - Upload/modify files in Drive")
    print("  3. delete_files - Delete files from Drive")
    print("  4. search - Search for files")
    
    permissions = []
    if confirm("Enable read_files?"):
        permissions.append("read_files")
    if confirm("Enable write_files?"):
        permissions.append("write_files")
    if confirm("Enable delete_files?"):
        permissions.append("delete_files")
    if confirm("Enable search?"):
        permissions.append("search")
    
    if not permissions:
        print_error("At least one permission is required")
        return None
    
    connector_name = get_input("Connector name", "Google Drive - Production")
    connector_desc = get_input("Connector description", "Production Google Drive integration")
    
    return {
        "connector_type": "google_drive",
        "name": connector_name,
        "description": connector_desc,
        "auth_config": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        },
        "permissions": permissions
    }


def create_connector(config: Dict) -> Optional[str]:
    """Create connector via API"""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/connectors",
            json=config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                connector_id = data.get("connector_id")
                print_success(f"Connector created successfully!")
                print_info(f"Connector ID: {connector_id}")
                return connector_id
            else:
                print_error(f"Failed to create connector: {data.get('message', 'Unknown error')}")
                return None
        else:
            print_error(f"API error: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating connector: {str(e)}")
        return None


def test_connector(connector_id: str, connector_type: str):
    """Test connector connection"""
    print_step(3, f"Testing {connector_type} connection")
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/connectors/{connector_id}/test")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Connection test successful!")
                details = data.get("details", {})
                test_result = details.get("test_result", {})
                
                if test_result.get("success"):
                    print_info(f"Service: {test_result.get('service', 'Unknown')}")
                    print_info(f"API Version: {test_result.get('api_version', 'Unknown')}")
                    print_info(f"Response time: {details.get('response_time_ms', 0)}ms")
                    
                    # Check if it's demo mode or real
                    message = test_result.get("message", "")
                    if "demo mode" in message.lower():
                        print_info("⚠️  Running in DEMO MODE")
                        print_info("The connector is using simulated credentials.")
                    else:
                        print_success("✅ Connected to REAL API!")
                        print_success("The connector is using production credentials.")
                else:
                    print_error("Connection test failed")
                    print_error(f"Message: {test_result.get('message', 'Unknown error')}")
            else:
                print_error(f"Test failed: {data.get('message', 'Unknown error')}")
        else:
            print_error(f"API error: {response.status_code}")
            print_error(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Error testing connector: {str(e)}")


def main():
    print_header("Production Connector Setup Wizard")
    print_info("This wizard will help you set up production credentials for:")
    print_info("  • Microsoft Teams")
    print_info("  • Google Drive\n")
    
    # Check if API server is running
    try:
        response = requests.get(f"{API_BASE}/api/v1/connectors/available", timeout=2)
        if response.status_code != 200:
            print_error("API server is not responding correctly")
            print_info(f"Please start the API server with: python3 api_server.py")
            sys.exit(1)
    except Exception as e:
        print_error("Cannot connect to API server at http://localhost:8084")
        print_info("Please start the API server with: python3 api_server.py")
        print_error(f"Error: {str(e)}")
        sys.exit(1)
    
    print_success("API server is running\n")
    
    # Setup Microsoft Teams
    if confirm("Set up Microsoft Teams connector?"):
        teams_config = setup_microsoft_teams()
        if teams_config:
            print_step(2, "Creating Microsoft Teams connector")
            connector_id = create_connector(teams_config)
            if connector_id:
                test_connector(connector_id, "Microsoft Teams")
                print_success(f"\n🎉 Microsoft Teams connector is ready!")
                print_info(f"You can now use it in your AI agents with ID: {connector_id}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Setup Google Drive
    if confirm("Set up Google Drive connector?"):
        drive_config = setup_google_drive()
        if drive_config:
            print_step(2, "Creating Google Drive connector")
            connector_id = create_connector(drive_config)
            if connector_id:
                test_connector(connector_id, "Google Drive")
                print_success(f"\n🎉 Google Drive connector is ready!")
                print_info(f"You can now use it in your AI agents with ID: {connector_id}")
    
    print_header("Setup Complete!")
    print_success("Your production connectors are configured and ready to use!")
    print_info("\nNext steps:")
    print("  1. View your connectors: http://localhost:8084/enhanced-dashboard.html")
    print("  2. Check the 'Connected' tab to see status")
    print("  3. Use the connector IDs in your AI agent code")
    print("\nDocumentation:")
    print("  • Full guide: CONNECTORS.md")
    print("  • Quick start: CONNECTORS_QUICKSTART.md")
    print("  • API docs: http://localhost:8084/docs\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)
