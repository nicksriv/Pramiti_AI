from typing import Dict, List, Any, Optional
from datetime import datetime
from core.base_agent import BaseAgent, AgentRole, Message, MessageType

class IncidentManagementAgent(BaseAgent):
    """
    Specialized agent for handling IT incidents
    """
    
    def __init__(self, agent_id: str, name: str, manager_id: str):
        super().__init__(agent_id, name, AgentRole.SME, "incident_management", manager_id)
        self.incident_types = ["hardware", "software", "network", "security", "performance"]
        self.severity_levels = ["low", "medium", "high", "critical"]
        self.knowledge_base: Dict[str, Any] = {}
        self.active_incidents: List[Dict[str, Any]] = []
    
    def process_message(self, message: Message) -> Optional[Message]:
        """Process incident-related messages"""
        if message.message_type == MessageType.REQUEST:
            return self._handle_incident_request(message)
        elif message.message_type == MessageType.RESPONSE:
            return self._handle_response(message)
        
        return super().process_message(message)
    
    def _handle_incident_request(self, message: Message) -> Optional[Message]:
        """Handle new incident requests"""
        incident_data = message.content
        
        # Analyze the incident
        analysis = self._analyze_incident(incident_data)
        
        # Make decision on handling
        decision = self.make_decision({"incident": incident_data, "analysis": analysis})
        
        if decision["action"] == "escalate":
            return self.escalate_to_manager(incident_data, priority=decision.get("priority", 3))
        else:
            # Handle incident directly
            resolution = self._resolve_incident(incident_data, analysis)
            return self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                resolution,
                priority=message.priority
            )
    
    def _analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incident characteristics"""
        return {
            "severity": self._assess_severity(incident),
            "category": self._categorize_incident(incident),
            "complexity": self._assess_complexity(incident),
            "known_issue": self._check_known_issues(incident)
        }
    
    def _assess_severity(self, incident: Dict[str, Any]) -> str:
        """Assess incident severity"""
        affected_users = incident.get("affected_users", 0)
        critical_systems = incident.get("critical_systems_affected", False)
        
        if critical_systems or affected_users > 100:
            return "critical"
        elif affected_users > 20:
            return "high"
        elif affected_users > 5:
            return "medium"
        else:
            return "low"
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision on incident handling"""
        incident = context.get("incident", {})
        analysis = context.get("analysis", {})
        
        severity = analysis.get("severity", "medium")
        complexity = analysis.get("complexity", "low")
        
        # Escalate high severity or complex incidents
        if severity in ["critical", "high"] or complexity == "high":
            return {
                "action": "escalate",
                "priority": 4 if severity == "critical" else 3,
                "confidence": 0.9
            }
        else:
            return {
                "action": "resolve",
                "confidence": 0.8
            }

class ProblemManagementAgent(BaseAgent):
    """
    Specialized agent for problem management and root cause analysis
    """
    
    def __init__(self, agent_id: str, name: str, manager_id: str):
        super().__init__(agent_id, name, AgentRole.SME, "problem_management", manager_id)
        self.root_cause_database: Dict[str, Any] = {}
        self.problem_patterns: List[Dict[str, Any]] = []
        
    def process_message(self, message: Message) -> Optional[Message]:
        """Process problem management requests"""
        if message.message_type == MessageType.REQUEST:
            return self._handle_problem_request(message)
        
        return super().process_message(message)
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision on problem resolution approach"""
        problem = context.get("problem", {})
        
        # Complex problems require escalation
        incident_count = problem.get("related_incidents", 0)
        
        if incident_count > 5:
            return {
                "action": "escalate",
                "priority": 3,
                "confidence": 0.85
            }
        else:
            return {
                "action": "investigate",
                "confidence": 0.75
            }

class ChangeManagementAgent(BaseAgent):
    """
    Specialized agent for change management and approval workflows
    """
    
    def __init__(self, agent_id: str, name: str, manager_id: str):
        super().__init__(agent_id, name, AgentRole.SME, "change_management", manager_id)
        self.change_categories = ["emergency", "standard", "normal"]
        self.risk_levels = ["low", "medium", "high", "very_high"]
        self.approval_matrix: Dict[str, List[str]] = {}
    
    def process_message(self, message: Message) -> Optional[Message]:
        """Process change management requests"""
        if message.message_type == MessageType.REQUEST:
            return self._handle_change_request(message)
        
        return super().process_message(message)
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision on change approval"""
        change = context.get("change", {})
        
        risk_level = self._assess_change_risk(change)
        change_type = change.get("type", "normal")
        
        # High risk or emergency changes need management approval
        if risk_level in ["high", "very_high"] or change_type == "emergency":
            return {
                "action": "escalate",
                "priority": 4 if change_type == "emergency" else 3,
                "confidence": 0.9
            }
        else:
            return {
                "action": "approve",
                "confidence": 0.8
            }
    
    def _assess_change_risk(self, change: Dict[str, Any]) -> str:
        """Assess risk level of proposed change"""
        affected_systems = len(change.get("affected_systems", []))
        business_impact = change.get("business_impact", "low")
        
        if business_impact == "critical" or affected_systems > 10:
            return "very_high"
        elif business_impact == "high" or affected_systems > 5:
            return "high"
        elif affected_systems > 2:
            return "medium"
        else:
            return "low"