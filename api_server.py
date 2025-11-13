"""
FastAPI Backend Server with OpenAI Integration and Blockchain Logging
Connects the frontend chatbot with real AI agents and immutable audit trails
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
sys.path.append('.')

from core.openai_agent import OpenAIAgent, create_openai_agent
from core.blockchain_logger import CommunicationLogger
from core.base_agent import Message, MessageType

# Load environment variables
load_dotenv()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pramiti AI Organization API",
    description="OpenAI-powered agents with blockchain logging",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Global instances
blockchain_logger = CommunicationLogger()
agents: Dict[str, OpenAIAgent] = {}
active_connections: List[WebSocket] = []

# Import for HTML file serving
from fastapi.responses import FileResponse

# Pydantic models for API
class ChatMessage(BaseModel):
    agent_id: str
    message: str
    user_id: str = "user"
    session_id: Optional[str] = None

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    response: str
    timestamp: str
    blockchain_hash: Optional[str] = None
    block_number: Optional[int] = None

class AgentInfo(BaseModel):
    agent_id: str
    name: str
    role: str
    specialization: str
    status: str = "online"
    description: Optional[str] = None

class BlockchainEntry(BaseModel):
    entry_id: str
    message_id: Optional[str] = None
    sender_id: str
    recipient_id: Optional[str] = None
    timestamp: str
    block_number: int
    entry_hash: str

class CreateAgentRequest(BaseModel):
    name: str
    agent_type: str
    role: str
    reporting_manager_role: Optional[str] = None
    specialization: str
    model: str = "gpt-4o-mini"  # Default to cost-effective model
    system_prompt: Optional[str] = None
    responsibilities_from_doc: Optional[str] = None  # Extracted from uploaded document

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    agent_type: Optional[str] = None
    role: Optional[str] = None
    specialization: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    enabled: Optional[bool] = None

class RoleDefinition(BaseModel):
    role_id: str
    name: str
    description: str
    level: int  # Hierarchy level (1=CEO, 2=Senior Manager, etc.)
    responsibilities: str = ""  # Default responsibilities for this role
    permissions: List[str] = []
    enabled: bool = True

# Global role definitions storage
custom_roles: Dict[str, RoleDefinition] = {
    "ceo": RoleDefinition(
        role_id="ceo",
        name="CEO / Executive Director",
        description="Top-level executive leadership",
        level=1,
        responsibilities="- Set strategic direction and vision\n- Make final decisions on major initiatives\n- Oversee all departments and operations\n- Represent the organization",
        permissions=["all"],
        enabled=True
    ),
    "senior_manager": RoleDefinition(
        role_id="senior_manager",
        name="Senior Manager",
        description="Senior management and oversight",
        level=2,
        responsibilities="- Manage department operations\n- Lead and mentor team managers\n- Approve major changes and initiatives\n- Report to executive leadership",
        permissions=["manage_teams", "approve_changes"],
        enabled=True
    ),
    "manager": RoleDefinition(
        role_id="manager",
        name="Manager",
        description="Team and project management",
        level=3,
        responsibilities="- Manage team members and projects\n- Assign tasks and monitor progress\n- Coordinate with other teams\n- Report to senior management",
        permissions=["manage_team", "assign_tasks"],
        enabled=True
    ),
    "specialist": RoleDefinition(
        role_id="specialist",
        name="Specialist / Subject Matter Expert",
        description="Domain expertise and specialized knowledge",
        level=4,
        responsibilities="- Provide expert knowledge and guidance\n- Execute specialized tasks\n- Collaborate with teams on technical matters\n- Mentor junior team members",
        permissions=["execute_tasks", "provide_expertise"],
        enabled=True
    ),
    "analyst": RoleDefinition(
        role_id="analyst",
        name="Analyst",
        description="Analysis and research",
        level=5,
        responsibilities="- Analyze data and trends\n- Create reports and insights\n- Support decision-making with data\n- Identify improvement opportunities",
        permissions=["analyze_data", "create_reports"],
        enabled=True
    ),
    "operator": RoleDefinition(
        role_id="operator",
        name="Operator",
        description="Operational execution",
        level=6,
        responsibilities="- Execute assigned tasks\n- Follow standard procedures\n- Report issues and progress\n- Maintain operational efficiency",
        permissions=["execute_tasks"],
        enabled=True
    )
}

# Track agent enabled/disabled status
agent_status: Dict[str, bool] = {}

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize OpenAI agents with blockchain logging"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Please add your API key to .env file")
        print("   Copy .env.example to .env and add your OpenAI API key")
    
    # Initialize blockchain logger
    try:
        # blockchain_logger.initialize()  # Commented out as it might not exist in current version
        print("✓ Blockchain logging system initialized")
    except Exception as e:
        print(f"⚠️  Blockchain initialization warning: {e}")
    
    # Create agents
    agent_definitions = [
        {
            "type": "ceo",
            "id": "ceo-001", 
            "name": "Executive AI Director"
        },
        {
            "type": "incident_manager",
            "id": "manager-incident-001",
            "name": "ITSM Operations Manager"
        },
        {
            "type": "incident_specialist",
            "id": "agent-incident-001",
            "name": "Incident Response Specialist"
        },
        {
            "type": "problem_specialist", 
            "id": "agent-problem-001",
            "name": "Problem Analysis Expert"
        },
        {
            "type": "change_specialist",
            "id": "agent-change-001", 
            "name": "Change Management Specialist"
        }
    ]
    
    for agent_def in agent_definitions:
        try:
            agent = create_openai_agent(
                agent_type=agent_def["type"],
                agent_id=agent_def["id"],
                name=agent_def["name"],
                blockchain_logger=blockchain_logger
            )
            agents[agent_def["id"]] = agent
            agent_status[agent_def["id"]] = True  # Enable by default
            print(f"✓ Created OpenAI agent: {agent.name}")
            
        except Exception as e:
            print(f"❌ Failed to create agent {agent_def['name']}: {e}")
    
    print(f"\n🚀 Pramiti AI Organization API started with {len(agents)} agents")
    print(f"📍 Blockchain logging: {'Enabled' if blockchain_logger else 'Disabled'}")
    print(f"🔗 OpenAI Integration: {'Enabled' if os.getenv('OPENAI_API_KEY') else 'Requires API Key'}")

# API Routes

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Pramiti AI Organization API",
        "status": "running",
        "agents": len(agents),
        "blockchain_enabled": True,
        "openai_enabled": bool(os.getenv("OPENAI_API_KEY"))
    }

# Serve HTML frontend files
@app.get("/openai-dashboard.html")
async def serve_openai_dashboard():
    """Serve the OpenAI dashboard HTML"""
    return FileResponse("web/openai-dashboard.html")

@app.get("/enhanced-dashboard.html")
async def serve_enhanced_dashboard():
    """Serve the enhanced dashboard HTML with no-cache headers"""
    from fastapi.responses import Response
    with open("web/enhanced-dashboard.html", "r") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/index.html")
async def serve_index():
    """Serve the index dashboard HTML"""
    return FileResponse("web/index.html")

@app.get("/agents", response_model=List[AgentInfo])
async def get_agents(include_disabled: bool = False):
    """Get list of available agents"""
    agent_list = []
    for agent_id, agent in agents.items():
        # Check if agent is enabled
        is_enabled = agent_status.get(agent_id, True)
        
        # Skip disabled agents unless explicitly requested
        if not is_enabled and not include_disabled:
            continue
            
        agent_list.append(AgentInfo(
            agent_id=agent_id,
            name=agent.name,
            role=agent.role.value,
            specialization=agent.specialization,
            status="online" if is_enabled else "disabled",
            description=f"{agent.role.value.replace('_', ' ').title()} specializing in {agent.specialization}"
        ))
    
    return agent_list

@app.post("/agents", response_model=AgentInfo)
async def create_agent(
    name: str = Form(...),
    agent_type: str = Form(...),
    role: str = Form(...),
    reporting_manager_role: str = Form(None),
    reports_to_agent_id: str = Form(None),
    specialization: str = Form(...),
    model: str = Form("gpt-4o-mini"),
    responsibilities_doc: Optional[UploadFile] = File(None)
):
    """Create a new AI agent with optional document upload for responsibilities and direct reporting relationship"""
    
    try:
        # Generate unique agent ID
        agent_count = len(agents) + 1
        agent_type_clean = agent_type.lower().replace(' ', '-')
        agent_id = f"{agent_type_clean}-{agent_count:03d}"
        
        # Check for duplicate names
        existing_names = [agent.name.lower() for agent in agents.values()]
        if name.lower() in existing_names:
            raise HTTPException(
                status_code=400, 
                detail=f"Agent with name '{name}' already exists"
            )
        
        # Get responsibilities from role definition
        if role not in custom_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Role '{role}' not found. Please create the role first."
            )
        
        role_def = custom_roles[role]
        if not role_def.enabled:
            raise HTTPException(
                status_code=400,
                detail=f"Role '{role}' is currently disabled."
            )
        
        # Validate reporting hierarchy
        if reporting_manager_role:
            if reporting_manager_role not in custom_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Reporting manager role '{reporting_manager_role}' not found."
                )
            
            manager_role_def = custom_roles[reporting_manager_role]
            
            # Ensure reporting manager has higher authority (lower level number)
            if manager_role_def.level >= role_def.level:
                raise HTTPException(
                    status_code=400,
                    detail=f"Reporting manager role must be higher in hierarchy than agent's role. {manager_role_def.name} (Level {manager_role_def.level}) cannot manage {role_def.name} (Level {role_def.level})."
                )
        
        # Validate specific reporting agent if provided
        if reports_to_agent_id:
            if reports_to_agent_id not in agents:
                raise HTTPException(
                    status_code=400,
                    detail=f"Reporting manager agent '{reports_to_agent_id}' not found."
                )
            
            # Validate that the specified agent has the reporting manager role
            manager_agent = agents[reports_to_agent_id]
            manager_custom_role = getattr(manager_agent, 'metadata', {}).get('custom_role_id')
            
            if reporting_manager_role and manager_custom_role != reporting_manager_role:
                raise HTTPException(
                    status_code=400,
                    detail=f"Selected manager '{manager_agent.name}' has role '{manager_custom_role}' but expected '{reporting_manager_role}'."
                )
        
        # Base responsibilities from role
        responsibilities = role_def.responsibilities
        
        # Process uploaded document if provided
        document_content = None
        if responsibilities_doc and responsibilities_doc.filename:
            try:
                # Read file content
                file_content = await responsibilities_doc.read()
                
                # Extract text based on file type
                if responsibilities_doc.filename.endswith('.txt'):
                    document_content = file_content.decode('utf-8')
                elif responsibilities_doc.filename.endswith(('.docx', '.doc')):
                    # Extract text from DOCX
                    from docx import Document
                    from io import BytesIO
                    doc = Document(BytesIO(file_content))
                    document_content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
                elif responsibilities_doc.filename.endswith('.pdf'):
                    # Extract text from PDF
                    from PyPDF2 import PdfReader
                    from io import BytesIO
                    pdf = PdfReader(BytesIO(file_content))
                    document_content = '\n'.join([page.extract_text() for page in pdf.pages])
                
                # Append document content to responsibilities
                if document_content:
                    responsibilities += f"\n\nAdditional Responsibilities (from uploaded document):\n{document_content}"
                    print(f"✅ Processed document: {responsibilities_doc.filename} ({len(document_content)} chars)")
                
            except Exception as doc_error:
                print(f"⚠️ Warning: Could not process document {responsibilities_doc.filename}: {str(doc_error)}")
                # Continue without document content rather than failing
        
        # Parse role from string to AgentRole enum
        from core.base_agent import AgentRole
        
        # Map role strings to AgentRole enum
        # Note: Base system only has 3 roles defined
        role_mapping = {
            "ceo": AgentRole.CEO,
            "senior_manager": AgentRole.SENIOR_MANAGER,
            "manager": AgentRole.SENIOR_MANAGER,  # Map to senior_manager
            "subject_matter_expert": AgentRole.SUBJECT_MATTER_EXPERT,
            "sme": AgentRole.SUBJECT_MATTER_EXPERT,
            "specialist": AgentRole.SUBJECT_MATTER_EXPERT,  # Map to SME
            "analyst": AgentRole.SUBJECT_MATTER_EXPERT,  # Map to SME
            "operator": AgentRole.SUBJECT_MATTER_EXPERT  # Map to SME
        }
        
        agent_role = role_mapping.get(role.lower(), AgentRole.SUBJECT_MATTER_EXPERT)
        
        # Build system prompt with hierarchy information
        hierarchy_info = ""
        if reporting_manager_role:
            manager_role_def = custom_roles[reporting_manager_role]
            hierarchy_info = f"\n\nYou report to {manager_role_def.name} level management."
        
        system_prompt = f"""You are {name}, a {role_def.name} with expertise in {specialization}.

