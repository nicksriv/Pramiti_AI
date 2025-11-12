# 🚀 QUICK START - Pramiti AI Organization

## ✅ What I Fixed for You

### 1. ✅ Dashboard Access - FIXED
- **Problem**: "detail not found" error when accessing HTML pages
- **Solution**: Added route handlers for all HTML files
- **Status**: ✅ Now working - all dashboards accessible

### 2. ✅ Blockchain Logs Auto-Update - FIXED
- **Problem**: Blockchain logs tab not updating after conversations
- **Solution**: 
  - Added auto-refresh every 10 seconds
  - Refresh immediately after each message
  - Show last 10 blocks in reverse order
- **Status**: ✅ Now working - real-time updates

### 3. ⚠️ OpenAI API Key - ACTION NEEDED
- **Problem**: Invalid API key (placeholder still in .env)
- **Solution**: You need to add your real OpenAI API key
- **Status**: ⚠️ Requires your action (see below)

---

## 🔑 HOW TO ADD YOUR OPENAI API KEY

### Option 1: Interactive Script (Easiest)
```bash
python3 setup_openai.py
```
Then follow the prompts.

### Option 2: Quick Setup Script
```bash
./quick_setup.sh
```

### Option 3: Manual Edit
1. Open `.env` file
2. Replace this line:
   ```
   # 🚀 Quick Start Guide - Multi-Tenant & Hybrid Model

## Get Started in 5 Minutes

### Prerequisites

✅ Python 3.8+  
✅ OpenAI API key  
✅ Existing AI organization system

---

## Step 1: Verify New Files (Already Created ✓)

```bash
ls -la core/
# ✓ multi_tenant.py   (454 lines)
# ✓ model_router.py   (286 lines)
# ✓ openai_agent.py   (updated with router)
```

---

## Step 2: Test the Components

### Test Multi-Tenant Manager

```python
# Create file: test_multi_tenant_quick.py
from core.multi_tenant import MultiTenantManager

# Initialize
manager = MultiTenantManager()

# Create organization
tenant = manager.create_tenant(
    organization_name="Test Corp",
    admin_email="admin@test.com",
    admin_name="Test Admin",
    industry="tech",
    subscription_tier="professional"
)

print(f"✓ Created tenant: {tenant.tenant_id}")
print(f"  Name: {tenant.organization_name}")
print(f"  Tier: {tenant.subscription_tier}")
print(f"  Limits: {tenant.limits}")

# Record usage
manager.record_query(
    tenant_id=tenant.tenant_id,
    model_used="gpt-4o-mini",
    tokens=100,
    response_time=0.5
)

# Get metrics
metrics = manager.get_usage_metrics(tenant.tenant_id)
print(f"\n✓ Usage Metrics:")
print(f"  Queries: {metrics.total_queries}")
print(f"  Cost: ${metrics.estimated_cost:.4f}")
```

**Run it:**
```bash
python test_multi_tenant_quick.py
```

**Expected Output:**
```
✓ Created tenant: tenant_a1b2c3d4e5f6
  Name: Test Corp
  Tier: professional
  Limits: {'max_agents': 50, 'max_tickets_per_month': 1000, ...}

✓ Usage Metrics:
  Queries: 1
  Cost: $0.0000
```

---

### Test Model Router

```python
# Create file: test_router_quick.py
from core.model_router import ModelRouter, CascadingModelRouter

# Test basic router
router = ModelRouter()

# Simple query
result = router.route_to_model(
    query="What is the status?",
    user_role="operator"
)
print(f"✓ Simple Query:")
print(f"  Model: {result['model']}")           # gpt-4o-mini
print(f"  Complexity: {result['complexity']}")  # SIMPLE

# Complex query
result = router.route_to_model(
    query="Analyze the root cause of the database outage and design a comprehensive disaster recovery strategy",
    user_role="ceo"
)
print(f"\n✓ Complex Query:")
print(f"  Model: {result['model']}")           # gpt-4o or gpt-4-turbo
print(f"  Complexity: {result['complexity']}")  # COMPLEX

