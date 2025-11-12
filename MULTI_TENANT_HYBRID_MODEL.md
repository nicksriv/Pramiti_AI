# Multi-Tenant Organization & Hybrid Model Architecture

## Overview

The system now supports:
1. **Multi-Tenant Organizations**: Isolated data and configurations for multiple organizations
2. **Hybrid SLM/LLM Routing**: Intelligent cost optimization using model complexity analysis
3. **Cascading Fallback**: Automatic upgrade from cheaper to expensive models on low confidence

---

## 🏢 Multi-Tenant Architecture

### Key Features

- **Tenant Isolation**: Each organization has isolated agents, roles, tickets, and documents
- **Subscription Tiers**: Basic, Professional, Enterprise with different limits
- **Industry Customization**: Specific settings for finance, healthcare, tech, etc.
- **Usage Tracking**: Monitor queries, tokens, costs per tenant
- **Quota Management**: Enforce limits on agents, tickets, documents, API calls

### Tenant Configuration

```python
from core.multi_tenant import MultiTenantManager

# Initialize multi-tenant manager
tenant_manager = MultiTenantManager()

# Create a new tenant organization
tenant = tenant_manager.create_tenant(
    organization_name="Acme Corp",
    admin_email="admin@acme.com",
    admin_name="John Doe",
    industry="finance",        # finance, healthcare, tech, retail, general
    size="medium",             # small, medium, large, enterprise
    subscription_tier="professional"  # basic, professional, enterprise
)

print(f"Created tenant: {tenant.tenant_id}")
```

### Subscription Tiers & Limits

| Feature | Basic | Professional | Enterprise |
|---------|-------|--------------|------------|
| Max Agents | 10 | 50 | 500 |
| Max Roles | 5 | 20 | 100 |
| Monthly Tickets | 100 | 1,000 | 10,000 |
| Document Storage | 100 MB | 1 GB | 10 GB |
| Daily API Calls | 1,000 | 10,000 | 100,000 |

### Industry-Specific Settings

**Finance**:
- `prefer_quality = True` (uses better models)
- Compliance: SOC2, PCI-DSS
- Higher accuracy requirements

**Healthcare**:
- `prefer_quality = True`
- Compliance: HIPAA
- Data region restrictions

**Tech/Startups**:
- `prefer_cost = True` (cost optimization)
- Advanced analytics enabled
- Flexible scaling

### Tenant Data Isolation

```python
# Each tenant has isolated data
tenant_data = {
    'agents': {},           # Tenant-specific agents
    'roles': [],           # Tenant-specific roles
    'tickets': [],         # Tenant-specific tickets
    'documents': [],       # Tenant-specific documents
    'users': [],           # Tenant users
    'conversations': []    # Tenant conversations
}

# Access tenant data
agents = tenant_manager.get_tenant_agents(tenant_id)
tickets = tenant_manager.get_tenant_tickets(tenant_id)
documents = tenant_manager.get_tenant_documents(tenant_id)
```

### Usage Tracking

```python
# Record query usage
tenant_manager.record_query(
    tenant_id=tenant_id,
    model_used="gpt-4o-mini",
    tokens=150,
    response_time=0.8
)

# Get usage metrics
metrics = tenant_manager.get_usage_metrics(tenant_id)
print(f"Total queries: {metrics.total_queries}")
print(f"SLM queries: {metrics.slm_queries}")
print(f"LLM queries: {metrics.llm_queries}")
print(f"Estimated cost: ${metrics.estimated_cost:.2f}")
```

---

## 🤖 Hybrid Model Router

### How It Works

The **ModelRouter** analyzes each query to determine complexity and routes to the appropriate model:

1. **Simple Queries** → `gpt-4o-mini` (SLM) - 15x cheaper
2. **Moderate Queries** → `gpt-4o-mini` (SLM) - Still cost-effective
3. **Complex Queries** → `gpt-4o` (LLM Standard) - High quality
4. **Critical Queries** → `gpt-4-turbo-preview` (LLM Advanced) - Best quality

### Complexity Analysis

The router uses multiple heuristics:

