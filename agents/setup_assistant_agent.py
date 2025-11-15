"""
Setup Assistant Agent
Guides IT admins through OAuth configuration for Microsoft 365 and Google Workspace
"""

import re
import os
import json
from typing import Dict, Any, Optional
from core.base_agent import BaseAgent, Message, MessageType


class SetupAssistantAgent(BaseAgent):
    """
    Agent that helps IT admins configure OAuth credentials through conversational interface
    """
    
    def __init__(self):
        super().__init__(
            agent_id="setup-assistant-001",
            name="Setup Assistant",
            specialization="OAuth and system configuration",
            role="assistant"
        )
        
        # Track setup sessions per user
        self.setup_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Configuration file path (for multi-tenant support)
        self.config_dir = "config/oauth"
        os.makedirs(self.config_dir, exist_ok=True)
    
    def handle_chat_message(self, message: str, user_id: str) -> str:
        """
        Simple handler for chat messages that returns a string response
        
        Args:
            message: User's message text
            user_id: User identifier (organization ID or admin ID)
            
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
    
    def detect_setup_intent(self, message: str) -> Optional[str]:
        """
        Detect if user wants to set up OAuth
        
        Returns:
            'microsoft', 'google', 'setup', or None
        """
        message_lower = message.lower()
        
        # Setup keywords
        setup_keywords = ['setup', 'configure', 'install', 'set up', 'initialize', 
                         'credentials', 'oauth', 'integration', 'connect']
        
        # Microsoft keywords
        microsoft_keywords = ['microsoft', 'microsoft 365', 'office 365', 'm365', 
                             'o365', 'azure', 'teams']
        
        # Google keywords
        google_keywords = ['google', 'google workspace', 'gmail', 'g suite', 
                          'gsuite', 'workspace']
        
        has_setup_intent = any(keyword in message_lower for keyword in setup_keywords)
        
        if has_setup_intent:
            if any(keyword in message_lower for keyword in microsoft_keywords):
                return 'microsoft'
            elif any(keyword in message_lower for keyword in google_keywords):
                return 'google'
            else:
                return 'setup'  # General setup
        
        return None
    
    def process_message(self, message: Message) -> Message:
        """Process user message and help with setup"""
        
        # Extract text from content dict
        if isinstance(message.content, dict):
            user_message_text = message.content.get('text', str(message.content))
            user_id = message.content.get('user_id', message.sender_id)
        else:
            user_message_text = str(message.content)
            user_id = message.sender_id
        
        user_message = user_message_text.lower()
        
        # Check if user is in an active setup session
        if user_id in self.setup_sessions:
            return self._handle_setup_step(user_message_text, user_id)
        
        # Check for status/help commands FIRST (before setup intent)
        if any(word in user_message for word in ['status', 'configured', 'check', 'list']):
            return self._check_status()
        
        if any(word in user_message for word in ['help', 'guide', 'how to', 'instructions']):
            return self._show_help()
        
        # Check for setup intent
        setup_type = self.detect_setup_intent(user_message)
        
        if setup_type:
            return self._start_setup(setup_type, user_id)
        
        # Default help message
        return self._show_help()
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method - Setup agent makes configuration decisions"""
        return {
            "decision": "handle_setup",
            "action": "process_configuration",
            "context": context
        }
    
    def _start_setup(self, setup_type: str, user_id: str) -> Message:
        """Start a new setup session"""
        
        if setup_type == 'microsoft':
            # Initialize Microsoft OAuth setup
            self.setup_sessions[user_id] = {
                'type': 'microsoft',
                'step': 'client_id',
                'data': {}
            }
            
            response = """
🔧 **Microsoft 365 OAuth Setup**

Great! I'll guide you through setting up Microsoft 365 OAuth credentials.

**What you'll need:**
1. Azure Client ID
2. Azure Client Secret
3. Azure Tenant ID

**How to get these credentials:**

📋 **Step 1: Go to Azure Portal**
• Visit: https://portal.azure.com
• Sign in with your admin account

📋 **Step 2: Navigate to App Registrations**
• Search for "App registrations" in the top search bar
• Click on "App registrations"

📋 **Step 3: Create or Select an App**
• Click "+ New registration" (or select existing app)
• Name it something like "Pramiti AI Integration"
• Supported account types: "Single tenant" or "Multitenant"
• Click "Register"

📋 **Step 4: Copy Client ID & Tenant ID**
• You'll see "Application (client) ID" - this is your **Client ID**
• You'll see "Directory (tenant) ID" - this is your **Tenant ID**
• Copy both of these

📋 **Step 5: Create Client Secret**
• Go to "Certificates & secrets" in the left menu
• Click "+ New client secret"
• Add a description and choose expiration
• Click "Add"
• **COPY THE SECRET VALUE NOW** (you can't see it again!)

📋 **Step 6: Configure API Permissions**
• Go to "API permissions" in the left menu
• Click "+ Add a permission" → "Microsoft Graph"
• Choose "Delegated permissions"
• Add these permissions:
  - User.Read
  - Mail.Read
  - Mail.ReadWrite
  - Mail.Send
  - Files.Read.All
  - Files.ReadWrite.All
  - Calendars.Read
  - Calendars.ReadWrite
  - OnlineMeetings.ReadWrite
• Click "Add permissions"
• Click "Grant admin consent" (requires admin)

📋 **Step 7: Configure Redirect URI**
• Go to "Authentication" in the left menu
• Click "+ Add a platform" → "Web"
• Add redirect URI: `http://localhost:8084/api/v1/oauth/callback/microsoft`
• Save

---

✅ **Ready? Let's start!**

Please provide your **Azure Client ID** (Application ID):
            """.strip()
            
        elif setup_type == 'google':
            # Initialize Google OAuth setup
            self.setup_sessions[user_id] = {
                'type': 'google',
                'step': 'client_id',
                'data': {}
            }
            
            response = """
🔧 **Google Workspace OAuth Setup**

Great! I'll guide you through setting up Google Workspace OAuth credentials.

**What you'll need:**
1. Google Client ID
2. Google Client Secret

**How to get these credentials:**

📋 **Step 1: Go to Google Cloud Console**
• Visit: https://console.cloud.google.com
• Sign in with your admin account

📋 **Step 2: Create a Project**
• Click on project dropdown at the top
• Click "New Project"
• Name it "Pramiti AI" or similar
• Click "Create"

📋 **Step 3: Enable Required APIs**
• Go to "APIs & Services" → "Library"
• Search and enable these APIs:
  - Gmail API
  - Google Drive API
  - Google Calendar API
  - Google People API

📋 **Step 4: Configure OAuth Consent Screen**
• Go to "APIs & Services" → "OAuth consent screen"
• Choose "External" (unless you have Workspace)
• Fill in:
  - App name: "Pramiti AI"
  - User support email: your email
  - Developer contact: your email
• Add scopes:
  - .../auth/gmail.readonly
  - .../auth/gmail.send
  - .../auth/drive.readonly
  - .../auth/drive.file
  - .../auth/calendar
  - .../auth/userinfo.email
  - .../auth/userinfo.profile
• Save

📋 **Step 5: Create OAuth Credentials**
• Go to "APIs & Services" → "Credentials"
• Click "+ Create Credentials" → "OAuth 2.0 Client ID"
• Application type: "Web application"
• Name: "Pramiti AI Web Client"
• Authorized redirect URIs:
  - `http://localhost:8084/api/v1/oauth/callback/google`
• Click "Create"

📋 **Step 6: Copy Credentials**
• You'll see your **Client ID** (ends with .apps.googleusercontent.com)
• You'll see your **Client Secret**
• Copy both of these

---

✅ **Ready? Let's start!**

Please provide your **Google Client ID**:
            """.strip()
            
        else:
            # General setup - ask which provider
            response = """
🔧 **OAuth Setup Assistant**

I can help you configure OAuth credentials for your organization.

**Which service would you like to set up?**

1️⃣ **Microsoft 365** (Outlook, OneDrive, Teams)
   - Type: "setup microsoft" or "microsoft oauth"

2️⃣ **Google Workspace** (Gmail, Drive, Calendar)
   - Type: "setup google" or "google oauth"

3️⃣ **Both**
   - Type: "setup both"

Or type **"help"** for more information about OAuth setup.
            """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response},
            sender_id=self.agent_id,
            metadata={'action': 'start_setup', 'setup_type': setup_type}
        )
    
    def _handle_setup_step(self, user_input: str, user_id: str) -> Message:
        """Handle each step of the setup process"""
        
        session = self.setup_sessions[user_id]
        setup_type = session['type']
        current_step = session['step']
        
        # Allow user to cancel
        if user_input.lower() in ['cancel', 'stop', 'quit', 'exit']:
            del self.setup_sessions[user_id]
            return Message(
                message_type=MessageType.RESPONSE,
                content={"text": "❌ Setup cancelled. Type 'setup' to start again."},
                sender_id=self.agent_id
            )
        
        if setup_type == 'microsoft':
            return self._handle_microsoft_step(user_input, user_id, current_step, session)
        elif setup_type == 'google':
            return self._handle_google_step(user_input, user_id, current_step, session)
    
    def _handle_microsoft_step(self, user_input: str, user_id: str, 
                               current_step: str, session: Dict) -> Message:
        """Handle Microsoft OAuth setup steps"""
        
        if current_step == 'client_id':
            # Validate Client ID format (GUID)
            client_id = user_input.strip()
            if self._validate_guid(client_id):
                session['data']['client_id'] = client_id
                session['step'] = 'client_secret'
                
                response = f"""
✅ **Client ID saved:** `{client_id[:10]}...{client_id[-10:]}`

Next, please provide your **Azure Client Secret**:
(This is the secret value you copied when creating the client secret)
                """.strip()
            else:
                response = """
❌ **Invalid Client ID format**

The Client ID should be a GUID (32 hexadecimal characters with hyphens).
Example: `12345678-1234-1234-1234-123456789abc`

Please provide your **Azure Client ID** again:
                """.strip()
        
        elif current_step == 'client_secret':
            # Save client secret (any non-empty string)
            client_secret = user_input.strip()
            if len(client_secret) > 10:
                session['data']['client_secret'] = client_secret
                session['step'] = 'tenant_id'
                
                response = f"""
✅ **Client Secret saved:** `{client_secret[:5]}...{client_secret[-5:]}`

Finally, please provide your **Azure Tenant ID** (Directory ID):
(This is also a GUID from your Azure app registration)
                """.strip()
            else:
                response = """
❌ **Client Secret seems too short**

Please provide your **Azure Client Secret** again:
                """.strip()
        
        elif current_step == 'tenant_id':
            # Validate Tenant ID format (GUID)
            tenant_id = user_input.strip()
            if self._validate_guid(tenant_id) or tenant_id.lower() == 'common':
                session['data']['tenant_id'] = tenant_id
                
                # Save configuration
                saved = self._save_microsoft_config(
                    user_id,
                    session['data']['client_id'],
                    session['data']['client_secret'],
                    tenant_id
                )
                
                # Clear session
                del self.setup_sessions[user_id]
                
                if saved:
                    response = f"""
✅ **Microsoft 365 OAuth Setup Complete!**

**Configuration Summary:**
• Client ID: `{session['data']['client_id'][:10]}...`
• Tenant ID: `{tenant_id[:10]}...` if len(tenant_id) > 10 else tenant_id
• Client Secret: `***configured***`

**What's Next:**

1️⃣ **Test the Connection**
   Type: "connect my outlook" in the chat to test

2️⃣ **Configuration Saved**
   Your credentials are saved in: `config/oauth/microsoft_{user_id}.json`

3️⃣ **Redirect URI Reminder**
   Make sure you've added this to Azure:
   `http://localhost:8084/api/v1/oauth/callback/microsoft`

🎉 **You're all set!** Users can now authenticate with Microsoft 365.

Need to setup Google Workspace too? Type: "setup google"
                    """.strip()
                else:
                    response = """
❌ **Failed to save configuration**

Please check file permissions and try again.
Type "setup microsoft" to restart.
                    """.strip()
            else:
                response = """
❌ **Invalid Tenant ID format**

The Tenant ID should be a GUID or "common" for multi-tenant apps.
Example: `12345678-1234-1234-1234-123456789abc`

Please provide your **Azure Tenant ID** again:
                """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response},
            sender_id=self.agent_id
        )
    
    def _handle_google_step(self, user_input: str, user_id: str, 
                           current_step: str, session: Dict) -> Message:
        """Handle Google OAuth setup steps"""
        
        if current_step == 'client_id':
            # Validate Google Client ID format
            client_id = user_input.strip()
            if '.apps.googleusercontent.com' in client_id:
                session['data']['client_id'] = client_id
                session['step'] = 'client_secret'
                
                response = f"""
✅ **Client ID saved:** `{client_id[:20]}...`

Next, please provide your **Google Client Secret**:
                """.strip()
            else:
                response = """
❌ **Invalid Google Client ID format**

The Client ID should end with `.apps.googleusercontent.com`
Example: `123456789-abc.apps.googleusercontent.com`

Please provide your **Google Client ID** again:
                """.strip()
        
        elif current_step == 'client_secret':
            # Save client secret
            client_secret = user_input.strip()
            if len(client_secret) > 10:
                session['data']['client_secret'] = client_secret
                
                # Save configuration
                saved = self._save_google_config(
                    user_id,
                    session['data']['client_id'],
                    client_secret
                )
                
                # Clear session
                del self.setup_sessions[user_id]
                
                if saved:
                    response = f"""
✅ **Google Workspace OAuth Setup Complete!**

**Configuration Summary:**
• Client ID: `{session['data']['client_id'][:30]}...`
• Client Secret: `***configured***`

**What's Next:**

1️⃣ **Test the Connection**
   Type: "connect my gmail" in the chat to test

2️⃣ **Configuration Saved**
   Your credentials are saved in: `config/oauth/google_{user_id}.json`

3️⃣ **Redirect URI Reminder**
   Make sure you've added this to Google Cloud Console:
   `http://localhost:8084/api/v1/oauth/callback/google`

🎉 **You're all set!** Users can now authenticate with Google Workspace.

Need to setup Microsoft 365 too? Type: "setup microsoft"
                    """.strip()
                else:
                    response = """
❌ **Failed to save configuration**

Please check file permissions and try again.
Type "setup google" to restart.
                    """.strip()
            else:
                response = """
❌ **Client Secret seems too short**

Please provide your **Google Client Secret** again:
                """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response},
            sender_id=self.agent_id
        )
    
    def _validate_guid(self, value: str) -> bool:
        """Validate GUID format"""
        guid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(guid_pattern, value.lower()))
    
    def _save_microsoft_config(self, org_id: str, client_id: str, 
                               client_secret: str, tenant_id: str) -> bool:
        """Save Microsoft OAuth configuration"""
        try:
            config = {
                'provider': 'microsoft',
                'client_id': client_id,
                'client_secret': client_secret,
                'tenant_id': tenant_id,
                'redirect_uri': 'http://localhost:8084/api/v1/oauth/callback/microsoft'
            }
            
            config_file = os.path.join(self.config_dir, f'microsoft_{org_id}.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Also update .env if org_id is 'default' or main instance
            if org_id in ['default', 'main', 'admin']:
                self._update_env_file('MICROSOFT', client_id, client_secret, tenant_id)
            
            return True
        except Exception as e:
            print(f"Error saving Microsoft config: {e}")
            return False
    
    def _save_google_config(self, org_id: str, client_id: str, client_secret: str) -> bool:
        """Save Google OAuth configuration"""
        try:
            config = {
                'provider': 'google',
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': 'http://localhost:8084/api/v1/oauth/callback/google'
            }
            
            config_file = os.path.join(self.config_dir, f'google_{org_id}.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Also update .env if org_id is 'default' or main instance
            if org_id in ['default', 'main', 'admin']:
                self._update_env_file('GOOGLE', client_id, client_secret)
            
            return True
        except Exception as e:
            print(f"Error saving Google config: {e}")
            return False
    
    def _update_env_file(self, provider: str, client_id: str, 
                        client_secret: str, tenant_id: str = None):
        """Update .env file with OAuth credentials"""
        try:
            env_file = '.env'
            
            # Read existing .env
            env_lines = []
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add credentials
            updated = {
                f'{provider}_CLIENT_ID': False,
                f'{provider}_CLIENT_SECRET': False,
            }
            if tenant_id:
                updated[f'{provider}_TENANT_ID'] = False
            
            for i, line in enumerate(env_lines):
                for key in updated.keys():
                    if line.startswith(f'{key}='):
                        if key.endswith('CLIENT_ID'):
                            env_lines[i] = f'{key}={client_id}\n'
                        elif key.endswith('CLIENT_SECRET'):
                            env_lines[i] = f'{key}={client_secret}\n'
                        elif key.endswith('TENANT_ID'):
                            env_lines[i] = f'{key}={tenant_id}\n'
                        updated[key] = True
            
            # Add missing credentials
            for key, exists in updated.items():
                if not exists:
                    if key.endswith('CLIENT_ID'):
                        env_lines.append(f'\n# {provider} OAuth Credentials\n')
                        env_lines.append(f'{key}={client_id}\n')
                    elif key.endswith('CLIENT_SECRET'):
                        env_lines.append(f'{key}={client_secret}\n')
                    elif key.endswith('TENANT_ID'):
                        env_lines.append(f'{key}={tenant_id}\n')
            
            # Write back
            with open(env_file, 'w') as f:
                f.writelines(env_lines)
            
            print(f"✅ Updated {env_file} with {provider} credentials")
            
        except Exception as e:
            print(f"Error updating .env file: {e}")
    
    def _check_status(self) -> Message:
        """Check configured OAuth providers"""
        
        configured = []
        
        # Check Microsoft
        ms_configs = [f for f in os.listdir(self.config_dir) if f.startswith('microsoft_')]
        if ms_configs or os.getenv('MICROSOFT_CLIENT_ID'):
            configured.append("✅ Microsoft 365")
        else:
            configured.append("❌ Microsoft 365 (not configured)")
        
        # Check Google
        g_configs = [f for f in os.listdir(self.config_dir) if f.startswith('google_')]
        if g_configs or os.getenv('GOOGLE_CLIENT_ID'):
            configured.append("✅ Google Workspace")
        else:
            configured.append("❌ Google Workspace (not configured)")
        
        response = f"""
📊 **OAuth Configuration Status**

{chr(10).join(configured)}

**Configured Organizations:** {len(ms_configs) + len(g_configs)}

To setup a new provider, type:
• "setup microsoft" for Microsoft 365
• "setup google" for Google Workspace
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response},
            sender_id=self.agent_id
        )
    
    def _show_help(self) -> Message:
        """Show help message"""
        
        response = """
🔧 **Setup Assistant - Help**

I help IT administrators configure OAuth credentials for their organization.

**Available Commands:**

📋 **Setup OAuth Providers**
• `setup microsoft` - Configure Microsoft 365 OAuth
• `setup google` - Configure Google Workspace OAuth
• `setup both` - Configure both providers

📊 **Check Status**
• `status` - View configured providers
• `check config` - List all configurations

❓ **Get Help**
• `help` - Show this message
• `guide` - Detailed setup instructions

🚫 **Cancel Setup**
• `cancel` - Cancel current setup session

---

**Why OAuth?**
OAuth 2.0 is the industry-standard protocol for secure authentication. 
It allows users to grant your application access to their data without 
sharing their passwords.

**Multi-Organization Support:**
This system supports multiple organizations. Each organization can have 
its own OAuth credentials, allowing you to serve multiple clients securely.

Ready to get started? Type: `setup microsoft` or `setup google`
        """.strip()
        
        return Message(
            message_type=MessageType.RESPONSE,
            content={"text": response},
            sender_id=self.agent_id
        )


# Create global instance
setup_assistant = SetupAssistantAgent()