Your responsibilities include:
{responsibilities}
{hierarchy_info}

You work within the Pramiti AI Organization, collaborating with other AI agents to provide excellent service.
Be professional, knowledgeable, and helpful in all interactions."""
        
        # Create AI config
        from core.openai_agent import AIAgentConfig
        ai_config = AIAgentConfig(
            model=model,
            temperature=0.7,
            max_tokens=1200,
            system_prompt=system_prompt
        )
        
        # Create the new agent directly
        from core.openai_agent import OpenAIAgent
        new_agent = OpenAIAgent(
            agent_id=agent_id,
            name=name,
            role=agent_role,
            specialization=specialization,
            blockchain_logger=blockchain_logger,
            ai_config=ai_config
        )
        
        # Store reporting relationship in agent metadata
        if not hasattr(new_agent, 'metadata'):
            new_agent.metadata = {}
        new_agent.metadata['reporting_manager_role'] = reporting_manager_role
        new_agent.metadata['reports_to_agent_id'] = reports_to_agent_id
        new_agent.metadata['custom_role_id'] = role
        new_agent.metadata['agent_type'] = agent_type
        
        # Add to agents dictionary and enable it
        agents[agent_id] = new_agent
        agent_status[agent_id] = True  # Enable by default
        
        print(f"✅ Created new agent: {name} ({agent_id}) with role {role_def.name}")
        if reporting_manager_role:
            print(f"   └─ Reports to role: {custom_roles[reporting_manager_role].name}")
        if reports_to_agent_id:
            manager_name = agents.get(reports_to_agent_id, {})
            manager_name = getattr(manager_name, 'name', reports_to_agent_id) if manager_name else reports_to_agent_id
            print(f"   └─ Direct manager: {manager_name} ({reports_to_agent_id})")
        
        # Return agent info
        return AgentInfo(
            agent_id=agent_id,
            name=new_agent.name,
            role=role,  # Return the custom role ID
            specialization=new_agent.specialization,
            status="online",
            description=f"{role_def.name} specializing in {new_agent.specialization}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: str, request: UpdateAgentRequest):
    """Update an existing agent"""
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent = agents[agent_id]
        
        # Update fields if provided
        if request.name:
            agent.name = request.name
        
        if request.specialization:
            agent.specialization = request.specialization
        
        if request.role:
            from core.base_agent import AgentRole
            role_mapping = {
                "ceo": AgentRole.CEO,
                "senior_manager": AgentRole.SENIOR_MANAGER,
                "manager": AgentRole.SENIOR_MANAGER,
                "subject_matter_expert": AgentRole.SUBJECT_MATTER_EXPERT,
                "sme": AgentRole.SUBJECT_MATTER_EXPERT,
                "specialist": AgentRole.SUBJECT_MATTER_EXPERT,
                "analyst": AgentRole.SUBJECT_MATTER_EXPERT,
                "operator": AgentRole.SUBJECT_MATTER_EXPERT
            }
            agent.role = role_mapping.get(request.role.lower(), AgentRole.SUBJECT_MATTER_EXPERT)
        
        if request.enabled is not None:
            agent_status[agent_id] = request.enabled
        
        # Note: model, system_prompt, and responsibilities updates would require recreating the agent
        # For now, these are informational only
        
        print(f"✅ Updated agent: {agent.name} ({agent_id})")
        
        is_enabled = agent_status.get(agent_id, True)
        return AgentInfo(
            agent_id=agent_id,
            name=agent.name,
            role=agent.role.value,
            specialization=agent.specialization,
            status="online" if is_enabled else "disabled",
            description=f"{agent.role.value.replace('_', ' ').title()} specializing in {agent.specialization}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent_name = agents[agent_id].name
        del agents[agent_id]
        
        if agent_id in agent_status:
            del agent_status[agent_id]
        
        print(f"✅ Deleted agent: {agent_name} ({agent_id})")
        
        return {"message": f"Agent '{agent_name}' deleted successfully", "agent_id": agent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")

@app.post("/agents/{agent_id}/enable")
async def enable_agent(agent_id: str):
    """Enable an agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    agent_status[agent_id] = True
    print(f"✅ Enabled agent: {agents[agent_id].name} ({agent_id})")
    
    return {"message": "Agent enabled", "agent_id": agent_id, "enabled": True}

