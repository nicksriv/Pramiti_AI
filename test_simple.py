#!/usr/bin/env python3
"""
Simple test version of the Agentic AI Organization
This version works without blockchain dependencies for initial testing
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simplified blockchain logger for testing
class TestCommunicationLogger:
    """Simple test logger that doesn't require blockchain dependencies"""
    
    def __init__(self):
        self.logs = []
        
    def initialize(self):
        print("✅ Test communication logger initialized")
        
    def log_communication(self, sender_id: str, recipient_id: str, 
                         message_type: str, metadata: Dict[str, Any]) -> str:
        log_entry = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "message_type": message_type,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.logs.append(log_entry)
        return f"log_{len(self.logs)}"
    
    def close(self):
        pass

def run_simple_test():
    """Run a simple test of the organization without full dependencies"""
    print("🧪 Running Simple Agentic AI Organization Test")
    print("=" * 50)
    
    try:
        # Import our modules
        from core.base_agent import BaseAgent, AgentRole, Message, MessageType
        
        print("✅ Core modules imported successfully")
        
        # Create test agents
        ceo = BaseAgent("ceo-001", "Test CEO", AgentRole.CEO, "executive_leadership")
        manager = BaseAgent("mgr-001", "Test Manager", AgentRole.SENIOR_MANAGER, "test_operations", "ceo-001")
        sme = BaseAgent("sme-001", "Test SME", AgentRole.SME, "test_specialist", "mgr-001")
        
        print("✅ Test agents created successfully")
        
        # Test message creation
        test_message = Message(
            message_id="test_msg_001",
            sender_id=sme.agent_id,
            recipient_id=manager.agent_id,
            message_type=MessageType.ESCALATION,
            content={"issue": "Test escalation", "priority": "high"}
        )
        
        print("✅ Test message created successfully")
        
        # Test message processing
        response = manager.process_message(test_message)
        
        if response:
            print("✅ Message processed and response generated")
        else:
            print("✅ Message processed (no response needed)")
        
        # Test agent status
        status = sme.get_status()
        print(f"✅ Agent status retrieved: {status['name']} - {status['role']}")
        
        print("\n🎉 Simple test completed successfully!")
        print("The core agent system is working properly.")
        print("\nNext steps:")
        print("1. Run 'python setup.py' to complete full setup")
        print("2. Install dependencies with 'pip install -r requirements.txt'")
        print("3. Run 'python main.py' for the full experience")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)