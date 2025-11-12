from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import asyncio
import json
from enum import Enum
from dataclasses import dataclass, asdict
import threading
import queue
import time

from core.base_agent import BaseAgent, AgentRole, Message, MessageType
from core.blockchain_logger import CommunicationLogger
from agents.itsm_agents import IncidentManagementAgent, ProblemManagementAgent, ChangeManagementAgent
from agents.management_agents import SeniorManager, CEOAgent

class MessagePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class RoutingRule:
    """Defines message routing rules"""
    source_role: AgentRole
    target_role: AgentRole
    message_types: List[MessageType]
    priority_threshold: int = 1
    conditions: Dict[str, Any] = None

class MessageQueue:
    """Thread-safe message queue with priority handling"""
    
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._lock = threading.Lock()
    
    def put(self, message: Message):
        """Add message to queue with priority"""
        priority_value = 6 - message.priority  # Lower number = higher priority
        timestamp = datetime.now().timestamp()
        
        # Priority queue item: (priority, timestamp, message)
        self._queue.put((priority_value, timestamp, message))
    
    def get(self, timeout: Optional[float] = None) -> Optional[Message]:
        """Get highest priority message from queue"""
        try:
            _, _, message = self._queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        return self._queue.empty()
    
    def size(self) -> int:
        """Get queue size"""
        return self._queue.qsize()