#### 1. Keyword Detection
```python
SIMPLE_KEYWORDS = ["hello", "hi", "thanks", "status", "list"]
MODERATE_KEYWORDS = ["explain", "how to", "what is", "describe"]
COMPLEX_KEYWORDS = ["analyze", "compare", "design", "strategy", "troubleshoot"]
CRITICAL_KEYWORDS = ["critical incident", "security breach", "compliance", "audit"]
```

#### 2. Query Length
- **< 50 chars**: SIMPLE
- **50-150 chars**: MODERATE  
- **150-300 chars**: COMPLEX
- **> 300 chars**: CRITICAL

#### 3. Contextual Factors
- User role (CEO gets better models)
- Conversation length (complex discussions)
- Multiple questions (higher complexity)
- Technical indicators (code, config, logs)

### Usage Example

```python
from core.model_router import ModelRouter

router = ModelRouter()

# Route a simple query
result = router.route_to_model(
    query="What is the status of ticket #123?",
    user_role="operator"
)

print(f"Model: {result['model']}")           # gpt-4o-mini
print(f"Complexity: {result['complexity']}")  # SIMPLE
print(f"Confidence: {result['confidence']}")  # 0.95

# Route a complex query
result = router.route_to_model(
    query="Analyze the root cause of the database outage and design a comprehensive disaster recovery strategy",
    user_role="ceo"
)

print(f"Model: {result['model']}")           # gpt-4o or gpt-4-turbo-preview
print(f"Complexity: {result['complexity']}")  # COMPLEX or CRITICAL
```

### Cascading Model Router

The **CascadingModelRouter** automatically upgrades if the initial response is poor:

```python
from core.model_router import CascadingModelRouter

router = CascadingModelRouter()

result = router.route_with_cascade(
    query="Help me debug this Python code",
    initial_response="I'm not sure about that.",  # Low confidence response
    confidence_threshold=0.6
)

if result['cascaded']:
    print(f"Upgraded from {result['initial_model']} to {result['final_model']}")
    print(f"Reason: {result['cascade_reason']}")
```

**Cascade Triggers**:
1. **Low Confidence**: Response confidence < 0.6
2. **Uncertainty Phrases**: "I'm not sure", "I don't know", "Maybe"
3. **Brief Responses**: Response < 50 characters
4. **Question Responses**: Response ends with "?"

### Cost Savings Analysis

```python
router = ModelRouter()
stats = router.get_performance_stats()

print(f"SLM Usage: {stats['slm_usage_percent']:.1f}%")
print(f"Cost Savings: {stats['cost_savings_estimate']:.1f}%")
print(f"Total Queries: {stats['total_queries']}")
```

**Cost Multipliers**:
- `gpt-4o-mini`: 1.0x (baseline)
- `gpt-4o`: 15.0x (15x more expensive)
- `gpt-4-turbo-preview`: 30.0x (30x more expensive)

**Example Savings**:
If 70% of queries use SLM:
- Cost savings ≈ 60-70%
- Quality maintained via cascading
- Faster response times for simple queries

---

## 🔗 Integration with OpenAI Agent

### Creating Agents with Router

```python
from core.openai_agent import create_openai_agent

# Create agent with model router enabled (default)
agent = create_openai_agent(
    agent_type="incident_specialist",
    agent_id="agent_001",
    name="Alex Thompson",
    use_model_router=True,    # Enable intelligent routing
    tenant_id="tenant_abc123"  # Associate with tenant
)

# Create agent without router (uses default model always)
agent = create_openai_agent(
    agent_type="ceo",
    agent_id="agent_002",
    name="Sarah Johnson",
    use_model_router=False   # Disable router, use gpt-4o always
)
```

### Routing Statistics

```python
# Get routing statistics for an agent
stats = agent.get_routing_statistics()

print(f"Router enabled: {stats['router_enabled']}")
print(f"Total queries: {stats['agent_stats']['total_queries']}")
print(f"SLM queries: {stats['agent_stats']['slm_queries']}")
print(f"LLM queries: {stats['agent_stats']['llm_queries']}")
print(f"Cascaded queries: {stats['agent_stats']['cascaded_queries']}")
print(f"Cascade rate: {stats['cost_analysis']['cascade_rate']:.1f}%")
print(f"Estimated savings: {stats['cost_analysis']['estimated_savings_percent']:.1f}%")
```

