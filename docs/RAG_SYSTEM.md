# RAG (Retrieval-Augmented Generation) Self-Learning System

## Overview

The Pramiti AI platform includes a comprehensive RAG system that enables **self-learning** from user interactions. The system stores conversations in a **vector database**, retrieves relevant context using **semantic search**, and improves over time based on **user feedback**.

## 🎯 Key Features

### 1. **Semantic Memory**
- All conversations are embedded using OpenAI's `text-embedding-ada-002` model (1536 dimensions)
- Stored in ChromaDB vector database for fast similarity search
- Retrieves relevant past conversations to provide context-aware responses

### 2. **Per-Tenant Isolation**
- Each organization has a separate ChromaDB collection: `kb_{org_id}`
- Ensures data privacy and regulatory compliance (GDPR, HIPAA)
- No cross-tenant data leakage

### 3. **Feedback-Driven Learning**
- Users rate responses with 👍 (thumbs up) or 👎 (thumbs down)
- Feedback stored in both vector metadata and conversation JSON
- System prioritizes context from highly-rated conversations

### 4. **Analytics & Insights**
- Track total conversations per organization
- Monitor satisfaction rate (% of positive feedback)
- Measure improvement over time

### 5. **Context Injection**
- Automatically retrieves top 3 most similar past conversations
- Injects context (max 2000 chars) into AI prompts
- Improves accuracy and confidence in responses

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│  (Frontend with thumbs up/down feedback buttons)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Endpoints                            │
│  • POST /api/v1/rag/chat      - Chat with RAG              │
│  • POST /api/v1/rag/feedback  - Submit feedback            │
│  • GET  /api/v1/rag/search    - Search knowledge base      │
│  • GET  /api/v1/rag/stats     - Learning statistics        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              RAGKnowledgeBase Class                         │
│  • generate_rag_response()    - Enhanced AI responses      │
│  • store_conversation()       - Save with embeddings       │
│  • search_similar_conversations() - Semantic search        │
│  • record_feedback()          - User ratings               │
│  • get_learning_stats()       - Analytics                  │
└────────┬───────────────────────┬────────────────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────────┐
│   ChromaDB       │    │  OpenAI Embeddings   │
│ (Vector Storage) │    │  (text-embedding-    │
│                  │    │   ada-002)           │
│ • Collections    │    │                      │
│   per tenant     │    │ • 1536 dimensions    │
│ • Persistent     │    │ • Semantic similarity│
│ • Metadata       │    │                      │
└──────────────────┘    └──────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Conversation JSON Files             │
│  data/rag/conversations/{org_id}/    │
│  • Full conversation history         │
│  • Feedback records                  │
│  • Metadata and timestamps           │
└──────────────────────────────────────┘
```

## 📦 Installation

### 1. Install Dependencies

```bash
pip install chromadb openai tiktoken
```

### 2. Configure OpenAI API Key

Add to `.env` file:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Initialize ChromaDB

The system auto-creates the vector database on first use:

```python
# Directory: data/rag/chromadb/
# Collections: kb_{org_id} (one per organization)
```

## 🚀 Usage

### API Examples

#### 1. Chat with RAG

```bash
curl -X POST http://localhost:8084/api/v1/rag/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Org-ID: acme_corp" \
  -H "X-User-ID: john@acme.com" \
  -d '{
    "message": "How do I configure Microsoft Teams integration?",
    "conversation_id": "conv_12345"
  }'
```

**Response:**
```json
{
  "success": true,
  "conversation_id": "conv_12345",
  "message": "To configure Microsoft Teams integration...",
  "metadata": {
    "context_used": true,
    "context_length": 1247,
    "model": "gpt-4-turbo-preview",
    "learning_enabled": true
  }
}
```

#### 2. Submit Feedback

```bash
curl -X POST http://localhost:8084/api/v1/rag/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Org-ID: acme_corp" \
  -H "X-User-ID: john@acme.com" \
  -d '{
    "doc_id": "abc123def456",
    "rating": 1,
    "feedback_text": "Very helpful, thank you!"
  }'
```

**Ratings:**
- `1` = 👍 Thumbs up (helpful)
- `0` = Neutral (no feedback)
- `-1` = 👎 Thumbs down (not helpful)

#### 3. Search Knowledge Base

```bash
curl -X GET "http://localhost:8084/api/v1/rag/search?query=slack%20integration&top_k=5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Org-ID: acme_corp" \
  -H "X-User-ID: john@acme.com"