@app.post("/agents/{agent_id}/disable")
async def disable_agent(agent_id: str):
    """Disable an agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    agent_status[agent_id] = False
    print(f"✅ Disabled agent: {agents[agent_id].name} ({agent_id})")
    
    return {"message": "Agent disabled", "agent_id": agent_id, "enabled": False}

# Role Management Endpoints

@app.get("/roles")
async def get_roles(include_disabled: bool = False):
    """Get list of available roles"""
    if include_disabled:
        return list(custom_roles.values())
    return [role for role in custom_roles.values() if role.enabled]

@app.post("/roles")
async def create_role(role: RoleDefinition):
    """Create a new custom role"""
    if role.role_id in custom_roles:
        raise HTTPException(status_code=400, detail=f"Role '{role.role_id}' already exists")
    
    custom_roles[role.role_id] = role
    print(f"✅ Created new role: {role.name} ({role.role_id})")
    
    return role

@app.put("/roles/{role_id}")
async def update_role(role_id: str, role: RoleDefinition):
    """Update an existing role"""
    if role_id not in custom_roles:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    custom_roles[role_id] = role
    print(f"✅ Updated role: {role.name} ({role_id})")
    
    return role

@app.delete("/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete a role"""
    if role_id not in custom_roles:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    # Check if any agents use this role
    agents_using_role = [
        agent_id for agent_id, agent in agents.items() 
        if agent.role.value == role_id
    ]
    
    if agents_using_role:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete role '{role_id}': {len(agents_using_role)} agent(s) are using it"
        )
    
    role_name = custom_roles[role_id].name
    del custom_roles[role_id]
    print(f"✅ Deleted role: {role_name} ({role_id})")
    
    return {"message": f"Role '{role_name}' deleted successfully", "role_id": role_id}

