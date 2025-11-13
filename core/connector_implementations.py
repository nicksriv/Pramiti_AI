"""
Production-grade connector implementations for Microsoft Teams and Google Drive.
These classes provide actual API integration for AI agents to read/write data.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

# Import OAuth manager
try:
    from core.oauth_manager import oauth_token_manager, get_oauth_flow
except ImportError:
    oauth_token_manager = None
    get_oauth_flow = None

logger = logging.getLogger(__name__)


class ConnectorImplementation(ABC):
    """Base class for connector implementations"""
    
    def __init__(self, connector_id: str, auth_config: Dict[str, Any]):
        self.connector_id = connector_id
        self.auth_config = auth_config
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the service"""
        pass
    
    def is_token_valid(self) -> bool:
        """Check if access token is still valid"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.is_token_valid():
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }


class MicrosoftTeamsConnector(ConnectorImplementation):
    """Production Microsoft Teams connector using Microsoft Graph API"""
    
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    BETA_API_BASE = "https://graph.microsoft.com/beta"
    
    def authenticate(self) -> bool:
        """
        Authenticate using OAuth 2.0.
        Supports both delegated (user) and application (app-only) authentication.
        Delegated auth is preferred for user-specific operations (email, OneDrive, calendar).
        """
        try:
            tenant_id = self.auth_config.get('tenant_id', 'common')
            client_id = self.auth_config.get('client_id')
            client_secret = self.auth_config.get('client_secret')
            
            if not client_id or not client_secret:
                logger.error("Missing client_id or client_secret for Teams connector")
                return False
            
            # In demo mode, simulate authentication
            if client_id.startswith('demo-'):
                logger.info(f"Demo mode: Simulating Teams authentication for {self.connector_id}")
                self.access_token = "demo_access_token"
                self.token_expiry = datetime.now()
                return True
            
            # Try delegated authentication first (if OAuth manager available and has refresh token)
            if oauth_token_manager and oauth_token_manager.has_refresh_token(self.connector_id):
                logger.info(f"Using delegated auth with refresh token for {self.connector_id}")
                token_data = oauth_token_manager.get_tokens(self.connector_id)
                
                # Check if token is still valid
                if 'expires_at' in token_data:
                    expiry = datetime.fromisoformat(token_data['expires_at'])
                    if datetime.now() < expiry - timedelta(minutes=5):
                        # Token still valid
                        self.access_token = token_data['access_token']
                        self.token_expiry = expiry
                        logger.info(f"Using cached access token for {self.connector_id}")
                        return True
                
                # Token expired, refresh it
                logger.info(f"Refreshing access token for {self.connector_id}")
                if get_oauth_flow:
                    oauth_flow = get_oauth_flow(client_id, client_secret, tenant_id)
                    new_token_data = oauth_flow.refresh_access_token(token_data['refresh_token'])
                    
                    if new_token_data:
                        # Preserve refresh token if not returned
                        if 'refresh_token' not in new_token_data:
                            new_token_data['refresh_token'] = token_data['refresh_token']
                        
                        oauth_token_manager.save_tokens(self.connector_id, new_token_data)
                        self.access_token = new_token_data['access_token']
                        expires_in = new_token_data.get('expires_in', 3600)
                        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                        logger.info(f"Successfully refreshed token for {self.connector_id}")
                        return True
                
                logger.warning(f"Failed to refresh token for {self.connector_id}, falling back to app-only auth")
            
            # Fall back to application (client credentials) authentication
            logger.info(f"Using application auth (client credentials) for {self.connector_id}")
            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                logger.info(f"Successfully authenticated with app-only auth for {self.connector_id}")
                return True
            else:
                logger.error(f"Teams authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating Teams connector: {str(e)}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection by trying to get user info"""
        try:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
            
            # In demo mode, return success
            if self.access_token == "demo_access_token":
                return {
                    "success": True,
                    "message": "Connection test successful (demo mode)",
                    "service": "Microsoft Teams",
                    "api_version": "v1.0"
                }
            
            # Test actual connection to Graph API
            headers = self.get_headers()
            response = requests.get(f"{self.GRAPH_API_BASE}/me", headers=headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Connection test successful",
                    "service": "Microsoft Teams",
                    "api_version": "v1.0"
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all channels in a team"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/teams/{team_id}/channels"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
        except Exception as e:
            logger.error(f"Error getting channels: {str(e)}")
            return []
    
    def send_message(self, team_id: str, channel_id: str, message: str) -> bool:
        """Send a message to a Teams channel"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/teams/{team_id}/channels/{channel_id}/messages"
            
            payload = {
                "body": {
                    "content": message,
                    "contentType": "text"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def get_messages(self, team_id: str, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from a Teams channel"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/teams/{team_id}/channels/{channel_id}/messages"
            params = {'$top': limit}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def search_messages(self, query: str) -> List[Dict[str, Any]]:
        """Search for messages across Teams"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/search/query"
            
            payload = {
                "requests": [{
                    "entityTypes": ["chatMessage"],
                    "query": {
                        "queryString": query
                    }
                }]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                hits = response.json().get('value', [{}])[0].get('hitsContainers', [{}])[0].get('hits', [])
                return [hit.get('resource', {}) for hit in hits]
            return []
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams the user is a member of"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/joinedTeams"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
        except Exception as e:
            logger.error(f"Error getting teams: {str(e)}")
            return []
    
    def create_online_meeting(self, subject: str, start_time: str, end_time: str, 
                             attendees: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create an online Teams meeting
        
        Args:
            subject: Meeting subject/title
            start_time: ISO 8601 format (e.g., "2025-11-13T14:00:00Z")
            end_time: ISO 8601 format (e.g., "2025-11-13T15:00:00Z")
            attendees: List of email addresses
        
        Returns:
            Meeting details including join URL
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/onlineMeetings"
            
            payload = {
                "subject": subject,
                "startDateTime": start_time,
                "endDateTime": end_time
            }
            
            if attendees:
                payload["participants"] = {
                    "attendees": [{"upn": email, "role": "attendee"} for email in attendees]
                }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 201:
                meeting_data = response.json()
                return {
                    "success": True,
                    "meeting_id": meeting_data.get('id'),
                    "join_url": meeting_data.get('joinWebUrl'),
                    "subject": meeting_data.get('subject'),
                    "start_time": meeting_data.get('startDateTime'),
                    "end_time": meeting_data.get('endDateTime')
                }
            else:
                logger.error(f"Failed to create meeting: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "details": response.text
                }
            
        except Exception as e:
            logger.error(f"Error creating online meeting: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get current user's profile information"""
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    # ==================== EMAIL METHODS ====================
    
    def send_email(self, to_recipients: List[str], subject: str, body: str, 
                   cc_recipients: List[str] = None, is_html: bool = True) -> Dict[str, Any]:
        """
        Send an email via Outlook
        
        Args:
            to_recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            cc_recipients: Optional list of CC recipient email addresses
            is_html: Whether body is HTML (default True) or plain text
        
        Returns:
            Success status and message details
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/sendMail"
            
            # Build recipient list
            to_list = [{"emailAddress": {"address": email}} for email in to_recipients]
            
            # Build message payload
            message = {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": to_list
            }
            
            # Add CC recipients if provided
            if cc_recipients:
                message["ccRecipients"] = [{"emailAddress": {"address": email}} for email in cc_recipients]
            
            payload = {
                "message": message,
                "saveToSentItems": True
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 202:  # Accepted
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "subject": subject,
                    "to": to_recipients
                }
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "details": response.text
                }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_emails(self, folder: str = "inbox", top: int = 10, 
                    unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Read emails from Outlook mailbox
        
        Args:
            folder: Folder to read from (inbox, sent, drafts, etc.)
            top: Number of emails to retrieve (max 50)
            unread_only: Only return unread emails
        
        Returns:
            List of email message objects
        """
        try:
            headers = self.get_headers()
            
            # Construct URL with parameters
            url = f"{self.GRAPH_API_BASE}/me/mailFolders/{folder}/messages"
            params = {
                "$top": min(top, 50),  # Limit to 50
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,toRecipients,receivedDateTime,bodyPreview,isRead,hasAttachments"
            }
            
            if unread_only:
                params["$filter"] = "isRead eq false"
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('value', [])
                # Format messages for better readability
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        "id": msg.get('id'),
                        "subject": msg.get('subject', 'No Subject'),
                        "from": msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
                        "from_name": msg.get('from', {}).get('emailAddress', {}).get('name', 'Unknown'),
                        "received": msg.get('receivedDateTime'),
                        "preview": msg.get('bodyPreview', ''),
                        "is_read": msg.get('isRead', False),
                        "has_attachments": msg.get('hasAttachments', False)
                    })
                return formatted_messages
            else:
                logger.error(f"Failed to read emails: {response.status_code} - {response.text}")
                return []
            
        except Exception as e:
            logger.error(f"Error reading emails: {str(e)}")
            return []
    
    def get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a specific email
        
        Args:
            message_id: The ID of the email message
        
        Returns:
            Complete email message object including body
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/messages/{message_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                msg = response.json()
                return {
                    "id": msg.get('id'),
                    "subject": msg.get('subject', 'No Subject'),
                    "from": msg.get('from', {}).get('emailAddress', {}),
                    "to_recipients": [r.get('emailAddress', {}) for r in msg.get('toRecipients', [])],
                    "cc_recipients": [r.get('emailAddress', {}) for r in msg.get('ccRecipients', [])],
                    "received": msg.get('receivedDateTime'),
                    "body_type": msg.get('body', {}).get('contentType'),
                    "body": msg.get('body', {}).get('content', ''),
                    "is_read": msg.get('isRead', False),
                    "has_attachments": msg.get('hasAttachments', False),
                    "attachments": msg.get('attachments', [])
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting email details: {str(e)}")
            return None
    
    def search_emails(self, query: str, top: int = 20) -> List[Dict[str, Any]]:
        """
        Search for emails in mailbox
        
        Args:
            query: Search query (subject, from, body text, etc.)
            top: Number of results to return (max 50)
        
        Returns:
            List of matching email messages
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/messages"
            
            params = {
                "$search": f'"{query}"',
                "$top": min(top, 50),
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,receivedDateTime,bodyPreview,isRead"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('value', [])
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        "id": msg.get('id'),
                        "subject": msg.get('subject', 'No Subject'),
                        "from": msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
                        "from_name": msg.get('from', {}).get('emailAddress', {}).get('name', 'Unknown'),
                        "received": msg.get('receivedDateTime'),
                        "preview": msg.get('bodyPreview', ''),
                        "is_read": msg.get('isRead', False)
                    })
                return formatted_messages
            return []
            
        except Exception as e:
            logger.error(f"Error searching emails: {str(e)}")
            return []
    
    def mark_email_as_read(self, message_id: str, is_read: bool = True) -> bool:
        """
        Mark an email as read or unread
        
        Args:
            message_id: The ID of the email message
            is_read: True to mark as read, False to mark as unread
        
        Returns:
            Success status
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/messages/{message_id}"
            
            payload = {"isRead": is_read}
            response = requests.patch(url, headers=headers, json=payload)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error marking email: {str(e)}")
            return False
    
    # ==================== ONEDRIVE METHODS ====================
    
    def list_onedrive_files(self, folder_path: str = None, search_query: str = None, 
                           top: int = 100) -> List[Dict[str, Any]]:
        """
        List files in OneDrive
        
        Args:
            folder_path: Path to folder (e.g., "/Documents") or None for root
            search_query: Search query to filter files
            top: Maximum number of files to return (max 200)
        
        Returns:
            List of file/folder objects
        """
        try:
            headers = self.get_headers()
            
            if search_query:
                # Search across all of OneDrive
                url = f"{self.GRAPH_API_BASE}/me/drive/root/search(q='{search_query}')"
                params = {"$top": min(top, 200)}
            elif folder_path:
                # List specific folder
                url = f"{self.GRAPH_API_BASE}/me/drive/root:{folder_path}:/children"
                params = {"$top": min(top, 200)}
            else:
                # List root folder
                url = f"{self.GRAPH_API_BASE}/me/drive/root/children"
                params = {"$top": min(top, 200)}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                formatted_items = []
                for item in items:
                    formatted_items.append({
                        "id": item.get('id'),
                        "name": item.get('name'),
                        "type": "folder" if 'folder' in item else "file",
                        "size": item.get('size', 0),
                        "created": item.get('createdDateTime'),
                        "modified": item.get('lastModifiedDateTime'),
                        "web_url": item.get('webUrl'),
                        "download_url": item.get('@microsoft.graph.downloadUrl'),
                        "path": item.get('parentReference', {}).get('path', '')
                    })
                return formatted_items
            else:
                logger.error(f"Failed to list OneDrive files: {response.status_code} - {response.text}")
                return []
            
        except Exception as e:
            logger.error(f"Error listing OneDrive files: {str(e)}")
            return []
    
    def download_onedrive_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get download URL and metadata for a OneDrive file
        
        Args:
            file_id: The ID of the file
        
        Returns:
            File metadata including download URL
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/drive/items/{file_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                item = response.json()
                return {
                    "id": item.get('id'),
                    "name": item.get('name'),
                    "size": item.get('size'),
                    "download_url": item.get('@microsoft.graph.downloadUrl'),
                    "web_url": item.get('webUrl'),
                    "mime_type": item.get('file', {}).get('mimeType'),
                    "created": item.get('createdDateTime'),
                    "modified": item.get('lastModifiedDateTime')
                }
            return None
            
        except Exception as e:
            logger.error(f"Error downloading OneDrive file: {str(e)}")
            return None
    
    def upload_onedrive_file(self, file_name: str, content: bytes, 
                            folder_path: str = None) -> Optional[Dict[str, Any]]:
        """
        Upload a file to OneDrive
        
        Args:
            file_name: Name for the file
            content: File content as bytes
            folder_path: Path to folder (e.g., "/Documents") or None for root
        
        Returns:
            Uploaded file metadata
        """
        try:
            headers = self.get_headers()
            headers['Content-Type'] = 'application/octet-stream'
            
            if folder_path:
                url = f"{self.GRAPH_API_BASE}/me/drive/root:{folder_path}/{file_name}:/content"
            else:
                url = f"{self.GRAPH_API_BASE}/me/drive/root:/{file_name}:/content"
            
            response = requests.put(url, headers=headers, data=content)
            
            if response.status_code in [200, 201]:
                item = response.json()
                return {
                    "success": True,
                    "id": item.get('id'),
                    "name": item.get('name'),
                    "size": item.get('size'),
                    "web_url": item.get('webUrl'),
                    "created": item.get('createdDateTime')
                }
            else:
                logger.error(f"Failed to upload file: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Upload failed with status {response.status_code}",
                    "details": response.text
                }
            
        except Exception as e:
            logger.error(f"Error uploading OneDrive file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_onedrive_folder(self, folder_name: str, 
                              parent_path: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new folder in OneDrive
        
        Args:
            folder_name: Name for the new folder
            parent_path: Path to parent folder or None for root
        
        Returns:
            Created folder metadata
        """
        try:
            headers = self.get_headers()
            
            if parent_path:
                url = f"{self.GRAPH_API_BASE}/me/drive/root:{parent_path}:/children"
            else:
                url = f"{self.GRAPH_API_BASE}/me/drive/root/children"
            
            payload = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                item = response.json()
                return {
                    "success": True,
                    "id": item.get('id'),
                    "name": item.get('name'),
                    "web_url": item.get('webUrl'),
                    "created": item.get('createdDateTime')
                }
            else:
                logger.error(f"Failed to create folder: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Creation failed with status {response.status_code}"
                }
            
        except Exception as e:
            logger.error(f"Error creating OneDrive folder: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_onedrive_item(self, item_id: str) -> bool:
        """
        Delete a file or folder from OneDrive
        
        Args:
            item_id: The ID of the item to delete
        
        Returns:
            Success status
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/drive/items/{item_id}"
            
            response = requests.delete(url, headers=headers)
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Error deleting OneDrive item: {str(e)}")
            return False
    
    def share_onedrive_file(self, item_id: str, 
                           share_type: str = "view") -> Optional[Dict[str, Any]]:
        """
        Create a sharing link for a OneDrive file or folder
        
        Args:
            item_id: The ID of the item to share
            share_type: Type of sharing link ("view" or "edit")
        
        Returns:
            Sharing link information
        """
        try:
            headers = self.get_headers()
            url = f"{self.GRAPH_API_BASE}/me/drive/items/{item_id}/createLink"
            
            payload = {
                "type": share_type,
                "scope": "anonymous"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                link_data = response.json()
                return {
                    "success": True,
                    "link": link_data.get('link', {}).get('webUrl'),
                    "type": share_type,
                    "scope": "anonymous"
                }
            else:
                logger.error(f"Failed to create share link: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Sharing failed with status {response.status_code}"
                }
            
        except Exception as e:
            logger.error(f"Error sharing OneDrive item: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class GoogleDriveConnector(ConnectorImplementation):
    """Production Google Drive connector using Google Drive API v3"""
    
    DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
    UPLOAD_API_BASE = "https://www.googleapis.com/upload/drive/v3"
    
    def authenticate(self) -> bool:
        """
        Authenticate using OAuth 2.0.
        In production, this would exchange auth code or refresh token for access token.
        """
        try:
            client_id = self.auth_config.get('client_id')
            client_secret = self.auth_config.get('client_secret')
            refresh_token = self.auth_config.get('refresh_token')
            
            if not client_id or not client_secret:
                logger.error("Missing client_id or client_secret for Drive connector")
                return False
            
            # In demo mode, simulate authentication
            if client_id.startswith('demo-'):
                logger.info(f"Demo mode: Simulating Drive authentication for {self.connector_id}")
                self.access_token = "demo_access_token"
                self.token_expiry = datetime.now()
                return True
            
            # Production authentication with refresh token
            if not refresh_token:
                logger.error("Missing refresh_token for Drive connector")
                return False
            
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                from datetime import timedelta
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                logger.info(f"Successfully authenticated Drive connector {self.connector_id}")
                return True
            else:
                logger.error(f"Drive authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating Drive connector: {str(e)}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection by getting user's drive info"""
        try:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
            
            # In demo mode, return success
            if self.access_token == "demo_access_token":
                return {
                    "success": True,
                    "message": "Connection test successful (demo mode)",
                    "service": "Google Drive",
                    "api_version": "v3"
                }
            
            # Test actual connection
            headers = self.get_headers()
            response = requests.get(f"{self.DRIVE_API_BASE}/about?fields=user", headers=headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Connection test successful",
                    "service": "Google Drive",
                    "api_version": "v3",
                    "user": response.json().get('user', {})
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List files in Google Drive"""
        try:
            headers = self.get_headers()
            params = {
                'pageSize': limit,
                'fields': 'files(id,name,mimeType,createdTime,modifiedTime,size,webViewLink)'
            }
            
            if query:
                params['q'] = query
            
            response = requests.get(f"{self.DRIVE_API_BASE}/files", headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('files', [])
            return []
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Search for files by name or content"""
        search_query = f"name contains '{query}' or fullText contains '{query}'"
        return self.list_files(query=search_query)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Download file content"""
        try:
            headers = self.get_headers()
            url = f"{self.DRIVE_API_BASE}/files/{file_id}?alt=media"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            return None
            
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            return None
    
    def upload_file(self, file_name: str, content: bytes, mime_type: str = "application/octet-stream",
                   folder_id: Optional[str] = None) -> Optional[str]:
        """Upload a file to Google Drive"""
        try:
            headers = self.get_headers()
            headers['Content-Type'] = 'application/json'
            
            # File metadata
            metadata = {
                'name': file_name,
                'mimeType': mime_type
            }
            
            if folder_id:
                metadata['parents'] = [folder_id]
            
            # Upload file
            url = f"{self.UPLOAD_API_BASE}/files?uploadType=multipart"
            files = {
                'data': ('metadata', json.dumps(metadata), 'application/json'),
                'file': (file_name, content, mime_type)
            }
            
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                return response.json().get('id')
            return None
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Create a folder in Google Drive"""
        try:
            headers = self.get_headers()
            metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                metadata['parents'] = [parent_id]
            
            response = requests.post(f"{self.DRIVE_API_BASE}/files", 
                                   headers=headers, json=metadata)
            
            if response.status_code == 200:
                return response.json().get('id')
            return None
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None


# Connector factory
def get_connector_implementation(connector_type: str, connector_id: str, 
                                auth_config: Dict[str, Any]) -> Optional[ConnectorImplementation]:
    """Factory function to get appropriate connector implementation"""
    connectors = {
        'microsoft_teams': MicrosoftTeamsConnector,
        'google_drive': GoogleDriveConnector
    }
    
    connector_class = connectors.get(connector_type)
    if connector_class:
        return connector_class(connector_id, auth_config)
    return None