```

**Response:**
```json
{
  "success": true,
  "query": "slack integration",
  "results_count": 3,
  "results": [
    {
      "user_message": "How do I set up Slack?",
      "ai_response": "To set up Slack integration...",
      "similarity": 0.92,
      "timestamp": "2024-01-15T10:30:00Z",
      "rating": 1
    }
  ]
}
```

#### 4. Get Learning Statistics

```bash
curl -X GET http://localhost:8084/api/v1/rag/stats \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Org-ID: acme_corp" \
  -H "X-User-ID: john@acme.com"
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_conversations": 247,
    "total_feedback": 189,
    "positive_feedback": 167,
    "negative_feedback": 22,
    "satisfaction_rate": 88.36,
    "avg_confidence": 0.87
  }
}
```

## 🧠 How RAG Learning Works

### 1. **Conversation Storage**

When a user sends a message:

1. Message is sent to the agent routing system
2. AI generates a response
3. Both user message and AI response are **embedded** using OpenAI
4. Conversation is stored in:
   - **ChromaDB** (vector database) with embeddings
   - **JSON file** (full conversation history)

### 2. **Context Retrieval**

When generating a new response:

1. User's question is embedded
2. System searches ChromaDB for **semantically similar** past conversations
3. Top 3 most relevant conversations retrieved (min similarity: 0.7)
4. Optionally filters by rating (e.g., only 👍 conversations)
5. Context injected into AI prompt

### 3. **Response Generation**

```python
# System prompt with injected context
prompt = f"""
You are Pramiti AI, an enterprise ITSM assistant.

RELEVANT PAST CONVERSATIONS:
{context_from_similar_conversations}

USER QUESTION: {user_message}

Provide a helpful, accurate response based on the context above.
"""
```

### 4. **Feedback Loop**

1. User rates response with 👍 or 👎
2. Rating stored in both:
   - Vector database metadata
   - Conversation JSON file
3. Future searches can prioritize highly-rated conversations
4. System learns which responses are most helpful

## 📊 Data Storage

### ChromaDB Collections

Each organization has a collection: `kb_{org_id}`

**Example:**
```
kb_acme_corp
kb_globex_inc
kb_initech_llc
```

**Metadata per document:**
```json
{
  "conversation_id": "conv_12345",
  "user_id": "john@acme.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "rating": 1,
  "user_message": "How do I set up Slack?",
  "ai_response": "To set up Slack integration...",
  "agent": "OAuth Assistant",
  "model": "gpt-4-turbo-preview"
}
```

### Conversation JSON Files

**Location:** `data/rag/conversations/{org_id}/{conversation_id}.json`

**Example:**
```json
{
  "conversation_id": "conv_12345",
  "org_id": "acme_corp",
  "user_id": "john@acme.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:15Z",
  "messages": [
    {
      "role": "user",
      "content": "How do I set up Slack?",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "To set up Slack integration...",
      "timestamp": "2024-01-15T10:30:05Z",
      "doc_id": "abc123def456",
      "rating": 1,
      "feedback_timestamp": "2024-01-15T10:32:15Z"
    }
  ],
  "metadata": {
    "agent": "OAuth Assistant",
    "routing_reason": "OAuth keywords detected"
  }
}
```

## 🎨 Frontend Integration

### HTML Interface

Open `web/rag-chat-interface.html` in a browser:

```bash
# Start the API server first
python api_server.py

# Then open in browser
http://localhost:8084/static/rag-chat-interface.html
```

### Features

- 💬 Real-time chat with RAG-enhanced AI
- 👍👎 Feedback buttons on every AI response
- 📊 Live learning statistics (conversations, satisfaction rate)
- 🎯 Visual indicators for RAG and context usage
- 🔒 Per-organization data isolation

### Feedback UI

Each AI message includes:

```html
<div class="feedback-buttons">
    <button onclick="submitFeedback(doc_id, 1)">👍 Helpful</button>
    <button onclick="submitFeedback(doc_id, -1)">👎 Not Helpful</button>
</div>
```

## 🔒 Security & Privacy

### 1. **Data Isolation**

- Each organization has a **separate ChromaDB collection**
- Cross-tenant queries are **blocked** at the API level
- Embeddings and conversations are **never shared** between orgs

### 2. **GDPR Compliance**

- **Right to Erasure:** Delete conversation endpoint available
- **Data Portability:** Export conversations in JSON format
- **Consent Management:** User opt-in/opt-out for learning

### 3. **Data Encryption**

- Conversations stored with **AES-256 encryption** (via `core.secrets_manager`)
- Vector embeddings are **non-reversible** (cannot reconstruct original text)
- Audit logs track all access to RAG data

### 4. **Authentication**

All RAG endpoints require:
- Valid JWT token
- Org ID verification
- User ID verification

## 📈 Performance Optimization

### 1. **Vector Search Speed**

- ChromaDB uses **HNSW algorithm** for fast approximate nearest neighbor search
- Typical query time: **< 50ms** for 10,000 documents
- Scales to **millions of conversations** per organization

### 2. **Embedding Costs**

- OpenAI `text-embedding-ada-002`: **$0.0001 per 1K tokens**
- Average conversation: ~200 tokens = **$0.00002 per conversation**
- 10,000 conversations/month = **~$0.20/month**

### 3. **Token Optimization**

- Context limited to **2000 characters** (prevents prompt overflow)
- Only top 3 similar conversations retrieved
- Optional filtering by rating (reduces low-quality context)

## 🛠️ Advanced Configuration

### Custom Embedding Model

Edit `core/rag_knowledge_base.py`:

```python
# Change model
EMBEDDING_MODEL = "text-embedding-3-large"  # More accurate, higher cost
EMBEDDING_DIM = 3072  # Different dimension
```

### Adjust Similarity Threshold

```python
# In search_similar_conversations()
min_similarity = 0.8  # Higher = stricter matching (default: 0.7)
```

### Change Top-K Results

```python
# In get_relevant_context()
top_k = 5  # More context (default: 3)
max_chars = 3000  # More characters (default: 2000)
```

## 🐛 Troubleshooting

### Issue: "ChromaDB collection not found"

**Solution:**
```bash
# Ensure ChromaDB directory exists
mkdir -p data/rag/chromadb