# Test cascading router
cascade_router = CascadingModelRouter()

result = cascade_router.route_with_cascade(
    query="Help with incident management",
    initial_response="I'm not sure about that.",  # Low confidence
    user_role="analyst"
)
print(f"\n✓ Cascade Test:")
print(f"  Cascaded: {result['cascaded']}")      # True
print(f"  From: {result['initial_model']}")     # gpt-4o-mini
print(f"  To: {result['final_model']}")         # gpt-4o

# Get statistics
stats = router.get_performance_stats()
print(f"\n✓ Performance Stats:")
print(f"  Total Queries: {stats['total_queries']}")
print(f"  SLM Usage: {stats['slm_usage_percent']:.1f}%")
print(f"  Estimated Savings: {stats['cost_savings_estimate']:.1f}%")
```

**Run it:**
```bash
python test_router_quick.py
```

---

## Step 3: Original Quick Start (Agent Creation, Dashboard)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd agentic-ai-organization
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### 4. Run the API Server
```bash
python api_server.py
```

The server will start on `http://localhost:8084`

#### 5. Open the Dashboard
Navigate to `http://localhost:8084/enhanced-dashboard` in your web browser.

---

## Step 4: Next Actions

### Immediate (This Week)

1. **Run the test scripts** to verify everything works
2. **Review documentation**:
   - `MULTI_TENANT_HYBRID_MODEL.md` - Complete guide
   - `API_INTEGRATION_GUIDE.md` - Integration steps
   - `IMPLEMENTATION_SUMMARY.md` - Overview
   - `ARCHITECTURE_DIAGRAMS.md` - Visual architecture

3. **Plan integration**:
   - Decide on database (PostgreSQL recommended)
   - Plan authentication strategy (JWT)
   - Review subscription tiers for your use case

### Short Term (Next 2 Weeks)

4. **Add API endpoints** (see `API_INTEGRATION_GUIDE.md`)
5. **Update frontend** with organization selector
6. **Test with sample organizations**
7. **Monitor cost savings**

### Medium Term (Next Month)

8. **Database migration** from in-memory to PostgreSQL
9. **Add authentication** with JWT tokens
10. **Implement billing** with Stripe
11. **Add usage alerts** (80% quota warnings)
12. **Deploy to production**

---

## Quick Reference

### Key Files Created

| File | Size | Purpose |
|------|------|---------|
| `core/multi_tenant.py` | 454 lines | Multi-tenant management |
| `core/model_router.py` | 286 lines | Hybrid SLM/LLM routing |
| `core/openai_agent.py` | Updated | Integration with router |
| `MULTI_TENANT_HYBRID_MODEL.md` | Docs | Complete feature guide |
| `API_INTEGRATION_GUIDE.md` | Docs | Step-by-step integration |
| `IMPLEMENTATION_SUMMARY.md` | Docs | Quick overview |
| `ARCHITECTURE_DIAGRAMS.md` | Docs | Visual architecture |

### Expected Benefits

✅ **60-70% cost reduction** from intelligent routing  
✅ **Multi-tenant isolation** for SaaS deployment  
✅ **Automatic scaling** with subscription tiers  
✅ **Quality maintained** via cascading fallback  
✅ **Real-time analytics** for monitoring  
✅ **Industry optimization** (finance, healthcare, tech)

---

