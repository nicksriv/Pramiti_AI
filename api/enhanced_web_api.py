from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import uvicorn
from pathlib import Path
from pydantic import BaseModel
import uuid

# Import our agent system
from core.communication_orchestrator import CommunicationOrchestrator
from agents.management_agents import CEOAgent, SeniorManager
from agents.itsm_agents import IncidentManagementAgent, ProblemManagementAgent, ChangeManagementAgent
from core.blockchain_logger import CommunicationLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class AgentCreate(BaseModel):
    name: str
    type: str  # executive, manager, specialist
    role: str
    specialization: str
    responsibilities: List[str]
    capabilities: str
    reportsTo: Optional[str] = None
    icon: str

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None
    specialization: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    capabilities: Optional[str] = None
    reportsTo: Optional[str] = None
    icon: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    saveToBlockchain: Optional[bool] = True
    timestamp: Optional[str] = None

class UserBotMessage(BaseModel):
    message: str
    timestamp: Optional[str] = None
    sessionId: Optional[str] = None

class HierarchyData(BaseModel):
    structure: Dict[str, Any]
    agents: Dict[str, Any]

class EnhancedWebDashboardAPI:
    """Enhanced FastAPI application for the Agentic AI Organization with chat and agent management"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Agentic AI Organization - Enhanced Dashboard",
            description="Complete web interface for managing AI agents with chat functionality",
            version="2.0.0"
        )
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        self.chat_connections: Dict[str, WebSocket] = {}
        
        # Initialize agent system
        self.orchestrator = None
        self.blockchain_logger = None
        self.agents = {}
        self.agent_configurations = {}
        self.chat_sessions = {}
        self.conversation_history = {}
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_static_files()
        
    def setup_middleware(self):
        """Configure CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_static_files(self):
        """Mount static file directories"""
        web_dir = Path(__file__).parent / "web"
        
        # Serve static files (CSS, JS, images)
        self.app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
        
    def setup_routes(self):
        """Configure API routes and endpoints"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def serve_enhanced_dashboard():
            """Serve the enhanced dashboard HTML"""
            web_dir = Path(__file__).parent / "web"
            html_file = web_dir / "enhanced-dashboard.html"
            
            if html_file.exists():
                return FileResponse(str(html_file))
            else:
                return HTMLResponse("Enhanced Dashboard not found", status_code=404)
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.connect_websocket(websocket)
        
        @self.app.websocket("/ws/chat")
        async def chat_websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for chat functionality"""
            await self.connect_chat_websocket(websocket)
        
        # System Health and Status
        @self.app.get("/api/v1/system/health")
        async def get_system_health():
            """Get system health status"""
            return {
                "status": "healthy" if self.orchestrator else "initializing",
                "timestamp": datetime.now().isoformat(),
                "agents_active": len(self.agents),
                "uptime": self.get_uptime(),
                "connections": len(self.active_connections),
                "chat_connections": len(self.chat_connections)
            }
        
        # Dashboard KPIs
        @self.app.get("/api/v1/dashboard/kpis")
        async def get_dashboard_kpis():
            """Get KPI data for dashboard"""
            return await self.calculate_kpis()
        
        # Agent Management Endpoints
        @self.app.get("/api/v1/agents")
        async def list_agents():
            """List all agents with their configurations"""
            agents_list = []
            for agent_id, config in self.agent_configurations.items():
                agent_data = {
                    "id": agent_id,
                    "name": config["name"],
                    "type": config["type"],
                    "role": config["role"],
                    "specialization": config["specialization"],
                    "responsibilities": config["responsibilities"],
                    "capabilities": config["capabilities"],
                    "reportsTo": config.get("reportsTo"),
                    "icon": config["icon"],
                    "status": "online" if agent_id in self.agents else "offline",
                    "last_activity": datetime.now().isoformat(),
                    "message_queue_size": self.orchestrator.get_queue_size(agent_id) if self.orchestrator and agent_id in self.agents else 0
                }
                agents_list.append(agent_data)
            
            return {"agents": agents_list}
        
        @self.app.get("/api/v1/agents/{agent_id}")
        async def get_agent_details(agent_id: str):
            """Get detailed information about a specific agent"""
            if agent_id not in self.agent_configurations:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            config = self.agent_configurations[agent_id]
            agent = self.agents.get(agent_id)
            
            return {
                "id": agent_id,
                "name": config["name"],
                "type": config["type"],
                "role": config["role"],
                "specialization": config["specialization"],
                "responsibilities": config["responsibilities"],
                "capabilities": config["capabilities"],
                "reportsTo": config.get("reportsTo"),
                "icon": config["icon"],
                "status": "online" if agent else "offline",
                "message_queue_size": self.orchestrator.get_queue_size(agent_id) if self.orchestrator and agent else 0,
                "total_messages_processed": config.get("total_messages", 0),
                "last_activity": config.get("last_activity", datetime.now().isoformat()),
                "conversation_count": len(self.conversation_history.get(agent_id, [])),
                "created_at": config.get("created_at", datetime.now().isoformat())
            }
        
        @self.app.post("/api/v1/agents")
        async def create_agent(agent_data: AgentCreate):
            """Create a new agent"""
            agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            
            # Store agent configuration
            config = {
                "id": agent_id,
                "name": agent_data.name,
                "type": agent_data.type,
                "role": agent_data.role,
                "specialization": agent_data.specialization,
                "responsibilities": agent_data.responsibilities,
                "capabilities": agent_data.capabilities,
                "reportsTo": agent_data.reportsTo,
                "icon": agent_data.icon,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "total_messages": 0
            }
            
            self.agent_configurations[agent_id] = config
            
            # Create and register agent instance
            await self.create_agent_instance(agent_id, config)
            
            # Broadcast update
            await self.broadcast_to_websockets({
                "type": "agent_created",
                "payload": {
                    "agent_id": agent_id,
                    "agent": config
                }
            })
            
            return {"status": "created", "agent_id": agent_id, "agent": config}
        
        @self.app.put("/api/v1/agents/{agent_id}")
        async def update_agent(agent_id: str, agent_data: AgentUpdate):
            """Update an existing agent"""
            if agent_id not in self.agent_configurations:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            config = self.agent_configurations[agent_id]
            
            # Update configuration
            for field, value in agent_data.dict(exclude_unset=True).items():
                if value is not None:
                    config[field] = value
            
            config["last_activity"] = datetime.now().isoformat()
            
            # Update agent instance if it exists
            if agent_id in self.agents:
                await self.update_agent_instance(agent_id, config)
            
            # Broadcast update
            await self.broadcast_to_websockets({
                "type": "agent_updated",
                "payload": {
                    "agent_id": agent_id,
                    "agent": config
                }
            })
            
            return {"status": "updated", "agent": config}
        
        @self.app.delete("/api/v1/agents/{agent_id}")
        async def delete_agent(agent_id: str):
            """Delete an agent"""
            if agent_id not in self.agent_configurations:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            # Remove from orchestrator
            if self.orchestrator and agent_id in self.agents:
                await self.orchestrator.unregister_agent(agent_id)
            
            # Remove from collections
            self.agents.pop(agent_id, None)
            config = self.agent_configurations.pop(agent_id, None)
            self.conversation_history.pop(agent_id, None)
            
            # Broadcast update
            await self.broadcast_to_websockets({
                "type": "agent_deleted",
                "payload": {
                    "agent_id": agent_id
                }
            })
            
            return {"status": "deleted", "agent_id": agent_id}
        
        # Chat Endpoints
        @self.app.post("/api/v1/agents/{agent_id}/chat")
        async def send_message_to_agent(agent_id: str, message: ChatMessage):
            """Send a message to a specific agent"""
            if agent_id not in self.agent_configurations:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            if not self.orchestrator or agent_id not in self.agents:
                raise HTTPException(status_code=503, detail="Agent not available")
            
            try:
                # Store message in conversation history
                conversation_id = f"user_to_{agent_id}"
                if conversation_id not in self.conversation_history:
                    self.conversation_history[conversation_id] = []
                
                user_message = {
                    "id": str(uuid.uuid4()),
                    "type": "user",
                    "content": message.message,
                    "timestamp": message.timestamp or datetime.now().isoformat(),
                    "agent_id": agent_id
                }
                
                self.conversation_history[conversation_id].append(user_message)
                
                # Route message through orchestrator
                await self.orchestrator.route_message(
                    sender_id="dashboard_user",
                    recipient_id=agent_id,
                    message_type="chat",
                    content=message.message,
                    priority="normal"
                )
                
                # Generate agent response (simulate intelligent response)
                agent_response = await self.generate_agent_response(agent_id, message.message)
                
                # Store agent response
                agent_message = {
                    "id": str(uuid.uuid4()),
                    "type": "agent",
                    "content": agent_response,
                    "timestamp": datetime.now().isoformat(),
                    "agent_id": agent_id
                }
                
                self.conversation_history[conversation_id].append(agent_message)
                
                # Update agent activity
                if agent_id in self.agent_configurations:
                    self.agent_configurations[agent_id]["last_activity"] = datetime.now().isoformat()
                    self.agent_configurations[agent_id]["total_messages"] = \
                        self.agent_configurations[agent_id].get("total_messages", 0) + 1
                
                # Log to blockchain if requested
                if message.saveToBlockchain and self.blockchain_logger:
                    await self.blockchain_logger.log_communication(
                        sender_id="dashboard_user",
                        recipient_id=agent_id,
                        message_type="chat",
                        content=message.message
                    )
                
                # Broadcast to WebSocket clients
                await self.broadcast_chat_message(agent_id, "agent_response", agent_response)
                
                return {
                    "status": "sent",
                    "message_id": user_message["id"],
                    "response": agent_response,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in agent chat: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/agents/{agent_id}/conversation")
        async def get_agent_conversation(agent_id: str, limit: int = 50):
            """Get conversation history with an agent"""
            conversation_id = f"user_to_{agent_id}"
            conversation = self.conversation_history.get(conversation_id, [])
            
            # Return latest messages
            return {
                "agent_id": agent_id,
                "conversation": conversation[-limit:],
                "total_messages": len(conversation)
            }
        
        @self.app.delete("/api/v1/agents/{agent_id}/conversation")
        async def clear_agent_conversation(agent_id: str):
            """Clear conversation history with an agent"""
            conversation_id = f"user_to_{agent_id}"
            if conversation_id in self.conversation_history:
                del self.conversation_history[conversation_id]
            
            return {"status": "cleared", "agent_id": agent_id}
        
        # User Chatbot Endpoints
        @self.app.post("/api/v1/userbot/chat")
        async def userbot_chat(message: UserBotMessage):
            """Chat with the user-facing organization bot"""
            try:
                # Generate session ID if not provided
                session_id = message.sessionId or str(uuid.uuid4())
                
                # Store user message
                if session_id not in self.conversation_history:
                    self.conversation_history[session_id] = []
                
                user_msg = {
                    "id": str(uuid.uuid4()),
                    "type": "user",
                    "content": message.message,
                    "timestamp": message.timestamp or datetime.now().isoformat()
                }
                
                self.conversation_history[session_id].append(user_msg)
                
                # Generate intelligent response
                bot_response = await self.generate_userbot_response(message.message, session_id)
                
                # Store bot response
                bot_msg = {
                    "id": str(uuid.uuid4()),
                    "type": "bot",
                    "content": bot_response,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.conversation_history[session_id].append(bot_msg)
                
                return {
                    "session_id": session_id,
                    "message": bot_response,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in userbot chat: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/userbot/conversation/{session_id}")
        async def get_userbot_conversation(session_id: str):
            """Get userbot conversation history"""
            conversation = self.conversation_history.get(session_id, [])
            return {
                "session_id": session_id,
                "conversation": conversation,
                "total_messages": len(conversation)
            }
        
        # Hierarchy Management
        @self.app.get("/api/v1/hierarchy")
        async def get_hierarchy():
            """Get current organization hierarchy"""
            hierarchy = {
                "levels": ["executive", "manager", "specialist"],
                "structure": {},
                "agents": {}
            }
            
            # Group agents by type
            for agent_id, config in self.agent_configurations.items():
                agent_type = config["type"]
                if agent_type not in hierarchy["structure"]:
                    hierarchy["structure"][agent_type] = []
                
                hierarchy["structure"][agent_type].append(config)
                hierarchy["agents"][agent_id] = config
            
            return hierarchy
        
        @self.app.post("/api/v1/hierarchy")
        async def save_hierarchy(hierarchy_data: HierarchyData):
            """Save organization hierarchy"""
            try:
                # Update agent configurations based on hierarchy
                for agent_id, agent_config in hierarchy_data.agents.items():
                    if agent_id in self.agent_configurations:
                        self.agent_configurations[agent_id].update(agent_config)
                
                # Broadcast hierarchy update
                await self.broadcast_to_websockets({
                    "type": "hierarchy_updated",
                    "payload": hierarchy_data.dict()
                })
                
                return {"status": "saved", "timestamp": datetime.now().isoformat()}
                
            except Exception as e:
                logger.error(f"Error saving hierarchy: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Communication and Blockchain Logs
        @self.app.get("/api/v1/communications/recent")
        async def get_recent_communications():
            """Get recent communication logs"""
            communications = []
            
            # Get recent conversations from all agents
            for conversation_id, messages in list(self.conversation_history.items())[-10:]:
                for message in messages[-5:]:  # Last 5 messages per conversation
                    communications.append({
                        "id": message["id"],
                        "type": "communication",
                        "title": f"Message from {message['type']}",
                        "description": message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"],
                        "timestamp": message["timestamp"],
                        "icon": "fas fa-comment"
                    })
            
            # Sort by timestamp
            communications.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {"communications": communications[:20]}
        
        # Additional utility endpoints...
        @self.app.post("/api/v1/system/emergency-stop")
        async def emergency_stop():
            """Emergency stop all agents"""
            try:
                if self.orchestrator:
                    await self.orchestrator.emergency_stop()
                
                await self.broadcast_to_websockets({
                    "type": "system_alert",
                    "payload": {
                        "message": "Emergency stop activated",
                        "level": "error"
                    }
                })
                
                return {"status": "stopped", "timestamp": datetime.now().isoformat()}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    # Helper methods for agent management
    async def create_agent_instance(self, agent_id: str, config: Dict[str, Any]):
        """Create and register an agent instance based on configuration"""
        try:
            # Create agent based on type and specialization
            if config["type"] == "executive":
                agent = CEOAgent(agent_id, config["name"])
            elif config["type"] == "manager":
                agent = SeniorManager(agent_id, config["name"])
            else:  # specialist
                if "incident" in config["specialization"].lower():
                    agent = IncidentManagementAgent(agent_id, config["name"])
                elif "problem" in config["specialization"].lower():
                    agent = ProblemManagementAgent(agent_id, config["name"])
                elif "change" in config["specialization"].lower():
                    agent = ChangeManagementAgent(agent_id, config["name"])
                else:
                    # Create a generic specialist agent
                    agent = IncidentManagementAgent(agent_id, config["name"])  # Default to incident
            
            # Store agent
            self.agents[agent_id] = agent
            
            # Register with orchestrator
            if self.orchestrator:
                await self.orchestrator.register_agent(agent_id, agent)
            
            logger.info(f"Created agent: {agent_id} ({config['name']})")
            
        except Exception as e:
            logger.error(f"Error creating agent {agent_id}: {e}")
            raise
    
    async def update_agent_instance(self, agent_id: str, config: Dict[str, Any]):
        """Update an existing agent instance"""
        try:
            agent = self.agents.get(agent_id)
            if agent:
                # Update agent properties
                agent.name = config["name"]
                agent.role = config["role"]
                # Update other properties as needed
                
            logger.info(f"Updated agent: {agent_id} ({config['name']})")
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
    
    async def generate_agent_response(self, agent_id: str, user_message: str) -> str:
        """Generate intelligent response based on agent type and message"""
        config = self.agent_configurations.get(agent_id, {})
        agent_type = config.get("type", "specialist")
        specialization = config.get("specialization", "").lower()
        
        # Simple response generation based on agent type and message content
        message_lower = user_message.lower()
        
        if agent_type == "executive":
            if "strategic" in message_lower or "decision" in message_lower:
                return f"As the CEO, I'll need to consider the strategic implications of this. Let me analyze the organizational impact and coordinate with the leadership team."
            elif "budget" in message_lower or "resource" in message_lower:
                return f"Resource allocation requires careful consideration. I'll review this with our financial planning and ensure it aligns with our strategic objectives."
            else:
                return f"Thank you for bringing this to my attention. I'll ensure the appropriate teams are informed and will provide executive guidance on the next steps."
        
        elif agent_type == "manager":
            if "priority" in message_lower or "urgent" in message_lower:
                return f"I understand this is a priority. I'll coordinate with my team to ensure immediate attention and proper resource allocation."
            elif "team" in message_lower or "assign" in message_lower:
                return f"I'll handle the team coordination for this. Let me assign the right specialists and monitor progress."
            else:
                return f"I'll manage this through our standard operational procedures and ensure proper follow-through with the specialist teams."
        
        else:  # specialist
            if "incident" in specialization:
                if "urgent" in message_lower or "down" in message_lower:
                    return f"I'm treating this as a high-priority incident. Initiating immediate response procedures and will coordinate with relevant teams for rapid resolution."
                else:
                    return f"I've logged this incident and will begin investigation. I'll provide regular updates as we work toward resolution."
            
            elif "problem" in specialization:
                if "root cause" in message_lower or "analysis" in message_lower:
                    return f"I'll conduct thorough root cause analysis using our problem management methodologies. This will help prevent future occurrences."
                else:
                    return f"Let me analyze this issue systematically to identify underlying causes and develop preventive measures."
            
            elif "change" in specialization:
                if "risk" in message_lower or "impact" in message_lower:
                    return f"I'll assess the risk and impact of this change through our standard evaluation process. We need to ensure minimal disruption."
                else:
                    return f"This change request will need proper assessment and approval. I'll coordinate the evaluation and implementation planning."
            
            else:
                return f"I'll handle this according to my specialized expertise in {specialization}. Let me process this request appropriately."
    
    async def generate_userbot_response(self, user_message: str, session_id: str) -> str:
        """Generate intelligent userbot response"""
        message_lower = user_message.lower()
        
        # Intent detection and routing
        if any(keyword in message_lower for keyword in ["incident", "problem", "issue", "down", "error", "broken"]):
            return self.handle_incident_request(user_message)
        elif any(keyword in message_lower for keyword in ["change", "modify", "update", "upgrade"]):
            return self.handle_change_request(user_message)
        elif any(keyword in message_lower for keyword in ["request", "need", "access", "permission"]):
            return self.handle_service_request(user_message)
        elif any(keyword in message_lower for keyword in ["status", "check", "update", "progress"]):
            return self.handle_status_inquiry(user_message)
        else:
            return self.handle_general_inquiry(user_message)
    
    def handle_incident_request(self, message: str) -> str:
        """Handle incident-related requests"""
        return f"I understand you're experiencing an issue. I'm routing this to our Incident Management team for immediate attention. Can you provide:\n\n1. What system/service is affected?\n2. When did this start?\n3. How many users are impacted?\n4. Error messages (if any)\n\nIncident ticket INC-{datetime.now().strftime('%Y%m%d')}-001 has been created."
    
    def handle_change_request(self, message: str) -> str:
        """Handle change-related requests"""
        return f"I've received your change request. Our Change Management team will review this for impact and risk assessment. Please provide:\n\n1. Description of the change\n2. Business justification\n3. Preferred implementation timeframe\n4. Potential impact on users\n\nChange request CHG-{datetime.now().strftime('%Y%m%d')}-001 has been created."
    
    def handle_service_request(self, message: str) -> str:
        """Handle service requests"""
        return f"I can help you with your service request. Based on your message, I'm creating a service ticket. Please specify:\n\n1. What service/access do you need?\n2. Business justification\n3. Urgency level\n4. Manager approval (if required)\n\nService request REQ-{datetime.now().strftime('%Y%m%d')}-001 has been created."
    
    def handle_status_inquiry(self, message: str) -> str:
        """Handle status checks"""
        return f"I can check the status of your tickets. Here's what I found:\n\n• INC-20241109-001: In Progress (assigned to technical team)\n• REQ-20241108-003: Approved (pending implementation)\n• CHG-20241107-002: Under Review (scheduled for next maintenance window)\n\nWould you like details on any specific ticket?"
    
    def handle_general_inquiry(self, message: str) -> str:
        """Handle general questions"""
        return f"I'm here to help with your IT service needs. I can assist with:\n\n• 🚨 Incident reporting and tracking\n• 🎫 Service requests (access, hardware, software)\n• 📋 Change requests and approvals\n• 📊 Status updates and ticket information\n• ❓ General IT policy questions\n\nWhat would you like help with today?"
    
    # WebSocket management methods
    async def connect_websocket(self, websocket: WebSocket):
        """Handle general WebSocket connections"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            await websocket.send_text(json.dumps({
                "type": "system_status",
                "payload": {
                    "status": "connected",
                    "agents_count": len(self.agents),
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def connect_chat_websocket(self, websocket: WebSocket):
        """Handle chat-specific WebSocket connections"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.chat_connections[connection_id] = websocket
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle chat-specific WebSocket messages
                message = json.loads(data)
                await self.handle_chat_websocket_message(connection_id, message)
        except WebSocketDisconnect:
            self.chat_connections.pop(connection_id, None)
        except Exception as e:
            logger.error(f"Chat WebSocket error: {e}")
            self.chat_connections.pop(connection_id, None)
    
    async def handle_chat_websocket_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle messages received via chat WebSocket"""
        message_type = message.get("type")
        
        if message_type == "typing":
            # Broadcast typing indicator
            await self.broadcast_chat_message(
                message.get("agent_id"),
                "user_typing",
                None
            )
        elif message_type == "stop_typing":
            # Broadcast stop typing
            await self.broadcast_chat_message(
                message.get("agent_id"),
                "user_stopped_typing",
                None
            )
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all general WebSocket clients"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    async def broadcast_chat_message(self, agent_id: str, message_type: str, content: str):
        """Broadcast chat message to all chat WebSocket clients"""
        if not self.chat_connections:
            return
        
        message = {
            "type": message_type,
            "agent_id": agent_id,
            "message": content,
            "timestamp": datetime.now().isoformat()
        }
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection_id, connection in self.chat_connections.items():
            try:
                await connection.send_text(message_text)
            except:
                disconnected.append(connection_id)
        
        for connection_id in disconnected:
            self.chat_connections.pop(connection_id, None)
    
    # Existing methods from the previous implementation...
    async def initialize_agent_system(self):
        """Initialize the agent system"""
        try:
            logger.info("Initializing enhanced agent system...")
            
            # Initialize blockchain logger
            self.blockchain_logger = CommunicationLogger()
            
            # Initialize communication orchestrator
            self.orchestrator = CommunicationOrchestrator(self.blockchain_logger)
            
            # Load default agents
            await self.load_default_agents()
            
            # Start the orchestrator
            await self.orchestrator.start()
            
            logger.info(f"Enhanced agent system initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            raise
    
    async def load_default_agents(self):
        """Load default agent configurations and instances"""
        default_configs = [
            {
                "id": "ceo",
                "name": "CEO Agent",
                "type": "executive",
                "role": "Chief Executive Officer",
                "specialization": "Strategic Leadership",
                "responsibilities": ["Strategic Planning", "Decision Making", "Organizational Oversight"],
                "capabilities": "High-level strategic thinking, decision making, and organizational leadership",
                "reportsTo": None,
                "icon": "fas fa-crown"
            },
            {
                "id": "senior_manager",
                "name": "Senior Manager",
                "type": "manager",
                "role": "ITSM Senior Manager",
                "specialization": "IT Service Management",
                "responsibilities": ["Team Coordination", "Task Assignment", "Performance Monitoring"],
                "capabilities": "Team management, ITSM processes, and operational coordination",
                "reportsTo": "ceo",
                "icon": "fas fa-user-tie"
            },
            {
                "id": "incident_agent",
                "name": "Incident Management Agent",
                "type": "specialist",
                "role": "Incident Management Specialist",
                "specialization": "Incident Response & Resolution",
                "responsibilities": ["Incident Detection", "Response Coordination", "Resolution Tracking"],
                "capabilities": "Rapid incident response, troubleshooting, and escalation management",
                "reportsTo": "senior_manager",
                "icon": "fas fa-exclamation-triangle"
            },
            {
                "id": "problem_agent",
                "name": "Problem Management Agent",
                "type": "specialist",
                "role": "Problem Management Specialist",
                "specialization": "Root Cause Analysis",
                "responsibilities": ["Problem Investigation", "Root Cause Analysis", "Prevention Strategies"],
                "capabilities": "Deep analytical thinking, pattern recognition, and preventive solution design",
                "reportsTo": "senior_manager",
                "icon": "fas fa-search"
            },
            {
                "id": "change_agent",
                "name": "Change Management Agent",
                "type": "specialist",
                "role": "Change Management Specialist",
                "specialization": "Change Implementation",
                "responsibilities": ["Change Assessment", "Risk Evaluation", "Implementation Planning"],
                "capabilities": "Change impact analysis, risk assessment, and implementation coordination",
                "reportsTo": "senior_manager",
                "icon": "fas fa-cogs"
            }
        ]
        
        for config in default_configs:
            config["created_at"] = datetime.now().isoformat()
            config["last_activity"] = datetime.now().isoformat()
            config["total_messages"] = 0
            
            self.agent_configurations[config["id"]] = config
            await self.create_agent_instance(config["id"], config)
    
    async def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate KPI metrics"""
        active_agents = len([a for a in self.agents.values() if a])
        total_messages = sum(
            config.get("total_messages", 0) 
            for config in self.agent_configurations.values()
        )
        
        return {
            "activeAgents": active_agents,
            "totalMessages": total_messages,
            "avgResponseTime": 1.2,  # TODO: Calculate actual response time
            "systemUptime": 99.9,    # TODO: Calculate actual uptime
            "conversationsToday": len(self.conversation_history),
            "agentTypes": {
                "executive": len([c for c in self.agent_configurations.values() if c.get("type") == "executive"]),
                "manager": len([c for c in self.agent_configurations.values() if c.get("type") == "manager"]),
                "specialist": len([c for c in self.agent_configurations.values() if c.get("type") == "specialist"])
            }
        }
    
    def get_uptime(self) -> str:
        """Calculate system uptime"""
        return "99.9%"

def create_enhanced_app() -> FastAPI:
    """Factory function to create the enhanced FastAPI application"""
    dashboard = EnhancedWebDashboardAPI()
    return dashboard.app, dashboard

if __name__ == "__main__":
    app, dashboard = create_enhanced_app()
    
    @app.on_event("startup")
    async def startup():
        await dashboard.initialize_agent_system()
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")