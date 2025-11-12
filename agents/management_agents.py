from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from core.base_agent import BaseAgent, AgentRole, Message, MessageType
import statistics

class SeniorManager(BaseAgent):
    """
    Senior Manager agent that oversees multiple SME agents
    """
    
    def __init__(self, agent_id: str, name: str, specialization_area: str, ceo_id: str):
        super().__init__(agent_id, name, AgentRole.SENIOR_MANAGER, specialization_area, ceo_id)
        self.team_performance: Dict[str, Any] = {}
        self.escalation_threshold: int = 3
        self.sla_monitoring: Dict[str, Any] = {}
        self.decision_history: List[Dict[str, Any]] = []
    
    def add_subordinate(self, agent_id: str):
        """Add SME agent to this manager's team"""
        if agent_id not in self.subordinates:
            self.subordinates.append(agent_id)
            self.team_performance[agent_id] = {
                "tasks_completed": 0,
                "escalations_received": 0,
                "average_resolution_time": 0.0,
                "success_rate": 100.0,
                "last_performance_review": datetime.now().isoformat()
            }
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make management decision based on context"""
        decision_type = context.get("type")
        
        if decision_type == "escalation_response":
            return self._make_escalation_decision(context)
        elif decision_type == "resource_allocation":
            return self._make_resource_decision(context)
        elif decision_type == "team_performance":
            return self._make_performance_decision(context)
        
        return {"action": "review", "confidence": 0.5}
    
    def _make_escalation_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision on how to handle escalation"""
        escalation = context.get("escalation", {})
        analysis = context.get("analysis", {})
        
        business_impact = analysis.get("business_impact", "low")
        complexity = analysis.get("complexity", "low")
        
        if business_impact == "high" or complexity == "high":
            decision = {
                "action": "immediate_intervention",
                "guidance": [
                    "Prioritize this issue above others",
                    "Allocate additional resources",
                    "Provide hourly updates"
                ],
                "resources": analysis.get("resource_requirements", []),
                "follow_up": True,
                "escalate_to_ceo": business_impact == "high" and complexity == "high",
                "confidence": 0.9
            }
        else:
            decision = {
                "action": "guided_resolution",
                "guidance": [
                    "Follow standard procedures",
                    "Keep me informed of progress",
                    "Escalate if no progress in 4 hours"
                ],
                "resources": [],
                "follow_up": True,
                "escalate_to_ceo": False,
                "confidence": 0.8
            }
        
        # Track decision
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "escalation_response",
            "decision": decision,
            "context": context
        })
        
        return decision

class CEOAgent(BaseAgent):
    """
    CEO Agent - Top-level decision maker for the AI organization
    """
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, AgentRole.CEO, "executive_leadership", None)
        self.organizational_metrics: Dict[str, Any] = {}
        self.strategic_initiatives: List[Dict[str, Any]] = []
        self.board_reports: List[Dict[str, Any]] = []
        self.budget_allocation: Dict[str, float] = {}
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make executive-level decisions"""
        decision_type = context.get("type")
        
        if decision_type == "executive_escalation":
            return self._make_executive_decision(context)
        elif decision_type == "strategic_planning":
            return self._make_strategic_decision(context)
        elif decision_type == "resource_allocation":
            return self._make_budget_decision(context)
        
        return {"action": "delegate", "confidence": 0.7}
    
    def _make_executive_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make high-level executive decision"""
        escalation = context.get("escalation", {})
        analysis = context.get("analysis", {})
        
        business_risk = analysis.get("business_continuity_risk", "low")
        financial_impact = analysis.get("financial_impact", "low")
        
        if business_risk == "high" or financial_impact == "high":
            decision = {
                "action": "crisis_management",
                "guidance": [
                    "Activate crisis management protocol",
                    "Establish executive oversight committee",
                    "Prepare stakeholder communications"
                ],
                "resources": {
                    "budget_authorization": "$100,000",
                    "additional_staff": "as_needed",
                    "external_consultants": "approved"
                },
                "communication": [
                    "Notify board of directors",
                    "Prepare customer communications",
                    "Brief key stakeholders"
                ],
                "follow_up": [
                    "Daily executive briefings",
                    "Board updates every 12 hours",
                    "Post-incident review required"
                ],
                "confidence": 0.95
            }
        else:
            decision = {
                "action": "standard_escalation_response",
                "guidance": [
                    "Follow established escalation procedures",
                    "Ensure adequate resource allocation",
                    "Monitor progress closely"
                ],
                "resources": {
                    "budget_authorization": "$10,000",
                    "additional_staff": "limited",
                    "external_consultants": "if_required"
                },
                "communication": [
                    "Keep senior management informed",
                    "Prepare status updates for stakeholders"
                ],
                "follow_up": [
                    "Regular progress reports",
                    "Final resolution report required"
                ],
                "confidence": 0.85
            }
        
        return decision
    
    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generate executive dashboard with organizational metrics"""
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "organization_health": {
                "total_agents": len(self.subordinates),
                "active_escalations": self._count_active_escalations(),
                "average_response_time": self._calculate_org_response_time(),
                "success_rate": self._calculate_org_success_rate()
            },
            "financial_metrics": {
                "operational_costs": self._calculate_operational_costs(),
                "roi_improvement": self._calculate_roi_improvement(),
                "budget_utilization": self._calculate_budget_utilization()
            },
            "strategic_progress": {
                "initiatives_on_track": self._count_initiatives_on_track(),
                "key_milestones_achieved": self._count_milestones_achieved(),
                "risk_factors": self._identify_risk_factors()
            },
            "recommendations": self._generate_executive_recommendations()
        }
        
        return dashboard
    
    def _count_active_escalations(self) -> int:
        """Count currently active escalations"""
        return len([msg for msg in self.inbox if msg.message_type == MessageType.ESCALATION])
    
    def _calculate_org_response_time(self) -> float:
        """Calculate organization-wide average response time"""
        return 45.5  # minutes - placeholder
    
    def _calculate_org_success_rate(self) -> float:
        """Calculate organization-wide success rate"""
        return 92.3  # percentage - placeholder
    
    def _generate_executive_recommendations(self) -> List[str]:
        """Generate strategic recommendations"""
        return [
            "Continue investment in AI agent training",
            "Expand blockchain logging capabilities",
            "Implement advanced analytics for predictive insights",
            "Consider adding specialized compliance agents"
        ]