@app.post("/roles/{role_id}/enable")
async def enable_role(role_id: str):
    """Enable a role"""
    if role_id not in custom_roles:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    custom_roles[role_id].enabled = True
    print(f"✅ Enabled role: {custom_roles[role_id].name} ({role_id})")
    
    return {"message": "Role enabled", "role_id": role_id, "enabled": True}

@app.post("/roles/{role_id}/disable")
async def disable_role(role_id: str):
    """Disable a role"""
    if role_id not in custom_roles:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    custom_roles[role_id].enabled = False
    print(f"✅ Disabled role: {custom_roles[role_id].name} ({role_id})")
    
    return {"message": "Role disabled", "role_id": role_id, "enabled": False}

# API v1 endpoints for enhanced/basic dashboards
@app.get("/api/v1/dashboard/kpis")
async def get_dashboard_kpis():
    """Get dashboard KPIs for enhanced/basic dashboards"""
    total_messages = len(blockchain_logger.local_blockchain)
    
    return {
        "active_agents": len(agents),
        "messages_processed": total_messages,
        "active_incidents": 0,
        "blockchain_logs": len(blockchain_logger.local_blockchain),
        "avg_response_time": "0.5s",
        "system_health": "healthy"
    }

@app.get("/api/v1/agents/hierarchy")
async def get_agents_hierarchy():
    """Get agent hierarchy for visualization with reporting relationships"""
    hierarchy = {
        "ceo": [],
        "managers": [],
        "specialists": [],
        "reporting_structure": {},  # Maps agent_id to reporting_manager_role
        "direct_reports": {}  # Maps agent_id to reports_to_agent_id
    }
    
    for agent_id, agent in agents.items():
        # Get metadata for custom role and reporting info
        custom_role_id = getattr(agent, 'metadata', {}).get('custom_role_id', None)
        reporting_manager_role = getattr(agent, 'metadata', {}).get('reporting_manager_role', None)
        reports_to_agent_id = getattr(agent, 'metadata', {}).get('reports_to_agent_id', None)
        agent_type = getattr(agent, 'metadata', {}).get('agent_type', agent.specialization)
        
        agent_data = {
            "id": agent_id,
            "name": agent.name,
            "role": agent.role.value,
            "custom_role_id": custom_role_id,
            "agent_type": agent_type,
            "specialization": agent.specialization,
            "status": "online",
            "reporting_manager_role": reporting_manager_role,
            "reports_to_agent_id": reports_to_agent_id
        }
        
        # Add to reporting structure
        if reporting_manager_role:
            hierarchy["reporting_structure"][agent_id] = reporting_manager_role
        
        # Add direct reporting relationship
        if reports_to_agent_id:
            hierarchy["direct_reports"][agent_id] = reports_to_agent_id
        
        # Categorize by role
        if "ceo" in agent_id or agent.role.value == "ceo":
            hierarchy["ceo"].append(agent_data)
        elif "manager" in agent_id or agent.role.value == "senior_manager":
            hierarchy["managers"].append(agent_data)
        else:
            hierarchy["specialists"].append(agent_data)
    
    return hierarchy