### Agent Report with Cost Analysis

```python
# Generate comprehensive report
report = agent.generate_agent_report()

if report['cost_optimization']:
    cost = report['cost_optimization']
    print(f"SLM Usage: {cost['slm_usage_percent']:.1f}%")
    print(f"Cost Savings: {cost['estimated_cost_savings_percent']:.1f}%")
    print(f"Queries - Total: {cost['queries_routed']['total']}")
    print(f"Queries - SLM: {cost['queries_routed']['slm']}")
    print(f"Queries - LLM: {cost['queries_routed']['llm']}")
    print(f"Queries - Cascaded: {cost['queries_routed']['cascaded']}")
```

---

## 📊 Multi-Tenant Statistics

### Overall System Stats

```python
stats = tenant_manager.get_tenant_statistics()

print(f"Total Tenants: {stats['total_tenants']}")
print(f"Tier Distribution: {stats['tier_distribution']}")
print(f"Industry Distribution: {stats['industry_distribution']}")
print(f"Total Queries (All Tenants): {stats['total_queries_all_tenants']}")
print(f"Total Cost (All Tenants): ${stats['total_estimated_cost']:.2f}")
```

### Per-Tenant Analytics

```python
for tenant_info in stats['tenants']:
    tenant_id = tenant_info['tenant_id']
    metrics = tenant_manager.get_usage_metrics(tenant_id)
    
    print(f"\n{tenant_info['name']} ({tenant_info['tier']})")
    print(f"  Queries: {metrics.total_queries}")
    print(f"  SLM: {metrics.slm_queries} ({metrics.slm_queries/metrics.total_queries*100:.1f}%)")
    print(f"  LLM: {metrics.llm_queries} ({metrics.llm_queries/metrics.total_queries*100:.1f}%)")
    print(f"  Cost: ${metrics.estimated_cost:.2f}")
    print(f"  Avg Response Time: {metrics.avg_response_time:.2f}s")
```

---

## 🔐 Tenant Isolation Best Practices

### 1. Always Use Tenant Context

```python
# BAD - No tenant context
agents = get_all_agents()  # Returns agents from all tenants!

# GOOD - Tenant-specific
agents = tenant_manager.get_tenant_agents(tenant_id)
```

### 2. Enforce Quota Limits

```python
# Check limits before creating resources
within_limit, limit = tenant_manager.check_limits(
    tenant_id=tenant_id,
    resource='agents',
    current_value=len(current_agents)
)

if not within_limit:
    raise Exception(f"Agent limit ({limit}) exceeded for tenant")
```

### 3. Track Usage for Billing

```python
# Always record queries for billing
tenant_manager.record_query(
    tenant_id=tenant_id,
    model_used=model_name,
    tokens=token_count,
    response_time=elapsed_time
)
```

### 4. Export Tenant Data

```python
# Backup or migration
data = tenant_manager.export_tenant_data(tenant_id)

# Save to file
import json
with open(f"{tenant_id}_backup.json", "w") as f:
    json.dump(data, f, indent=2, default=str)
```

---

## 🎯 Optimization Strategies

### For Cost-Conscious Tenants

```python
# Update tenant preferences
tenant_manager.update_tenant(tenant_id, {
    "prefer_cost": True,
    "prefer_quality": False,
    "max_monthly_budget": 500.0  # USD
})

# Optimize router for tenant
router = ModelRouter()
router.optimize_for_tenant(
    tenant_id=tenant_id,
    preferences={
        "prefer_quality": False,
        "prefer_cost": True
    }
)
```

### For Quality-Focused Tenants (Finance, Healthcare)

```python
# Update tenant preferences
tenant_manager.update_tenant(tenant_id, {
    "prefer_quality": True,
    "prefer_cost": False
})

# Optimize router
router.optimize_for_tenant(
    tenant_id=tenant_id,
    preferences={
        "prefer_quality": True,
        "industry": "finance"
    }
)
```

---

## 📈 Expected Performance

### Cost Optimization

