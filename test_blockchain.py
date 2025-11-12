#!/usr/bin/env python3
"""
Blockchain Logging Test Script for Agentic AI Organization
Tests the blockchain communication logging functionality
"""

import sys
import os

# Change to the correct path for the agentic-ai-org directory
agentic_ai_org_path = '/Users/nikhilsrivastava/Documents/GitHub/VSCode/Pramiti_AI/agentic-ai-org'
if os.path.exists(agentic_ai_org_path):
    sys.path.append(agentic_ai_org_path)
    from core.blockchain_logger import CommunicationLogger, BlockchainTransaction
    from core.base_agent import Message, MessageType
else:
    # Try to import from current directory structure
    try:
        from core.blockchain_logger import CommunicationLogger, BlockchainTransaction
        from core.base_agent import Message, MessageType
    except ImportError:
        print("❌ Could not import blockchain modules. Please check the file paths.")
        sys.exit(1)
from datetime import datetime, timedelta
import json
import uuid

class BlockchainTester:
    """Test class for blockchain logging functionality"""
    
    def __init__(self):
        self.logger = CommunicationLogger()
        self.test_results = []
        print("🚀 Initializing Blockchain Logging Test Suite")
        print("=" * 60)
    
    def test_message_logging(self):
        """Test logging of agent-to-agent messages"""
        print("\n📝 Test 1: Message Logging")
        print("-" * 30)
        
        # Create test message
        test_message = Message(
            sender_id="ceo-001",
            recipient_id="manager-001", 
            content="Please review the incident report for INC-2024-001",
            message_type=MessageType.REQUEST,
            priority=2
        )
        
        # Log message to blockchain
        transaction = self.logger.log_message(test_message)
        
        print(f"✓ Message logged with transaction ID: {transaction.transaction_id}")
        print(f"✓ Transaction hash: {transaction.transaction_hash[:16]}...")
        print(f"✓ Block number: {transaction.block_number}")
        print(f"✓ Status: {transaction.status}")
        
        # Verify message in blockchain
        audit_trail = self.logger.get_audit_trail(test_message.id)
        if audit_trail:
            print(f"✓ Message found in blockchain audit trail")
            self.test_results.append("PASS: Message logging")
            return True
        else:
            print("❌ Message not found in blockchain")
            self.test_results.append("FAIL: Message logging")
            return False
    
    def test_decision_logging(self):
        """Test logging of agent decisions"""
        print("\n🧠 Test 2: Decision Logging")
        print("-" * 30)
        
        decision_context = {
            "incident_id": "INC-2024-001",
            "severity": "high",
            "affected_services": ["email", "crm"],
            "user_reports": 45
        }
        
        decision_outcome = {
            "type": "escalation",
            "action": "escalate_to_senior_manager",
            "confidence": 0.85,
            "reasoning": [
                "High severity incident affecting multiple services",
                "User impact exceeds threshold (>40 users)",
                "Requires senior management coordination"
            ]
        }
        
        # Log decision to blockchain
        transaction = self.logger.log_decision("agent-incident-001", decision_context, decision_outcome)
        
        print(f"✓ Decision logged with transaction ID: {transaction.transaction_id}")
        print(f"✓ Transaction hash: {transaction.transaction_hash[:16]}...")
        print(f"✓ Block number: {transaction.block_number}")
        
        self.test_results.append("PASS: Decision logging")
        return True
    
    def test_communication_history(self):
        """Test retrieval of communication history"""
        print("\n📚 Test 3: Communication History")
        print("-" * 30)
        
        # Log multiple messages
        agents = ["ceo-001", "manager-001", "agent-incident-001", "agent-problem-001"]
        message_count = 0
        
        for i in range(5):
            sender = agents[i % len(agents)]
            recipient = agents[(i + 1) % len(agents)]
            
            test_message = Message(
                sender_id=sender,
                recipient_id=recipient,
                content=f"Test communication #{i+1}",
                message_type=MessageType.NOTIFICATION
            )
            
            self.logger.log_message(test_message)
            message_count += 1
        
        print(f"✓ Logged {message_count} test messages")
        
        # Retrieve history for specific agent
        history = self.logger.get_communication_history("ceo-001")
        print(f"✓ Retrieved {len(history)} messages for CEO agent")
        
        if len(history) > 0:
            print(f"✓ Latest message timestamp: {history[-1]['timestamp']}")
            self.test_results.append("PASS: Communication history")
            return True
        else:
            print("❌ No communication history found")
            self.test_results.append("FAIL: Communication history")
            return False
    
    def test_blockchain_integrity(self):
        """Test blockchain integrity verification"""
        print("\n🔐 Test 4: Blockchain Integrity")
        print("-" * 30)
        
        # Verify blockchain integrity
        integrity_status = self.logger.verify_blockchain_integrity()
        
        if integrity_status:
            print("✓ Blockchain integrity verified - all hashes are valid")
            print("✓ Chain of trust is maintained")
            self.test_results.append("PASS: Blockchain integrity")
            return True
        else:
            print("❌ Blockchain integrity check failed")
            self.test_results.append("FAIL: Blockchain integrity")
            return False
    
    def test_compliance_report(self):
        """Test compliance report generation"""
        print("\n📊 Test 5: Compliance Report Generation")
        print("-" * 30)
        
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now()
        
        report = self.logger.generate_compliance_report(start_date, end_date)
        
        print(f"✓ Compliance report generated")
        print(f"✓ Report ID: {report['report_id']}")
        print(f"✓ Total communications: {report['total_communications']}")
        print(f"✓ Agent activity tracked: {len(report['agent_activity'])} agents")
        print(f"✓ Integrity status: {report['integrity_status']}")
        
        # Display communication breakdown
        if report['communication_breakdown']:
            print("✓ Communication breakdown:")
            for msg_type, count in report['communication_breakdown'].items():
                print(f"    - {msg_type}: {count}")
        
        self.test_results.append("PASS: Compliance report")
        return True
    
    def test_blockchain_export_import(self):
        """Test blockchain export/import functionality"""
        print("\n💾 Test 6: Blockchain Export/Import")
        print("-" * 30)
        
        # Export blockchain
        exported_data = self.logger.export_blockchain()
        print(f"✓ Exported blockchain with {len(exported_data)} blocks")
        
        # Create new logger and import data
        new_logger = CommunicationLogger()
        import_success = new_logger.import_blockchain(exported_data)
        
        if import_success:
            print("✓ Blockchain imported successfully")
            print("✓ Integrity verified after import")
            self.test_results.append("PASS: Export/Import")
            return True
        else:
            print("❌ Blockchain import failed")
            self.test_results.append("FAIL: Export/Import")
            return False
    
    def display_blockchain_contents(self):
        """Display current blockchain contents"""
        print("\n🔗 Current Blockchain Contents")
        print("=" * 60)
        
        blockchain_data = self.logger.export_blockchain()
        
        for i, block in enumerate(blockchain_data[-5:]):  # Show last 5 blocks
            print(f"\nBlock #{block['block_number']}:")
            print(f"  Entry ID: {block['entry_id']}")
            print(f"  Type: {block.get('type', 'message')}")
            
            if 'sender_id' in block:
                print(f"  Sender: {block['sender_id']}")
                print(f"  Recipient: {block['recipient_id']}")
                print(f"  Message Type: {block['message_type']}")
            elif 'agent_id' in block:
                print(f"  Agent: {block['agent_id']}")
                print(f"  Decision Type: {block['metadata'].get('decision_type')}")
            
            print(f"  Timestamp: {block['timestamp']}")
            print(f"  Hash: {block['entry_hash'][:16]}...")
            print(f"  Previous Hash: {block['previous_hash'][:16]}...")
    
    def run_all_tests(self):
        """Run all blockchain tests"""
        print("🧪 Running Blockchain Logging Test Suite")
        print("🔗 Testing immutable communication audit trails")
        
        tests = [
            self.test_message_logging,
            self.test_decision_logging,
            self.test_communication_history,
            self.test_blockchain_integrity,
            self.test_compliance_report,
            self.test_blockchain_export_import
        ]
        
        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                self.test_results.append(f"ERROR: {test.__name__}")
        
        # Display blockchain contents
        self.display_blockchain_contents()
        
        # Summary
        print(f"\n📋 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(tests) - passed_tests}")
        
        print(f"\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result.startswith("PASS") else "❌"
            print(f"  {status} {result}")
        
        if passed_tests == len(tests):
            print(f"\n🎉 All tests passed! Blockchain logging is fully functional.")
        else:
            print(f"\n⚠️  Some tests failed. Check the results above.")
        
        return passed_tests == len(tests)

def main():
    """Main function to run blockchain tests"""
    print("🔗 Agentic AI Organization - Blockchain Logging Test")
    print("📍 Testing immutable audit trails for agent communications")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = BlockchainTester()
    success = tester.run_all_tests()
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🚀 Blockchain logging system is ready for production!")
    else:
        print("🔧 Some issues found. Please review the test results.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())