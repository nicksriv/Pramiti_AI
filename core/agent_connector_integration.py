"""
Agent-Connector Integration Module
This module provides high-level functions for AI agents to interact with connected services.
"""

import logging
from typing import Dict, List, Any, Optional
from core.connector_implementations import get_connector_implementation

logger = logging.getLogger(__name__)


class AgentConnectorBridge:
    """Bridge between AI agents and external service connectors"""
    
    def __init__(self, connector_manager):
        self.connector_manager = connector_manager
        self.active_connectors = {}
    
    def get_connector(self, connector_id: str):
        """Get or create connector implementation instance"""
        if connector_id in self.active_connectors:
            return self.active_connectors[connector_id]
        
        # Get connector config
        config = self.connector_manager.get_connector(connector_id)
        if not config:
            raise ValueError(f"Connector {connector_id} not found")
        
        # Create connector implementation
        connector = get_connector_implementation(
            config.connector_type.value,
            connector_id,
            config.auth_config
        )
        
        if connector:
            self.active_connectors[connector_id] = connector
            return connector
        
        raise ValueError(f"No implementation found for connector type {config.connector_type.value}")
    
    # ==== Microsoft Teams Functions ====
    
    def teams_send_message(self, connector_id: str, team_id: str, 
                          channel_id: str, message: str) -> bool:
        """
        AI Agent function: Send message to Teams channel
        
        Args:
            connector_id: ID of the Teams connector
            team_id: Microsoft Teams team ID
            channel_id: Channel ID within the team
            message: Message content to send
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            connector = self.get_connector(connector_id)
            result = connector.send_message(team_id, channel_id, message)
            logger.info(f"Agent sent message to Teams channel {channel_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error sending Teams message: {str(e)}")
            return False
    
    def teams_get_messages(self, connector_id: str, team_id: str, 
                          channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        AI Agent function: Read messages from Teams channel
        
        Args:
            connector_id: ID of the Teams connector
            team_id: Microsoft Teams team ID
            channel_id: Channel ID within the team
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message objects
        """
        try:
            connector = self.get_connector(connector_id)
            messages = connector.get_messages(team_id, channel_id, limit)
            logger.info(f"Agent retrieved {len(messages)} messages from Teams")
            return messages
        except Exception as e:
            logger.error(f"Error getting Teams messages: {str(e)}")
            return []
    
    def teams_search(self, connector_id: str, query: str) -> List[Dict[str, Any]]:
        """
        AI Agent function: Search Teams messages
        
        Args:
            connector_id: ID of the Teams connector
            query: Search query string
            
        Returns:
            List of matching messages
        """
        try:
            connector = self.get_connector(connector_id)
            results = connector.search_messages(query)
            logger.info(f"Agent found {len(results)} Teams messages matching '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error searching Teams: {str(e)}")
            return []
    
    # ==== Google Drive Functions ====
    
    def drive_list_files(self, connector_id: str, query: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        AI Agent function: List files in Google Drive
        
        Args:
            connector_id: ID of the Drive connector
            query: Optional filter query
            limit: Maximum number of files to return
            
        Returns:
            List of file objects
        """
        try:
            connector = self.get_connector(connector_id)
            files = connector.list_files(query, limit)
            logger.info(f"Agent retrieved {len(files)} files from Drive")
            return files
        except Exception as e:
            logger.error(f"Error listing Drive files: {str(e)}")
            return []
    
    def drive_search_files(self, connector_id: str, query: str) -> List[Dict[str, Any]]:
        """
        AI Agent function: Search for files in Google Drive
        
        Args:
            connector_id: ID of the Drive connector
            query: Search query string
            
        Returns:
            List of matching files
        """
        try:
            connector = self.get_connector(connector_id)
            files = connector.search_files(query)
            logger.info(f"Agent found {len(files)} Drive files matching '{query}'")
            return files
        except Exception as e:
            logger.error(f"Error searching Drive: {str(e)}")
            return []
    
    def drive_get_file_content(self, connector_id: str, file_id: str) -> Optional[bytes]:
        """
        AI Agent function: Download file content from Google Drive
        
        Args:
            connector_id: ID of the Drive connector
            file_id: ID of the file to download
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            connector = self.get_connector(connector_id)
            content = connector.get_file_content(file_id)
            if content:
                logger.info(f"Agent downloaded file {file_id} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None
    
    def drive_upload_file(self, connector_id: str, file_name: str, content: bytes,
                         mime_type: str = "application/octet-stream",
                         folder_id: Optional[str] = None) -> Optional[str]:
        """
        AI Agent function: Upload file to Google Drive
        
        Args:
            connector_id: ID of the Drive connector
            file_name: Name for the uploaded file
            content: File content as bytes
            mime_type: MIME type of the file
            folder_id: Optional parent folder ID
            
        Returns:
            File ID if successful, None otherwise
        """
        try:
            connector = self.get_connector(connector_id)
            file_id = connector.upload_file(file_name, content, mime_type, folder_id)
            if file_id:
                logger.info(f"Agent uploaded file '{file_name}' to Drive: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def drive_create_folder(self, connector_id: str, folder_name: str,
                           parent_id: Optional[str] = None) -> Optional[str]:
        """
        AI Agent function: Create folder in Google Drive
        
        Args:
            connector_id: ID of the Drive connector
            folder_name: Name for the new folder
            parent_id: Optional parent folder ID
            
        Returns:
            Folder ID if successful, None otherwise
        """
        try:
            connector = self.get_connector(connector_id)
            folder_id = connector.create_folder(folder_name, parent_id)
            if folder_id:
                logger.info(f"Agent created folder '{folder_name}' in Drive: {folder_id}")
            return folder_id
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None


# Example usage for AI agents
class AgentConnectorExamples:
    """Example integration patterns for AI agents"""
    
    @staticmethod
    def example_teams_notification(bridge: AgentConnectorBridge, 
                                   connector_id: str, team_id: str, 
                                   channel_id: str):
        """
        Example: AI agent sends notification to Teams
        """
        message = "🤖 AI Agent Update: Task completed successfully!"
        success = bridge.teams_send_message(connector_id, team_id, channel_id, message)
        return success
    
    @staticmethod
    def example_teams_monitor(bridge: AgentConnectorBridge,
                             connector_id: str, team_id: str,
                             channel_id: str):
        """
        Example: AI agent monitors Teams channel for mentions
        """
        messages = bridge.teams_get_messages(connector_id, team_id, channel_id, limit=20)
        
        # Filter messages mentioning the AI agent
        ai_mentions = [msg for msg in messages 
                      if 'content' in msg.get('body', {}) 
                      and '@AI' in msg['body']['content']]
        
        return ai_mentions
    
    @staticmethod
    def example_drive_backup(bridge: AgentConnectorBridge,
                            connector_id: str, file_content: str,
                            backup_folder_id: str):
        """
        Example: AI agent backs up data to Google Drive
        """
        from datetime import datetime
        
        file_name = f"ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        content = file_content.encode('utf-8')
        
        file_id = bridge.drive_upload_file(
            connector_id, file_name, content,
            mime_type="application/json",
            folder_id=backup_folder_id
        )
        
        return file_id
    
    @staticmethod
    def example_drive_search_and_analyze(bridge: AgentConnectorBridge,
                                        connector_id: str, search_term: str):
        """
        Example: AI agent searches Drive and analyzes documents
        """
        # Search for files
        files = bridge.drive_search_files(connector_id, search_term)
        
        # Download and analyze text files
        analyzed_files = []
        for file in files[:5]:  # Limit to 5 files
            if file.get('mimeType', '').startswith('text/'):
                content = bridge.drive_get_file_content(connector_id, file['id'])
                if content:
                    analyzed_files.append({
                        'name': file['name'],
                        'size': len(content),
                        'preview': content[:200].decode('utf-8', errors='ignore')
                    })
        
        return analyzed_files
