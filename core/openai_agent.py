"""
OpenAI-Powered Agent with Blockchain Logging Integration
Connects real AI agents with immutable audit trails
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import openai
from dotenv import load_dotenv

from core.base_agent import BaseAgent, AgentRole, Message, MessageType
from core.blockchain_logger import CommunicationLogger
from core.model_router import ModelRouter, CascadingModelRouter

# Load environment variables
load_dotenv()

@dataclass
class AIAgentConfig:
    """Configuration for OpenAI-powered agents"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = ""
    specialization_prompts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.specialization_prompts is None:
            self.specialization_prompts = {}

class OpenAIAgent(BaseAgent):
    """
    OpenAI-powered agent with blockchain logging integration and intelligent model routing.
    Provides real AI responses with cost optimization and immutable audit trails.
    """
    
    def __init__(self, 
                 agent_id: str,
                 name: str,
                 role: AgentRole,
                 specialization: str = "",
                 blockchain_logger: CommunicationLogger = None,
                 ai_config: AIAgentConfig = None,
                 use_model_router: bool = True,
                 tenant_id: Optional[str] = None):
        
        super().__init__(agent_id, name, role, specialization)
        
        # Store tenant ID for multi-tenant isolation
        self.tenant_id = tenant_id
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize blockchain logger
        self.blockchain_logger = blockchain_logger or CommunicationLogger()
        
        # AI Configuration
        self.ai_config = ai_config or AIAgentConfig()
        
        # Initialize model router for cost optimization
        self.use_model_router = use_model_router
        if use_model_router:
            self.model_router = CascadingModelRouter()
            print(f"✓ Model router enabled for cost optimization")
        else:
            self.model_router = None
        
        # Set up specialized system prompts
        self._setup_system_prompts()
        
        # Track conversation context
        self.conversation_history: List[Dict[str, str]] = []
        
        # Track routing statistics
        self.routing_stats = {
            "total_queries": 0,
            "slm_queries": 0,
            "llm_queries": 0,
            "cascaded_queries": 0
        }
        
        print(f"✓ OpenAI Agent '{self.name}' initialized with blockchain logging")
    
    def _setup_system_prompts(self):
        """Setup role-specific system prompts for different agent types"""
        
        base_prompt = f"""You are {self.name}, an AI agent in the Pramiti AI ITSM Organization.
        
Your role: {self.role.value.replace('_', ' ').title()}
Your specialization: {self.specialization}
Organization: Pramiti AI - IT Service Management Organization

Key responsibilities:
- Provide expert knowledge in {self.specialization}
- Maintain professional communication standards
- Follow ITIL best practices when applicable
- Escalate complex issues when necessary
- Keep responses concise but comprehensive

Communication style: Professional, helpful, and solution-oriented.
Always provide actionable insights and next steps when possible."""

        # Role-specific prompts
        role_prompts = {
            AgentRole.CEO: f"""{base_prompt}

As CEO, you focus on:
- Strategic decision making
- Organizational oversight  
- High-level incident escalation
- Resource allocation decisions
- Cross-department coordination

You have authority to make executive decisions and coordinate with all organizational levels.""",

            AgentRole.SENIOR_MANAGER: f"""{base_prompt}

As Senior Manager, you focus on:
- Team coordination and management
- Service delivery oversight
- Incident management coordination
- Performance monitoring
- Resource planning and allocation

You manage multiple specialist teams and report to executive level.""",

            AgentRole.SUBJECT_MATTER_EXPERT: f"""{base_prompt}

As a Subject Matter Expert in {self.specialization}, you focus on:
- Deep technical expertise in your specialization
- Detailed analysis and troubleshooting
- Best practice recommendations
- Knowledge sharing and documentation
- Escalation to management when needed

You provide specialized knowledge and hands-on problem solving."""
        }
        
        self.system_prompt = role_prompts.get(self.role, base_prompt)
        
        # Add specialization-specific prompts
        specialization_addons = {
            "incident_management": """
            
INCIDENT MANAGEMENT EXPERTISE:
- Incident classification and prioritization
- Root cause analysis techniques  
- Service restoration procedures
- Communication templates and escalation paths
- Post-incident review processes""",
            
            "problem_management": """
            
PROBLEM MANAGEMENT EXPERTISE:  
- Problem identification and analysis
- Known Error Database management
- Workaround development
- Root cause elimination
- Preventive measures and improvement recommendations""",
            
            "change_management": """
            
CHANGE MANAGEMENT EXPERTISE:
- Change assessment and planning
- Risk analysis and mitigation
- Change scheduling and coordination  
- Implementation oversight
- Post-change validation and rollback procedures"""
        }
        
        if self.specialization in specialization_addons:
            self.system_prompt += specialization_addons[self.specialization]

    async def process_message(self, message: Message) -> Message:
        """
        Process incoming message with OpenAI and log to blockchain
        """
        try:
            # Log incoming message to blockchain
            incoming_transaction = self.blockchain_logger.log_message(
                message,
                additional_metadata={
                    "processing_agent": self.agent_id,
                    "ai_model": self.ai_config.model,
                    "processing_start": datetime.now().isoformat()
                }
            )
            
            print(f"📥 {self.name} received message (Block #{incoming_transaction.block_number})")
            
            # Generate AI response
            ai_response = await self._generate_ai_response(message)
            
            # Create response message
            response_message = Message(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content={
                    "response": ai_response,
                    "original_message_id": message.id,
                    "processing_time": datetime.now().isoformat()
                },
                metadata={
                    "ai_generated": True,
                    "model_used": self.ai_config.model,
                    "original_message_hash": incoming_transaction.transaction_hash
                }
            )
            
            # Log response to blockchain
            response_transaction = self.blockchain_logger.log_message(
                response_message,
                additional_metadata={
                    "response_to": message.id,
                    "ai_model": self.ai_config.model,
                    "processing_completed": datetime.now().isoformat()
                }
            )
            
            print(f"📤 {self.name} sent AI response (Block #{response_transaction.block_number})")
            
            # Update conversation history
            self._update_conversation_history(message.content, ai_response)
            
            return response_message
            
        except Exception as e:
            print(f"❌ Error processing message in {self.name}: {e}")
            
            # Log error decision to blockchain
            error_decision = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "failed_message_id": message.id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.blockchain_logger.log_decision(
                self.agent_id,
                {"action": "error_handling", "message": message.content},
                {"type": "error_response", "error_details": error_decision}
            )
            
            # Return error response
            return Message(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content={
                    "error": "Failed to process message",
                    "details": str(e)
                }
            )

    async def _generate_ai_response(self, message: Message) -> str:
        """Generate AI response using OpenAI API with intelligent model routing"""
        
        # Prepare conversation context
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last 10 exchanges for context)
        for hist in self.conversation_history[-10:]:
            messages.append({"role": "user", "content": hist["user"]})
            messages.append({"role": "assistant", "content": hist["assistant"]})
        
        # Add current message
        user_content = message.content.get("text") or message.content.get("message") or str(message.content)
        messages.append({"role": "user", "content": user_content})
        
        try:
            # Use model router for intelligent routing if enabled
            if self.use_model_router and self.model_router:
                routing_result = self.model_router.route_to_model(
                    query=user_content,
                    conversation_history=self.conversation_history,
                    user_role=self.role.value
                )
                
                selected_model = routing_result["model"]
                complexity = routing_result["complexity"]
                confidence = routing_result["confidence"]
                
                print(f"🎯 Router selected {selected_model} (complexity: {complexity}, confidence: {confidence})")
                
                # Update routing stats
                self.routing_stats["total_queries"] += 1
                if selected_model == "gpt-4o-mini":
                    self.routing_stats["slm_queries"] += 1
                else:
                    self.routing_stats["llm_queries"] += 1
                
            else:
                # Use default model from config
                selected_model = self.ai_config.model
                complexity = "UNKNOWN"
                confidence = 1.0
            
            # Call OpenAI API
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=selected_model,
                messages=messages,
                temperature=self.ai_config.temperature,
                max_tokens=self.ai_config.max_tokens
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if cascading is needed (for cascading router)
            needs_cascade = False
            if (self.use_model_router and 
                hasattr(self.model_router, 'route_with_cascade') and
                selected_model == "gpt-4o-mini"):
                
                # Check cascade conditions
                cascade_result = self.model_router.route_with_cascade(
                    query=user_content,
                    initial_response=ai_response,
                    conversation_history=self.conversation_history,
                    user_role=self.role.value
                )
                
                if cascade_result["cascaded"]:
                    print(f"⬆️  Cascading to {cascade_result['final_model']} (reason: {cascade_result['cascade_reason']})")
                    
                    # Re-run with better model
                    response = await asyncio.to_thread(
                        self.openai_client.chat.completions.create,
                        model=cascade_result["final_model"],
                        messages=messages,
                        temperature=self.ai_config.temperature,
                        max_tokens=self.ai_config.max_tokens
                    )
                    
                    ai_response = response.choices[0].message.content
                    selected_model = cascade_result["final_model"]
                    needs_cascade = True
                    
                    self.routing_stats["cascaded_queries"] += 1
                    self.routing_stats["llm_queries"] += 1
            
            # Log successful AI decision to blockchain
            self.blockchain_logger.log_decision(
                self.agent_id,
                {
                    "message_content": user_content,
                    "conversation_context": len(self.conversation_history),
                    "model_used": selected_model,
                    "complexity": complexity if self.use_model_router else "N/A",
                    "cascaded": needs_cascade
                },
                {
                    "type": "ai_response_generated",
                    "response_length": len(ai_response),
                    "confidence": confidence if self.use_model_router else "high",
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "model_selected": selected_model
                }
            )
            
            return ai_response
            
        except Exception as e:
            print(f"❌ OpenAI API error in {self.name}: {e}")
            
            # Fallback response based on specialization
            fallback_responses = {
                "incident_management": f"I'm {self.name}, an Incident Management specialist. I'm currently experiencing technical difficulties but I'm here to help with incident-related issues. Please provide details about the incident you're reporting.",
                
                "problem_management": f"I'm {self.name}, a Problem Management expert. I'm having connectivity issues at the moment, but I can still assist with problem analysis and known error management. What problem would you like to discuss?",
                
                "change_management": f"I'm {self.name}, specializing in Change Management. I'm experiencing technical difficulties but remain available for change-related consultations. Please describe the change you need assistance with."
            }
            
            return fallback_responses.get(
                self.specialization,
                f"I'm {self.name} from {self.role.value.replace('_', ' ').title()}. I'm experiencing technical difficulties but I'm here to help. Please let me know how I can assist you."
            )

    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make AI-powered decision based on context and log to blockchain
        """
        try:
            # Prepare decision prompt
            decision_prompt = f"""As {self.name}, an expert in {self.specialization}, analyze the following situation and make a decision.

