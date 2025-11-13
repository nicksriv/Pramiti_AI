"""
OAuth Assistant Agent
Handles user authentication through natural conversation
"""

import re
from typing import Dict, Any, Optional
from core.base_agent import BaseAgent, Message, MessageType


class OAuthAssistantAgent(BaseAgent):
    """
    Agent that helps users authenticate with Microsoft 365 or Google Workspace
    through natural conversation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="oauth-assistant-001",
            name="OAuth Authentication Assistant",
            specialization="User authentication and access management",
            role="assistant"
        )
        
        # Track authentication sessions
        self.auth_sessions: Dict[str, Dict[str, Any]] = {}
    
    def handle_chat_message(self, message: str, user_id: str) -> str:
        """
        Simple handler for chat messages that returns a string response
        
        Args:
            message: User's message text
            user_id: User identifier
            
        Returns:
            String response to display in chat
        """
        # Create Message object
        msg = Message(
            message_type=MessageType.REQUEST,
            content={"text": message, "user_id": user_id},
            sender_id=user_id
        )
        
        # Process through standard flow
        response = self.process_message(msg)
        
        # Extract text response from content
        if isinstance(response.content, dict) and "text" in response.content:
            return response.content["text"]
        elif isinstance(response.content, str):
            return response.content
        else:
            return str(response.content)
    
    def detect_auth_intent(self, message: str) -> Optional[str]:
        """
        Detect if user wants to authenticate
        
        Returns:
            'microsoft' or 'google' or None
        """
        message_lower = message.lower()
        
        # Microsoft auth keywords
        microsoft_keywords = [
            'microsoft', 'outlook', 'onedrive', 'teams', 
            'microsoft 365', 'office 365', 'm365', 'o365',
            'exchange', 'sharepoint'
        ]
        
        # Google auth keywords
        google_keywords = [
            'google', 'gmail', 'google drive', 'drive',
            'google calendar', 'calendar', 'workspace',
            'google workspace', 'g suite', 'gsuite'
        ]
        
        # Action keywords
        auth_keywords = [
            'login', 'sign in', 'authenticate', 'connect',
            'access', 'authorize', 'link', 'setup', 'configure'
        ]
        
        has_auth_intent = any(keyword in message_lower for keyword in auth_keywords)
        
        if has_auth_intent or 'email' in message_lower or 'calendar' in message_lower:
            if any(keyword in message_lower for keyword in microsoft_keywords):
                return 'microsoft'
            elif any(keyword in message_lower for keyword in google_keywords):
                return 'google'
        
        return None
    
    def extract_email(self, message: str) -> Optional[str]:
        """Extract email address from message"""
        # Simple email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, message)
        return matches[0] if matches else None
    
    def process_message(self, message: Message) -> Message:
        """Process user message and help with authentication"""
        
        # Extract text from content dict
        if isinstance(message.content, dict):
            user_message_text = message.content.get('text', str(message.content))
        else:
            user_message_text = str(message.content)
        
        user_message = user_message_text.lower()
        
        # Check if user wants to authenticate
        auth_type = self.detect_auth_intent(user_message)
        
        if auth_type:
            # Extract email if provided
            user_email = self.extract_email(user_message_text)
            
            if user_email:
                # User provided email, generate auth URL
                return self._start_auth_flow(user_email, auth_type)
            else:
                # Ask for email
                response = self._ask_for_email(auth_type)
                return Message(
                    message_type=MessageType.RESPONSE,
                    content={"text": response},
                    sender_id=self.agent_id,
                    metadata={
                        'requires_email': True,
                        'auth_type': auth_type
                    }
                )
        
        # Check if this is a follow-up with email
        if '@' in user_message_text:
            user_email = self.extract_email(user_message_text)
            if user_email:
                # Determine provider from email domain
                domain = user_email.split('@')[1].lower()
                if 'google' in domain or 'gmail' in domain:
                    auth_type = 'google'
                else:
                    auth_type = 'microsoft'  # Default to Microsoft
                
                return self._start_auth_flow(user_email, auth_type)
        
        # Check if user is asking about authentication status
        if any(word in user_message for word in ['authenticated', 'logged in', 'connected', 'status']):
            return self._check_auth_status()
        
        # Check if user wants to logout/disconnect
        if any(word in user_message for word in ['logout', 'sign out', 'disconnect', 'revoke']):
            user_email = self.extract_email(user_message_text)
            if user_email:
                return self._revoke_auth(user_email)
            else:
                return Message(
                    message_type=MessageType.RESPONSE,
                    content={"text": "Which email account would you like to disconnect? Please provide your email address."},
                    sender_id=self.agent_id
                )
        
        # Default help message
        return self._show_help()
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method - OAuth agent makes authentication decisions"""
        return {
            "decision": "handle_oauth",
            "action": "process_authentication_request",
            "context": context
        }
    
    def _ask_for_email(self, auth_type: str) -> str:
        """Ask user for their email address"""
        provider = "Microsoft 365" if auth_type == "microsoft" else "Google Workspace"
        
        # For now, use a generic placeholder that will be caught by API
        # This allows direct OAuth flow without email
        placeholder_email = "user@placeholder.com"
        
        return f"""
🔐 **{provider} Authentication**

Great! I'll redirect you to {provider} to sign in.

🔗 **Click here to authenticate:** [Login with {provider}](#auth-{auth_type}-{placeholder_email})

**What happens next:**
1. You'll be redirected to {provider} login page
2. Log in with your work account credentials
3. Accept the requested permissions
4. You'll be redirected back to the application
5. Done! You can now use all features

**Permissions requested:**
{"• Read and send emails (Outlook)" if auth_type == "microsoft" else "• Read and send emails (Gmail)"}
{"• Access files (OneDrive)" if auth_type == "microsoft" else "• Access files (Google Drive)"}
{"• Manage calendar events" if auth_type == "microsoft" else "• Manage calendar events (Google Calendar)"}
{"• Create meetings (Teams)" if auth_type == "microsoft" else ""}

🔒 **Security:** Your tokens are encrypted and stored separately. We never see your password.

_This is a one-time setup. Your authentication will be remembered for future sessions._
        """.strip()
    
    def _start_auth_flow(self, user_email: str, auth_type: str) -> Message:
        """Start OAuth authentication flow"""
        
        provider = "Microsoft 365" if auth_type == "microsoft" else "Google Workspace"
        
        # Generate auth URL (this will be done via API call in practice)
        response_content = f"""
✅ **Authentication Started for {user_email}**

**Provider:** {provider}

I'm generating your secure login link... 

🔗 **Click here to authenticate:** [Login with {provider}](#auth-{auth_type}-{user_email})

**What happens next:**
1. You'll be redirected to {provider} login page
2. Log in with your work account credentials
3. Accept the requested permissions
4. You'll be redirected back to the application
5. Done! You can now use all features

**Permissions requested:**
{"• Read and send emails (Outlook)" if auth_type == "microsoft" else "• Read and send emails (Gmail)"}
{"• Access files (OneDrive)" if auth_type == "microsoft" else "• Access files (Google Drive)"}
{"• Manage calendar events" if auth_type == "microsoft" else "• Manage calendar events (Google Calendar)"}
{"• Create meetings (Teams)" if auth_type == "microsoft" else ""}

🔒 **Security:** Your tokens are encrypted and stored separately. We never see your password.

_This is a one-time setup. Your authentication will be remembered for future sessions._
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response_content},
            sender_id=self.agent_id,
            metadata={
                'action': 'start_oauth',
                'user_email': user_email,
                'auth_type': auth_type,
                'requires_redirect': True
            }
        )
    
    def _check_auth_status(self) -> Message:
        """Check authentication status"""
        
        content = """
