# Architecture Diagrams

## Multi-Tenant & Hybrid Model System Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Multi-Tenant SaaS Platform                    │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Tenant A       │  │   Tenant B       │  │   Tenant C       │
│   (Finance)      │  │   (Healthcare)   │  │   (Tech)         │
│                  │  │                  │  │                  │
│  10 Agents       │  │  25 Agents       │  │  5 Agents        │
│  50 Tickets      │  │  200 Tickets     │  │  15 Tickets      │
│  500 MB Docs     │  │  2 GB Docs       │  │  100 MB Docs     │
│                  │  │                  │  │                  │
│  Tier: Pro       │  │  Tier: Enterprise│  │  Tier: Basic     │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                  ┌────────────────────────┐
                  │  Multi-Tenant Manager  │
                  │  - Isolation           │
                  │  - Quota Enforcement   │
                  │  - Usage Tracking      │
                  └────────────────────────┘
```

### Hybrid Model Routing Flow

```
User Query
    │
    ├─► "Hi, how are you?"
    │       │
    │       ├─► Router Analysis
    │       │   ├─ Keywords: ["hi"] → SIMPLE
    │       │   ├─ Length: 15 chars → SIMPLE
    │       │   └─ Complexity: SIMPLE
    │       │
    │       ├─► Model Selection: gpt-4o-mini (SLM)
    │       │   └─ Cost: $0.0001
    │       │
    │       ├─► Generate Response
    │       │   └─ "Hello! I'm doing well..."
    │       │
    │       └─► Cascade Check
    │           ├─ Confidence: 0.98 ✓
    │           └─ No cascade needed
    │
    │
    ├─► "Analyze the root cause of database outage..."
    │       │
    │       ├─► Router Analysis
    │       │   ├─ Keywords: ["analyze", "root cause"] → COMPLEX
    │       │   ├─ Length: 120 chars → MODERATE
    │       │   ├─ Technical terms: Yes
    │       │   └─ Complexity: COMPLEX
    │       │
    │       ├─► Model Selection: gpt-4o (LLM)
    │       │   └─ Cost: $0.0015
    │       │
    │       ├─► Generate Response
    │       │   └─ [Detailed analysis...]
    │       │
    │       └─► No cascade (already on LLM)
    │
    │
    └─► "Tell me about incident management" [SLM tries first]
            │
            ├─► Router Analysis → MODERATE
            ├─► Model Selection: gpt-4o-mini (SLM)
            ├─► Generate Response: "I'm not sure about that..."
            │
            ├─► Cascade Check
            │   ├─ Confidence: 0.45 ❌ (< 0.6)
            │   ├─ Uncertainty phrase detected ✓
            │   └─ CASCADE TRIGGERED!
            │
            └─► Upgrade to gpt-4o (LLM)
                ├─ Re-generate: [Comprehensive answer...]
                └─ Cascade successful ✓
```

### Cost Optimization Visualization

```
Without Router (100% LLM):
█████████████████████████████████████████████████ 100% LLM ($100/mo)

With Hybrid Router:
████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 70% SLM, 30% LLM ($35/mo)

Savings: 65% ↓
```

### Complexity Distribution (Typical)

```
Query Types:

SIMPLE (60%)     ████████████████████████████████████
"What is status?"
"Hello"
"List tickets"
                 → gpt-4o-mini ($0.15/1M tokens)

MODERATE (15%)   ████████████
"How to reset password?"
"Explain incident workflow"
                 → gpt-4o-mini ($0.15/1M tokens)

COMPLEX (20%)    ████████████████
"Analyze outage root cause"
"Design recovery strategy"
                 → gpt-4o ($2.50/1M tokens)

CRITICAL (5%)    ████
"Security breach response"
"Compliance audit prep"
                 → gpt-4-turbo ($10/1M tokens)
```

### Tenant Data Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    Database / Storage                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │   Tenant A Data    │  │   Tenant B Data    │            │
│  ├────────────────────┤  ├────────────────────┤            │
│  │ agents_a {}        │  │ agents_b {}        │            │
│  │ tickets_a []       │  │ tickets_b []       │            │
│  │ documents_a []     │  │ documents_b []     │            │
│  │ roles_a []         │  │ roles_b []         │            │
│  └────────────────────┘  └────────────────────┘            │
│                                                              │
│  ┌───────────────────────────────────────────┐             │
│  │   Tenant Usage Metrics                     │             │
│  ├───────────────────────────────────────────┤             │
│  │ Tenant A: 1000 queries, $15, 70% SLM      │             │
│  │ Tenant B: 5000 queries, $85, 65% SLM      │             │
│  └───────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow with Multi-Tenant

```
1. User Request
   │
   └─► Header: X-Tenant-ID: tenant_abc123
       │
       ▼
