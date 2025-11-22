# Pramiti AI - Comprehensive System Architecture

**Version:** 2.1  
**Last Updated:** November 21, 2025  
**Status:** Production-Ready with Enterprise Security, RBAC & Self-Learning

**Recent Updates:**
- ✅ **RBAC Implementation**: 50+ granular permissions, 3-tier role hierarchy (USER → ADMIN → SUPER_ADMIN)
- ✅ **30+ Secured API Endpoints**: Server-side permission enforcement with decorators
- ✅ **Tenant Isolation Architecture**: Comprehensive multi-tenant security (see TENANT_ISOLATION.md)
- ✅ **Optional Authentication Pattern**: Support for public/anonymous access with org isolation

---

## 📋 Table of Contents

1. [Executive Overview](#executive-overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Security Architecture](#security-architecture)
5. [RAG Self-Learning System](#rag-self-learning-system)
6. [Multi-Tenant Architecture](#multi-tenant-architecture)
7. [Data Flow](#data-flow)
8. [Technology Stack](#technology-stack)
9. [Deployment Architecture](#deployment-architecture)
10. [API Architecture](#api-architecture)
11. [Integration Points](#integration-points)
12. [Scalability & Performance](#scalability--performance)

---

## 🎯 Executive Overview

Pramiti AI is an **enterprise-grade, multi-tenant AI platform** that combines:
- **Hierarchical AI Agents** for IT Service Management (ITSM)
- **Self-Learning RAG System** that improves from user feedback
- **Enterprise Security** with multi-cloud secrets management and comprehensive audit trails
- **Blockchain-Based Logging** for immutable audit trails
- **OAuth Integration Hub** for Microsoft, Google, Slack, Jira, and more

### Key Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **Intelligent Routing** | AI-powered routing to specialized agents | ✅ Production |
| **Self-Learning** | RAG with semantic search and feedback loops | ✅ Production |
| **Enterprise Security** | AES-256 encryption, bcrypt, JWT, audit logging | ✅ Production |
| **Multi-Tenant** | Per-organization isolation with data privacy | ✅ Production |
| **OAuth Hub** | Centralized OAuth for 10+ platforms | ✅ Production |
| **Blockchain Audit** | Immutable communication logs | ✅ Production |
| **Real-Time Chat** | WebSocket support for instant responses | ✅ Production |

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ RAG Chat UI      │  │ Admin Dashboard  │  │ OAuth Setup UI   │     │
│  │ (Self-Learning)  │  │ (Agent Mgmt)     │  │ (Connectors)     │     │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘     │
└───────────┼──────────────────────┼──────────────────────┼───────────────┘
            │                      │                      │
            ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY LAYER (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ /api/v1/rag  │  │ /user-chat   │  │ /api/v1/auth │  │ /api/v1/   │ │
│  │ (RAG Endpoints)│ │ (Routing)   │  │ (Security)   │  │ oauth      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼────────────────┼────────┘
          │                  │                  │                │
          ▼                  ▼                  ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         MIDDLEWARE LAYER                                │
│  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐   │
│  │ Authentication    │  │ Rate Limiting     │  │ CORS & Security  │   │
│  │ (JWT + bcrypt)    │  │ (5 req/5min/IP)   │  │ Headers          │   │
│  └─────────┬─────────┘  └─────────┬─────────┘  └────────┬─────────┘   │
└────────────┼──────────────────────┼──────────────────────┼─────────────┘
             │                      │                      │
             ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BUSINESS LOGIC LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AI AGENT ORCHESTRATION                       │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │   │
│  │  │   CEO Agent  │◄───│Senior Manager│◄───│ Specialist   │     │   │
│  │  │  (Strategic) │    │  (Oversight) │    │  Agents      │     │   │
│  │  └──────────────┘    └──────────────┘    └──────┬───────┘     │   │
│  │                                                   │             │   │
│  │  ┌────────────────────────────────────────────┐  │             │   │
│  │  │ Agent Types:                               │  │             │   │
│  │  │ • Incident Management                      │◄─┘             │   │
│  │  │ • Problem Management                       │                │   │
│  │  │ • Change Management                        │                │   │
│  │  │ • Setup Assistant                          │                │   │
│  │  │ • OAuth Assistant                          │                │   │
│  │  └────────────────────────────────────────────┘                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               RAG KNOWLEDGE BASE (Self-Learning)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │ Conversation │  │   Semantic   │  │   Feedback   │         │   │
│  │  │   Storage    │  │    Search    │  │  Collection  │         │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │   │
│  │         │                  │                  │                 │   │
│  │         └──────────────────┼──────────────────┘                 │   │
│  │                            ▼                                    │   │
│  │                  ┌──────────────────┐                           │   │
│  │                  │ Context Injection│                           │   │
│  │                  │ (Top-3 Similar)  │                           │   │
│  │                  └──────────────────┘                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   SECURITY LAYER                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │   Secrets    │  │  Audit Log   │  │  Encryption  │         │   │
│  │  │  Manager     │  │  (Tamper-    │  │  (AES-256)   │         │   │
│  │  │ (Multi-Cloud)│  │   Proof)     │  │              │         │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │   │
│  │         │                  │                  │                 │   │
│  │         └──────────────────┴──────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   ChromaDB   │  │  Blockchain  │  │ PostgreSQL/  │  │   Redis   │  │
│  │   (Vectors)  │  │   (Audit)    │  │   MongoDB    │  │  (Cache)  │  │
│  │              │  │              │  │              │  │           │  │
│  │ • Embeddings │  │ • Immutable  │  │ • User Data  │  │ • Session │  │
│  │ • Per-Tenant │  │ • Hash Chain │  │ • Org Configs│  │ • Rate    │  │
│  │ • Similarity │  │ • Timestamped│  │ • Tokens     │  │   Limits  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  OpenAI API  │  │  Microsoft   │  │   Google     │  │   Slack   │  │
│  │  (GPT-4 +    │  │  (Teams/365) │  │  Workspace   │  │   (API)   │  │
│  │  Embeddings) │  │              │  │              │  │           │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │     Jira     │  │  ServiceNow  │  │  Confluence  │  │  GitHub   │  │
│  │   (Issues)   │  │    (ITSM)    │  │    (Docs)    │  │  (Repos)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Components

### 1. Agent Orchestration System

**Location:** `core/openai_agent.py`, `agents/`

**Hierarchical Structure:**

```
CEO Agent (Strategic Decisions)
    │
    ├─► Senior Manager - ITSM
    │       │
    │       ├─► Incident Manager
    │       │       └─► Incident Specialists (3)
    │       │
    │       ├─► Problem Manager
    │       │       └─► Problem Specialists (3)
    │       │
    │       └─► Change Manager
    │               └─► Change Specialists (3)
    │
    ├─► Setup Assistant (Configuration)
    │
    └─► OAuth Assistant (Authentication)
```

**Agent Capabilities:**
- **Autonomous Decision Making**: Each agent has specialized knowledge and decision authority
- **Escalation Protocol**: Issues automatically escalate up the hierarchy when needed
- **Context Awareness**: Agents share context and history through blockchain logs
- **Multi-Modal Communication**: Text, structured data, and API calls

**Key Classes:**
```python
class OpenAIAgent:
    - process_message()      # Main message processing
    - delegate_to_subordinate()  # Task delegation
    - escalate_to_manager()  # Escalation logic
    - log_to_blockchain()    # Immutable audit trail
```

---

### 2. RAG Self-Learning System

**Location:** `core/rag_knowledge_base.py`

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                  RAG Knowledge Base                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  1. INGESTION PIPELINE                               │ │
│  │     User Message → OpenAI Embedding → Vector DB      │ │
│  │     (text-embedding-ada-002, 1536 dimensions)        │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  2. STORAGE                                          │ │
│  │     ChromaDB: kb_{org_id} collections               │ │
│  │     JSON Files: Full conversation history           │ │
│  │     Metadata: Ratings, timestamps, user_id          │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  3. RETRIEVAL (Semantic Search)                     │ │
│  │     Query → Embedding → Similarity Search           │ │
│  │     Filters: min_rating=1 (only helpful responses)  │ │
│  │     Top-K: 3-5 most similar conversations           │ │
│  │     Similarity Threshold: 0.7                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  4. CONTEXT INJECTION                               │ │
│  │     Enhanced Prompt = Base + Context (max 2000 chars)│ │
│  │     Format: Q&A pairs with similarity scores        │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  5. RESPONSE GENERATION                             │ │
│  │     GPT-4 Turbo Preview                             │ │
│  │     Context-aware, improved accuracy                │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  6. FEEDBACK LOOP                                   │ │
│  │     User Rating (👍/👎) → Vector DB Metadata       │ │
│  │     Future searches prioritize high-rated responses │ │
│  │     Satisfaction rate tracking                      │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Key Methods:**

| Method | Purpose | Performance |
|--------|---------|-------------|
| `store_conversation()` | Store with embeddings | ~200ms |
| `search_similar_conversations()` | Semantic search | <50ms |
| `get_relevant_context()` | Build prompt context | ~100ms |
| `record_feedback()` | Update ratings | ~20ms |
| `generate_rag_response()` | Full RAG pipeline | ~3-5s |
| `get_learning_stats()` | Analytics | ~10ms |

**Data Model:**

```json
{
  "doc_id": "abc123def456",
  "org_id": "acme_corp",
  "user_id": "john@acme.com",
  "conversation_id": "conv_12345",
  "user_message": "How do I set up Slack?",
  "ai_response": "To set up Slack integration...",
  "embedding": [0.123, -0.456, ...],  // 1536 dimensions
  "rating": 1,  // -1, 0, 1
  "helpful": true,
  "timestamp": "2025-11-21T10:30:00Z",
  "metadata": {
    "agent": "Setup Assistant",
    "model": "gpt-4-turbo-preview",
    "context_used": true
  }
}
```

---

### 3. Security Architecture

**Location:** `core/secrets_manager.py`, `core/security_audit.py`, `core/session_manager_secure.py`, `core/connector_manager_secure.py`, `core/rbac.py`

**Security Layers:**

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: AUTHENTICATION & AUTHORIZATION                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • JWT Tokens (HS256/RS256)                           │ │
│  │ • bcrypt Password Hashing (12 rounds)                │ │
│  │ • Rate Limiting (5 attempts per 5 min per IP)        │ │
│  │ • Token Rotation (Access + Refresh)                  │ │
│  │ • Password Policy (12+ chars, complexity)            │ │
│  │ • RBAC with 50+ Granular Permissions                │ │
│  │ • Role Hierarchy: USER → ADMIN → SUPER_ADMIN        │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: ROLE-BASED ACCESS CONTROL (RBAC)                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • Server-Side Permission Enforcement                 │ │
│  │ • 50+ Granular Permissions:                          │ │
│  │   - Agent Management (VIEW/CREATE/UPDATE/DELETE)     │ │
│  │   - Chat & Communications                            │ │
│  │   - Blockchain & Audit Logs                          │ │
│  │   - Connectors & OAuth Setup                         │ │
│  │   - Tickets, Archives, Settings                      │ │
│  │ • Role Hierarchy with Permission Inheritance         │ │
│  │ • Audit Trail for All RBAC Actions                   │ │
│  │ • Decorators: @require_permission, @require_role     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: ENCRYPTION AT REST                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • AES-256 Encryption (Fernet)                        │ │
│  │ • PBKDF2HMAC Key Derivation (100,000 iterations)     │ │
│  │ • Per-Tenant Encryption Keys                         │ │
│  │ • Encrypted: Credentials, Tokens, Secrets            │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: SECRETS MANAGEMENT                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • Multi-Cloud Support:                               │ │
│  │   - AWS Secrets Manager                              │ │
│  │   - HashiCorp Vault                                  │ │
│  │   - Azure Key Vault                                  │ │
│  │   - Encrypted Local Storage                          │ │
│  │ • Cache with 5-minute TTL                            │ │
│  │ • Automatic Key Rotation                             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 5: AUDIT LOGGING                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • 40+ Security Event Types                           │ │
│  │ • Tamper-Evident (SHA-256 Checksums)                 │ │
│  │ • Structured JSON for SIEM                           │ │
│  │ • Real-Time Incident Detection                       │ │
│  │ • Compliance Ready (SOC 2, GDPR, HIPAA)              │ │
│  │ • RBAC Action Auditing (@audit_action decorator)     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 6: TENANT ISOLATION                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ • Per-Tenant ChromaDB Collections (kb_{org_id})      │ │
│  │ • Per-Org Configuration Files                        │ │
│  │ • Per-User Token Storage                             │ │
│  │ • Zero Cross-Tenant Data Leakage                     │ │
│  │ • Separate Knowledge Bases (RAG)                     │ │
│  │ • Isolated Conversation History                      │ │
│  │ • Tenant-Scoped Feedback & Learning                  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**RBAC Permission Matrix:**

```python
Role.USER Permissions (7):
- CHAT_WITH_USER_BOT, CHAT_WITH_RAG
- SUBMIT_FEEDBACK, VIEW_RAG_STATS
- CREATE_TICKETS, VIEW_TICKETS (own)
- VIEW_CHAT_HISTORY (own)

Role.ADMIN Permissions (45+):
- All USER permissions
- Agent Management (VIEW/CREATE/UPDATE/DELETE)
- Dashboard & Analytics (VIEW_KPI, VIEW_ANALYTICS)
- Chat & Communications (VIEW_COMMUNICATIONS)
- Blockchain & Audit (VIEW_BLOCKCHAIN, VIEW_AUDIT_TRAIL)
- Connectors (MANAGE_CONNECTORS, SETUP_OAUTH)
- Tickets (Full CRUD + ASSIGN)
- Archives (VIEW/CREATE/MANAGE)
- Settings (VIEW/UPDATE)

Role.SUPER_ADMIN Permissions:
- ALL PERMISSIONS (inherits everything)
- Organization Management
- Role Assignment & Management
- System-Level Configuration
```

**Security Event Types:**

```python
class SecurityEventType(Enum):
    # Authentication
    LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, TOKEN_CREATED, 
    TOKEN_EXPIRED, TOKEN_REVOKED, PASSWORD_CHANGED
    
    # Authorization & RBAC
    ACCESS_GRANTED, ACCESS_DENIED, PERMISSION_CHANGED,
    ROLE_ASSIGNED, ROLE_REVOKED, RBAC_CHECK_FAILED,
    INSUFFICIENT_PERMISSIONS
    
    # API Security
    RATE_LIMIT_EXCEEDED, INVALID_INPUT, SUSPICIOUS_REQUEST,
    API_KEY_CREATED, API_KEY_REVOKED
    
    # Data Operations
    SENSITIVE_DATA_ACCESSED, DATA_EXPORTED, DATA_DELETED,
    BULK_OPERATION
    
    # Connectors
    CONNECTOR_CONFIGURED, CONNECTOR_AUTHORIZED, 
    CONNECTOR_REVOKED, OAUTH_FLOW_STARTED, 
    OAUTH_FLOW_COMPLETED, OAUTH_FLOW_FAILED
    
    # Secrets
    SECRET_ACCESSED, SECRET_CREATED, SECRET_UPDATED,
    SECRET_DELETED, SECRET_ACCESS_FAILED
    
    # Incidents
    MULTIPLE_FAILED_LOGINS, ACCOUNT_LOCKED,
    SUSPICIOUS_ACTIVITY, INTRUSION_DETECTED,
    DATA_BREACH_SUSPECTED
```

**Authentication Patterns:**

The system supports two authentication patterns for different API endpoints:

1. **Required Authentication** (Protected Resources):
```python
@require_permission(Permission.VIEW_AGENTS)
async def get_agents(current_user: dict = Depends(get_current_user)):
    # User MUST be authenticated
    # JWT token required with valid user_id, org_id, role
    # Permission checked against user's role
    pass
```

2. **Optional Authentication** (Public/Anonymous Access):
```python
async def chat_endpoint(current_user: dict = Depends(get_current_user_optional)):
    # User MAY be authenticated or anonymous
    # Authenticated: Uses JWT user_id, org_id, role
    # Anonymous: Uses default {"user_id": "anonymous", "org_id": "default", "role": "user"}
    # Tenant isolation maintained via org_id
    pass
```

**Use Cases:**
- **Required Auth**: Agent management, settings, blockchain, connectors, OAuth, tickets, archives
- **Optional Auth**: Public chat, RAG queries, self-learning agents, knowledge base search

**Multi-Tenant Security:**

See [TENANT_ISOLATION.md](TENANT_ISOLATION.md) for comprehensive tenant isolation architecture.

**Key Security Guarantees:**
- ✅ Separate ChromaDB collections per organization (`kb_{org_id}`)
- ✅ Anonymous users isolated to "default" organization
- ✅ Authenticated users bound to their org_id via JWT
- ✅ Zero cross-tenant data leakage in RAG queries
- ✅ Isolated conversation history per tenant
- ✅ Tenant-scoped feedback and self-learning

---

### 4. Blockchain Communication Logger

**Location:** `core/blockchain_logger.py`

**Architecture:**

```
┌────────────────────────────────────────────────────────┐
│           BLOCKCHAIN COMMUNICATION LOGGER              │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Block Structure                                 │ │
│  │  {                                               │ │
│  │    "block_number": 123,                          │ │
│  │    "timestamp": "2025-11-21T10:30:00Z",         │ │
│  │    "sender": "agent-001",                        │ │
│  │    "recipient": "agent-002",                     │ │
│  │    "message": "Escalating incident...",          │ │
│  │    "previous_hash": "abc123...",                 │ │
│  │    "current_hash": "def456...",  // SHA-256      │ │
│  │    "nonce": 42                                   │ │
│  │  }                                               │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Features:                                             │
│  • Immutable audit trail                              │
│  • Hash chain verification                            │
│  • Timestamped communications                         │
│  • Proof of conversation flow                         │
│  • Tamper detection                                   │
└────────────────────────────────────────────────────────┘
```

---

### 5. Multi-Tenant Connector Management

**Location:** `core/connector_manager_secure.py`, `core/connectors.py`

**Supported Connectors:**

| Platform | Auth Type | Scopes | Status |
|----------|-----------|--------|--------|
| Microsoft Teams | OAuth 2.0 | Chat, Channels, Calendar | ✅ |
| Microsoft 365 | OAuth 2.0 | Mail, OneDrive, SharePoint | ✅ |
| Google Workspace | OAuth 2.0 | Gmail, Drive, Calendar | ✅ |
| Slack | OAuth 2.0 | Channels, Messages, Users | ✅ |
| Jira | OAuth 2.0 | Issues, Projects | ✅ |
| ServiceNow | OAuth 2.0 | Incidents, Changes | ✅ |
| Confluence | OAuth 2.0 | Pages, Spaces | ✅ |
| GitHub | OAuth 2.0 | Repos, Issues, PRs | ✅ |
| SharePoint | OAuth 2.0 | Sites, Lists, Files | ✅ |
| Zendesk | API Key | Tickets, Users | ✅ |

**Connector Data Model:**

```json
{
  "org_id": "acme_corp",
  "connector_type": "microsoft_teams",
  "auth_type": "oauth2",
  "config": {
    "client_id": "encrypted_value",
    "client_secret": "encrypted_value",
    "tenant_id": "encrypted_value",
    "redirect_uri": "http://localhost:8084/callback"
  },
  "scopes": [
    "Chat.Read",
    "Chat.ReadWrite",
    "ChannelMessage.Read"
  ],
  "status": "active",
  "created_at": "2025-11-21T10:00:00Z"
}
```

**User Token Storage:**

```json
{
  "user_id": "john@acme.com",
  "org_id": "acme_corp",
  "connector_type": "microsoft_teams",
  "access_token": "encrypted_token",
  "refresh_token": "encrypted_token",
  "expires_at": "2025-11-21T11:00:00Z",
  "scopes": ["Chat.Read", "Chat.ReadWrite"]
}
```

---

## 🔄 Data Flow

### User Chat Flow (with RAG)

```
1. USER SUBMITS MESSAGE
   └─► Frontend (rag-chat-interface.html)
        │
        ▼
2. API ENDPOINT
   └─► POST /api/v1/rag/chat
        │
        ├─► Authentication Middleware
        │    └─► JWT Token Validation
        │         └─► User Context Extraction
        │
        ▼
3. RAG KNOWLEDGE BASE
   └─► generate_rag_response()
        │
        ├─► Search Similar Conversations
        │    └─► ChromaDB Semantic Search
        │         └─► Filter by min_rating=1
        │              └─► Top-3 Results
        │
        ├─► Build Context
        │    └─► Format Q&A pairs
        │         └─► Max 2000 characters
        │
        ├─► Inject Context into Prompt
        │    └─► Enhanced system prompt
        │
        ▼
4. AI PROCESSING
   └─► OpenAI GPT-4 Turbo
        │
        ├─► Process enhanced prompt
        ├─► Generate response
        │
        ▼
5. STORAGE & LOGGING
   └─► store_conversation()
        │
        ├─► Generate embedding (OpenAI)
        ├─► Store in ChromaDB
        ├─► Save JSON file
        ├─► Security audit log
        │
        ▼
6. RETURN RESPONSE
   └─► JSON Response
        │
        ├─► ai_response (text)
        ├─► doc_id (for feedback)
        ├─► metadata (context_used, etc.)
        │
        ▼
7. USER FEEDBACK
   └─► POST /api/v1/rag/feedback
        │
        ├─► record_feedback()
        │    └─► Update ChromaDB metadata
        │         └─► rating = 1 or -1
        │              └─► Future searches prioritize
        │
        ▼
8. LEARNING COMPLETE
   └─► System improved for next query
```

### OAuth Authorization Flow

```
1. USER INITIATES OAUTH
   └─► POST /api/v1/oauth/user/authorize
        │
        ├─► connector_type: "microsoft_teams"
        ├─► user_email: "john@acme.com"
        │
        ▼
2. LOAD ORG CONFIG
   └─► SecureConnectorManager.load_org_config()
        │
        ├─► Decrypt client_id, client_secret
        ├─► Audit log: OAUTH_FLOW_STARTED
        │
        ▼
3. GENERATE AUTHORIZATION URL
   └─► Build OAuth URL
        │
        ├─► Redirect URI
        ├─► Scopes
        ├─► State (CSRF protection)
        │
        ▼
4. USER AUTHORIZES
   └─► External OAuth Provider
        │
        ├─► User signs in
        ├─► Grants permissions
        ├─► Redirects with auth code
        │
        ▼
5. CALLBACK HANDLER
   └─► GET /api/v1/oauth/callback/{connector}
        │
        ├─► Validate state token
        ├─► Exchange code for tokens
        │    └─► access_token
        │    └─► refresh_token
        │
        ▼
6. ENCRYPT & STORE TOKENS
   └─► SecureConnectorManager.save_user_token()
        │
        ├─► AES-256 encryption
        ├─► Per-user storage
        ├─► Audit log: OAUTH_FLOW_COMPLETED
        │
        ▼
7. AUTHORIZATION COMPLETE
   └─► User can now use connector
```

---

## 🛠️ Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **API Framework** | FastAPI | 0.104.1 | REST API, WebSockets |
| **AI/ML** | LangChain | 0.0.350 | Agent orchestration |
| **AI Agents** | CrewAI | 0.1.0 | Multi-agent coordination |
| **LLM** | OpenAI GPT-4 | Latest | AI responses |
| **Embeddings** | OpenAI text-embedding-ada-002 | Latest | Vector embeddings |
| **Vector DB** | ChromaDB | 0.4.22 | Semantic search |
| **Blockchain** | Web3.py | 6.12.0 | Audit trail |
| **Database** | PostgreSQL/MongoDB | Latest | Relational/Document data |
| **Cache** | Redis | 5.0.1 | Session & rate limiting |
| **Security** | cryptography | 42.0.0+ | AES-256 encryption |
| **Auth** | bcrypt, PyJWT | 1.7.4, 2.8.0 | Password hashing, tokens |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **UI Framework** | HTML5, CSS3, JavaScript | Interactive interfaces |
| **Styling** | Custom CSS with gradients | Modern design |
| **Communication** | Fetch API, WebSockets | Real-time updates |
| **Charts** | Chart.js (optional) | Analytics visualization |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Server** | Uvicorn | ASGI server |
| **Container** | Docker | Containerization |
| **Orchestration** | Docker Compose | Multi-container apps |
| **Secrets** | AWS/Vault/Azure | Cloud secrets management |
| **Monitoring** | Prometheus | Metrics collection |
| **Logging** | structlog | Structured logging |

---

## 🌐 API Architecture

### API Endpoint Structure

```
/api/v1/
├── auth/
│   ├── POST /login                    # User login
│   ├── POST /logout                   # User logout
│   ├── POST /refresh                  # Refresh token
│   └── GET  /me                       # Current user info
│
├── rag/
│   ├── POST   /chat                   # RAG-enhanced chat
│   ├── POST   /feedback               # Submit feedback
│   ├── GET    /search                 # Search knowledge base
│   ├── GET    /stats                  # Learning statistics
│   ├── GET    /conversations/{id}     # Get conversation
│   └── DELETE /conversations/{id}     # Delete conversation (GDPR)
│
├── oauth/
│   ├── POST /setup/{connector}        # Configure connector
│   ├── POST /user/authorize           # Start OAuth flow
│   ├── GET  /callback/{connector}     # OAuth callback
│   ├── GET  /configured               # List configured
│   └── GET  /authorized               # List user's authorized
│
├── agents/
│   ├── GET  /list                     # List all agents
│   ├── GET  /master                   # Master agents only
│   ├── POST /create                   # Create agent
│   └── GET  /{agent_id}               # Agent details
│
├── tenant/
│   ├── POST /chat                     # Tenant-specific chat
│   ├── GET  /agents                   # Tenant's agents
│   └── GET  /stats                    # Tenant statistics
│
└── blockchain/
    ├── GET  /entries                  # List blockchain entries
    ├── GET  /verify/{hash}            # Verify entry
    └── GET  /chain                    # Full chain
```

### API Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    "message": "Response data here",
    "metadata": {
      "timestamp": "2025-11-21T10:30:00Z",
      "request_id": "req_abc123"
    }
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials",
    "details": {
      "attempts_remaining": 3
    }
  }
}
```

---

## 📊 Scalability & Performance

### Performance Metrics

| Operation | Target | Actual | Notes |
|-----------|--------|--------|-------|
| **RAG Chat Response** | <5s | 3-5s | Including GPT-4 API call |
| **Vector Search** | <100ms | <50ms | 10K documents |
| **Authentication** | <200ms | ~150ms | JWT validation + bcrypt |
| **OAuth Callback** | <1s | ~800ms | Token exchange |
| **API Throughput** | 1000 req/s | TBD | Load testing needed |
| **Conversation Storage** | <500ms | ~200ms | Embedding + storage |

### Scalability Considerations

**Horizontal Scaling:**
```
┌──────────────────────────────────────────────────────┐
│           Load Balancer (Nginx/ALB)                  │
└───────────┬──────────────────────────────────────────┘
            │
     ┌──────┴──────┬──────────┬──────────┐
     │             │          │          │
┌────▼────┐  ┌────▼────┐  ┌──▼─────┐  ┌▼──────────┐
│ API     │  │ API     │  │ API    │  │ API       │
│ Server  │  │ Server  │  │ Server │  │ Server    │
│ (Pod 1) │  │ (Pod 2) │  │(Pod 3) │  │ (Pod N)   │
└────┬────┘  └────┬────┘  └──┬─────┘  └┬──────────┘
     │            │           │         │
     └────────────┴───────────┴─────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
┌────▼─────┐            ┌─────▼──────┐
│ ChromaDB │            │ PostgreSQL │
│ Cluster  │            │ (Primary + │
│          │            │  Replicas) │
└──────────┘            └────────────┘
```

**Caching Strategy:**
- Redis for session data (5-minute TTL)
- ChromaDB built-in caching
- Secrets manager cache (5-minute TTL)
- API response caching for static data

**Database Sharding:**
- ChromaDB: Per-tenant collections
- PostgreSQL: Partition by org_id
- MongoDB: Shard by org_id

---

## 🔌 Integration Points

### External Services

**OpenAI Integration:**
```python
# GPT-4 for chat responses
openai.ChatCompletion.create(
    model="gpt-4-turbo-preview",
    messages=[...]
)

# Embeddings for RAG
openai.Embedding.create(
    model="text-embedding-ada-002",
    input="text to embed"
)
```

**OAuth Providers:**
- Microsoft Azure AD
- Google OAuth 2.0
- Slack OAuth 2.0
- Jira OAuth 1.0a/2.0
- ServiceNow OAuth 2.0

**Secrets Management:**
- AWS Secrets Manager (boto3)
- HashiCorp Vault (hvac)
- Azure Key Vault (azure-keyvault-secrets)

---

## 🚀 Deployment Architecture

### Development Environment

```
Local Machine
├── Python 3.8+ Virtual Environment
├── ChromaDB (local storage)
├── PostgreSQL (local or Docker)
├── Redis (local or Docker)
└── .env file with secrets
```

### Production Environment

```
Cloud Infrastructure (AWS/Azure/GCP)
│
├── Kubernetes Cluster
│   ├── API Pods (3+ replicas)
│   ├── Worker Pods (for background tasks)
│   └── Ingress Controller (HTTPS/TLS)
│
├── Managed Databases
│   ├── RDS PostgreSQL (Multi-AZ)
│   ├── ElastiCache Redis (Cluster mode)
│   └── ChromaDB (Persistent volumes)
│
├── Secrets Management
│   └── AWS Secrets Manager / Azure Key Vault
│
├── Monitoring
│   ├── CloudWatch / Azure Monitor
│   ├── Prometheus + Grafana
│   └── SIEM Integration
│
└── Load Balancing
    └── Application Load Balancer (ALB)
```

### Environment Variables

```bash
# Core
ENVIRONMENT=production
PORT=8084

# OpenAI
OPENAI_API_KEY=sk-xxx

# Security
MASTER_ENCRYPTION_PASSWORD=xxx
JWT_SECRET_KEY=xxx

# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Secrets Backend
SECRETS_BACKEND=aws  # aws|vault|azure|local
AWS_REGION=us-east-1
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=xxx
AZURE_VAULT_URL=https://xxx.vault.azure.net

# OAuth (if not using secrets manager)
MICROSOFT_CLIENT_ID=xxx
MICROSOFT_CLIENT_SECRET=xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
```

---

## 📈 Monitoring & Observability

### Metrics Collected

**Application Metrics:**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Active connections
- RAG cache hit rate
- Vector search performance

**Business Metrics:**
- Conversations per day
- Satisfaction rate (%)
- Feedback collection rate
- Active users per org
- OAuth authorizations
- Agent utilization

**Security Metrics:**
- Failed login attempts
- Rate limit violations
- Suspicious activities detected
- Secret access attempts
- Token expirations

### Logging Strategy

**Log Levels:**
```python
DEBUG   # Development debugging
INFO    # Normal operations, business events
WARNING # Degraded performance, unusual behavior
ERROR   # Errors that need attention
CRITICAL # System failures, security incidents
```

**Log Structure (JSON):**
```json
{
  "timestamp": "2025-11-21T10:30:00Z",
  "level": "INFO",
  "event": "rag_chat_completed",
  "user_id": "john@acme.com",
  "org_id": "acme_corp",
  "duration_ms": 3200,
  "context_used": true,
  "metadata": {
    "doc_id": "abc123",
    "model": "gpt-4-turbo-preview"
  }
}
```

---

## 🔐 Security Compliance

### Compliance Standards

| Standard | Status | Notes |
|----------|--------|-------|
| **SOC 2 Type II** | ✅ Ready | Audit logging, encryption |
| **GDPR** | ✅ Compliant | Right to erasure, data portability |
| **HIPAA** | ✅ Ready | Encryption, audit trails |
| **ISO 27001** | ✅ Ready | Information security management |
| **PCI DSS** | ⚠️ Partial | Not handling payment cards directly |

### Data Privacy

**Personal Data Handling:**
- ✅ Encrypted at rest (AES-256)
- ✅ Encrypted in transit (TLS 1.3)
- ✅ Per-tenant isolation
- ✅ Right to erasure (DELETE endpoints)
- ✅ Data export capability
- ✅ Consent management
- ✅ Audit trail of all access

**Data Retention:**
- Conversations: Configurable (default: 1 year)
- Audit logs: 7 years (compliance requirement)
- User tokens: Until revoked or expired
- Feedback data: Indefinite (anonymized)

---

## 📋 System Requirements

### Minimum Requirements

**Development:**
- Python 3.8+
- 4 GB RAM
- 10 GB disk space
- Internet connection (for OpenAI API)

**Production:**
- 4 vCPUs (8+ recommended)
- 16 GB RAM (32+ recommended)
- 100 GB SSD storage
- High-bandwidth internet
- Load balancer
- SSL certificate

### Dependencies

See `requirements.txt` for complete list:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- langchain==0.0.350
- crewai==0.1.0
- chromadb==0.4.22
- openai==1.7.2
- cryptography>=42.0.0
- bcrypt
- PyJWT==2.8.0
- web3==6.12.0
- redis==5.0.1
- (and more...)

---

## 🎯 Future Enhancements

### Roadmap

**Q1 2026:**
- [ ] Multi-modal RAG (images, PDFs, documents)
- [ ] Active learning with auto-prompt improvement
- [ ] A/B testing framework for RAG strategies
- [ ] Real-time collaboration features

**Q2 2026:**
- [ ] Mobile applications (iOS, Android)
- [ ] Voice interface integration
- [ ] Advanced analytics dashboard
- [ ] Custom model fine-tuning

**Q3 2026:**
- [ ] Kubernetes Helm charts
- [ ] Multi-region deployment
- [x] **Advanced RBAC with fine-grained permissions** ✅ (Implemented: 50+ permissions, 3-tier role hierarchy, 30+ protected endpoints)
- [ ] Workflow automation builder

**Q4 2026:**
- [ ] On-premise deployment option
- [ ] Air-gapped environment support
- [ ] Advanced threat detection with ML
- [ ] Compliance automation tools

---

## 📞 Support & Documentation

**Documentation:**
- [README.md](README.md) - Getting started
- [SECURITY_IMPLEMENTATION_SUMMARY.md](SECURITY_IMPLEMENTATION_SUMMARY.md) - Security overview
- [RAG_SYSTEM.md](docs/RAG_SYSTEM.md) - RAG documentation
- [RAG_QUICK_REFERENCE.md](docs/RAG_QUICK_REFERENCE.md) - Quick reference
- [API Documentation](http://localhost:8084/docs) - Interactive API docs

**Support Channels:**
- GitHub Issues: Bug reports and feature requests
- Email: support@pramiti.ai
- Slack: [Pramiti AI Community]

---

## 📄 License

Proprietary - Pramiti AI Platform  
Copyright © 2025 Pramiti AI. All rights reserved.

---

## 🙏 Acknowledgments

**Technologies:**
- OpenAI for GPT-4 and embeddings API
- FastAPI for excellent API framework
- ChromaDB for vector database
- LangChain and CrewAI for agent orchestration

**Security Frameworks:**
- OWASP Top 10
- NIST Cybersecurity Framework
- CIS Controls

---

**Document Version:** 2.0  
**Last Updated:** November 21, 2025  
**Maintained By:** Pramiti AI Architecture Team