class CommunicationOrchestrator:
    """
    Central orchestrator for agent-to-agent communication
    Handles message routing, protocol enforcement, and blockchain logging
    """
    
    def __init__(self, blockchain_logger: CommunicationLogger):
        self.agents: Dict[str, BaseAgent] = {}
        self.routing_rules: List[RoutingRule] = []
        self.message_queues: Dict[str, MessageQueue] = {}
        self.blockchain_logger = blockchain_logger
        
        # Communication statistics
        self.stats = {
            "messages_processed": 0,
            "messages_failed": 0,
            "average_processing_time": 0.0,
            "active_conversations": 0,
            "escalations_count": 0
        }
        
        # Active conversations tracking
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        
        # Message processing threads
        self.processing_threads: List[threading.Thread] = []
        self.shutdown_event = threading.Event()
        
        self._setup_default_routing_rules()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.message_queues[agent.agent_id] = MessageQueue()
        
        print(f"Registered agent: {agent.name} ({agent.agent_id}) - Role: {agent.role.value}")
    
    def _setup_default_routing_rules(self):
        """Setup default message routing rules"""
        # SME to Senior Manager escalations
        self.routing_rules.append(RoutingRule(
            source_role=AgentRole.SME,
            target_role=AgentRole.SENIOR_MANAGER,
            message_types=[MessageType.ESCALATION, MessageType.REPORT],
            priority_threshold=2
        ))
        
        # Senior Manager to CEO escalations
        self.routing_rules.append(RoutingRule(
            source_role=AgentRole.SENIOR_MANAGER,
            target_role=AgentRole.CEO,
            message_types=[MessageType.ESCALATION, MessageType.REPORT],
            priority_threshold=4
        ))
        
        # Response messages flow back down the hierarchy
        self.routing_rules.append(RoutingRule(
            source_role=AgentRole.SENIOR_MANAGER,
            target_role=AgentRole.SME,
            message_types=[MessageType.RESPONSE, MessageType.INSTRUCTION],
            priority_threshold=1
        ))
        
        self.routing_rules.append(RoutingRule(
            source_role=AgentRole.CEO,
            target_role=AgentRole.SENIOR_MANAGER,
            message_types=[MessageType.RESPONSE, MessageType.INSTRUCTION],
            priority_threshold=1
        ))
    
    def send_message(self, message: Message) -> bool:
        """Send message through the orchestration system"""
        try:
            # Validate message
            if not self._validate_message(message):
                self.stats["messages_failed"] += 1
                return False
            
            # Log to blockchain
            self._log_message_to_blockchain(message)
            
            # Route message to appropriate queue
            target_agent_id = self._route_message(message)
            if not target_agent_id:
                self.stats["messages_failed"] += 1
                return False
            
            # Update message with routing info
            message.recipient_id = target_agent_id
            message.timestamp = datetime.now().isoformat()
            
            # Add to target agent's queue
            if target_agent_id in self.message_queues:
                self.message_queues[target_agent_id].put(message)
                self.stats["messages_processed"] += 1
                
                # Track conversation
                self._track_conversation(message)
                
                return True
            else:
                print(f"Target agent {target_agent_id} not found")
                self.stats["messages_failed"] += 1
                return False
                
        except Exception as e:
            print(f"Error sending message: {e}")
            self.stats["messages_failed"] += 1
            return False
    
    def _validate_message(self, message: Message) -> bool:
        """Validate message structure and content"""
        if not message.sender_id or not message.content:
            return False
        
        if message.sender_id not in self.agents:
            return False
        
        return True
    
    def _route_message(self, message: Message) -> Optional[str]:
        """Route message based on routing rules and hierarchy"""
        sender_agent = self.agents.get(message.sender_id)
        if not sender_agent:
            return None
        
        # If explicit recipient is set, use it (but validate)
        if hasattr(message, 'recipient_id') and message.recipient_id:
            if message.recipient_id in self.agents:
                return message.recipient_id
        
        # Route based on message type and agent hierarchy
        if message.message_type == MessageType.ESCALATION:
            return self._route_escalation(sender_agent)
        elif message.message_type == MessageType.RESPONSE:
            return self._route_response(message)
        elif message.message_type == MessageType.REPORT:
            return self._route_report(sender_agent)
        
        return None
    
    def _route_escalation(self, sender_agent: BaseAgent) -> Optional[str]:
        """Route escalation to appropriate manager"""
        if sender_agent.role == AgentRole.SME:
            # Route to Senior Manager
            return sender_agent.manager_id
        elif sender_agent.role == AgentRole.SENIOR_MANAGER:
            # Route to CEO
            return sender_agent.manager_id
        
        return None
    
    def _route_response(self, message: Message) -> Optional[str]:
        """Route response message back to original sender"""
        # For responses, we need to track the original conversation
        conversation_id = message.content.get("conversation_id")
        if conversation_id and conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id].get("original_sender")
        
        return None
    
    def _route_report(self, sender_agent: BaseAgent) -> Optional[str]:
        """Route report to manager"""
        return sender_agent.manager_id
    
    def _log_message_to_blockchain(self, message: Message):
        """Log message to blockchain for audit trail"""
        try:
            # Create blockchain log entry
            log_data = {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": getattr(message, 'recipient_id', 'unknown'),
                "message_type": message.message_type.value,
                "priority": message.priority,
                "timestamp": message.timestamp,
                "content_hash": self._hash_content(message.content)
            }
            
            # Log to blockchain (async)
            self.blockchain_logger.log_communication(
                message.sender_id,
                getattr(message, 'recipient_id', 'unknown'),
                message.message_type.value,
                log_data
            )
            
        except Exception as e:
            print(f"Failed to log message to blockchain: {e}")
    
    def _hash_content(self, content: Dict[str, Any]) -> str:
        """Create hash of message content for blockchain logging"""
        import hashlib
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _track_conversation(self, message: Message):
        """Track active conversations for response routing"""
        if message.message_type in [MessageType.ESCALATION, MessageType.REQUEST]:
            conversation_id = message.message_id
            self.active_conversations[conversation_id] = {
                "original_sender": message.sender_id,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 1,
                "status": "active"
            }
        elif message.message_type == MessageType.RESPONSE:
            # Update existing conversation
            conversation_id = message.content.get("conversation_id")
            if conversation_id and conversation_id in self.active_conversations:
                self.active_conversations[conversation_id]["last_activity"] = datetime.now().isoformat()
                self.active_conversations[conversation_id]["message_count"] += 1
    
    def start_processing(self):
        """Start message processing threads"""
        # Start processing thread for each agent
        for agent_id in self.agents:
            thread = threading.Thread(
                target=self._process_agent_messages,
                args=(agent_id,),
                daemon=True
            )
            thread.start()
            self.processing_threads.append(thread)
        
        print(f"Started {len(self.processing_threads)} message processing threads")
    
    def _process_agent_messages(self, agent_id: str):
        """Process messages for a specific agent"""
        agent = self.agents[agent_id]
        message_queue = self.message_queues[agent_id]
        
        while not self.shutdown_event.is_set():
            try:
                # Get message from queue (with timeout)
                message = message_queue.get(timeout=1.0)
                
                if message:
                    start_time = time.time()
                    
                    # Process message with agent
                    response = agent.process_message(message)
                    
                    # If agent generated a response, send it
                    if response:
                        self.send_message(response)
                    
                    # Update processing time statistics
                    processing_time = time.time() - start_time
                    self._update_processing_stats(processing_time)
                    
            except Exception as e:
                print(f"Error processing message for agent {agent_id}: {e}")
                continue
    
    def _update_processing_stats(self, processing_time: float):
        """Update message processing statistics"""
        # Simple moving average
        alpha = 0.1  # Learning rate
        self.stats["average_processing_time"] = (
            alpha * processing_time + 
            (1 - alpha) * self.stats["average_processing_time"]
        )
    
    def stop_processing(self):
        """Stop all processing threads"""
        self.shutdown_event.set()
        
        # Wait for threads to finish
        for thread in self.processing_threads:
            thread.join(timeout=5.0)
        
        print("Stopped message processing threads")
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status information for an agent"""
        if agent_id not in self.agents:
            return {}
        
        agent = self.agents[agent_id]
        queue = self.message_queues[agent_id]
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "role": agent.role.value,
            "specialization": agent.specialization,
            "queue_size": queue.size(),
            "performance_metrics": agent.performance_metrics,
            "last_activity": agent.performance_metrics.get("last_activity")
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for agent_id in self.agents:
            agent_statuses[agent_id] = self.get_agent_status(agent_id)
        
        return {
            "total_agents": len(self.agents),
            "processing_stats": self.stats,
            "active_conversations": len(self.active_conversations),
            "queue_sizes": {agent_id: queue.size() for agent_id, queue in self.message_queues.items()},
            "agent_statuses": agent_statuses,
            "system_health": self._assess_system_health()
        }
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        total_queue_size = sum(queue.size() for queue in self.message_queues.values())
        failure_rate = (
            self.stats["messages_failed"] / 
            max(self.stats["messages_processed"] + self.stats["messages_failed"], 1)
        )
        
        if total_queue_size > 100 or failure_rate > 0.1:
            return "degraded"
        elif total_queue_size > 50 or failure_rate > 0.05:
            return "warning"
        else:
            return "healthy"

class AgentFactory:
    """Factory for creating and configuring agents"""
    
    @staticmethod
    def create_itsm_sme_agent(agent_id: str, name: str, specialization: str, manager_id: str) -> BaseAgent:
        """Create ITSM SME agent based on specialization"""
        specialization_lower = specialization.lower()
        
        if "incident" in specialization_lower:
            return IncidentManagementAgent(agent_id, name, manager_id)
        elif "problem" in specialization_lower:
            return ProblemManagementAgent(agent_id, name, manager_id)
        elif "change" in specialization_lower:
            return ChangeManagementAgent(agent_id, name, manager_id)
        else:
            # Generic ITSM agent
            return IncidentManagementAgent(agent_id, name, manager_id)
    
    @staticmethod
    def create_senior_manager(agent_id: str, name: str, specialization_area: str, ceo_id: str) -> SeniorManager:
        """Create senior manager agent"""
        return SeniorManager(agent_id, name, specialization_area, ceo_id)
    
    @staticmethod
    def create_ceo_agent(agent_id: str, name: str) -> CEOAgent:
        """Create CEO agent"""
        return CEOAgent(agent_id, name)