2. API Server
   │
   ├─► Extract tenant_id from header/token
   │
   ├─► Validate tenant exists
   │
   └─► Check quota limits
       │
       ▼
3. Agent Processing
   │
   ├─► Get tenant-specific agent
   │
   ├─► Router analyzes query complexity
   │
   └─► Select model (SLM or LLM)
       │
       ▼
4. OpenAI API Call
   │
   └─► Generate response
       │
       ▼
5. Usage Tracking
   │
   ├─► Record query count
   ├─► Record tokens used
   ├─► Calculate cost
   └─► Update tenant metrics
       │
       ▼
6. Response to User
   │
   └─► Return answer with metadata
```

### Subscription Tier Comparison

```
┌──────────────┬─────────────┬────────────────┬──────────────┐
│   Feature    │    Basic    │  Professional  │  Enterprise  │
├──────────────┼─────────────┼────────────────┼──────────────┤
│ Agents       │     10 ░░░  │      50 ████   │   500 █████  │
│ Tickets/mo   │    100 ░░   │   1,000 ████   │ 10,000 █████ │
│ Storage      │  100MB ░░   │    1GB ████    │  10GB █████  │
│ API Calls/d  │  1,000 ░░   │  10,000 ████   │100,000 █████ │
│ Cost/mo      │ $50-100     │   $300-600     │ $2k-4k       │
├──────────────┼─────────────┼────────────────┼──────────────┤
│ Router       │      ✓      │       ✓        │      ✓       │
│ Analytics    │      ✗      │       ✓        │      ✓       │
│ SSO          │      ✗      │       ✗        │      ✓       │
│ Custom Model │      ✗      │       ✗        │      ✓       │
│ Support      │  Standard   │    Priority    │   24/7       │
└──────────────┴─────────────┴────────────────┴──────────────┘
```

### Cascading Decision Tree

```
                    Query Received
                          │
                          ▼
                 ┌─────────────────┐
                 │ Analyze Complexity│
                 └────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    SIMPLE           MODERATE           COMPLEX
        │                 │                 │
        ▼                 ▼                 ▼
   gpt-4o-mini       gpt-4o-mini         gpt-4o
        │                 │                 │
        ▼                 ▼                 ▼
  Generate Resp     Generate Resp    Generate Resp
        │                 │                 │
        ▼                 ▼                 ▼
   Check Cascade     Check Cascade     No Cascade
        │                 │                 │
   ┌────┴────┐       ┌────┴────┐           │
   │         │       │         │           │
Conf>0.6  Conf<0.6 Conf>0.6 Conf<0.6      │
   │         │       │         │           │
   ▼         ▼       ▼         ▼           ▼
  Done   Upgrade    Done   Upgrade      Done
           │                   │
           ▼                   ▼
       gpt-4o            gpt-4o/gpt-4-turbo
           │                   │
           ▼                   ▼
      Re-generate        Re-generate
           │                   │
           └─────────┬─────────┘
                     ▼
                   Done
```

### Performance Metrics Dashboard (Conceptual)

```
┌────────────────────────────────────────────────────────────┐
│  Cost Optimization Dashboard                               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Total Queries Today: 10,000                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ SLM (gpt-4o-mini)     █████████████████  70%  7,000 │  │
│  │ LLM (gpt-4o)          ██████            25%  2,500 │  │
│  │ LLM+ (gpt-4-turbo)    █                  5%    500 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Cost Breakdown:                                           │
│  ├─ SLM:   $1.05  (7,000 queries × $0.00015)              │
│  ├─ LLM:   $6.25  (2,500 queries × $0.0025)               │
│  └─ LLM+:  $5.00  (  500 queries × $0.01)                 │
│                                                             │
│  Total Cost: $12.30                                        │
│  vs. All LLM: $25.00                                       │
│  Savings: $12.70 (51%)                                     │
│                                                             │
│  Cascade Rate: 7.2% (504 cascades)                         │
│  Avg Response Time: 1.2s                                   │
│  Error Rate: 0.3%                                          │
└────────────────────────────────────────────────────────────┘
```

### Industry-Specific Routing Profiles

```
Finance Industry:
┌────────────────────────────────────┐
│ Prefer Quality: ✓                  │
│ Compliance: SOC2, PCI-DSS          │
├────────────────────────────────────┤
│ Simple    → gpt-4o-mini      (40%) │
│ Moderate  → gpt-4o           (30%) │
│ Complex   → gpt-4o           (20%) │
│ Critical  → gpt-4-turbo      (10%) │
└────────────────────────────────────┘
Lower SLM usage, higher quality

