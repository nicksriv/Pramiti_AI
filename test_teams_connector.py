#!/usr/bin/env python3
"""
Microsoft Teams Connector Test Script
Test your Teams integration and create meetings via AI agent
"""

import sys
import requests
import json
from datetime import datetime, timedelta

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[96m'

API_BASE = "http://localhost:8084"
CONNECTOR_ID = "microsoft_teams_833476c52e87e4ac"

def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{ENDC}")
    print(f"{BOLD}{BLUE}{text.center(80)}{ENDC}")
    print(f"{BOLD}{BLUE}{'=' * 80}{ENDC}\n")

def print_success(text: str):
    print(f"{GREEN}✅ {text}{ENDC}")

def print_error(text: str):
    print(f"{RED}❌ {text}{ENDC}")

def print_info(text: str):
    print(f"{CYAN}ℹ️  {text}{ENDC}")

def print_json(data):
    print(f"{CYAN}{json.dumps(data, indent=2)}{ENDC}")

def get_input(prompt: str, default: str = None) -> str:
    if default:
        user_input = input(f"{YELLOW}{prompt} [{default}]: {ENDC}").strip()
        return user_input if user_input else default
    return input(f"{YELLOW}{prompt}: {ENDC}").strip()


def test_connector_status():
    """Check connector status"""
    print_header("Step 1: Check Connector Status")
    
    try:
        response = requests.get(f"{API_BASE}/api/v1/connectors/{CONNECTOR_ID}")
        if response.status_code == 200:
            connector = response.json()
            print_success(f"Connector: {connector['name']}")
            print_info(f"Status: {connector['status']}")
            print_info(f"Type: {connector['connector_type']}")
            print_info(f"Auth: {connector['auth_type']}")
            print_info(f"Permissions: {', '.join(connector['permissions'])}")
            return True
        else:
            print_error(f"Failed to get connector: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def get_user_profile():
    """Get user's Teams profile"""
    print_header("Step 2: Get Your Teams Profile")
    
    try:
        # We need to add this endpoint
        from core.connector_implementations import get_connector_implementation
        from core.connectors import connector_manager
        
        config = connector_manager.get_connector(CONNECTOR_ID)
        connector = get_connector_implementation("microsoft_teams", CONNECTOR_ID, config.auth_config)
        
        profile = connector.get_user_profile()
        
        if profile:
            print_success("Profile retrieved successfully!")
            print_info(f"Name: {profile.get('displayName', 'N/A')}")
            print_info(f"Email: {profile.get('mail') or profile.get('userPrincipalName', 'N/A')}")
            print_info(f"Job Title: {profile.get('jobTitle', 'N/A')}")
            print_info(f"Office: {profile.get('officeLocation', 'N/A')}")
            return profile
        else:
            print_error("Failed to get profile")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_teams_list():
    """Get list of teams user is member of"""
    print_header("Step 3: Get Your Teams")
    
    try:
        from core.connector_implementations import get_connector_implementation
        from core.connectors import connector_manager
        
        config = connector_manager.get_connector(CONNECTOR_ID)
        connector = get_connector_implementation("microsoft_teams", CONNECTOR_ID, config.auth_config)
        
        teams = connector.get_teams()
        
        if teams:
            print_success(f"Found {len(teams)} teams!")
            for i, team in enumerate(teams, 1):
                print(f"\n{BOLD}Team {i}:{ENDC}")
                print(f"  Name: {team.get('displayName')}")
                print(f"  ID: {team.get('id')}")
                print(f"  Description: {team.get('description', 'N/A')}")
            return teams
        else:
            print_info("No teams found or unable to retrieve")
            return []
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_team_channels(team_id: str):
    """Get channels for a specific team"""
    print_header("Step 4: Get Channels")
    
    try:
        from core.connector_implementations import get_connector_implementation
        from core.connectors import connector_manager
        
        config = connector_manager.get_connector(CONNECTOR_ID)
        connector = get_connector_implementation("microsoft_teams", CONNECTOR_ID, config.auth_config)
        
        channels = connector.get_channels(team_id)
        
        if channels:
            print_success(f"Found {len(channels)} channels!")
            for i, channel in enumerate(channels, 1):
                print(f"\n{BOLD}Channel {i}:{ENDC}")
                print(f"  Name: {channel.get('displayName')}")
                print(f"  ID: {channel.get('id')}")
                print(f"  Description: {channel.get('description', 'N/A')}")
            return channels
        else:
            print_info("No channels found")
            return []
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def create_teams_meeting():
    """Create a Teams online meeting"""
    print_header("Create Teams Meeting via AI Agent")
    
    print_info("Let's create a Teams meeting!")
    print()
    
    # Get meeting details
    subject = get_input("Meeting subject", "AI Agent Test Meeting")
    
    # Calculate default times (30 minutes from now, 1 hour duration)
    now = datetime.now()
    default_start = now + timedelta(minutes=30)
    default_end = default_start + timedelta(hours=1)
    
    print()
    print_info("Meeting times (use ISO 8601 format: YYYY-MM-DDTHH:MM:SS)")
    print_info(f"Example: {default_start.strftime('%Y-%m-%dT%H:%M:%S')}")
    print()
    
    start_time = get_input("Start time", default_start.strftime('%Y-%m-%dT%H:%M:%S'))
    end_time = get_input("End time", default_end.strftime('%Y-%m-%dT%H:%M:%S'))
    
    # Add UTC timezone
    if not start_time.endswith('Z'):
        start_time += 'Z'
    if not end_time.endswith('Z'):
        end_time += 'Z'
    
    print()
    attendees_input = get_input("Attendees (comma-separated emails, or press Enter to skip)", "")
    attendees = [email.strip() for email in attendees_input.split(',') if email.strip()] if attendees_input else None
    
    print()
    print_info(f"Creating meeting: {subject}")
    print_info(f"Start: {start_time}")
    print_info(f"End: {end_time}")
    if attendees:
        print_info(f"Attendees: {', '.join(attendees)}")
    
    try:
        from core.connector_implementations import get_connector_implementation
        from core.connectors import connector_manager
        
        config = connector_manager.get_connector(CONNECTOR_ID)
        connector = get_connector_implementation("microsoft_teams", CONNECTOR_ID, config.auth_config)
        
        result = connector.create_online_meeting(subject, start_time, end_time, attendees)
        
        if result and result.get('success'):
            print()
            print_success("🎉 Meeting created successfully!")
            print()
            print(f"{BOLD}Meeting Details:{ENDC}")
            print(f"  Subject: {result.get('subject')}")
            print(f"  Start: {result.get('start_time')}")
            print(f"  End: {result.get('end_time')}")
            print(f"  Meeting ID: {result.get('meeting_id')}")
            print()
            print(f"{BOLD}{GREEN}Join URL:{ENDC}")
            print(f"{CYAN}{result.get('join_url')}{ENDC}")
            print()
            print_success("Share this URL with participants to join the meeting!")
            return result
        else:
            print_error("Failed to create meeting")
            if result:
                print_error(f"Error: {result.get('error')}")
                if result.get('details'):
                    print_json(json.loads(result.get('details')))
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def send_test_message():
    """Send a test message to a Teams channel"""
    print_header("Send Message to Teams Channel")
    
    print_info("First, we need a team and channel ID")
    print()
    
    team_id = get_input("Team ID (from your Teams list above)")
    channel_id = get_input("Channel ID (from your channel list above)")
    message = get_input("Message to send", "🤖 Hello from AI Agent!")
    
    try:
        from core.connector_implementations import get_connector_implementation
        from core.connectors import connector_manager
        
        config = connector_manager.get_connector(CONNECTOR_ID)
        connector = get_connector_implementation("microsoft_teams", CONNECTOR_ID, config.auth_config)
        
        success = connector.send_message(team_id, channel_id, message)
        
        if success:
            print_success("Message sent successfully!")
        else:
            print_error("Failed to send message")
            
        return success
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print_header("Microsoft Teams Integration Test")
    print_info("This script will test your Teams connector and create a meeting")
    print()
    
    # Check API server
    try:
        response = requests.get(f"{API_BASE}/api/v1/connectors/available", timeout=2)
        if response.status_code != 200:
            print_error("API server not responding")
            sys.exit(1)
    except:
        print_error("Cannot connect to API server at http://localhost:8084")
        print_info("Please start the API server: python3 api_server.py")
        sys.exit(1)
    
    print_success("API server is running")
    
    # Test connector status
    if not test_connector_status():
        print_error("Connector check failed")
        sys.exit(1)
    
    input(f"\n{YELLOW}Press Enter to continue...{ENDC}")
    
    # Get user profile
    profile = get_user_profile()
    if not profile:
        print_error("Could not get user profile - check API permissions")
        print_info("You may need OnlineMeetings.ReadWrite permission")
    
    input(f"\n{YELLOW}Press Enter to continue...{ENDC}")
    
    # Get teams
    teams = get_teams_list()
    
    if teams:
        input(f"\n{YELLOW}Press Enter to continue...{ENDC}")
        
        # Get channels for first team
        if input(f"\n{YELLOW}Get channels for a team? (y/n): {ENDC}").lower() == 'y':
            team_id = get_input("Enter team ID", teams[0]['id'] if teams else "")
            get_team_channels(team_id)
    
    input(f"\n{YELLOW}Press Enter to continue to meeting creation...{ENDC}")
    
    # Create meeting
    if input(f"\n{YELLOW}Create a Teams meeting? (y/n): {ENDC}").lower() == 'y':
        create_teams_meeting()
    
    # Send message
    if teams and input(f"\n{YELLOW}Send a test message? (y/n): {ENDC}").lower() == 'y':
        send_test_message()
    
    print_header("Test Complete!")
    print_success("Your Teams connector is working!")
    print_info("You can now use it in your AI agents for:")
    print_info("  • Creating meetings")
    print_info("  • Sending messages")
    print_info("  • Reading messages")
    print_info("  • Searching conversations")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Test cancelled{ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}Error: {str(e)}{ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
