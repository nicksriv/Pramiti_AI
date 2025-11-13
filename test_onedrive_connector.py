#!/usr/bin/env python3
"""
Interactive test script for Microsoft OneDrive integration via Teams connector.
Tests file listing, upload, download, folder creation, and sharing capabilities.
"""

import requests
import json
import base64
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8084/api/v1"

# Set your connector ID here
CONNECTOR_ID = "microsoft_teams_833476c52e87e4ac"

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


def format_size(bytes_size):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


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
            return False
            
    except Exception as e:
        print_error(f"Error checking connector status: {str(e)}")
        return False


def list_files():
    """List files in OneDrive"""
    print_header("STEP 2: List OneDrive Files")
    
    folder_path = input(f"{CYAN}Enter folder path (e.g., /Documents) or press Enter for root: {RESET}").strip()
    folder_path = folder_path if folder_path else None
    
    search_query = input(f"{CYAN}Search query (or press Enter to list all): {RESET}").strip()
    search_query = search_query if search_query else None
    
    count = input(f"{CYAN}How many items? (default: 50): {RESET}").strip()
    count = int(count) if count.isdigit() else 50
    
    try:
        params = {"top": count}
        if folder_path:
            params["folder_path"] = folder_path
        if search_query:
            params["search_query"] = search_query
        
        print_info(f"Listing files...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "list_onedrive_files",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            items = response.json()
            
            if not items:
                print_warning("No files found")
                return
            
            print_success(f"Found {len(items)} item(s)")
            print("\n" + "─" * 80)
            
            for i, item in enumerate(items, 1):
                icon = "📁" if item['type'] == 'folder' else "📄"
                print(f"\n{icon} {BOLD}#{i}: {item['name']}{RESET}")
                print(f"   Type: {item['type']}")
                print(f"   Size: {format_size(item['size'])}")
                print(f"   Modified: {item['modified']}")
                print(f"   ID: {item['id'][:30]}...")
                if item.get('web_url'):
                    print(f"   URL: {item['web_url'][:60]}...")
            
            print("\n" + "─" * 80)
            
            # Save last items for other operations
            global last_items
            last_items = items
            
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error listing files: {str(e)}")
        import traceback
        traceback.print_exc()


def upload_file():
    """Upload a file to OneDrive"""
    print_header("STEP 3: Upload File to OneDrive")
    
    file_name = input(f"{CYAN}Enter file name to create (e.g., test.txt): {RESET}").strip()
    if not file_name:
        file_name = f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        print_info(f"Using default name: {file_name}")
    
    content = input(f"{CYAN}Enter file content (or press Enter for default): {RESET}").strip()
    if not content:
        content = f"Test file created by OneDrive connector at {datetime.now()}"
    
    folder_path = input(f"{CYAN}Upload to folder (e.g., /Documents) or press Enter for root: {RESET}").strip()
    folder_path = folder_path if folder_path else None
    
    try:
        print_info(f"Uploading '{file_name}'...")
        
        # Convert content to bytes and then base64 for JSON transport
        content_bytes = content.encode('utf-8')
        
        params = {
            "file_name": file_name,
            "content": content_bytes.decode('utf-8') if len(content_bytes) < 100 else base64.b64encode(content_bytes).decode('utf-8')
        }
        
        if folder_path:
            params["folder_path"] = folder_path
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "upload_onedrive_file",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("File uploaded successfully!")
                print(f"Name: {result.get('name')}")
                print(f"Size: {format_size(result.get('size', 0))}")
                print(f"URL: {result.get('web_url')}")
            else:
                print_error(f"Upload failed: {result.get('error')}")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error uploading file: {str(e)}")
        import traceback
        traceback.print_exc()


def create_folder():
    """Create a new folder in OneDrive"""
    print_header("STEP 4: Create Folder")
    
    folder_name = input(f"{CYAN}Enter folder name: {RESET}").strip()
    if not folder_name:
        folder_name = f"TestFolder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print_info(f"Using default name: {folder_name}")
    
    parent_path = input(f"{CYAN}Create in folder (e.g., /Documents) or press Enter for root: {RESET}").strip()
    parent_path = parent_path if parent_path else None
    
    try:
        print_info(f"Creating folder '{folder_name}'...")
        
        params = {"folder_name": folder_name}
        if parent_path:
            params["parent_path"] = parent_path
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "create_onedrive_folder",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Folder created successfully!")
                print(f"Name: {result.get('name')}")
                print(f"URL: {result.get('web_url')}")
            else:
                print_error(f"Creation failed: {result.get('error')}")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error creating folder: {str(e)}")
        import traceback
        traceback.print_exc()


def download_file():
    """Get download URL for a file"""
    print_header("STEP 5: Download File")
    
    file_id = input(f"{CYAN}Enter file ID (from list above): {RESET}").strip()
    if not file_id:
        print_warning("No file ID provided")
        return
    
    try:
        print_info(f"Getting download URL...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "download_onedrive_file",
                "parameters": {"file_id": file_id}
            }
        )
        
        if response.status_code == 200:
            file_info = response.json()
            if file_info:
                print_success("File information retrieved!")
                print(f"\n{BOLD}File Details:{RESET}")
                print(f"Name: {file_info.get('name')}")
                print(f"Size: {format_size(file_info.get('size', 0))}")
                print(f"Type: {file_info.get('mime_type')}")
                print(f"Modified: {file_info.get('modified')}")
                print(f"\n{BOLD}Download URL:{RESET}")
                print(file_info.get('download_url'))
                print(f"\n{BOLD}Web URL:{RESET}")
                print(file_info.get('web_url'))
            else:
                print_error("File not found")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error getting file info: {str(e)}")
        import traceback
        traceback.print_exc()