Healthcare Industry:
┌────────────────────────────────────┐
│ Prefer Quality: ✓                  │
│ Compliance: HIPAA                  │
├────────────────────────────────────┤
│ Simple    → gpt-4o-mini      (45%) │
│ Moderate  → gpt-4o           (30%) │
│ Complex   → gpt-4o           (15%) │
│ Critical  → gpt-4-turbo      (10%) │
└────────────────────────────────────┘
Balance quality & cost

Tech/Startup:
┌────────────────────────────────────┐
│ Prefer Cost: ✓                     │
│ Compliance: None                   │
├────────────────────────────────────┤
│ Simple    → gpt-4o-mini      (75%) │
│ Moderate  → gpt-4o-mini      (15%) │
│ Complex   → gpt-4o            (8%) │
│ Critical  → gpt-4o            (2%) │
└────────────────────────────────────┘
Maximum cost savings
```

### Integration Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend (HTML/JS)                       │
│  - Organization selector                                      │
│  - Usage dashboard                                            │
│  - Routing statistics                                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   API Server (FastAPI)                        │
│  ┌──────────────────────────────────────────────────┐        │
│  │  Organization Endpoints                           │        │
│  │  - POST   /api/v1/organizations                  │        │
│  │  - GET    /api/v1/organizations                  │        │
│  │  - GET    /api/v1/organizations/{id}             │        │
│  │  - GET    /api/v1/organizations/{id}/usage       │        │
│  │  - DELETE /api/v1/organizations/{id}             │        │
│  └──────────────────────────────────────────────────┘        │
│  ┌──────────────────────────────────────────────────┐        │
│  │  Agent Endpoints (Updated)                        │        │
│  │  - POST /agents?tenant_id=xxx                    │        │
│  │  - GET  /agents/{id}/routing-stats               │        │
│  └──────────────────────────────────────────────────┘        │
└────────────────────────┬─────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌─────────────┐ ┌──────────────┐
│ Multi-Tenant   │ │Model Router │ │OpenAI Agent  │
│ Manager        │ │             │ │              │
│                │ │             │ │              │
│ - Isolation    │ │- Complexity │ │- Routing     │
│ - Quotas       │ │- Selection  │ │- Cascade     │
│ - Usage        │ │- Stats      │ │- Blockchain  │
└────────────────┘ └─────────────┘ └──────────────┘
```

### Data Flow Example

```
Step 1: Create Organization
  POST /api/v1/organizations
  Body: {
    "organization_name": "Acme Corp",
    "industry": "tech",
    "subscription_tier": "professional"
  }
  Response: {
    "tenant_id": "tenant_abc123",
    "limits": {
      "max_agents": 50,
      "max_tickets_per_month": 1000
    }
  }

Step 2: Create Agent for Tenant
  POST /agents?tenant_id=tenant_abc123
  Body: {
    "name": "Support Bot",
    "role_name": "Subject Matter Expert",
    "use_model_router": true
  }
  Response: {
    "agent_id": "agent_001",
    "tenant_id": "tenant_abc123",
    "model_router_enabled": true
  }

Step 3: User Query
  WebSocket: /ws/chat
  Message: {
    "message": "How do I reset my password?",
    "agent_id": "agent_001",
    "tenant_id": "tenant_abc123"
  }

Step 4: Router Processing
  - Analyze: MODERATE complexity
  - Select: gpt-4o-mini (SLM)
  - Generate: "To reset your password..."
  - Cascade: Not needed (confidence 0.92)

Step 5: Usage Tracking
  - Record: tenant_abc123, gpt-4o-mini, 85 tokens, 0.8s
  - Update metrics:
    * total_queries: 1 → 2
    * slm_queries: 1 → 2
    * estimated_cost: $0.0001 → $0.0002

Step 6: Response
  {
    "response": "To reset your password...",
    "model_used": "gpt-4o-mini",
    "cost_saved": true
  }
```

---

## Summary

This architecture provides:

1. **Complete Isolation**: Each tenant has separate data, agents, and resources
2. **Cost Optimization**: 60-70% savings via intelligent SLM/LLM routing
3. **Quality Assurance**: Cascading fallback maintains response quality
4. **Scalability**: Support unlimited tenants with quota management
5. **Flexibility**: Industry-specific optimization (finance, healthcare, tech)
6. **Transparency**: Real-time usage tracking and cost analytics
7. **Security**: Tenant isolation prevents cross-contamination

Ready for production after:
- Database integration (PostgreSQL/MongoDB)
- Authentication (JWT with tenant claims)
- Billing integration (Stripe)
- Frontend updates (organization UI)
