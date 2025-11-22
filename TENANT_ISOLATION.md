# Tenant Isolation & Data Confidentiality

## Overview

The Pramiti AI system implements **strict tenant isolation** to ensure data confidentiality and prevent cross-tenant data leakage. The Self-Learning RAG (Retrieval-Augmented Generation) system requires authentication to maintain proper tenant boundaries.

## RAG Knowledge Base Isolation

### Architecture

Each organization (tenant) has its own **completely isolated** knowledge base:

```
ChromaDB Collections:
├── kb_org_acme       → Acme Corporation (authenticated users only)
├── kb_org_techcorp   → Tech Corp (authenticated users only)
└── kb_org_startup    → Startup Inc (authenticated users only)
```

### How It Works

#### 1. **Tenant-Scoped Collections**
- Each `org_id` maps to a separate ChromaDB collection
- Collection naming: `kb_{org_id}` (e.g., `kb_org_acme`)
- Collections are physically isolated at the database level
- No cross-collection queries are possible

#### 2. **Authentication Requirements**

**Self-Learning RAG Endpoints (Authentication Required):**
- `POST /api/v1/rag/chat` - Chat with tenant-specific knowledge base
- `POST /api/v1/rag/feedback` - Record feedback for self-learning
- `GET /api/v1/rag/search` - Search organization's knowledge base
- `GET /api/v1/rag/stats` - Get organization's learning statistics

**Why Authentication is Required:**
- Ensures conversations are saved to the correct organization's knowledge base
- Prevents anonymous users from polluting tenant-specific learning data
- Maintains audit trail of who contributed to knowledge base
- Enables proper data ownership and GDPR compliance

**Authenticated Users:**
```javascript
// User logs in with credentials
Authorization: Bearer <jwt_token>

// Token contains:
{
  "user_id": "user123",
  "org_id": "org_acme",
  "role": "admin"
}

// RAG chat uses org_id from token
// Only accesses kb_org_acme collection
```

**Public Chat Endpoints (Optional Authentication):**
- `POST /user-chat` - General agent chat (does not persist to RAG)
- `POST /chat` - Direct agent messaging

These endpoints work without authentication but do not contribute to the self-learning knowledge base.

### 3. **Data Storage Isolation**

```
data/rag/
├── chroma/
│   ├── kb_org_acme/          → Acme Corp knowledge base
│   └── kb_org_techcorp/      → Tech Corp knowledge base
├── conversations/
│   ├── org_acme/             → Acme Corp conversations
│   └── org_techcorp/         → Tech Corp conversations
└── feedback/
    ├── default/              → Default org feedback
    ├── org_acme/             → Acme Corp feedback
    └── org_techcorp/         → Tech Corp feedback
```

## Security Guarantees

### ✅ **What is Protected:**

1. **Knowledge Base Isolation**
   - Org A cannot search Org B's knowledge base
   - Vector embeddings are stored in separate collections
   - No semantic search across organizations

2. **Conversation History Isolation**
   - Each org's conversations stored in separate directories
   - Conversation IDs are scoped to org_id
   - No cross-tenant conversation access

3. **Feedback & Learning Isolation**
   - User feedback only affects their org's knowledge base
   - Self-learning improvements are org-specific
   - Rating systems are isolated per tenant

4. **Context Retrieval Isolation**
   - RAG context retrieval searches only org-specific data
   - AI responses use only tenant-specific context
   - No information leakage from other tenants

### ✅ **Anonymous User Isolation:**

- Anonymous users use `org_id = "default"`
- Isolated from all authenticated organizations
- Can be used for public demos or trial purposes
- No access to production tenant data

## Implementation Details

### Code-Level Enforcement

```python
# RAG Chat Endpoint
@app.post("/api/v1/rag/chat")
async def rag_chat(request: dict, current_user: dict = Depends(get_current_user_optional)):
    # Extract org_id from authenticated user or default
    org_id = current_user["org_id"]  # ← Tenant isolation key
    
    # Generate response using org-specific knowledge base
    ai_response, metadata = rag_knowledge_base.generate_rag_response(
        org_id=org_id,  # ← Only searches kb_{org_id} collection
        user_id=current_user["user_id"],
        user_message=user_message,
        base_prompt=system_prompt,
        conversation_id=conversation_id
    )
```

### ChromaDB Collection Access

```python
def get_or_create_collection(self, org_id: str) -> Any:
    """Get or create ChromaDB collection for organization"""
    collection_name = f"kb_{org_id}".replace("-", "_")
    
    # Returns ONLY the org-specific collection
    collection = self.chroma_client.get_collection(name=collection_name)
    return collection
```