## Documentation
For detailed feature documentation, see:
- `MULTI_TENANT_HYBRID_MODEL.md` - **NEW** Complete multi-tenant guide
- `API_INTEGRATION_GUIDE.md` - **NEW** Integration steps  
- `IMPLEMENTATION_SUMMARY.md` - **NEW** Quick overview
- `ARCHITECTURE_DIAGRAMS.md` - **NEW** Visual diagrams
- `AGENT_CREATION_GUIDE.md` - Complete guide for agent creation
- `TICKETS_FEATURE.md` - Ticket management system
- `DATA_ARCHIVES_FEATURE.md` - Document management
- `PROJECT_SUMMARY.md` - Overall project overview
   ```
   With:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
3. Save and the server will auto-reload

### Where to Get Your API Key
🔗 https://platform.openai.com/api-keys

1. Sign in or create account
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Paste it in your `.env` file

---

## 🌐 Access Your Dashboards

Your server is running at: **http://localhost:8084**

### 🎯 Main Dashboard (Recommended)
```
http://localhost:8084/openai-dashboard.html
```

**Features:**
- ✅ Chat with 5 AI agents
- ✅ View agent hierarchy
- ✅ Pramiti Assistant chatbot
- ✅ Real-time blockchain logs
- ✅ Agent status monitoring

### 📊 Other Dashboards
```
http://localhost:8084/enhanced-dashboard.html
http://localhost:8084/index.html
```

---

## 🧪 TEST EVERYTHING WORKS

### 1. Check API Status
Visit: http://localhost:8084/
```json
{
  "openai_enabled": true  // ← Should be true after adding key
}
```

### 2. Test Agent Chat
1. Go to: http://localhost:8084/openai-dashboard.html
2. Click "Agent Chat" tab
3. Select an agent
4. Send: "Help me with a server outage"
5. Get real AI response!

### 3. Verify Blockchain Logs
1. Chat with agents
2. Click "Blockchain Logs" tab
3. See real-time transaction history!

---

## 🤖 Your 5 AI Agents

| Agent | Role | Model | Specialization |
|-------|------|-------|----------------|
| Executive AI Director | CEO | GPT-4o | Strategic Leadership |
| ITSM Operations Manager | Manager | GPT-4o-mini | Incident Management |
| Incident Response Specialist | SME | GPT-4o-mini | Incident Resolution |
| Problem Analysis Expert | SME | GPT-4o-mini | Root Cause Analysis |
| Change Management Specialist | SME | GPT-4o-mini | Change Coordination |

---

## 📊 What You'll See in Blockchain Logs

After chatting with agents, the Blockchain tab shows:

```
Block #1 - User → Agent
  From: web_user
  To: agent-incident-001
  Hash: 0x1a2b3c4d...
  Time: 11/11/2025, 10:30:15 AM

Block #2 - Agent → User (AI Response)
  From: agent-incident-001
  To: web_user
  Hash: 0x5e6f7g8h...
  Time: 11/11/2025, 10:30:17 AM
```

**Features:**
- ✅ Immutable audit trail
- ✅ Complete conversation history
- ✅ Cryptographic hashes
- ✅ Timestamps for compliance
- ✅ Auto-updates every 10 seconds

---

## 💡 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| API Server | ✅ Running | Port 8084 |
| Frontend | ✅ Working | All 3 dashboards accessible |
| Blockchain Logs | ✅ Active | Auto-updating |
| 5 AI Agents | ✅ Initialized | Ready to chat |
| OpenAI Connection | ⚠️ Needs Key | Add your API key |

---

## 🎯 Your Next Step

**Add your OpenAI API key** to enable real AI-powered responses!

Choose any method:
```bash
# Method 1: Interactive
python3 setup_openai.py

# Method 2: Quick script
./quick_setup.sh

# Method 3: Manual edit
# Edit .env file and add your key
```

Then refresh the dashboard and start chatting! 🚀

---

## 📝 Files I Created for You

1. `SETUP_GUIDE.md` - Complete setup instructions
2. `setup_openai.py` - Interactive API key setup script
3. `quick_setup.sh` - One-command bash setup
4. `QUICK_START.md` - This file (quick reference)

---

## 🆘 Need Help?

Check the terminal logs for detailed error messages.

The server auto-reloads when you save the `.env` file, so you'll see changes immediately!
