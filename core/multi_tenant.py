"""
Multi-Tenant Organization Manager
Supports multiple organizations with isolated data and configurations
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class TenantConfig:
    """Configuration for a tenant organization"""
    tenant_id: str
    organization_name: str
    industry: str  # finance, healthcare, tech, retail, etc.
    size: str  # small, medium, large, enterprise
    created_at: datetime = field(default_factory=datetime.now)
    
    # Model preferences
    prefer_quality: bool = False  # Prefer better models over cost
    prefer_cost: bool = True      # Prefer cost savings
    max_monthly_budget: Optional[float] = None  # USD
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        'blockchain_logging': True,
        'advanced_analytics': False,
        'custom_models': False,
        'api_access': True,
        'sso': False,
        'data_retention_days': 90
    })
    
    # Customization
    branding: Dict[str, str] = field(default_factory=lambda: {
        'primary_color': '#667eea',
        'logo_url': '',
        'company_url': ''
    })
    
    # Limits and quotas
    limits: Dict[str, int] = field(default_factory=lambda: {
        'max_agents': 50,
        'max_roles': 20,
        'max_tickets_per_month': 1000,
        'max_documents_mb': 1000,
        'max_api_calls_per_day': 10000
    })
    
    # Contact info
    admin_email: str = ""
    admin_name: str = ""
    
    # Billing
    subscription_tier: str = "basic"  # basic, professional, enterprise
    billing_cycle: str = "monthly"
    
    # Compliance
    compliance_requirements: List[str] = field(default_factory=list)  # GDPR, HIPAA, SOC2, etc.
    data_region: str = "us-east-1"
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantUsageMetrics:
    """Track tenant usage for billing and limits"""
    tenant_id: str
    period_start: datetime
    period_end: datetime
    
    # Usage counters
    total_queries: int = 0
    slm_queries: int = 0
    llm_queries: int = 0
    total_tokens: int = 0
    
    # Resource usage
    active_agents: int = 0
    total_tickets: int = 0
    documents_stored_mb: float = 0.0
    api_calls: int = 0
    
    # Costs
    estimated_cost: float = 0.0
    
    # Performance
    avg_response_time: float = 0.0
    error_rate: float = 0.0


class MultiTenantManager:
    """
    Manages multiple tenant organizations with isolated data and configurations
    """
    
    def __init__(self):
        self.tenants: Dict[str, TenantConfig] = {}
        self.tenant_data: Dict[str, Dict[str, Any]] = {}  # Isolated data storage
        self.usage_metrics: Dict[str, TenantUsageMetrics] = {}
        
        logger.info("Multi-tenant manager initialized")
    
    def create_tenant(self, 
                     organization_name: str,
                     admin_email: str,
                     admin_name: str,
                     industry: str = "general",
                     size: str = "small",
                     subscription_tier: str = "basic") -> TenantConfig:
        """
        Create a new tenant organization
        
        Args:
            organization_name: Name of the organization
            admin_email: Admin email
            admin_name: Admin name
            industry: Industry type
            size: Organization size
            subscription_tier: Subscription level
            
        Returns:
            TenantConfig object
        """
        tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
        
        # Create tenant config
        tenant = TenantConfig(
            tenant_id=tenant_id,
            organization_name=organization_name,
            industry=industry,
            size=size,
            admin_email=admin_email,
            admin_name=admin_name,
            subscription_tier=subscription_tier
        )
        
        # Set tier-specific limits
        tenant.limits = self._get_tier_limits(subscription_tier)
        
        # Set industry-specific preferences
        if industry == "finance":
            tenant.prefer_quality = True
            tenant.compliance_requirements = ["SOC2", "PCI-DSS"]
        elif industry == "healthcare":
            tenant.prefer_quality = True
            tenant.compliance_requirements = ["HIPAA"]
        elif industry == "tech":
            tenant.features['advanced_analytics'] = True
        
        # Initialize tenant data storage
        self.tenant_data[tenant_id] = {
            'agents': {},
            'roles': [],
            'tickets': [],
            'documents': [],
            'users': [],
            'conversations': []
        }
        
        # Initialize usage metrics
        self.usage_metrics[tenant_id] = TenantUsageMetrics(
            tenant_id=tenant_id,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        # Store tenant
        self.tenants[tenant_id] = tenant
        
        logger.info(f"Created tenant: {tenant_id} - {organization_name} ({subscription_tier})")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration"""
        return self.tenants.get(tenant_id)
    
    def list_tenants(self) -> List[TenantConfig]:
        """List all tenants"""
        return list(self.tenants.values())
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant configuration"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            logger.error(f"Tenant not found: {tenant_id}")
            return False
        
        # Update allowed fields
        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        logger.info(f"Updated tenant: {tenant_id}")
        return True
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant and all associated data
        WARNING: This is irreversible!
        """
        if tenant_id not in self.tenants:
            return False
        
        # Remove tenant data
        if tenant_id in self.tenant_data:
            del self.tenant_data[tenant_id]
        
        # Remove metrics
        if tenant_id in self.usage_metrics:
            del self.usage_metrics[tenant_id]
        
        # Remove tenant config
        del self.tenants[tenant_id]
        
        logger.warning(f"Deleted tenant: {tenant_id}")
        return True
    
    def _get_tier_limits(self, tier: str) -> Dict[str, int]:
        """Get limits based on subscription tier"""
        tier_limits = {
            'basic': {
                'max_agents': 10,
                'max_roles': 5,
                'max_tickets_per_month': 100,
                'max_documents_mb': 100,
                'max_api_calls_per_day': 1000
            },
            'professional': {
                'max_agents': 50,
                'max_roles': 20,
                'max_tickets_per_month': 1000,
                'max_documents_mb': 1000,
                'max_api_calls_per_day': 10000
            },
            'enterprise': {
                'max_agents': 500,
                'max_roles': 100,
                'max_tickets_per_month': 10000,
                'max_documents_mb': 10000,
                'max_api_calls_per_day': 100000
            }
        }
        return tier_limits.get(tier, tier_limits['basic'])
    
    # ===== DATA ISOLATION =====
    
    def get_tenant_data(self, tenant_id: str, data_type: str) -> Any:
        """Get tenant-specific data (agents, roles, tickets, etc.)"""
        if tenant_id not in self.tenant_data:
            return None
        return self.tenant_data[tenant_id].get(data_type, [])
    
    def set_tenant_data(self, tenant_id: str, data_type: str, data: Any) -> bool:
        """Set tenant-specific data"""
        if tenant_id not in self.tenant_data:
            return False
        self.tenant_data[tenant_id][data_type] = data
        return True
    
    def add_tenant_item(self, tenant_id: str, data_type: str, item: Any) -> bool:
        """Add item to tenant data collection"""
        if tenant_id not in self.tenant_data:
            return False
        
        if data_type not in self.tenant_data[tenant_id]:
            self.tenant_data[tenant_id][data_type] = []
        
        self.tenant_data[tenant_id][data_type].append(item)
        return True
    
    # ===== USAGE TRACKING =====
    
    def record_query(self, tenant_id: str, model_used: str, tokens: int, response_time: float):
        """Record a query for usage tracking"""
        if tenant_id not in self.usage_metrics:
            return
        
        metrics = self.usage_metrics[tenant_id]
        metrics.total_queries += 1
        metrics.total_tokens += tokens
        
        if model_used == "gpt-4o-mini":
            metrics.slm_queries += 1
        else:
            metrics.llm_queries += 1
        
        # Update average response time
        if metrics.total_queries == 1:
            metrics.avg_response_time = response_time
        else:
            metrics.avg_response_time = (
                (metrics.avg_response_time * (metrics.total_queries - 1) + response_time) 
                / metrics.total_queries
            )
        
        # Estimate cost (rough approximation)
        cost_per_1k_tokens = {
            "gpt-4o-mini": 0.00015,
            "gpt-4o": 0.0025,
            "gpt-4-turbo-preview": 0.01
        }
        cost = (tokens / 1000) * cost_per_1k_tokens.get(model_used, 0.001)
        metrics.estimated_cost += cost
    
    def get_usage_metrics(self, tenant_id: str) -> Optional[TenantUsageMetrics]:
        """Get usage metrics for tenant"""
        return self.usage_metrics.get(tenant_id)
    
    def check_limits(self, tenant_id: str, resource: str, current_value: int) -> tuple[bool, Optional[int]]:
        """
        Check if tenant is within limits
        
        Returns:
            (within_limits, limit_value)
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False, None
        
        limit_key = f"max_{resource}"
        limit = tenant.limits.get(limit_key)
        
        if limit is None:
            return True, None
        
        return current_value < limit, limit
    
    # ===== TENANT ISOLATION HELPERS =====
    
    def get_tenant_agents(self, tenant_id: str) -> Dict[str, Any]:
        """Get all agents for a tenant"""
        return self.get_tenant_data(tenant_id, 'agents') or {}
    
    def add_tenant_agent(self, tenant_id: str, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Add agent to tenant"""
        agents = self.get_tenant_agents(tenant_id)
        
        # Check limits
        within_limit, limit = self.check_limits(tenant_id, 'agents', len(agents))
        if not within_limit:
            logger.warning(f"Tenant {tenant_id} exceeded agent limit ({limit})")
            return False
        
        agents[agent_id] = agent_data
        return self.set_tenant_data(tenant_id, 'agents', agents)
    
    def get_tenant_tickets(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all tickets for a tenant"""
        return self.get_tenant_data(tenant_id, 'tickets') or []
    
    def get_tenant_documents(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a tenant"""
        return self.get_tenant_data(tenant_id, 'documents') or []
    
    # ===== EXPORT/IMPORT =====
    
    def export_tenant_data(self, tenant_id: str) -> Dict[str, Any]:
        """Export all tenant data (for backup or migration)"""
        if tenant_id not in self.tenants:
            return {}
        
        return {
            'tenant_config': self.tenants[tenant_id].__dict__,
            'tenant_data': self.tenant_data.get(tenant_id, {}),
            'usage_metrics': self.usage_metrics.get(tenant_id).__dict__ if tenant_id in self.usage_metrics else {},
            'exported_at': datetime.now().isoformat()
        }
    
    def get_tenant_statistics(self) -> Dict[str, Any]:
        """Get overall multi-tenant statistics"""
        total_tenants = len(self.tenants)
        
        # Count by tier
        tier_counts = {}
        industry_counts = {}
        
        for tenant in self.tenants.values():
            tier_counts[tenant.subscription_tier] = tier_counts.get(tenant.subscription_tier, 0) + 1
            industry_counts[tenant.industry] = industry_counts.get(tenant.industry, 0) + 1
        
        # Calculate total usage
        total_queries = sum(m.total_queries for m in self.usage_metrics.values())
        total_cost = sum(m.estimated_cost for m in self.usage_metrics.values())
        
        return {
            'total_tenants': total_tenants,
            'tier_distribution': tier_counts,
            'industry_distribution': industry_counts,
            'total_queries_all_tenants': total_queries,
            'total_estimated_cost': total_cost,
            'tenants': [
                {
                    'tenant_id': t.tenant_id,
                    'name': t.organization_name,
                    'tier': t.subscription_tier,
                    'created': t.created_at.isoformat()
                }
                for t in self.tenants.values()
            ]
        }
