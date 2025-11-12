from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json

class AgentRole(Enum):
    CEO = "ceo"
    SENIOR_MANAGER = "senior_manager"
    SUBJECT_MATTER_EXPERT = "sme"

class MessageType(Enum):
    REPORT = "report"
    REQUEST = "request"
    RESPONSE = "response"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: MessageType = MessageType.NOTIFICATION
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1-5, 5 being highest
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMetrics:
    messages_sent: int = 0
    messages_received: int = 0
    tasks_completed: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_active: datetime = field(default_factory=datetime.now)

class BaseAgent(ABC):
    """
    Base class for all agents in the organization.
    Provides core functionality for communication, logging, and decision-making.
    """
    
    def __init__(self, 
                 agent_id: str,
                 name: str,
                 role: AgentRole,
                 specialization: str = "",
                 manager_id: Optional[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.specialization = specialization
        self.manager_id = manager_id
        self.subordinates: List[str] = []
        self.inbox: List[Message] = []
        self.sent_messages: List[Message] = []
        self.metrics = AgentMetrics()
        self.knowledge_base: Dict[str, Any] = {}
        self.active = True
        
    @abstractmethod
    def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and return response if needed"""
        pass
    
    @abstractmethod
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision based on provided context"""
        pass
    
    def send_message(self, recipient_id: str, message_type: MessageType, 
                    content: Dict[str, Any], priority: int = 1) -> Message:
        """Send message to another agent"""
        message = Message(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            priority=priority,
            metadata={"sender_role": self.role.value, "sender_specialization": self.specialization}
        )
        
        self.sent_messages.append(message)
        self.metrics.messages_sent += 1
        
        # This would be handled by the communication framework
        return message
    
    def receive_message(self, message: Message):
        """Receive and queue message for processing"""
        self.inbox.append(message)
        self.metrics.messages_received += 1
        self.metrics.last_active = datetime.now()
    
    def escalate_to_manager(self, issue: Dict[str, Any], priority: int = 3) -> Optional[Message]:
        """Escalate issue to direct manager"""
        if not self.manager_id:
            return None
            
        escalation_content = {
            "type": "escalation",
            "issue": issue,
            "escalated_by": self.agent_id,
            "escalation_reason": issue.get("reason", "Requires manager attention"),
            "recommended_action": issue.get("recommended_action", "Review and decide")
        }
        
        return self.send_message(
            self.manager_id, 
            MessageType.ESCALATION, 
            escalation_content, 
            priority
        )
    
    def report_to_manager(self, report_data: Dict[str, Any]) -> Optional[Message]:
        """Send regular report to manager"""
        if not self.manager_id:
            return None
            
        report_content = {
            "type": "status_report",
            "period": report_data.get("period", "daily"),
            "metrics": self.get_performance_metrics(),
            "achievements": report_data.get("achievements", []),
            "challenges": report_data.get("challenges", []),
            "recommendations": report_data.get("recommendations", [])
        }
        
        return self.send_message(
            self.manager_id,
            MessageType.REPORT,
            report_content,
            priority=2
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "messages_sent": self.metrics.messages_sent,
            "messages_received": self.metrics.messages_received,
            "tasks_completed": self.metrics.tasks_completed,
            "average_response_time": self.metrics.average_response_time,
            "success_rate": self.metrics.success_rate,
            "last_active": self.metrics.last_active.isoformat()
        }
    
    def update_knowledge_base(self, key: str, value: Any):
        """Update agent's knowledge base"""
        self.knowledge_base[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
            "updated_by": self.agent_id
        }
    
    def query_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Query agent's knowledge base"""
        # Simple keyword search - can be enhanced with semantic search
        results = []
        for key, data in self.knowledge_base.items():
            if query.lower() in key.lower() or query.lower() in str(data["value"]).lower():
                results.append({
                    "key": key,
                    "data": data
                })
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "specialization": self.specialization,
            "manager_id": self.manager_id,
            "subordinates": self.subordinates,
            "active": self.active,
            "metrics": {
                "messages_sent": self.metrics.messages_sent,
                "messages_received": self.metrics.messages_received,
                "tasks_completed": self.metrics.tasks_completed,
                "average_response_time": self.metrics.average_response_time,
                "success_rate": self.metrics.success_rate,
                "last_active": self.metrics.last_active.isoformat()
            }
        }