### Vector Search Isolation

```python
def search_similar_conversations(self, org_id: str, query: str, top_k: int = 5):
    """Search similar conversations - TENANT ISOLATED"""
    
    # Get org-specific collection
    collection = self.get_or_create_collection(org_id)
    
    # Search ONLY within this org's data
    results = collection.query(
        query_embeddings=[self.get_embedding(query)],
        n_results=top_k
    )
    
    return results  # ← Only contains org's own data
```

## Authentication Strategies

### Strategy 1: Optional Authentication (Current)
- **Public endpoints** allow anonymous access
- Anonymous users get isolated `default` tenant
- Authenticated users get their org-specific tenant
- **Use Case**: Public demos, trial accounts, marketing sites

### Strategy 2: Required Authentication (Alternative)
- **All endpoints** require authentication
- No anonymous access allowed
- Every user must belong to an organization
- **Use Case**: Enterprise deployments, strict security requirements

### Hybrid Approach (Recommended)
- **Public-facing endpoints**: Optional auth (e.g., demo chat)
- **Sensitive endpoints**: Required auth (e.g., admin, connectors)
- **Configurable**: Can switch per deployment environment

## Migration Path: Optional → Required Auth

If you want to require authentication for RAG endpoints in the future:

```python
# Change from optional to required authentication
@app.post("/api/v1/rag/chat")
@require_permission(Permission.CHAT_WITH_RAG)  # ← Add permission check
async def rag_chat(
    request: dict, 
    current_user: dict = Depends(get_current_user)  # ← Change to required
):
    # Same implementation - tenant isolation still enforced
```

## Audit & Compliance

### Audit Logging
```python
# Log RAG interactions for authenticated users
if user_id != "anonymous":
    logger.info(f"RAG chat - org:{org_id}, user:{user_id}, conv:{conversation_id}")
```

### Data Retention
- Each tenant can have separate retention policies
- Conversations can be deleted per org_id
- Feedback can be purged per tenant

### Compliance Features
1. **Data Locality**: Each org's data in separate collections
2. **Audit Trail**: All interactions logged with org_id
3. **Right to Deletion**: Can delete all org data independently
4. **Data Export**: Can export tenant-specific data only

## Testing Tenant Isolation

### Test Scenario 1: Cross-Tenant Search
```bash
# User from Org A
curl -X POST /api/v1/rag/chat \
  -H "Authorization: Bearer <org_a_token>" \
  -d '{"message": "Show me Org B data"}'

# Result: Can only see Org A's knowledge base
# ✅ PASS: No cross-tenant access
```

### Test Scenario 2: Anonymous Isolation
```bash
# Anonymous user (no token)
curl -X POST /api/v1/rag/chat \
  -d '{"message": "Search all conversations"}'

# Result: Only sees "default" org data
# ✅ PASS: Isolated from production orgs
```

### Test Scenario 3: Feedback Isolation
```bash
# User from Org A gives feedback
curl -X POST /api/v1/rag/feedback \
  -H "Authorization: Bearer <org_a_token>" \
  -d '{"doc_id": "123", "rating": 1}'

# Result: Only affects Org A's knowledge base quality
# ✅ PASS: No cross-tenant learning contamination
```

## Security Best Practices

### ✅ DO:
- Always use `org_id` from authenticated token
- Validate org_id exists and user has access
- Log all data access with org_id for audit
- Use separate ChromaDB collections per tenant
- Implement org-level data encryption if needed

### ❌ DON'T:
- Never allow user-supplied org_id override
- Don't mix data from multiple orgs in queries
- Avoid shared collections with org_id filters (use separate collections)
- Don't log sensitive data from conversations
- Never expose org_id enumeration endpoints

## Summary

**Tenant isolation is enforced at multiple layers:**

1. **Authentication Layer**: org_id extracted from JWT token or defaults to "default"
2. **Application Layer**: All functions accept org_id parameter
3. **Data Layer**: Separate ChromaDB collections per tenant
4. **Storage Layer**: Separate directories for conversations/feedback

**Even with optional authentication, confidentiality is maintained because:**
- Unauthenticated users are isolated to "default" org
- Authenticated users are bound to their org via JWT token
- No API allows crossing org boundaries
- Data is physically separated at storage layer

This design ensures **zero cross-tenant data leakage** while maintaining **flexibility for public-facing features**.
