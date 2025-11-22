"""
Enterprise RAG (Retrieval-Augmented Generation) System for Pramiti AI
Tenant-specific knowledge base with self-learning from user interactions

Features:
- Vector database for semantic search (ChromaDB)
- Conversation memory with embeddings
- User feedback collection (thumbs up/down)
- Confidence scoring based on past interactions
- Per-tenant knowledge isolation
- Automatic learning from successful interactions
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib

# Vector database
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not installed. Install: pip install chromadb")

# OpenAI for embeddings
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Install: pip install openai")

from core.security_audit import security_audit, SecurityEventType


class RAGKnowledgeBase:
    """
    Tenant-specific RAG knowledge base with self-learning
    
    Architecture:
    1. Vector Store: ChromaDB for semantic search
    2. Embeddings: OpenAI text-embedding-ada-002
    3. Conversation History: Per-tenant storage
    4. Feedback Loop: User ratings improve future responses
    5. Confidence Scoring: Based on past success rates
    """
    
    def __init__(
        self,
        data_dir: str = "data/rag",
        embedding_model: str = "text-embedding-ada-002"
    ):
        """
        Initialize RAG knowledge base
        
        Args:
            data_dir: Directory for vector database and conversation history
            embedding_model: OpenAI embedding model to use
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.openai_client = None
        
        # Initialize ChromaDB
        if CHROMADB_AVAILABLE:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.data_dir / "chroma"),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        else:
            self.chroma_client = None
        
        # Conversation history storage
        self.conversations_dir = self.data_dir / "conversations"
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Feedback storage
        self.feedback_dir = self.data_dir / "feedback"
        self.feedback_dir.mkdir(exist_ok=True)
    
    # ==================== COLLECTION MANAGEMENT ====================
    
    def get_or_create_collection(self, org_id: str) -> Any:
        """
        Get or create ChromaDB collection for organization
        
        Args:
            org_id: Organization ID
            
        Returns:
            ChromaDB collection
        """
        if not self.chroma_client:
            raise RuntimeError("ChromaDB not available")
        
        collection_name = f"kb_{org_id}".replace("-", "_")
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={
                    "org_id": org_id,
                    "created_at": datetime.utcnow().isoformat()
                }
            )
        
        return collection
    
    # ==================== EMBEDDINGS ====================
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions for ada-002)
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available")
        
        # Clean and truncate text
        text = text.strip()
        if len(text) > 8000:  # Token limit consideration
            text = text[:8000]
        
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        
        return response.data[0].embedding
    
    # ==================== CONVERSATION STORAGE ====================
    
    def store_conversation(
        self,
        org_id: str,
        user_id: str,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store conversation with embedding for future retrieval
        
        Args:
            org_id: Organization ID
            user_id: User ID
            conversation_id: Unique conversation ID
            user_message: User's message
            ai_response: AI's response
            metadata: Optional metadata (agent, timestamp, etc.)
            
        Returns:
            Document ID in vector store
        """
        collection = self.get_or_create_collection(org_id)
        
        # Create document combining question and answer
        combined_text = f"Question: {user_message}\nAnswer: {ai_response}"
        
        # Generate embedding
        embedding = self.get_embedding(combined_text)
        
        # Generate unique document ID
        doc_id = hashlib.sha256(
            f"{org_id}:{conversation_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Prepare metadata
        doc_metadata = {
            "org_id": org_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message[:500],  # Truncate for metadata
            "ai_response": ai_response[:500],
            "rating": 0,  # Will be updated with feedback
            "helpful": False,
            **(metadata or {})
        }
        
        # Store in ChromaDB
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[doc_metadata]
        )
        
        # Also store full conversation in JSON
        self._store_conversation_json(
            org_id, conversation_id, user_message, ai_response, doc_id, metadata
        )
        
        # Audit log
        security_audit.log_event(
            SecurityEventType.DATA_EXPORTED,  # Using closest available
            user_id=user_id,
            org_id=org_id,
            details={
                "action": "conversation_stored",
                "conversation_id": conversation_id,
                "doc_id": doc_id
            }
        )
        
        return doc_id
    
    def _store_conversation_json(
        self,
        org_id: str,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        doc_id: str,
        metadata: Optional[Dict] = None
    ):
        """Store full conversation in JSON file"""
        org_conv_dir = self.conversations_dir / org_id
        org_conv_dir.mkdir(exist_ok=True)
        
        conv_file = org_conv_dir / f"{conversation_id}.json"
        
        # Load existing or create new
        if conv_file.exists():
            with open(conv_file, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "conversation_id": conversation_id,
                "org_id": org_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": []
            }
        
        # Append message
        data["messages"].append({
            "doc_id": doc_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response,
            "rating": None,
            "feedback": None,
            "metadata": metadata or {}
        })
        
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Save
        with open(conv_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ==================== SEMANTIC SEARCH ====================
    
    def search_similar_conversations(
        self,
        org_id: str,
        query: str,
        top_k: int = 5,
        min_rating: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar past conversations using semantic search
        
        Args:
            org_id: Organization ID
            query: User's current query
            top_k: Number of results to return
            min_rating: Minimum rating filter (e.g., only positive feedback)
            
        Returns:
            List of similar conversations with metadata
        """
        collection = self.get_or_create_collection(org_id)
        
        # Generate query embedding
        query_embedding = self.get_embedding(query)
        
        # Build where filter - ChromaDB requires $and for multiple conditions
        if min_rating is not None:
            where_filter = {
                "$and": [
                    {"org_id": org_id},
                    {"rating": {"$gte": min_rating}}
                ]
            }
        else:
            where_filter = {"org_id": org_id}
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        similar_convs = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                similar_convs.append({
                    "doc_id": doc_id,
                    "distance": results['distances'][0][i] if results.get('distances') else 0,
                    "similarity": 1 - (results['distances'][0][i] if results.get('distances') else 0),
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "user_message": results['metadatas'][0][i].get('user_message', ''),
                    "ai_response": results['metadatas'][0][i].get('ai_response', ''),
                    "rating": results['metadatas'][0][i].get('rating', 0),
                    "helpful": results['metadatas'][0][i].get('helpful', False)
                })
        
        return similar_convs
    
    # ==================== CONTEXT RETRIEVAL ====================
    
    def get_relevant_context(
        self,
        org_id: str,
        query: str,
        max_context_length: int = 2000
    ) -> str:
        """
        Get relevant context from past conversations for RAG
        
        Args:
            org_id: Organization ID
            query: Current user query
            max_context_length: Maximum context length in characters
            
        Returns:
            Formatted context string for prompt injection
        """
        # Search for similar conversations (only helpful ones)
        similar_convs = self.search_similar_conversations(
            org_id=org_id,
            query=query,
            top_k=5,
            min_rating=1  # Only positive feedback
        )
        
        if not similar_convs:
            return ""
        
        # Build context from most relevant conversations
        context_parts = ["Here are similar questions I've answered before:\n"]
        current_length = len(context_parts[0])
        
        for conv in similar_convs:
            # Format: Q: ... A: ... (Rating: X, Similarity: Y%)
            conv_text = (
                f"\nQ: {conv['user_message']}\n"
                f"A: {conv['ai_response']}\n"
                f"(User rated this helpful, Similarity: {conv['similarity']*100:.1f}%)\n"
            )
            
            if current_length + len(conv_text) > max_context_length:
                break
            
            context_parts.append(conv_text)
            current_length += len(conv_text)
        
        return "".join(context_parts) if len(context_parts) > 1 else ""
    
    # ==================== FEEDBACK & LEARNING ====================
    
    def record_feedback(
        self,
        org_id: str,
        doc_id: str,
        user_id: str,
        rating: int,
        feedback_text: Optional[str] = None
    ):
        """
        Record user feedback for a conversation (self-learning)
        
        Args:
            org_id: Organization ID
            doc_id: Document ID from vector store
            user_id: User providing feedback
            rating: Rating (-1 for thumbs down, 0 for neutral, 1 for thumbs up)
            feedback_text: Optional text feedback
        """
        collection = self.get_or_create_collection(org_id)
        
        # Update vector store metadata
        try:
            collection.update(
                ids=[doc_id],
                metadatas=[{
                    "rating": rating,
                    "helpful": rating > 0,
                    "feedback_text": feedback_text or "",
                    "feedback_timestamp": datetime.utcnow().isoformat()
                }]
            )
        except Exception as e:
            print(f"⚠️  Failed to update feedback in vector store: {e}")
        
        # Store detailed feedback
        feedback_file = self.feedback_dir / org_id / f"{doc_id}.json"
        feedback_file.parent.mkdir(exist_ok=True)
        
        feedback_data = {
            "doc_id": doc_id,
            "org_id": org_id,
            "user_id": user_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        # Audit log
        security_audit.log_event(
            SecurityEventType.DATA_EXPORTED,
            user_id=user_id,
            org_id=org_id,
            details={
                "action": "feedback_recorded",
                "doc_id": doc_id,
                "rating": rating
            }
        )
    
    # ==================== ANALYTICS ====================
    
    def get_learning_stats(self, org_id: str) -> Dict[str, Any]:
        """
        Get learning statistics for organization
        
        Args:
            org_id: Organization ID
            
        Returns:
            Statistics dict with conversation count, ratings, etc.
        """
        collection = self.get_or_create_collection(org_id)
        
        # Get all documents
        results = collection.get()
        
        total_conversations = len(results['ids']) if results['ids'] else 0
        
        # Count ratings
        positive = 0
        negative = 0
        neutral = 0
        
        if results['metadatas']:
            for metadata in results['metadatas']:
                rating = metadata.get('rating', 0)
                if rating > 0:
                    positive += 1
                elif rating < 0:
                    negative += 1
                else:
                    neutral += 1
        
        return {
            "org_id": org_id,
            "total_conversations": total_conversations,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "neutral": neutral,
            "feedback_rate": (positive + negative) / max(total_conversations, 1) * 100,
            "satisfaction_rate": positive / max(positive + negative, 1) * 100 if (positive + negative) > 0 else 0
        }
    
    # ==================== ENHANCED RESPONSE GENERATION ====================
    
    def generate_rag_response(
        self,
        org_id: str,
        user_id: str,
        user_message: str,
        base_prompt: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate response using RAG with retrieved context
        
        Args:
            org_id: Organization ID
            user_id: User ID
            user_message: User's message
            base_prompt: Base system prompt
            conversation_id: Optional conversation ID
            
        Returns:
            Tuple of (ai_response, metadata with context info)
        """
        # Get relevant context from knowledge base
        context = self.get_relevant_context(org_id, user_message)
        
        # Build enhanced prompt
        if context:
            enhanced_prompt = f"{base_prompt}\n\n{context}\n\nBased on the above context and your knowledge, please answer the following question:"
        else:
            enhanced_prompt = base_prompt
        
        # Generate response using OpenAI
        if not self.openai_client:
            return "OpenAI not configured", {"context_used": False}
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            # Metadata about the generation
            metadata = {
                "context_used": bool(context),
                "context_length": len(context) if context else 0,
                "model": "gpt-4-turbo-preview",
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
            # Store conversation for future learning
            if conversation_id:
                self.store_conversation(
                    org_id=org_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    metadata=metadata
                )
            
            return ai_response, metadata
        
        except Exception as e:
            print(f"⚠️  Failed to generate RAG response: {e}")
            return f"Error generating response: {str(e)}", {"context_used": False, "error": str(e)}


# Global instance
rag_knowledge_base = RAGKnowledgeBase()