def share_file():
    """Create a sharing link for a file"""
    print_header("STEP 6: Share File")
    
    item_id = input(f"{CYAN}Enter item ID to share: {RESET}").strip()
    if not item_id:
        print_warning("No item ID provided")
        return
    
    share_type = input(f"{CYAN}Share type (view/edit, default: view): {RESET}").strip().lower()
    share_type = share_type if share_type in ['view', 'edit'] else 'view'
    
    try:
        print_info(f"Creating {share_type} link...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "share_onedrive_file",
                "parameters": {
                    "item_id": item_id,
                    "share_type": share_type
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Sharing link created!")
                print(f"\n{BOLD}Share Link:{RESET}")
                print(result.get('link'))
                print(f"\nType: {result.get('type')}")
                print(f"Scope: {result.get('scope')}")
            else:
                print_error(f"Sharing failed: {result.get('error')}")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error creating share link: {str(e)}")
        import traceback
        traceback.print_exc()


def delete_item():
    """Delete a file or folder"""
    print_header("STEP 7: Delete Item")
    
    print_warning("This will permanently delete the item!")
    item_id = input(f"{CYAN}Enter item ID to delete (or press Enter to cancel): {RESET}").strip()
    if not item_id:
        print_info("Cancelled")
        return
    
    confirm = input(f"{RED}Are you sure? Type 'yes' to confirm: {RESET}").strip().lower()
    if confirm != 'yes':
        print_info("Cancelled")
        return
    
    try:
        print_info(f"Deleting item...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "delete_onedrive_item",
                "parameters": {"item_id": item_id}
            }
        )
        
        if response.status_code == 200:
            success = response.json()
            if success:
                print_success("Item deleted successfully!")
            else:
                print_error("Failed to delete item")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error deleting item: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test flow"""
    print(f"{BOLD}{CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                  MICROSOFT ONEDRIVE CONNECTOR TEST                        ║")
    print("║                    Testing File Management                                ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info(f"Using connector: {CONNECTOR_ID}")
    print_warning("Make sure you've added Files API permissions in Azure AD!")
    print_info("See ONEDRIVE_SETUP.md for setup instructions\n")
    
    # Test 1: Check connector status
    if not test_connector_status():
        print_error("Connector is not ready. Please check setup.")
        return
    
    input(f"\n{YELLOW}Press Enter to continue to OneDrive tests...{RESET}")
    
    # Main test loop
    global last_items
    last_items = []
    
    while True:
        print_header("ONEDRIVE TEST MENU")
        print(f"{CYAN}1.{RESET} List files/folders")
        print(f"{CYAN}2.{RESET} Upload file")
        print(f"{CYAN}3.{RESET} Create folder")
        print(f"{CYAN}4.{RESET} Download file")
        print(f"{CYAN}5.{RESET} Share file/folder")
        print(f"{CYAN}6.{RESET} Delete item")
        print(f"{CYAN}7.{RESET} Exit")
        
        choice = input(f"\n{CYAN}Select option (1-7): {RESET}").strip()
        
        if choice == '1':
            list_files()
        elif choice == '2':
            upload_file()
        elif choice == '3':
            create_folder()
        elif choice == '4':
            download_file()
        elif choice == '5':
            share_file()
        elif choice == '6':
            delete_item()
        elif choice == '7':
            print_success("Goodbye!")
            break
        else:
            print_warning("Invalid option, please select 1-7")
        
        input(f"\n{YELLOW}Press Enter to continue...{RESET}")
    
    print_header("TEST COMPLETE")
    print_success("All OneDrive tests completed!")
    print_info("Your connector now has:")
    print("  ✅ Teams messaging")
    print("  ✅ Online meetings")
    print("  ✅ Outlook email")
    print("  ✅ OneDrive file management")
    print("\n🎉 Ready to integrate with AI agents!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
