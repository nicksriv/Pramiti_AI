from web3 import Web3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib
import uuid
from core.base_agent import Message, MessageType

@dataclass
class BlockchainTransaction:
    transaction_id: str
    block_number: Optional[int] = None
    transaction_hash: Optional[str] = None
    gas_used: Optional[int] = None
    status: str = "pending"  # pending, confirmed, failed
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class CommunicationLogger:
    """
    Blockchain-based communication logger for all A2A (Agent-to-Agent) communications.
    Ensures immutable audit trails and transparent decision-making processes.
    """
    
    def __init__(self, web3_provider_url: str = None, contract_address: str = None):
        # For development, we'll simulate blockchain operations
        # In production, connect to actual blockchain network
        self.web3_provider_url = web3_provider_url or "http://localhost:8545"
        self.contract_address = contract_address
        self.web3 = None
        self.contract = None
        
        # Local storage for development/testing
        self.local_blockchain: List[Dict[str, Any]] = []
        self.transaction_pool: List[Dict[str, Any]] = []
        
        if web3_provider_url:
            self._initialize_web3_connection()
    
    def _initialize_web3_connection(self):
        """Initialize Web3 connection to blockchain network"""
        try:
            self.web3 = Web3(Web3.HTTPProvider(self.web3_provider_url))
            if self.web3.is_connected():
                print(f"Connected to blockchain network at {self.web3_provider_url}")
            else:
                print("Failed to connect to blockchain network")
                self.web3 = None
        except Exception as e:
            print(f"Error connecting to blockchain: {e}")
            self.web3 = None
    
    def log_message(self, message: Message, additional_metadata: Dict[str, Any] = None) -> BlockchainTransaction:
        """
        Log agent-to-agent message to blockchain for immutable audit trail
        """
        # Create blockchain entry
        blockchain_entry = {
            "entry_id": str(uuid.uuid4()),
            "message_id": message.id,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "message_type": message.message_type.value,
            "content_hash": self._hash_content(message.content),
            "timestamp": message.timestamp.isoformat(),
            "priority": message.priority,
            "metadata": {
                **message.metadata,
                **(additional_metadata or {})
            },
            "block_number": len(self.local_blockchain) + 1,
            "previous_hash": self._get_previous_hash()
        }
        
        # Calculate entry hash
        blockchain_entry["entry_hash"] = self._hash_entry(blockchain_entry)
        
        # Create transaction
        transaction = BlockchainTransaction(
            transaction_id=blockchain_entry["entry_id"],
            block_number=blockchain_entry["block_number"],
            status="confirmed",
            timestamp=message.timestamp
        )
        
        if self.web3 and self.contract:
            # Actual blockchain transaction
            tx_hash = self._write_to_blockchain(blockchain_entry)
            transaction.transaction_hash = tx_hash
        else:
            # Simulated blockchain for development
            self.local_blockchain.append(blockchain_entry)
            transaction.transaction_hash = blockchain_entry["entry_hash"]
        
        return transaction
    
    def log_decision(self, agent_id: str, decision_context: Dict[str, Any], 
                    decision_outcome: Dict[str, Any]) -> BlockchainTransaction:
        """
        Log agent decision-making process to blockchain
        """
        decision_entry = {
            "entry_id": str(uuid.uuid4()),
            "type": "agent_decision",
            "agent_id": agent_id,
            "decision_context_hash": self._hash_content(decision_context),
            "decision_outcome_hash": self._hash_content(decision_outcome),
            "timestamp": datetime.now().isoformat(),
            "block_number": len(self.local_blockchain) + 1,
            "previous_hash": self._get_previous_hash(),
            "metadata": {
                "decision_type": decision_outcome.get("type", "unknown"),
                "confidence_score": decision_outcome.get("confidence", 0.0),
                "reasoning_steps": len(decision_outcome.get("reasoning", []))
            }
        }
        
        decision_entry["entry_hash"] = self._hash_entry(decision_entry)
        
        transaction = BlockchainTransaction(
            transaction_id=decision_entry["entry_id"],
            block_number=decision_entry["block_number"],
            status="confirmed",
            timestamp=datetime.now()
        )
        
        self.local_blockchain.append(decision_entry)
        transaction.transaction_hash = decision_entry["entry_hash"]
        
        return transaction
    
    def get_communication_history(self, agent_id: str, 
                                 start_time: datetime = None, 
                                 end_time: datetime = None) -> List[Dict[str, Any]]:
        """
        Retrieve communication history for specific agent
        """
        history = []
        for entry in self.local_blockchain:
            if entry.get("sender_id") == agent_id or entry.get("recipient_id") == agent_id:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                
                if start_time and entry_time < start_time:
                    continue
                if end_time and entry_time > end_time:
                    continue
                
                history.append(entry)
        
        return sorted(history, key=lambda x: x["timestamp"])
    
    def get_audit_trail(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete audit trail for specific message
        """
        for entry in self.local_blockchain:
            if entry.get("message_id") == message_id:
                return entry
        return None
    
    def verify_blockchain_integrity(self) -> bool:
        """
        Verify the integrity of the blockchain
        """
        for i, entry in enumerate(self.local_blockchain):
            if i == 0:
                continue
            
            expected_previous_hash = self.local_blockchain[i-1]["entry_hash"]
            if entry["previous_hash"] != expected_previous_hash:
                return False
            
            # Verify entry hash
            entry_copy = entry.copy()
            stored_hash = entry_copy.pop("entry_hash")
            calculated_hash = self._hash_entry(entry_copy)
            
            if stored_hash != calculated_hash:
                return False
        
        return True
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate compliance report for specified date range
        """
        filtered_entries = [
            entry for entry in self.local_blockchain
            if start_date <= datetime.fromisoformat(entry["timestamp"]) <= end_date
        ]
        
        report = {
            "report_id": str(uuid.uuid4()),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_communications": len(filtered_entries),
            "communication_breakdown": {},
            "agent_activity": {},
            "decision_audit": [],
            "integrity_status": self.verify_blockchain_integrity(),
            "generated_at": datetime.now().isoformat()
        }
        
        # Analyze communication patterns
        for entry in filtered_entries:
            msg_type = entry.get("message_type", "unknown")
            report["communication_breakdown"][msg_type] = report["communication_breakdown"].get(msg_type, 0) + 1
            
            # Track agent activity
            sender = entry.get("sender_id")
            if sender:
                if sender not in report["agent_activity"]:
                    report["agent_activity"][sender] = {"sent": 0, "received": 0, "decisions": 0}
                report["agent_activity"][sender]["sent"] += 1
            
            recipient = entry.get("recipient_id")
            if recipient:
                if recipient not in report["agent_activity"]:
                    report["agent_activity"][recipient] = {"sent": 0, "received": 0, "decisions": 0}
                report["agent_activity"][recipient]["received"] += 1
            
            # Track decisions
            if entry.get("type") == "agent_decision":
                agent_id = entry.get("agent_id")
                if agent_id:
                    report["agent_activity"][agent_id]["decisions"] += 1
                    report["decision_audit"].append({
                        "agent_id": agent_id,
                        "timestamp": entry["timestamp"],
                        "decision_type": entry["metadata"].get("decision_type"),
                        "confidence_score": entry["metadata"].get("confidence_score")
                    })
        
        return report
    
    def _hash_content(self, content: Any) -> str:
        """Create hash of message content"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _hash_entry(self, entry: Dict[str, Any]) -> str:
        """Create hash of blockchain entry"""
        # Remove hash fields for calculation
        entry_copy = entry.copy()
        entry_copy.pop("entry_hash", None)
        entry_str = json.dumps(entry_copy, sort_keys=True, default=str)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    def _get_previous_hash(self) -> str:
        """Get hash of previous block"""
        if not self.local_blockchain:
            return "0" * 64  # Genesis block
        return self.local_blockchain[-1]["entry_hash"]
    
    def _write_to_blockchain(self, entry: Dict[str, Any]) -> str:
        """
        Write entry to actual blockchain (placeholder for real implementation)
        """
        # This would contain actual smart contract interaction
        # For now, return simulated transaction hash
        return self._hash_entry(entry)
    
    def export_blockchain(self) -> List[Dict[str, Any]]:
        """Export entire blockchain for backup/analysis"""
        return self.local_blockchain.copy()
    
    def import_blockchain(self, blockchain_data: List[Dict[str, Any]]) -> bool:
        """Import blockchain data (for restoration/migration)"""
        try:
            self.local_blockchain = blockchain_data.copy()
            return self.verify_blockchain_integrity()
        except Exception as e:
            print(f"Error importing blockchain: {e}")
            return False