# RAG Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
./setup_rag.sh

# 2. Set API key
echo "OPENAI_API_KEY=sk-your-key" >> .env

# 3. Start server
python api_server.py
```

Then open: `http://localhost:8084/static/rag-chat-interface.html`

---

## 📡 API Endpoints

### Chat with RAG
```bash
POST /api/v1/rag/chat
Body: {
  "message": "Your question here",
  "conversation_id": "optional_conv_id"
}
```

### Submit Feedback
```bash
POST /api/v1/rag/feedback
Body: {
  "doc_id": "document_id_from_response",
  "rating": 1  # 1 = 👍, -1 = 👎, 0 = neutral
}
```

### Search Knowledge Base
```bash
GET /api/v1/rag/search?query=your+query&top_k=5
```

### Get Statistics
```bash
GET /api/v1/rag/stats
```

---

## 💻 Python Usage

### Generate RAG Response
```python
from core.rag_knowledge_base import rag_knowledge_base

response, metadata = rag_knowledge_base.generate_rag_response(
    org_id="acme_corp",
    user_id="john@acme.com",
    user_message="How do I set up Slack?",
    base_prompt="You are Pramiti AI...",
    conversation_id="conv_12345"
)
```

### Store Conversation
```python
doc_id = rag_knowledge_base.store_conversation(
    org_id="acme_corp",
    user_id="john@acme.com",
    user_message="How do I set up Slack?",
    ai_response="To set up Slack: 1) Go to...",
    conversation_id="conv_12345",
    metadata={"agent": "Setup Assistant"}
)
```

### Search Similar Conversations
```python
results = rag_knowledge_base.search_similar_conversations(
    org_id="acme_corp",
    query="slack integration",
    top_k=5,
    min_rating=1  # Only highly-rated conversations
)
```

### Record Feedback
```python
rag_knowledge_base.record_feedback(
    org_id="acme_corp",
    doc_id="abc123def456",
    user_id="john@acme.com",
    rating=1,  # 👍
    feedback_text="Very helpful!"
)
```

### Get Statistics
```python
stats = rag_knowledge_base.get_learning_stats("acme_corp")
print(f"Satisfaction Rate: {stats['satisfaction_rate']}%")
```

---

## 📁 File Structure

```
core/
  rag_knowledge_base.py     # Main RAG class

data/
  rag/
    chromadb/               # Vector database
    conversations/          # JSON files per org
      {org_id}/
        {conv_id}.json

web/
  rag-chat-interface.html   # Frontend UI

docs/
  RAG_SYSTEM.md             # Full documentation
  RAG_IMPLEMENTATION_SUMMARY.md  # Implementation details
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Customization (core/rag_knowledge_base.py)
```python
# Change embedding model
EMBEDDING_MODEL = "text-embedding-ada-002"  # Default
# EMBEDDING_MODEL = "text-embedding-3-large"  # More accurate

# Adjust similarity threshold
min_similarity = 0.7  # In search_similar_conversations()

# Change context size
max_chars = 2000  # In get_relevant_context()
top_k = 3  # Number of similar conversations
```

---

## 🎯 Key Concepts

### Embedding
Converting text to 1536-dimensional vector for semantic comparison.

### Similarity Score
0.0 to 1.0, where 1.0 = identical, 0.7+ = very similar

### Context Injection
Adding relevant past conversations to AI prompt for better responses.

### Feedback Loop
👍/👎 ratings stored and used to prioritize quality context.

---

## 🐛 Troubleshooting

### "ChromaDB not found"
```bash
pip install chromadb==0.4.22
```

### "OpenAI API key invalid"
```bash
echo "OPENAI_API_KEY=sk-your-key" >> .env
# Restart server
```

### "No similar conversations found"
- Need at least 1 stored conversation
- Check similarity threshold (min_similarity)
- Ensure org_id matches

### "Slow performance"
- Reduce top_k (default: 3)
- Reduce max_chars (default: 2000)
- Check ChromaDB indexing

---

## 📊 Response Metadata

```python
{
  "context_used": True,          # Was context retrieved?
  "context_length": 1247,        # Characters of context
  "model": "gpt-4-turbo-preview", # OpenAI model used
  "learning_enabled": True       # RAG learning active
}
```

---

## 🔒 Security Checklist

- ✅ Per-tenant isolation (separate collections)
- ✅ Authentication required (JWT tokens)
- ✅ Encrypted storage (AES-256)
- ✅ Audit logging (all operations logged)
- ✅ GDPR compliance (DELETE conversation endpoint)

---

## 📈 Performance Tips

1. **Batch Processing**: Store multiple conversations at once
2. **Filter by Rating**: Use `min_rating=1` for quality context
3. **Limit Context**: Keep `max_chars` under 3000
4. **Top-K Tuning**: 3-5 is optimal (default: 3)
5. **Caching**: ChromaDB caches embeddings automatically

---

## 🎨 Frontend Integration

### Add Feedback Buttons
```html
<button onclick="submitFeedback('doc_123', 1)">👍</button>
<button onclick="submitFeedback('doc_123', -1)">👎</button>
```

### Display Statistics
```javascript
fetch('/api/v1/rag/stats')
  .then(r => r.json())
  .then(data => {
    console.log(`Satisfaction: ${data.stats.satisfaction_rate}%`);
  });
```

---

## 📚 Documentation

- **[Full Guide](docs/RAG_SYSTEM.md)** - Complete documentation
- **[Implementation Summary](docs/RAG_IMPLEMENTATION_SUMMARY.md)** - What was built
- **[Security Guide](docs/SECURITY_IMPLEMENTATION.md)** - Enterprise security

---

## 🆘 Support

**Test Script:** `python test_rag_system.py`

**Setup Script:** `./setup_rag.sh`

**Logs:** Check `api_server.py` console output

**Issues:** File bug report with conversation_id and error message

---

## ✅ Quick Checklist

- [ ] Dependencies installed (`./setup_rag.sh`)
- [ ] OpenAI API key in `.env`
- [ ] Test script passes (`python test_rag_system.py`)
- [ ] API server running (`python api_server.py`)
- [ ] Chat interface accessible (http://localhost:8084/...)
- [ ] First conversation stored
- [ ] Feedback buttons working (👍/👎)
- [ ] Statistics updating

---

**🎊 Ready to Build Self-Learning AI!**

Your RAG system is configured and ready to learn from user interactions!
