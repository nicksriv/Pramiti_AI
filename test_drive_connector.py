#!/usr/bin/env python3
"""
Interactive test script for Google Drive connector.
Tests file listing, upload, download, search, and folder creation capabilities.
"""

import requests
import json
import base64
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8084/api/v1"

# Your connector ID will be set after creation
CONNECTOR_ID = None  # Will be prompted

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
    """Format file size"""
    if not bytes_size:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_connector_id():
    """Get connector ID from user or file"""
    global CONNECTOR_ID
    
    # Try to read from credentials file
    try:
        with open('drive_credentials.txt', 'r') as f:
            for line in f:
                if line.startswith('Connector ID:'):
                    CONNECTOR_ID = line.split(':', 1)[1].strip()
                    print_info(f"Found connector ID: {CONNECTOR_ID}")
                    return True
    except FileNotFoundError:
        pass
    
    # Prompt user
    CONNECTOR_ID = input(f"{CYAN}Enter your Google Drive connector ID: {RESET}").strip()
    if CONNECTOR_ID:
        return True
    
    print_error("Connector ID is required!")
    return False


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
    """List files in Google Drive"""
    print_header("STEP 2: List Google Drive Files")
    
    query = input(f"{CYAN}Enter query (or press Enter for all files): {RESET}").strip()
    query = query if query else None
    
    limit = input(f"{CYAN}How many files? (default: 50): {RESET}").strip()
    limit = int(limit) if limit.isdigit() else 50
    
    try:
        params = {"limit": limit}
        if query:
            params["query"] = query
        
        print_info(f"Listing files...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "list_files",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            files = response.json()
            
            if not files:
                print_warning("No files found")
                return
            
            print_success(f"Found {len(files)} file(s)")
            print("\n" + "─" * 80)
            
            for i, file in enumerate(files, 1):
                mime_type = file.get('mimeType', '')
                if 'folder' in mime_type:
                    icon = "📁"
                elif 'document' in mime_type:
                    icon = "📄"
                elif 'spreadsheet' in mime_type:
                    icon = "📊"
                elif 'presentation' in mime_type:
                    icon = "📽️"
                elif 'image' in mime_type:
                    icon = "🖼️"
                else:
                    icon = "📎"
                
                print(f"\n{icon} {BOLD}#{i}: {file.get('name')}{RESET}")
                print(f"   ID: {file.get('id')}")
                print(f"   Type: {mime_type}")
                if file.get('size'):
                    print(f"   Size: {format_size(int(file.get('size')))}")
                print(f"   Modified: {file.get('modifiedTime')}")
                if file.get('webViewLink'):
                    print(f"   URL: {file.get('webViewLink')[:60]}...")
            
            print("\n" + "─" * 80)
            
            global last_files
            last_files = files
            
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error listing files: {str(e)}")
        import traceback
        traceback.print_exc()


def search_files():
    """Search for files"""
    print_header("STEP 3: Search Files")
    
    query = input(f"{CYAN}Enter search query: {RESET}").strip()
    if not query:
        print_warning("No query provided")
        return
    
    try:
        print_info(f"Searching for '{query}'...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "search_files",
                "parameters": {"query": query}
            }
        )
        
        if response.status_code == 200:
            files = response.json()
            
            if not files:
                print_warning(f"No files found matching '{query}'")
                return
            
            print_success(f"Found {len(files)} matching file(s)")
            
            for i, file in enumerate(files, 1):
                print(f"\n{BOLD}Result #{i}:{RESET} {file.get('name')}")
                print(f"   ID: {file.get('id')}")
                print(f"   Type: {file.get('mimeType')}")
                
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error searching files: {str(e)}")
        import traceback
        traceback.print_exc()


def upload_file():
    """Upload a file to Google Drive"""
    print_header("STEP 4: Upload File")
    
    file_name = input(f"{CYAN}Enter file name (e.g., test.txt): {RESET}").strip()
    if not file_name:
        file_name = f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        print_info(f"Using default name: {file_name}")
    
    content = input(f"{CYAN}Enter file content: {RESET}").strip()
    if not content:
        content = f"Test file created at {datetime.now()}"
    
    folder_id = input(f"{CYAN}Upload to folder ID (or press Enter for root): {RESET}").strip()
    folder_id = folder_id if folder_id else None
    
    try:
        print_info(f"Uploading '{file_name}'...")
        
        params = {
            "file_name": file_name,
            "content": base64.b64encode(content.encode()).decode(),
            "mime_type": "text/plain"
        }
        
        if folder_id:
            params["folder_id"] = folder_id
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "upload_file",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            file_id = response.json()
            if file_id:
                print_success("File uploaded successfully!")
                print(f"File ID: {file_id}")
            else:
                print_error("Upload failed")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error uploading file: {str(e)}")
        import traceback
        traceback.print_exc()


