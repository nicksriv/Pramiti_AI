#!/usr/bin/env python3
"""
Interactive guide for setting up Google Drive connector with production credentials.
Walks through Google Cloud Console setup step-by-step.
"""

import json
import os
from datetime import datetime

# Color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{CYAN}ℹ️  {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_step(number, text):
    print(f"\n{BOLD}{CYAN}Step {number}:{RESET} {text}")


def main():
    print(f"{BOLD}{CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║              GOOGLE DRIVE CONNECTOR - PRODUCTION SETUP                   ║")
    print("║            Interactive Guide for Google Cloud Console                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info("This guide will walk you through setting up Google Drive API credentials.")
    print_info("You'll need a Google Cloud account with billing enabled.")
    print()
    
    input(f"{YELLOW}Press Enter when ready to begin...{RESET}")
    
    # Step 1: Create Project
    print_header("PART 1: CREATE GOOGLE CLOUD PROJECT")
    
    print_step(1, "Go to Google Cloud Console")
    print(f"   Open: {CYAN}https://console.cloud.google.com{RESET}")
    input(f"   {YELLOW}Press Enter when you're at the Google Cloud Console...{RESET}")
    
    print_step(2, "Create a New Project (or select existing)")
    print("   1. Click the project dropdown at the top")
    print("   2. Click 'NEW PROJECT'")
    print("   3. Project name: " + CYAN + "Agentic AI Drive Connector" + RESET)
    print("   4. Click 'CREATE'")
    print("   5. Wait for project creation (10-30 seconds)")
    print("   6. Select the new project from the dropdown")
    input(f"   {YELLOW}Press Enter when project is created and selected...{RESET}")
    
    # Step 2: Enable Drive API
    print_header("PART 2: ENABLE GOOGLE DRIVE API")
    
    print_step(1, "Go to APIs & Services")
    print("   1. Click the hamburger menu (☰) in top-left")
    print("   2. Navigate to: " + CYAN + "APIs & Services > Library" + RESET)
    input(f"   {YELLOW}Press Enter when you're in the API Library...{RESET}")
    
    print_step(2, "Enable Google Drive API")
    print("   1. In the search box, type: " + CYAN + "Google Drive API" + RESET)
    print("   2. Click on 'Google Drive API' from results")
    print("   3. Click the blue " + CYAN + "ENABLE" + RESET + " button")
    print("   4. Wait for API to be enabled")
    input(f"   {YELLOW}Press Enter when Drive API is enabled...{RESET}")
    
    # Step 3: Create OAuth Consent Screen
    print_header("PART 3: CONFIGURE OAuth CONSENT SCREEN")
    
    print_step(1, "Go to OAuth Consent Screen")
    print("   1. Click hamburger menu (☰)")
    print("   2. Go to: " + CYAN + "APIs & Services > OAuth consent screen" + RESET)
    input(f"   {YELLOW}Press Enter when you're at OAuth consent screen...{RESET}")
    
    print_step(2, "Configure Consent Screen")
    print("   1. User Type: Select " + CYAN + "External" + RESET)
    print("   2. Click " + CYAN + "CREATE" + RESET)
    print()
    print("   3. App information:")
    print(f"      - App name: {CYAN}Agentic AI Drive Integration{RESET}")
    print(f"      - User support email: {CYAN}[Your email]{RESET}")
    print()
    print("   4. Developer contact:")
    print(f"      - Email: {CYAN}[Your email]{RESET}")
    print()
    print("   5. Click " + CYAN + "SAVE AND CONTINUE" + RESET)
    input(f"   {YELLOW}Press Enter when app info is saved...{RESET}")
    
    print_step(3, "Add Scopes")
    print("   1. Click " + CYAN + "ADD OR REMOVE SCOPES" + RESET)
    print("   2. In the filter, search for: " + CYAN + "drive" + RESET)
    print("   3. Check these scopes:")
    print(f"      ✅ {CYAN}https://www.googleapis.com/auth/drive{RESET}")
    print(f"      ✅ {CYAN}https://www.googleapis.com/auth/drive.file{RESET}")
    print("   4. Click " + CYAN + "UPDATE" + RESET)
    print("   5. Click " + CYAN + "SAVE AND CONTINUE" + RESET)
    input(f"   {YELLOW}Press Enter when scopes are added...{RESET}")
    
    print_step(4, "Test Users (Optional)")
    print("   1. Click " + CYAN + "ADD USERS" + RESET)
    print(f"   2. Add your email: {CYAN}[Your Google email]{RESET}")
    print("   3. Click " + CYAN + "ADD" + RESET)
    print("   4. Click " + CYAN + "SAVE AND CONTINUE" + RESET)
    input(f"   {YELLOW}Press Enter when test users are added...{RESET}")
    
    print_step(5, "Review and Finish")
    print("   1. Review the summary")
    print("   2. Click " + CYAN + "BACK TO DASHBOARD" + RESET)
    input(f"   {YELLOW}Press Enter to continue...{RESET}")
    
    # Step 4: Create OAuth Client
    print_header("PART 4: CREATE OAuth CLIENT")
    
    print_step(1, "Go to Credentials")
    print("   1. Click hamburger menu (☰)")
    print("   2. Go to: " + CYAN + "APIs & Services > Credentials" + RESET)
    input(f"   {YELLOW}Press Enter when you're at Credentials page...{RESET}")
    
    print_step(2, "Create OAuth Client ID")
    print("   1. Click " + CYAN + "+ CREATE CREDENTIALS" + RESET + " at top")
    print("   2. Select " + CYAN + "OAuth client ID" + RESET)
    print()
    print("   3. Application type: " + CYAN + "Web application" + RESET)
    print(f"   4. Name: {CYAN}Agentic AI Drive Client{RESET}")
    print()
    print("   5. Authorized redirect URIs:")
    print(f"      Click {CYAN}+ ADD URI{RESET}")
    print(f"      Enter: {CYAN}http://localhost:8084/oauth/callback{RESET}")
    print()
    print("   6. Click " + CYAN + "CREATE" + RESET)
    input(f"   {YELLOW}Press Enter when OAuth client is created...{RESET}")
    
    # Step 5: Get Credentials
    print_header("PART 5: COPY YOUR CREDENTIALS")
    
    print_info("A popup should appear with your Client ID and Client Secret")
    print_warning("IMPORTANT: Copy these values carefully!")
    print()
    
    client_id = input(f"{CYAN}Enter your Client ID: {RESET}").strip()
    client_secret = input(f"{CYAN}Enter your Client Secret: {RESET}").strip()
    
    if not client_id or not client_secret:
        print_error("Client ID and Secret are required!")
        return
    
    print_success("Credentials saved!")
    
    # Step 6: Get Refresh Token
    print_header("PART 6: AUTHORIZATION & REFRESH TOKEN")
    
    print_warning("To get a refresh token, you need to complete OAuth flow")
    print_info("We'll use a special authorization URL for this")
    print()
    
    # Create authorization URL
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ]
    scope_string = " ".join(scopes)
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri=http://localhost:8084/oauth/callback&"
        f"response_type=code&"
        f"scope={scope_string.replace(' ', '%20')}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print_step(1, "Open Authorization URL")
    print(f"\n{BOLD}Copy this URL and open it in your browser:{RESET}")
    print(f"{CYAN}{auth_url}{RESET}\n")
    
    print_info("This will:")
    print("   1. Ask you to sign in with Google")
    print("   2. Show consent screen for Drive access")
    print("   3. Redirect to localhost with an authorization code")
    print()
    
    input(f"{YELLOW}Press Enter after you've opened the URL...{RESET}")
    
    print_step(2, "Get Authorization Code")
    print("   After authorizing, you'll be redirected to:")
    print(f"   {CYAN}http://localhost:8084/oauth/callback?code=...{RESET}")
    print()
    print("   The page might show an error (that's OK!)")
    print("   Look at the URL bar and copy the 'code' parameter")
    print()
    
    auth_code = input(f"{CYAN}Paste the authorization code here: {RESET}").strip()
    
    if not auth_code:
        print_error("Authorization code is required!")
        print_info("You can run this script again to retry")
        return
    
    print_step(3, "Exchange Code for Refresh Token")
    print_info("Making API call to exchange code for tokens...")
    
    import requests
    
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': 'http://localhost:8084/oauth/callback',
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            refresh_token = token_data.get('refresh_token')
            
            if refresh_token:
                print_success("Successfully obtained refresh token!")
            else:
                print_error("No refresh token in response. Try again with prompt=consent")
                print(f"Response: {token_data}")
                return
        else:
            print_error(f"Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
    except Exception as e:
        print_error(f"Error exchanging token: {str(e)}")
        return
    
    # Step 7: Save Credentials
    print_header("PART 7: SAVE CREDENTIALS")
    
    credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'scopes': scopes,
        'created_at': datetime.now().isoformat()
    }
    
    # Save to file
    creds_file = 'drive_credentials.txt'
    with open(creds_file, 'w') as f:
        f.write("=== GOOGLE DRIVE CREDENTIALS ===\n")
        f.write(f"Created: {datetime.now()}\n\n")
        f.write(f"Client ID: {client_id}\n")
        f.write(f"Client Secret: {client_secret}\n")
        f.write(f"Refresh Token: {refresh_token}\n")
        f.write(f"\nScopes:\n")
        for scope in scopes:
            f.write(f"  - {scope}\n")
    
    print_success(f"Credentials saved to: {creds_file}")
    print_warning("Keep this file secure and don't commit it to git!")
    
    # Save JSON for programmatic use
    json_file = 'drive_credentials.json'
    with open(json_file, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print_success(f"JSON credentials saved to: {json_file}")
    
    # Step 8: Create Connector
    print_header("PART 8: CREATE GOOGLE DRIVE CONNECTOR")
    
    print_info("Now let's create your Drive connector via API")
    print()
    
    create_connector = input(f"{CYAN}Create Drive connector now? (y/n): {RESET}").strip().lower()
    
    if create_connector == 'y':
        import requests
        
        try:
            api_url = "http://localhost:8084/api/v1/connectors"
            
            connector_data = {
                "connector_type": "google_drive",
                "name": "Google Drive Production",
                "auth_config": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token
                },
                "auto_refresh": True
            }
            
            print_info("Creating connector...")
            response = requests.post(api_url, json=connector_data)
            
            if response.status_code == 200:
                connector = response.json()
                connector_id = connector.get('id')
                
                print_success("Drive connector created successfully!")
                print(f"\n{BOLD}Connector Details:{RESET}")
                print(f"ID: {CYAN}{connector_id}{RESET}")
                print(f"Platform: {connector.get('platform')}")
                print(f"Status: {connector.get('status')}")
                
                # Save connector ID
                with open(creds_file, 'a') as f:
                    f.write(f"\nConnector ID: {connector_id}\n")
                
                print_info(f"Connector ID added to {creds_file}")
                
            else:
                print_error(f"Failed to create connector: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print_error(f"Error creating connector: {str(e)}")
            print_info("You can create it manually later")
    
    # Final Summary
    print_header("🎉 SETUP COMPLETE!")
    
    print_success("Your Google Drive connector is ready!")
    print()
    print(f"{BOLD}What you have:{RESET}")
    print("  ✅ Google Cloud Project created")
    print("  ✅ Drive API enabled")
    print("  ✅ OAuth consent screen configured")
    print("  ✅ OAuth client credentials obtained")
    print("  ✅ Refresh token acquired")
    print("  ✅ Credentials saved securely")
    if create_connector == 'y':
        print("  ✅ Drive connector created")
    print()
    print(f"{BOLD}Next steps:{RESET}")
    print("  1. Test the connector:")
    print(f"     {CYAN}python3 test_drive_connector.py{RESET}")
    print("  2. Integrate with your AI agents")
    print("  3. Start automating file operations!")
    print()
    print_warning(f"Keep {creds_file} and {json_file} secure!")
    print_info("Both files are in .gitignore to prevent accidental commits")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