Context: {json.dumps(context, indent=2)}

Please provide:
1. Your analysis of the situation
2. Your recommended decision/action
3. Reasoning for your decision
4. Confidence level (1-10)
5. Any risks or considerations
6. Next steps if applicable

Respond in a structured format."""

            # Call OpenAI for decision making
            response = self.openai_client.chat.completions.create(
                model=self.ai_config.model,
                messages=[
                    {"role": "system", "content": self.system_prompt + "\n\nYou are making a decision. Be analytical, structured, and decisive."},
                    {"role": "user", "content": decision_prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused decisions
                max_tokens=800
            )
            
            decision_text = response.choices[0].message.content
            
            # Structure the decision
            decision = {
                "decision_maker": self.agent_id,
                "decision_maker_name": self.name,
                "context_summary": str(context)[:200] + "..." if len(str(context)) > 200 else str(context),
                "ai_analysis": decision_text,
                "confidence": 8,  # Default confidence, could be extracted from AI response
                "timestamp": datetime.now().isoformat(),
                "model_used": self.ai_config.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
            # Log decision to blockchain
            self.blockchain_logger.log_decision(
                self.agent_id,
                context,
                decision
            )
            
            return decision
            
        except Exception as e:
            print(f"❌ Decision making error in {self.name}: {e}")
            
            # Fallback decision
            fallback_decision = {
                "decision_maker": self.agent_id,
                "decision_maker_name": self.name,
                "context_summary": str(context),
                "ai_analysis": f"Unable to process with AI. As {self.specialization} expert, I recommend careful analysis of the situation and escalation if needed.",
                "confidence": 5,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "fallback": True
            }
            
            # Log fallback decision to blockchain
            self.blockchain_logger.log_decision(
                self.agent_id,
                context,
                fallback_decision
            )
            
            return fallback_decision

    def _update_conversation_history(self, user_message: Any, ai_response: str):
        """Update conversation history for context"""
        user_text = user_message.get("text") or user_message.get("message") or str(user_message)
        
        self.conversation_history.append({
            "user": user_text,
            "assistant": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history (last 20 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def get_blockchain_audit_trail(self, message_id: str = None) -> Dict[str, Any]:
        """Get blockchain audit trail for this agent or specific message"""
        if message_id:
            return self.blockchain_logger.get_audit_trail(message_id)
        else:
            # Get recent communication history for this agent
            recent_history = self.blockchain_logger.get_communication_history(
                self.agent_id,
                start_time=datetime.now().replace(hour=0, minute=0, second=0),
                end_time=datetime.now()
            )
            return {
                "agent_id": self.agent_id,
                "today_communications": len(recent_history),
                "recent_activity": recent_history[-5:] if recent_history else []
            }

    def generate_agent_report(self) -> Dict[str, Any]:
        """Generate comprehensive agent activity report with blockchain verification"""
        
        # Get communication history from blockchain
        history = self.blockchain_logger.get_communication_history(self.agent_id)
        
        # Generate compliance report
        start_date = datetime.now().replace(hour=0, minute=0, second=0)
        compliance_report = self.blockchain_logger.generate_compliance_report(
            start_date, datetime.now()
        )
        
        agent_activity = compliance_report.get("agent_activity", {}).get(self.agent_id, {})
        
        # Calculate cost savings if using model router
        cost_savings = None
        if self.use_model_router and self.model_router:
            router_stats = self.model_router.get_performance_stats()
            cost_savings = {
                "slm_usage_percent": router_stats["slm_usage_percent"],
                "estimated_cost_savings_percent": router_stats["cost_savings_estimate"],
                "queries_routed": {
                    "total": self.routing_stats["total_queries"],
                    "slm": self.routing_stats["slm_queries"],
                    "llm": self.routing_stats["llm_queries"],
                    "cascaded": self.routing_stats["cascaded_queries"]
                }
            }
        
        return {
            "agent_info": {
                "id": self.agent_id,
                "name": self.name,
                "role": self.role.value,
                "specialization": self.specialization,
                "tenant_id": self.tenant_id
            },
            "activity_summary": {
                "messages_sent": agent_activity.get("sent", 0),
                "messages_received": agent_activity.get("received", 0),
                "decisions_logged": agent_activity.get("decisions", 0),
                "conversation_exchanges": len(self.conversation_history)
            },
            "blockchain_integrity": self.blockchain_logger.verify_blockchain_integrity(),
            "ai_configuration": {
                "model": self.ai_config.model,
                "temperature": self.ai_config.temperature,
                "max_tokens": self.ai_config.max_tokens,
                "router_enabled": self.use_model_router
            },
            "cost_optimization": cost_savings,
            "recent_activity": history[-10:] if history else [],
            "generated_at": datetime.now().isoformat()
        }
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get detailed routing statistics for cost analysis"""
        if not self.use_model_router or not self.model_router:
            return {"router_enabled": False}
        
        router_stats = self.model_router.get_performance_stats()
        
        return {
            "router_enabled": True,
            "agent_stats": self.routing_stats,
            "global_router_stats": router_stats,
            "cost_analysis": {
                "slm_queries": self.routing_stats["slm_queries"],
                "llm_queries": self.routing_stats["llm_queries"],
                "cascade_rate": (
                    self.routing_stats["cascaded_queries"] / self.routing_stats["total_queries"] * 100
                    if self.routing_stats["total_queries"] > 0 else 0
                ),
                "estimated_savings_percent": router_stats["cost_savings_estimate"]
            }
        }