def create_folder():
    """Create a new folder"""
    print_header("STEP 5: Create Folder")
    
    folder_name = input(f"{CYAN}Enter folder name: {RESET}").strip()
    if not folder_name:
        folder_name = f"TestFolder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print_info(f"Using default name: {folder_name}")
    
    parent_id = input(f"{CYAN}Parent folder ID (or press Enter for root): {RESET}").strip()
    parent_id = parent_id if parent_id else None
    
    try:
        print_info(f"Creating folder '{folder_name}'...")
        
        params = {"folder_name": folder_name}
        if parent_id:
            params["parent_id"] = parent_id
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "create_folder",
                "parameters": params
            }
        )
        
        if response.status_code == 200:
            folder_id = response.json()
            if folder_id:
                print_success("Folder created successfully!")
                print(f"Folder ID: {folder_id}")
                print(f"View at: https://drive.google.com/drive/folders/{folder_id}")
            else:
                print_error("Folder creation failed")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error creating folder: {str(e)}")
        import traceback
        traceback.print_exc()


def download_file():
    """Download file content"""
    print_header("STEP 6: Download File")
    
    file_id = input(f"{CYAN}Enter file ID to download: {RESET}").strip()
    if not file_id:
        print_warning("No file ID provided")
        return
    
    try:
        print_info(f"Downloading file...")
        
        response = requests.post(
            f"{API_BASE}/connectors/{CONNECTOR_ID}/execute",
            json={
                "action": "get_file_content",
                "parameters": {"file_id": file_id}
            }
        )
        
        if response.status_code == 200:
            content = response.json()
            if content:
                print_success("File content retrieved!")
                print(f"\n{BOLD}Content:{RESET}")
                print("─" * 80)
                # Try to decode if it's text
                try:
                    text = base64.b64decode(content).decode('utf-8')
                    print(text[:500])
                    if len(text) > 500:
                        print("... (truncated)")
                except:
                    print(f"Binary content, size: {format_size(len(content))}")
                print("─" * 80)
            else:
                print_error("Failed to get file content")
        else:
            print_error(f"API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print_error(f"Error downloading file: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test flow"""
    print(f"{BOLD}{CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                  GOOGLE DRIVE CONNECTOR TEST                              ║")
    print("║                    Testing File Operations                                ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    # Get connector ID
    if not get_connector_id():
        return
    
    print_info(f"Using connector: {CONNECTOR_ID}")
    print()
    
    # Test connector status
    if not test_connector_status():
        print_error("Connector is not ready. Please check setup.")
        return
    
    input(f"\n{YELLOW}Press Enter to continue to Drive tests...{RESET}")
    
    # Main test loop
    global last_files
    last_files = []
    
    while True:
        print_header("GOOGLE DRIVE TEST MENU")
        print(f"{CYAN}1.{RESET} List files")
        print(f"{CYAN}2.{RESET} Search files")
        print(f"{CYAN}3.{RESET} Upload file")
        print(f"{CYAN}4.{RESET} Create folder")
        print(f"{CYAN}5.{RESET} Download file")
        print(f"{CYAN}6.{RESET} Exit")
        
        choice = input(f"\n{CYAN}Select option (1-6): {RESET}").strip()
        
        if choice == '1':
            list_files()
        elif choice == '2':
            search_files()
        elif choice == '3':
            upload_file()
        elif choice == '4':
            create_folder()
        elif choice == '5':
            download_file()
        elif choice == '6':
            print_success("Goodbye!")
            break
        else:
            print_warning("Invalid option, please select 1-6")
        
        input(f"\n{YELLOW}Press Enter to continue...{RESET}")
    
    print_header("TEST COMPLETE")
    print_success("All Google Drive tests completed!")
    print()
    print_info("Your system now has:")
    print("  ✅ Microsoft 365 (Teams, Meetings, Email, OneDrive)")
    print("  ✅ Google Drive")
    print()
    print("🎉 Ready for full cloud integration with AI agents!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