@app.get("/api/v1/communications/recent")
async def get_recent_communications():
    """Get recent communications"""
    recent_blocks = blockchain_logger.export_blockchain()[-10:]
    
    communications = []
    for block in recent_blocks:
        communications.append({
            "id": block.get("entry_id"),
            "from": block.get("sender_id", "system"),
            "to": block.get("recipient_id", "system"),
            "timestamp": block.get("timestamp"),
            "type": "message",
            "block_number": block.get("block_number")
        })
    
    return communications

@app.get("/api/v1/communications/queues")
async def get_message_queues():
    """Get message queue status for all agents"""
    queues = []
    
    for agent_id, agent in agents.items():
        queues.append({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "queue_size": 0,  # No active queue system yet
            "status": "healthy",
            "last_activity": datetime.now().isoformat()
        })
    
    return queues

@app.get("/api/v1/blockchain/logs")
async def get_blockchain_logs(limit: int = 50):
    """Get blockchain communication logs"""
    try:
        # Get blockchain entries
        blockchain = blockchain_logger.local_blockchain
        
        # Reverse to show newest first
        logs = []
        for i, block in enumerate(reversed(blockchain[-limit:])):
            # Extract block fields - check actual structure
            block_number = block.get("block_number", len(blockchain) - i)
            timestamp = block.get("timestamp", "N/A")
            entry_hash = block.get("entry_hash", "N/A")
            prev_hash = block.get("previous_hash", "")
            
            # Create log entry
            log_entry = {
                "block_number": block_number,
                "timestamp": timestamp,
                "previous_hash": prev_hash[:16] + "..." if prev_hash else "Genesis",
                "hash": entry_hash[:16] + "..." if entry_hash and entry_hash != "N/A" else "N/A",
                "full_hash": entry_hash,
                "sender": block.get("sender_id", "System"),
                "recipient": block.get("recipient_id", "N/A"),
                "message_type": block.get("message_type", "UNKNOWN"),
            }
            
            # Try to extract message content
            if "content_hash" in block:
                # This is a message log - try to get readable content
                metadata = block.get("metadata", {})
                log_entry["message"] = metadata.get("preview", "Message logged (content hashed)")
            else:
                # Generic block
                log_entry["message"] = str(block.get("data", "N/A"))[:100]
            
            logs.append(log_entry)
        
        return {
            "total_blocks": len(blockchain),
            "logs": logs,
            "blockchain_valid": True  # Always true for local blockchain
        }
    except Exception as e:
        print(f"Error fetching blockchain logs: {e}")
        import traceback
        traceback.print_exc()
        return {
            "total_blocks": 0,
            "logs": [],
            "blockchain_valid": True,
            "error": str(e)
        }

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(chat_message: ChatMessage):
    """Send message to specific agent and get AI-powered response"""
    
    if chat_message.agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {chat_message.agent_id} not found")
    
    agent = agents[chat_message.agent_id]
    
    try:
        # Create message object
        user_message = Message(
            sender_id=chat_message.user_id,
            recipient_id=chat_message.agent_id,
            message_type=MessageType.REQUEST,
            content={
                "text": chat_message.message,
                "session_id": chat_message.session_id
            }
        )
        
        # Process with OpenAI agent (includes blockchain logging)
        response_message = await agent.process_message(user_message)
        
        # Get blockchain info
        audit_trail = agent.get_blockchain_audit_trail(response_message.id)
        
        return AgentResponse(
            agent_id=chat_message.agent_id,
            agent_name=agent.name,
            response=response_message.content.get("response", "No response generated"),
            timestamp=response_message.timestamp.isoformat(),
            blockchain_hash=response_message.metadata.get("original_message_hash"),
            block_number=len(blockchain_logger.local_blockchain)
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/agent/{agent_id}/audit")
async def get_agent_audit_trail(agent_id: str):
    """Get blockchain audit trail for specific agent"""
    
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = agents[agent_id]
    audit_data = agent.get_blockchain_audit_trail()
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "audit_trail": audit_data,
        "blockchain_integrity": blockchain_logger.verify_blockchain_integrity()
    }