With intelligent routing:
- **60-80%** of queries use SLM (gpt-4o-mini)
- **Overall cost reduction**: 60-70%
- **Cascade rate**: ~5-10% (upgrades when needed)
- **Quality maintained**: Cascading ensures accuracy

### Tenant Capacity

| Tier | Agents | Monthly Queries | Est. Monthly Cost |
|------|--------|-----------------|-------------------|
| Basic | 10 | 3,000 | $50-100 |
| Professional | 50 | 30,000 | $300-600 |
| Enterprise | 500 | 300,000 | $2,000-4,000 |

*Costs estimated with 70% SLM usage*

---

## 🚀 Next Steps

### Immediate Integration

1. **Update API Server**: Add multi-tenant middleware
2. **Add Organization Endpoints**: Create/list/manage organizations
3. **Update Agent Creation**: Include tenant_id parameter
4. **Add Usage Dashboard**: Visualize cost savings and routing stats
5. **Implement Billing**: Track usage and generate invoices

### Future Enhancements

1. **Database Integration**: Move from in-memory to PostgreSQL/MongoDB
2. **SSO Integration**: Enterprise authentication
3. **Custom Models**: Per-tenant fine-tuned models
4. **Advanced Analytics**: Predictive cost analysis
5. **API Keys**: Tenant-specific API authentication
6. **Webhooks**: Real-time notifications for quota limits

---

## 📚 API Reference

### Multi-Tenant Manager

```python
class MultiTenantManager:
    def create_tenant(...) -> TenantConfig
    def get_tenant(tenant_id) -> TenantConfig
    def list_tenants() -> List[TenantConfig]
    def update_tenant(tenant_id, updates) -> bool
    def delete_tenant(tenant_id) -> bool
    def get_tenant_data(tenant_id, data_type) -> Any
    def add_tenant_agent(tenant_id, agent_id, agent_data) -> bool
    def record_query(tenant_id, model_used, tokens, response_time)
    def get_usage_metrics(tenant_id) -> TenantUsageMetrics
    def check_limits(tenant_id, resource, current_value) -> (bool, int)
    def export_tenant_data(tenant_id) -> Dict
    def get_tenant_statistics() -> Dict
```

### Model Router

```python
class ModelRouter:
    def analyze_query_complexity(query, ...) -> QueryComplexity
    def route_to_model(query, ...) -> Dict
    def get_performance_stats() -> Dict
    def optimize_for_tenant(tenant_id, preferences) -> bool

class CascadingModelRouter(ModelRouter):
    def route_with_cascade(query, initial_response, ...) -> Dict
```

### OpenAI Agent

```python
class OpenAIAgent:
    def __init__(..., use_model_router=True, tenant_id=None)
    async def process_message(message) -> Message
    def generate_agent_report() -> Dict
    def get_routing_statistics() -> Dict
    def get_blockchain_audit_trail(message_id) -> Dict
```

---

## 💡 Tips & Best Practices

1. **Start with router enabled**: Let 70% of queries use cheap SLM
2. **Monitor cascade rate**: Should be 5-10%, higher means poor routing
3. **Customize per industry**: Finance/healthcare need quality, startups need cost savings
4. **Track usage daily**: Prevent quota exhaustion
5. **Use blockchain logging**: Immutable audit trail for compliance
6. **Export tenant data regularly**: Backups for disaster recovery
7. **Test with sample queries**: Validate routing before production
8. **Review cost savings monthly**: Optimize routing thresholds

---

## 🔍 Troubleshooting

### Router always uses LLM

**Cause**: Queries detected as complex
**Fix**: Adjust complexity keywords or length thresholds

### Too many cascades

**Cause**: SLM responses have low confidence
**Fix**: Lower cascade threshold or improve prompts

### Tenant quota exceeded

**Cause**: Usage beyond tier limits
**Fix**: Upgrade tier or implement rate limiting

### Cross-tenant data leak

**Cause**: Missing tenant_id in queries
**Fix**: Always filter by tenant_id in data access

---

For implementation examples, see:
- `core/multi_tenant.py` - Multi-tenant management
- `core/model_router.py` - Hybrid routing logic
- `core/openai_agent.py` - Integration with agents