# Restart API server
python api_server.py
```

### Issue: "OpenAI API key not configured"

**Solution:**
```bash
# Add to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Restart server
python api_server.py
```

### Issue: "Embeddings take too long"

**Solution:**
```python
# Use batch processing (future enhancement)
# Or switch to smaller model:
EMBEDDING_MODEL = "text-embedding-ada-002"  # Fastest
```

### Issue: "Out of memory"

**Solution:**
```bash
# Reduce context size
max_chars = 1000  # In get_relevant_context()

# Or limit collection size
max_conversations_per_org = 10000
```

## 📚 API Reference

### RAGKnowledgeBase Class Methods

#### `generate_rag_response(org_id, user_id, user_message, base_prompt, conversation_id)`

Generate AI response with RAG context injection.

**Parameters:**
- `org_id` (str): Organization ID
- `user_id` (str): User ID
- `user_message` (str): User's question
- `base_prompt` (str): System prompt
- `conversation_id` (str, optional): Conversation ID

**Returns:**
- `(response, metadata)`: Tuple of AI response and metadata dict

#### `store_conversation(org_id, user_id, user_message, ai_response, conversation_id, metadata)`

Store conversation in vector database and JSON.

**Parameters:**
- `org_id` (str): Organization ID
- `user_id` (str): User ID
- `user_message` (str): User's message
- `ai_response` (str): AI's response
- `conversation_id` (str): Conversation ID
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `doc_id` (str): Document ID for feedback

#### `search_similar_conversations(org_id, query, top_k, min_rating)`

Search for semantically similar past conversations.

**Parameters:**
- `org_id` (str): Organization ID
- `query` (str): Search query
- `top_k` (int): Number of results (default: 5)
- `min_rating` (int, optional): Minimum rating filter

**Returns:**
- `results` (list): List of similar conversations with metadata

#### `record_feedback(org_id, doc_id, user_id, rating, feedback_text)`

Record user feedback for a conversation.

**Parameters:**
- `org_id` (str): Organization ID
- `doc_id` (str): Document ID
- `user_id` (str): User ID
- `rating` (int): -1, 0, or 1
- `feedback_text` (str, optional): Text feedback

**Returns:**
- `success` (bool): Whether feedback was recorded

#### `get_learning_stats(org_id)`

Get learning statistics for an organization.

**Parameters:**
- `org_id` (str): Organization ID

**Returns:**
- `stats` (dict): Statistics including satisfaction rate, total conversations, etc.

## 🎯 Best Practices

### 1. **Prompt Engineering**

Write clear base prompts for better RAG performance:

```python
base_prompt = """
You are Pramiti AI, an expert in enterprise IT service management.

IMPORTANT CONTEXT from past conversations:
{context}

USER QUESTION: {user_message}

Provide a detailed, accurate response based on the context above.
If the context doesn't cover the question, say so clearly.
"""
```

### 2. **Feedback Collection**

Encourage users to provide feedback:
- Add feedback buttons to **every AI response**
- Show confirmation messages ("Thanks for the feedback!")
- Display satisfaction rate to incentivize participation

### 3. **Quality Control**

Periodically review low-rated conversations:
- Identify common failure patterns
- Update base prompts or routing logic
- Consider manual curation for critical topics

### 4. **Data Hygiene**

Regularly clean up old conversations:
- Archive conversations older than 1 year
- Remove duplicate or spam conversations
- Anonymize PII in stored conversations

## 🚀 Future Enhancements

- **Multi-modal RAG:** Support for images, PDFs, and documents
- **Active Learning:** Automatic prompt improvement based on feedback
- **A/B Testing:** Compare different RAG strategies
- **Explainability:** Show which past conversations influenced the response
- **Custom Models:** Fine-tuned embeddings for domain-specific knowledge

## 📄 License

This RAG system is part of the Pramiti AI platform and subject to the same license terms.

## 🤝 Support

For questions or issues:
- GitHub Issues: [link]
- Email: support@pramiti.ai
- Docs: https://docs.pramiti.ai/rag