📊 **Authentication Status**

To check your authentication status, I need your email address.

**Commands you can use:**
• `Check status for john.doe@company.com`
• `Am I logged in as jane@company.com?`
• `Show my authentication status`

Or simply provide your email address and I'll check if you're authenticated.
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": content},
            sender_id=self.agent_id,
            metadata={'action': 'check_status'}
        )
    
    def _revoke_auth(self, user_email: str) -> Message:
        """Revoke user authentication"""
        
        content = f"""
🔓 **Revoke Authentication**

Are you sure you want to disconnect **{user_email}**?

This will:
• Remove all stored authentication tokens
• Revoke access to your email, files, and calendar
• Require re-authentication to use services again

**To confirm, reply with:** `Yes, disconnect {user_email}`
**To cancel, reply with:** `Cancel`

🔒 Your data will remain secure. This only affects this application's access.
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": content},
            sender_id=self.agent_id,
            metadata={
                'action': 'confirm_revoke',
                'user_email': user_email
            }
        )
    
    def _show_help(self) -> Message:
        """Show help message"""
        
        content = """
👋 **OAuth Authentication Assistant**

I help you connect your work accounts to access emails, files, and calendars.

**What I can do:**
• 🔐 Set up Microsoft 365 authentication (Outlook, OneDrive, Teams)
• 🔐 Set up Google Workspace authentication (Gmail, Drive, Calendar)
• ✅ Check your authentication status
• 🔓 Disconnect your account

**How to get started:**
Simply tell me what you want to do! For example:

• "I want to connect my Microsoft account"
• "Login with Google"
• "Access my Outlook emails"
• "My email is john.doe@company.com"
• "Set up Gmail integration"

**Security & Privacy:**
• Each user's credentials are stored separately
• We use industry-standard OAuth 2.0
• You control what permissions to grant
• You can disconnect anytime
• Your password is never shared with us

**Need help with a specific service?**
Let me know if you want to connect Microsoft 365 or Google Workspace!
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": content},
            sender_id=self.agent_id,
            metadata={'action': 'help'}
        )


# Create global instance
oauth_assistant = OAuthAssistantAgent()
