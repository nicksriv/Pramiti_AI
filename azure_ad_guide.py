#!/usr/bin/env python3
"""
Azure AD Setup - Step-by-Step Interactive Guide
Follow along as we set up your Microsoft Teams connector
"""

import sys

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[96m'

def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{ENDC}")
    print(f"{BOLD}{BLUE}{text.center(80)}{ENDC}")
    print(f"{BOLD}{BLUE}{'=' * 80}{ENDC}\n")

def print_step(num: int, text: str):
    print(f"\n{BOLD}{CYAN}{'─' * 80}{ENDC}")
    print(f"{BOLD}{GREEN}STEP {num}: {text}{ENDC}")
    print(f"{BOLD}{CYAN}{'─' * 80}{ENDC}\n")

def print_action(text: str):
    print(f"{YELLOW}👉 ACTION: {text}{ENDC}")

def print_info(text: str):
    print(f"{CYAN}ℹ️  {text}{ENDC}")

def print_success(text: str):
    print(f"{GREEN}✅ {text}{ENDC}")

def print_important(text: str):
    print(f"{BOLD}{RED}⚠️  IMPORTANT: {text}{ENDC}")

def wait_for_enter(prompt="Press ENTER when done..."):
    input(f"\n{YELLOW}{prompt}{ENDC}")

def get_input(prompt: str) -> str:
    return input(f"{GREEN}{prompt}: {ENDC}").strip()

def main():
    print_header("Microsoft Teams - Azure AD Setup Guide")
    
    print(f"{BOLD}Welcome! Let's set up your Microsoft Teams connector.{ENDC}")
    print("This will take about 10-15 minutes.\n")
    print_info("You should have the Azure Portal open: https://portal.azure.com")
    
    wait_for_enter("Press ENTER to start...")
    
    # Step 1: Navigate to Azure AD
    print_step(1, "Navigate to Azure Active Directory")
    print_action("In the Azure Portal search bar at the top, type: Azure Active Directory")
    print_action("Click on 'Azure Active Directory' from the results")
    print()
    print_info("You should now see the Azure AD Overview page")
    wait_for_enter()
    
    # Step 2: Go to App registrations
    print_step(2, "Open App Registrations")
    print_action("In the left sidebar, find and click: App registrations")
    print()
    print_info("You should see a list of registered applications (may be empty)")
    wait_for_enter()
    
    # Step 3: Create new registration
    print_step(3, "Create New App Registration")
    print_action("Click the '+ New registration' button at the top")
    print()
    print_info("A form will appear for registering a new application")
    wait_for_enter()
    
    # Step 4: Fill registration form
    print_step(4, "Fill in the Registration Form")
    
    print(f"\n{BOLD}Field 1: Name{ENDC}")
    print_action("Enter name: Agentic AI Teams Connector")
    
    print(f"\n{BOLD}Field 2: Supported account types{ENDC}")
    print_action("Select: 'Accounts in this organizational directory only'")
    print_info("This should be the first option (Single tenant)")
    
    print(f"\n{BOLD}Field 3: Redirect URI (optional){ENDC}")
    print_action("Platform: Select 'Web' from the dropdown")
    print_action("URI: Enter exactly: http://localhost:8084/oauth/callback")
    print_important("Make sure there are NO spaces or extra characters!")
    
    print(f"\n{BOLD}When ready:{ENDC}")
    print_action("Click the 'Register' button at the bottom")
    
    wait_for_enter()
    
    # Step 5: Copy Application IDs
    print_step(5, "Copy Your Application Credentials")
    
    print_success("Your app should now be created!")
    print_info("You should see the Overview page with important IDs")
    print()
    
    print(f"{BOLD}You'll see 'Essentials' section with:{ENDC}\n")
    
    print(f"{BOLD}1. Application (client) ID{ENDC}")
    print_info("Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    print_action("Click the copy icon next to it")
    client_id = get_input("Paste it here")
    
    print(f"\n{BOLD}2. Directory (tenant) ID{ENDC}")
    print_info("Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    print_action("Click the copy icon next to it")
    tenant_id = get_input("Paste it here")
    
    print_success(f"\nClient ID saved: {client_id[:8]}...{client_id[-8:]}")
    print_success(f"Tenant ID saved: {tenant_id[:8]}...{tenant_id[-8:]}")
    
    # Step 6: Create Client Secret
    print_step(6, "Create Client Secret")
    
    print_action("In the left sidebar, click: Certificates & secrets")
    wait_for_enter()
    
    print_action("Click the '+ New client secret' button")
    wait_for_enter()
    
    print(f"\n{BOLD}In the form that appears:{ENDC}")
    print_action("Description: Enter 'Agentic AI Connector Secret'")
    print_action("Expires: Select '24 months' (or your preference)")
    print_action("Click 'Add' button")
    
    wait_for_enter()
    
    print_important("The secret value will appear ONLY ONCE!")
    print_important("You MUST copy it NOW - you won't see it again!")
    print()
    print_action("Look for the 'Value' column (NOT the 'Secret ID')")
    print_action("Click the copy icon next to the Value")
    print()
    client_secret = get_input("Paste the secret value here")
    
    print_success(f"Client Secret saved: {client_secret[:8]}...{client_secret[-8:]}")
    
    # Step 7: Add API Permissions
    print_step(7, "Configure API Permissions")
    
    print_action("In the left sidebar, click: API permissions")
    wait_for_enter()
    
    print_action("Click '+ Add a permission' button")
    wait_for_enter()
    
    print(f"\n{BOLD}A panel will slide in from the right{ENDC}")
    print_action("Click on 'Microsoft Graph'")
    print_info("It should be the first large tile")
    wait_for_enter()
    
    print_action("Click 'Application permissions' (NOT Delegated permissions)")
    print_important("Make sure you select 'Application permissions'!")
    wait_for_enter()
    
    print(f"\n{BOLD}Now add these 4 permissions:{ENDC}\n")
    
    permissions = [
        ("Team.ReadBasic.All", "Read basic team information"),
        ("Channel.ReadBasic.All", "Read basic channel information"),
        ("ChannelMessage.Read.All", "Read all channel messages"),
        ("ChannelMessage.Send", "Send messages to channels")
    ]
    
    for perm, desc in permissions:
        print(f"{GREEN}➜{ENDC} {BOLD}{perm}{ENDC}")
        print(f"  {desc}")
        print_action(f"Search for: {perm}")
        print_action(f"Check the checkbox next to {perm}")
        print_action("You can add more permissions before clicking 'Add permissions'")
        print()
    
    print_action("After adding all 4 permissions, click 'Add permissions' at the bottom")
    
    wait_for_enter()
    
    # Step 8: Grant Admin Consent
    print_step(8, "Grant Admin Consent")
    
    print_important("This is CRITICAL - permissions won't work without admin consent!")
    print()
    print_action("Look for the button: 'Grant admin consent for [Your Organization]'")
    print_action("Click that button")
    wait_for_enter()
    
    print_action("A confirmation dialog will appear")
    print_action("Click 'Yes' to confirm")
    wait_for_enter()
    
    print_success("Admin consent granted!")
    print_info("You should now see green checkmarks in the 'Status' column")
    print_info("Status should say: 'Granted for [Your Organization]'")
    
    wait_for_enter()
    
    # Summary
    print_step(9, "Summary - Your Credentials")
    
    print(f"\n{BOLD}{GREEN}✅ Azure AD Setup Complete!{ENDC}\n")
    
    print(f"{BOLD}Your credentials:{ENDC}\n")
    print(f"  Client ID:     {client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Tenant ID:     {tenant_id}")
    print(f"  Redirect URI:  http://localhost:8084/oauth/callback")
    
    print(f"\n{BOLD}Permissions granted:{ENDC}")
    for perm, _ in permissions:
        print(f"  ✅ {perm}")
    
    # Save to file
    print()
    if input(f"\n{YELLOW}Save these credentials to a file? (y/n): {ENDC}").lower() == 'y':
        with open('teams_credentials.txt', 'w') as f:
            f.write("Microsoft Teams Connector Credentials\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Client ID:     {client_id}\n")
            f.write(f"Client Secret: {client_secret}\n")
            f.write(f"Tenant ID:     {tenant_id}\n")
            f.write(f"Redirect URI:  http://localhost:8084/oauth/callback\n\n")
            f.write("Permissions:\n")
            for perm, _ in permissions:
                f.write(f"  - {perm}\n")
        
        print_success("Credentials saved to: teams_credentials.txt")
        print_important("Keep this file secure! Add it to .gitignore")
    
    # Next steps
    print_header("Next Steps")
    
    print(f"{BOLD}Option 1: Use the Setup Wizard{ENDC}")
    print("  Run: python3 setup_production_connectors.py")
    print("  Select 'y' for Microsoft Teams")
    print("  Enter the credentials above when prompted")
    print()
    
    print(f"{BOLD}Option 2: Create Connector via API{ENDC}")
    print("  Run the following command:\n")
    
    curl_cmd = f"""curl -X POST http://localhost:8084/api/v1/connectors \\
  -H "Content-Type: application/json" \\
  -d '{{
    "connector_type": "microsoft_teams",
    "name": "Microsoft Teams - Production",
    "description": "Production Microsoft Teams integration",
    "auth_config": {{
      "client_id": "{client_id}",
      "client_secret": "{client_secret}",
      "tenant_id": "{tenant_id}",
      "redirect_uri": "http://localhost:8084/oauth/callback"
    }},
    "permissions": ["read_messages", "write_messages", "read_channels"]
  }}'"""
    
    print(f"{CYAN}{curl_cmd}{ENDC}")
    
    print(f"\n{BOLD}Option 3: Use Dashboard UI{ENDC}")
    print("  1. Open: http://localhost:8084/enhanced-dashboard.html")
    print("  2. Click 'Connectors' tab")
    print("  3. Go to 'Available Connectors'")
    print("  4. Click 'Setup' on Microsoft Teams")
    print("  5. Enter the credentials above")
    
    print_header("Setup Complete!")
    print_success("🎉 Your Microsoft Teams connector is ready to create!")
    print_info("\nRun the wizard or use the dashboard to create your connector.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Setup cancelled{ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}Error: {str(e)}{ENDC}")
        sys.exit(1)