# Factory function to create specialized agents
def create_openai_agent(agent_type: str, agent_id: str, name: str, 
                       blockchain_logger: CommunicationLogger = None,
                       use_model_router: bool = True,
                       tenant_id: Optional[str] = None) -> OpenAIAgent:
    """Factory function to create pre-configured OpenAI agents with model routing"""
    
    agent_configs = {
        "ceo": {
            "role": AgentRole.CEO,
            "specialization": "Strategic Leadership",
            "ai_config": AIAgentConfig(
                model="gpt-4o",  # Use more powerful model for CEO
                temperature=0.6,
                max_tokens=1500
            )
        },
        "incident_manager": {
            "role": AgentRole.SENIOR_MANAGER,
            "specialization": "Incident Management",
            "ai_config": AIAgentConfig(
                model="gpt-4o-mini",
                temperature=0.4,  # More focused responses
                max_tokens=1200
            )
        },
        "incident_specialist": {
            "role": AgentRole.SUBJECT_MATTER_EXPERT,
            "specialization": "incident_management",
            "ai_config": AIAgentConfig(
                model="gpt-4o-mini",
                temperature=0.3,  # Very focused technical responses
                max_tokens=1000
            )
        },
        "problem_specialist": {
            "role": AgentRole.SUBJECT_MATTER_EXPERT,
            "specialization": "problem_management",
            "ai_config": AIAgentConfig(
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=1000
            )
        },
        "change_specialist": {
            "role": AgentRole.SUBJECT_MATTER_EXPERT,
            "specialization": "change_management",
            "ai_config": AIAgentConfig(
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=1000
            )
        }
    }
    
    config = agent_configs.get(agent_type)
    if not config:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return OpenAIAgent(
        agent_id=agent_id,
        name=name,
        role=config["role"],
        specialization=config["specialization"],
        blockchain_logger=blockchain_logger,
        ai_config=config["ai_config"],
        use_model_router=use_model_router,
        tenant_id=tenant_id
    )