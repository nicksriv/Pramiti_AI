#!/usr/bin/env python3
"""
Agentic AI Organization - Main Application
A sophisticated multi-agent AI system with hierarchical structure and blockchain logging
"""

import asyncio
import time
import signal
import sys
from typing import Dict, List, Any
from datetime import datetime
import json
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.base_agent import Message, MessageType
from core.blockchain_logger import CommunicationLogger
from core.communication_orchestrator import CommunicationOrchestrator, AgentFactory
from agents.itsm_agents import IncidentManagementAgent, ProblemManagementAgent, ChangeManagementAgent
from agents.management_agents import SeniorManager, CEOAgent

class AgenticAIOrganization:
    """
    Main application class for the Agentic AI Organization
    """
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.blockchain_logger = CommunicationLogger()
        self.orchestrator = CommunicationOrchestrator(self.blockchain_logger)
        self.agents = {}
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "organization": {
                "name": "Agentic AI ITSM Organization",
                "description": "AI-powered ITSM organization with hierarchical agent structure",
                "domain": "itsm",
                "version": "1.0.0"
            },
            "agents": {
                "ceo": {
                    "name": "Executive AI Director",
                    "id": "ceo-001"
                },
                "senior_managers": [
                    {
                        "name": "ITSM Operations Manager",
                        "id": "sm-itsm-001",
                        "specialization": "ITSM Operations",
                        "team_size": 6
                    }
                ],
                "sme_agents": [
                    {
                        "name": "Incident Response Specialist",
                        "id": "sme-incident-001",
                        "specialization": "incident_management",
                        "manager_id": "sm-itsm-001"
                    },
                    {
                        "name": "Incident Analysis Expert",
                        "id": "sme-incident-002",
                        "specialization": "incident_management",
                        "manager_id": "sm-itsm-001"
                    },
                    {
                        "name": "Problem Resolution Specialist",
                        "id": "sme-problem-001",
                        "specialization": "problem_management",
                        "manager_id": "sm-itsm-001"
                    },
                    {
                        "name": "Problem Analysis Expert",
                        "id": "sme-problem-002",
                        "specialization": "problem_management",
                        "manager_id": "sm-itsm-001"
                    },
                    {
                        "name": "Change Coordinator",
                        "id": "sme-change-001",
                        "specialization": "change_management",
                        "manager_id": "sm-itsm-001"
                    },
                    {
                        "name": "Change Approval Specialist",
                        "id": "sme-change-002",
                        "specialization": "change_management",
                        "manager_id": "sm-itsm-001"
                    }
                ]
            },
            "blockchain": {
                "network": "development",
                "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
                "gas_limit": 500000
            },
            "performance": {
                "max_queue_size": 100,
                "processing_timeout": 300,
                "conversation_cleanup_hours": 24
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._deep_merge(default_config, loaded_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                print("Using default configuration")
        
        return default_config
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Deep merge two dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def initialize_organization(self):
        """Initialize the complete agent organization"""
        print("🤖 Initializing Agentic AI Organization...")
        print("=" * 50)
        
        # 1. Create and register CEO
        ceo_config = self.config["agents"]["ceo"]
        ceo = AgentFactory.create_ceo_agent(
            ceo_config["id"],
            ceo_config["name"]
        )
        self.orchestrator.register_agent(ceo)
        self.agents[ceo.agent_id] = ceo
        print(f"✓ Created CEO: {ceo.name}")
        
        # 2. Create and register Senior Managers
        for sm_config in self.config["agents"]["senior_managers"]:
            senior_manager = AgentFactory.create_senior_manager(
                sm_config["id"],
                sm_config["name"],
                sm_config["specialization"],
                ceo_config["id"]
            )
            self.orchestrator.register_agent(senior_manager)
            self.agents[senior_manager.agent_id] = senior_manager
            print(f"✓ Created Senior Manager: {senior_manager.name}")
        
        # 3. Create and register SME agents
        for sme_config in self.config["agents"]["sme_agents"]:
            sme_agent = AgentFactory.create_itsm_sme_agent(
                sme_config["id"],
                sme_config["name"],
                sme_config["specialization"],
                sme_config["manager_id"]
            )
            self.orchestrator.register_agent(sme_agent)
            self.agents[sme_agent.agent_id] = sme_agent
            
            # Add to manager's team
            manager = self.agents.get(sme_config["manager_id"])
            if manager and hasattr(manager, 'add_subordinate'):
                manager.add_subordinate(sme_agent.agent_id)
            
            print(f"✓ Created SME Agent: {sme_agent.name} ({sme_agent.specialization})")
        
        # 4. Initialize blockchain logging
        try:
            self.blockchain_logger.initialize()
            print("✓ Blockchain logging system initialized")
        except Exception as e:
            print(f"⚠ Blockchain initialization failed: {e}")
            print("  Continuing with local logging only")
        
        print(f"\n🎉 Organization initialized with {len(self.agents)} agents")
        self._print_organization_structure()
    
    def _print_organization_structure(self):
        """Print the organizational hierarchy"""
        print("\n📋 Organizational Structure:")
        print("=" * 50)
        
        # Find CEO
        ceo = next((agent for agent in self.agents.values() 
                   if agent.role.value == "ceo"), None)
        
        if ceo:
            print(f"🏢 CEO: {ceo.name}")
            
            # Find Senior Managers
            managers = [agent for agent in self.agents.values() 
                       if agent.role.value == "senior_manager"]
            
            for manager in managers:
                print(f"  └── 👔 {manager.name} ({manager.specialization})")
                
                # Find SMEs under this manager
                smes = [agent for agent in self.agents.values() 
                       if hasattr(agent, 'manager_id') and agent.manager_id == manager.agent_id]
                
                for i, sme in enumerate(smes):
                    connector = "├──" if i < len(smes) - 1 else "└──"
                    print(f"      {connector} 🔧 {sme.name} ({sme.specialization})")
    
    def start(self):
        """Start the organization"""
        if self.running:
            print("Organization is already running")
            return
        
        print("\n🚀 Starting Agentic AI Organization...")
        
        # Start message processing
        self.orchestrator.start_processing()
        
        self.running = True
        print("✅ Organization is now operational!")
        
        # Display real-time status
        self._run_status_display()
    
    def _run_status_display(self):
        """Run real-time status display"""
        try:
            while self.running:
                # Clear screen and show status
                self._clear_screen()
                self._display_status()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            self.stop()
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _display_status(self):
        """Display current system status"""
        status = self.orchestrator.get_system_status()
        
        print("🤖 AGENTIC AI ORGANIZATION - LIVE STATUS")
        print("=" * 60)
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 System Health: {status['system_health'].upper()}")
        print(f"👥 Total Agents: {status['total_agents']}")
        print(f"💬 Active Conversations: {status['active_conversations']}")
        
        # Processing statistics
        stats = status['processing_stats']
        print(f"\n📊 Processing Statistics:")
        print(f"  • Messages Processed: {stats['messages_processed']}")
        print(f"  • Messages Failed: {stats['messages_failed']}")
        print(f"  • Avg Processing Time: {stats['average_processing_time']:.2f}s")
        
        # Queue status
        print(f"\n📬 Message Queues:")
        for agent_id, queue_size in status['queue_sizes'].items():
            agent_name = self.agents[agent_id].name if agent_id in self.agents else agent_id
            indicator = "🔴" if queue_size > 10 else "🟡" if queue_size > 5 else "🟢"
            print(f"  {indicator} {agent_name[:30]:30} | Queue: {queue_size:3d}")
        
        print(f"\n💡 Press Ctrl+C to shutdown gracefully")
    
    def stop(self):
        """Stop the organization"""
        if not self.running:
            return
        
        print("\n🛑 Shutting down Agentic AI Organization...")
        
        self.running = False
        
        # Stop message processing
        self.orchestrator.stop_processing()
        
        # Close blockchain connections
        try:
            self.blockchain_logger.close()
        except Exception as e:
            print(f"Warning: Blockchain cleanup failed: {e}")
        
        print("✅ Organization shutdown complete")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"\n📡 Received signal {signum}")
        self.stop()
        sys.exit(0)
    
    def create_test_scenario(self):
        """Create a test scenario to demonstrate the system"""
        print("\n🧪 Creating test scenario...")
        
        # Find an incident management agent
        incident_agent = next((agent for agent in self.agents.values() 
                             if isinstance(agent, IncidentManagementAgent)), None)
        
        if not incident_agent:
            print("No incident management agent found")
            return
        
        # Create a test incident
        test_incident = {
            "id": "INC-2024-001",
            "title": "Database Performance Degradation",
            "description": "Users reporting slow response times in the customer portal",
            "severity": "high",
            "affected_users": 150,
            "affected_systems": ["customer-portal", "user-database", "api-gateway"],
            "reported_by": "monitoring-system",
            "priority": 3
        }
        
        # Create escalation message
        escalation_message = Message(
            message_id=f"msg-{int(time.time())}",
            sender_id=incident_agent.agent_id,
            recipient_id=None,  # Will be routed automatically
            message_type=MessageType.ESCALATION,
            content={
                "issue": test_incident,
                "escalation_reason": "Complexity exceeds SME capabilities",
                "attempted_solutions": [
                    "Checked database performance metrics",
                    "Reviewed recent changes", 
                    "Analyzed error logs"
                ],
                "recommendation": "Requires senior management coordination"
            },
            priority=3
        )
        
        # Send the escalation
        success = self.orchestrator.send_message(escalation_message)
        
        if success:
            print(f"✅ Test escalation sent from {incident_agent.name}")
            print("   Watch the status display to see message processing...")
            time.sleep(2)
        else:
            print("❌ Failed to send test escalation")
    
    def generate_reports(self):
        """Generate organizational reports"""
        print("\n📈 Generating Reports...")
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        # CEO Dashboard
        ceo = next((agent for agent in self.agents.values() 
                   if isinstance(agent, CEOAgent)), None)
        
        if ceo:
            dashboard = ceo.generate_executive_dashboard()
            print("📊 Executive Dashboard generated")
            
            # Save to file
            report_file = f"reports/executive_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(dashboard, f, indent=2)
            print(f"   Saved to: {report_file}")
        
        # Senior Manager Reports
        managers = [agent for agent in self.agents.values() 
                   if isinstance(agent, SeniorManager)]
        
        for manager in managers:
            if hasattr(manager, 'generate_team_report'):
                try:
                    report = manager.generate_team_report()
                    print(f"📋 Team report generated for {manager.name}")
                    
                    # Save to file
                    report_file = f"reports/team_report_{manager.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(report_file, 'w') as f:
                        json.dump(report, f, indent=2)
                    print(f"   Saved to: {report_file}")
                except Exception as e:
                    print(f"❌ Failed to generate report for {manager.name}: {e}")
        
        # System status report
        system_status = self.orchestrator.get_system_status()
        status_file = f"reports/system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(status_file, 'w') as f:
            json.dump(system_status, f, indent=2)
        print(f"🔧 System status report saved to: {status_file}")

def main():
    """Main entry point"""
    print("🤖 Welcome to Agentic AI Organization")
    print("=====================================")
    
    # Create the organization
    config_file = "config.json" if os.path.exists("config.json") else None
    org = AgenticAIOrganization(config_file)
    
    try:
        # Initialize the organization
        org.initialize_organization()
        
        # Interactive menu
        while True:
            print("\nWhat would you like to do?")
            print("1. Start the organization")
            print("2. Create test scenario")
            print("3. Generate reports")
            print("4. Show current status")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                org.start()
                break
            elif choice == "2":
                if not org.running:
                    print("Organization must be running to create test scenarios.")
                    print("Please start the organization first (option 1).")
                else:
                    org.create_test_scenario()
            elif choice == "3":
                org.generate_reports()
            elif choice == "4":
                if org.running:
                    status = org.orchestrator.get_system_status()
                    print("\n📊 Current System Status:")
                    print(f"Total Agents: {status['total_agents']}")
                    print(f"System Health: {status['system_health']}")
                    print(f"Messages Processed: {status['processing_stats']['messages_processed']}")
                    print(f"Active Conversations: {status['active_conversations']}")
                else:
                    print("Organization is not running. Start it first to see status.")
            elif choice == "5":
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        org.stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        org.stop()

if __name__ == "__main__":
    main()