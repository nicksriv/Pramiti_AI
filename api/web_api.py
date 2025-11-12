from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uvicorn
from pathlib import Path
import os

# Import our agent system
from core.communication_orchestrator import CommunicationOrchestrator
from agents.management_agents import CEOAgent, SeniorManager
from agents.itsm_agents import IncidentManagementAgent, ProblemManagementAgent, ChangeManagementAgent
from core.blockchain_logger import CommunicationLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebDashboardAPI:
    """FastAPI application for the Agentic AI Organization web dashboard"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Agentic AI Organization Dashboard",
            description="Web interface for managing and monitoring the AI agent organization",
            version="1.0.0"
        )
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Initialize agent system
        self.orchestrator = None
        self.blockchain_logger = None
        self.agents = {}
        
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
        async def serve_dashboard():
            """Serve the main dashboard HTML"""
            web_dir = Path(__file__).parent / "web"
            html_file = web_dir / "index.html"
            
            if html_file.exists():
                return FileResponse(str(html_file))
            else:
                return HTMLResponse("Dashboard not found", status_code=404)
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.connect_websocket(websocket)
            
        # API Routes
        @self.app.get("/api/v1/system/health")
        async def get_system_health():
            """Get system health status"""
            return {
                "status": "healthy" if self.orchestrator else "initializing",
                "timestamp": datetime.now().isoformat(),
                "agents_active": len(self.agents),
                "uptime": self.get_uptime()
            }
        
        @self.app.get("/api/v1/dashboard/kpis")
        async def get_dashboard_kpis():
            """Get KPI data for dashboard"""
            return await self.calculate_kpis()
        
        @self.app.get("/api/v1/agents/hierarchy")
        async def get_agent_hierarchy():
            """Get agent organizational hierarchy"""
            return self.get_agent_hierarchy_data()
        
        @self.app.get("/api/v1/agents")
        async def list_agents():
            """List all agents with their status"""
            return {
                "agents": [
                    {
                        "id": agent_id,
                        "name": agent.name,
                        "role": agent.role,
                        "status": "online",
                        "last_activity": datetime.now().isoformat()
                    }
                    for agent_id, agent in self.agents.items()
                ]
            }
        
        @self.app.get("/api/v1/agents/{agent_id}")
        async def get_agent_details(agent_id: str):
            """Get detailed information about a specific agent"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent = self.agents[agent_id]
            return {
                "id": agent_id,
                "name": agent.name,
                "role": agent.role,
                "specialization": getattr(agent, 'specialization', None),
                "status": "online",
                "message_queue_size": self.orchestrator.get_queue_size(agent_id) if self.orchestrator else 0,
                "total_messages_processed": 0,  # TODO: Track this
                "last_activity": datetime.now().isoformat()
            }
        
        @self.app.post("/api/v1/agents/{agent_id}/message")
        async def send_message_to_agent(agent_id: str, message: Dict[str, Any]):
            """Send a message to a specific agent"""
            if not self.orchestrator:
                raise HTTPException(status_code=503, detail="System not initialized")
            
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            try:
                await self.orchestrator.route_message(
                    sender_id="dashboard",
                    recipient_id=agent_id,
                    message_type=message.get("type", "task"),
                    content=message.get("content", ""),
                    priority=message.get("priority", "normal")
                )
                
                return {"status": "sent", "timestamp": datetime.now().isoformat()}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/communications/recent")
        async def get_recent_communications():
            """Get recent communication logs"""
            if not self.blockchain_logger:
                return {"communications": []}
            
            # TODO: Implement blockchain log retrieval
            return {
                "communications": [
                    {
                        "id": "1",
                        "type": "communication",
                        "title": "Agent communication logged",
                        "description": "Message routed from CEO to Senior Manager",
                        "timestamp": datetime.now().isoformat(),
                        "icon": "fas fa-exchange-alt"
                    }
                ]
            }
        
        @self.app.get("/api/v1/communications/queues")
        async def get_message_queues():
            """Get current message queue status"""
            if not self.orchestrator:
                return {"queues": []}
            
            queues = []
            for agent_id, agent in self.agents.items():
                queue_size = self.orchestrator.get_queue_size(agent_id)
                queues.append({
                    "agent": agent.name,
                    "agent_id": agent_id,
                    "count": queue_size,
                    "status": "healthy" if queue_size < 10 else "warning"
                })
            
            return {"queues": queues}
        
        @self.app.get("/api/v1/blockchain/logs")
        async def get_blockchain_logs(limit: int = 50, offset: int = 0):
            """Get blockchain communication logs"""
            if not self.blockchain_logger:
                return {"logs": [], "total": 0}
            
            # TODO: Implement blockchain log retrieval with pagination
            return {
                "logs": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
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
        
        @self.app.post("/api/v1/system/restart")
        async def restart_system():
            """Restart the agent system"""
            try:
                await self.initialize_agent_system()
                
                await self.broadcast_to_websockets({
                    "type": "system_alert",
                    "payload": {
                        "message": "System restarted successfully",
                        "level": "success"
                    }
                })
                
                return {"status": "restarted", "timestamp": datetime.now().isoformat()}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def connect_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            # Send initial system status
            await websocket.send_text(json.dumps({
                "type": "system_status",
                "payload": {
                    "status": "connected",
                    "agents_count": len(self.agents),
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            # Keep connection alive
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    async def initialize_agent_system(self):
        """Initialize the agent system"""
        try:
            logger.info("Initializing agent system...")
            
            # Initialize blockchain logger
            self.blockchain_logger = CommunicationLogger()
            
            # Initialize communication orchestrator
            self.orchestrator = CommunicationOrchestrator(self.blockchain_logger)
            
            # Create agents
            self.agents = {
                "ceo": CEOAgent("ceo", "CEO Agent"),
                "senior_manager": SeniorManager("senior_manager", "Senior Manager"),
                "incident_agent": IncidentManagementAgent("incident_agent", "Incident Management Agent"),
                "problem_agent": ProblemManagementAgent("problem_agent", "Problem Management Agent"),
                "change_agent": ChangeManagementAgent("change_agent", "Change Management Agent")
            }
            
            # Register agents with orchestrator
            for agent_id, agent in self.agents.items():
                await self.orchestrator.register_agent(agent_id, agent)
            
            # Start the orchestrator
            await self.orchestrator.start()
            
            logger.info(f"Agent system initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            raise
    
    async def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate KPI metrics"""
        if not self.orchestrator:
            return {
                "activeAgents": 0,
                "totalMessages": 0,
                "avgResponseTime": 0.0,
                "systemUptime": 0.0
            }
        
        return {
            "activeAgents": len([a for a in self.agents.values() if a]),
            "totalMessages": sum(self.orchestrator.get_queue_size(aid) for aid in self.agents.keys()),
            "avgResponseTime": 1.2,  # TODO: Calculate actual response time
            "systemUptime": 99.9  # TODO: Calculate actual uptime
        }
    
    def get_agent_hierarchy_data(self) -> Dict[str, Any]:
        """Get agent hierarchy structure for visualization"""
        return {
            "ceo": {
                "id": "ceo",
                "name": "CEO Agent",
                "role": "Chief Executive",
                "status": "online",
                "reports": ["senior_manager"]
            },
            "senior_manager": {
                "id": "senior_manager",
                "name": "Senior Manager",
                "role": "Management Layer",
                "status": "online",
                "reports": ["incident_agent", "problem_agent", "change_agent"]
            },
            "sme_agents": [
                {
                    "id": "incident_agent",
                    "name": "Incident Management",
                    "role": "ITSM Specialist",
                    "status": "online",
                    "specialization": "Incident Resolution"
                },
                {
                    "id": "problem_agent",
                    "name": "Problem Management",
                    "role": "ITSM Specialist", 
                    "status": "online",
                    "specialization": "Root Cause Analysis"
                },
                {
                    "id": "change_agent",
                    "name": "Change Management",
                    "role": "ITSM Specialist",
                    "status": "online",
                    "specialization": "Change Implementation"
                }
            ]
        }
    
    def get_uptime(self) -> str:
        """Calculate system uptime"""
        # TODO: Implement actual uptime calculation
        return "99.9%"
    
    async def start_background_tasks(self):
        """Start background tasks for monitoring and updates"""
        # Task to broadcast periodic updates
        asyncio.create_task(self.periodic_updates())
    
    async def periodic_updates(self):
        """Send periodic updates to connected clients"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                if self.active_connections:
                    kpis = await self.calculate_kpis()
                    await self.broadcast_to_websockets({
                        "type": "kpi_update",
                        "payload": kpis
                    })
                    
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")

def create_app() -> FastAPI:
    """Factory function to create the FastAPI application"""
    dashboard = WebDashboardAPI()
    return dashboard.app, dashboard

async def startup_event(dashboard: WebDashboardAPI):
    """Startup event handler"""
    try:
        await dashboard.initialize_agent_system()
        await dashboard.start_background_tasks()
        logger.info("Dashboard API started successfully")
    except Exception as e:
        logger.error(f"Failed to start dashboard API: {e}")

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    app, dashboard = create_app()
    
    # Add startup event
    @app.on_event("startup")
    async def startup():
        await startup_event(dashboard)
    
    uvicorn.run(
        "api.web_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    print(f"Starting Agentic AI Organization Dashboard at http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    run_server(host, port, reload=True)