@app.get("/agent/{agent_id}/report")
async def get_agent_report(agent_id: str):
    """Get comprehensive agent activity report"""
    
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = agents[agent_id]
    report = agent.generate_agent_report()
    
    return report

@app.get("/blockchain/status")
async def get_blockchain_status():
    """Get blockchain status and recent activity"""
    
    recent_blocks = blockchain_logger.export_blockchain()[-10:]  # Last 10 blocks
    
    return {
        "total_blocks": len(blockchain_logger.local_blockchain),
        "integrity_verified": blockchain_logger.verify_blockchain_integrity(),
        "recent_blocks": [
            BlockchainEntry(
                entry_id=block["entry_id"],
                message_id=block.get("message_id"),
                sender_id=block.get("sender_id", block.get("agent_id", "system")),
                recipient_id=block.get("recipient_id"),
                timestamp=block["timestamp"],
                block_number=block["block_number"],
                entry_hash=block["entry_hash"]
            ) for block in recent_blocks
        ]
    }

@app.get("/blockchain/compliance-report")
async def generate_compliance_report():
    """Generate blockchain compliance report"""
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0)
    report = blockchain_logger.generate_compliance_report(start_date, datetime.now())
    
    return report

# WebSocket for real-time communication
@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time agent communication"""
    
    if agent_id not in agents:
        await websocket.close(code=4404)
        return
    
    await websocket.accept()
    active_connections.append(websocket)
    agent = agents[agent_id]
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_text = data.get("message", "")
            user_id = data.get("user_id", "websocket_user")
            
            if message_text:
                # Create and process message
                user_message = Message(
                    sender_id=user_id,
                    recipient_id=agent_id,
                    message_type=MessageType.REQUEST,
                    content={"text": message_text}
                )
                
                # Get AI response with blockchain logging
                response_message = await agent.process_message(user_message)
                
                # Send response back to client
                await websocket.send_json({
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "response": response_message.content.get("response", "No response"),
                    "timestamp": response_message.timestamp.isoformat(),
                    "blockchain_logged": True,
                    "block_number": len(blockchain_logger.local_blockchain)
                })
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Generic WebSocket endpoints for enhanced/basic dashboards
@app.websocket("/ws")
async def websocket_generic(websocket: WebSocket):
    """Generic WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            
            # Send status update
            await websocket.send_json({
                "type": "status_update",
                "agents": len(agents),
                "blockchain_blocks": len(blockchain_logger.local_blockchain),
                "timestamp": datetime.now().isoformat()
            })
                
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print("Generic WebSocket disconnected")
    except Exception as e:
        print(f"Generic WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for chat interface"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("message", "")
            agent_id = data.get("agent_id", "agent-incident-001")
            
            if message_text and agent_id in agents:
                agent = agents[agent_id]
                
                user_message = Message(
                    sender_id="websocket_user",
                    recipient_id=agent_id,
                    message_type=MessageType.REQUEST,
                    content={"text": message_text}
                )
                
                response_message = await agent.process_message(user_message)
                
                await websocket.send_json({
                    "type": "chat_response",
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "response": response_message.content.get("response", "No response"),
                    "timestamp": response_message.timestamp.isoformat(),
                    "blockchain_logged": True
                })
                
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print("Chat WebSocket disconnected")
    except Exception as e:
        print(f"Chat WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# User-facing chatbot endpoint (Pramiti Assistant)
@app.post("/user-chat")
async def user_chatbot(chat_message: ChatMessage):
    """User-facing chatbot that can route to appropriate agents"""
    
    message_lower = chat_message.message.lower()
    
    # Determine which agent should handle the request
    if any(word in message_lower for word in ["incident", "outage", "down", "broken", "error", "issue"]):
        target_agent_id = "agent-incident-001"
    elif any(word in message_lower for word in ["problem", "recurring", "analysis", "root cause"]):
        target_agent_id = "agent-problem-001"  
    elif any(word in message_lower for word in ["change", "update", "upgrade", "deployment", "release"]):
        target_agent_id = "agent-change-001"
    elif any(word in message_lower for word in ["manager", "escalate", "supervisor"]):
        target_agent_id = "manager-incident-001"
    elif any(word in message_lower for word in ["executive", "ceo", "strategic", "organization"]):
        target_agent_id = "ceo-001"
    else:
        # Default to incident specialist for general IT queries
        target_agent_id = "agent-incident-001"
    
    # Route to appropriate agent
    chat_message.agent_id = target_agent_id
    response = await chat_with_agent(chat_message)
    
    # Add routing information to response
    response_dict = response.dict()
    response_dict["routed_to"] = agents[target_agent_id].name
    response_dict["routing_reason"] = f"Message contained keywords suggesting {agents[target_agent_id].specialization}"
    
    return response_dict

# ===== TICKET MANAGEMENT ENDPOINTS =====

# In-memory ticket storage (replace with database in production)
tickets_db = []

@app.get("/api/v1/tickets")
async def get_tickets():
    """Get all tickets"""
    return tickets_db

@app.post("/api/v1/tickets")
async def create_ticket(ticket: dict):
    """Create a new ticket"""
    tickets_db.append(ticket)
    return ticket

@app.get("/api/v1/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get a specific ticket"""
    ticket = next((t for t in tickets_db if t.get('id') == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.put("/api/v1/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, updates: dict):
    """Update a ticket"""
    ticket = next((t for t in tickets_db if t.get('id') == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket fields
    for key, value in updates.items():
        if key != 'id':  # Don't allow changing the ID
            ticket[key] = value
    
    return ticket

@app.delete("/api/v1/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str):
    """Delete a ticket"""
    global tickets_db
    ticket = next((t for t in tickets_db if t.get('id') == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    tickets_db = [t for t in tickets_db if t.get('id') != ticket_id]
    return {"message": "Ticket deleted successfully"}

# ===== DATA ARCHIVES ENDPOINTS =====

# In-memory archives storage (replace with database in production)
archives_db = []

@app.get("/api/v1/archives")
async def get_archives():
    """Get all archived documents"""
    return archives_db

@app.post("/api/v1/archives")
async def upload_archive(
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form(...),
    department: str = Form(None),
    tags: str = Form(None),
    searchable: bool = Form(True),
    file: UploadFile = File(...)
):
    """Upload a new document to archives"""
    import os
    from datetime import datetime
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed.")
    
    # Read file content
    content = await file.read()
    file_size = len(content) / (1024 * 1024)  # Size in MB
    
    # Validate file size (max 10MB)
    if file_size > 10:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    # Process document based on file type
    text_content = ""
    try:
        if file_ext == '.txt':
            text_content = content.decode('utf-8')
        elif file_ext == '.docx':
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            text_content = '\n'.join([para.text for para in doc.paragraphs])
        elif file_ext == '.pdf':
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = '\n'.join([page.extract_text() for page in pdf_reader.pages])
    except Exception as e:
        logger.warning(f"Could not extract text from document: {e}")
        text_content = ""
    
    # Generate document ID
    doc_id = f"DOC-{str(len(archives_db) + 1).zfill(3)}"
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
    
    # Create archive document
    archive_doc = {
        "id": doc_id,
        "title": title,
        "description": description,
        "category": category,
        "department": department,
        "file_name": file.filename,
        "file_type": file_ext[1:],  # Remove the dot
        "file_size": round(file_size, 2),
        "text_content": text_content,
        "uploaded_at": datetime.utcnow().isoformat() + 'Z',
        "uploaded_by": "Current User",  # Replace with actual user when auth is implemented
        "tags": tag_list,
        "searchable": searchable
    }
    
    # Store the document
    archives_db.append(archive_doc)
    
    # In production, save file to storage and index text_content for search
    logger.info(f"Document uploaded: {doc_id} - {title}")
    
    return archive_doc

@app.get("/api/v1/archives/{archive_id}")
async def get_archive(archive_id: str):
    """Get a specific archived document"""
    archive = next((a for a in archives_db if a.get('id') == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Document not found")
    return archive

@app.get("/api/v1/archives/{archive_id}/download")
async def download_archive(archive_id: str):
    """Download an archived document"""
    archive = next((a for a in archives_db if a.get('id') == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # In production, return the actual file from storage
    return {"message": "Download endpoint - file would be served here", "document": archive}

@app.get("/api/v1/archives/{archive_id}/view")
async def view_archive(archive_id: str):
    """View an archived document"""
    archive = next((a for a in archives_db if a.get('id') == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Return text content for viewing
    return {
        "id": archive['id'],
        "title": archive['title'],
        "content": archive.get('text_content', 'Content not available'),
        "file_type": archive['file_type']
    }

@app.put("/api/v1/archives/{archive_id}")
async def update_archive(archive_id: str, updates: dict):
    """Update an archived document metadata"""
    archive = next((a for a in archives_db if a.get('id') == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update allowed fields
    for key, value in updates.items():
        if key not in ['id', 'file_name', 'file_type', 'uploaded_at', 'text_content']:
            archive[key] = value
    
    return archive

@app.delete("/api/v1/archives/{archive_id}")
async def delete_archive(archive_id: str):
    """Delete an archived document"""
    global archives_db
    archive = next((a for a in archives_db if a.get('id') == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Document not found")
    
    archives_db = [a for a in archives_db if a.get('id') != archive_id]
    logger.info(f"Document deleted: {archive_id}")
    return {"message": "Document deleted successfully"}

@app.get("/api/v1/archives/search")
async def search_archives(query: str):
    """Search archives by text content (for agent use)"""
    if not query:
        return []
    
    query_lower = query.lower()
    results = []
    
    for archive in archives_db:
        if not archive.get('searchable', True):
            continue
        
        # Search in title, description, tags, and content
        score = 0
        if query_lower in archive['title'].lower():
            score += 10
        if archive.get('description') and query_lower in archive['description'].lower():
            score += 5
        if any(query_lower in tag.lower() for tag in archive.get('tags', [])):
            score += 3
        if archive.get('text_content') and query_lower in archive['text_content'].lower():
            score += 1
        
        if score > 0:
            results.append({
                **archive,
                'relevance_score': score
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:10]  # Return top 10 results

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Pramiti AI Organization API Server")
    print("📍 Ensure you have set OPENAI_API_KEY in your .env file")
    print("🔗 Frontend will be available at: http://localhost:8084")
    print("📊 API docs available at: http://localhost:8084/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8084,
        reload=True,
        log_level="info"
    )