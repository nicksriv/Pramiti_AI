"""
Hybrid Model Router - Intelligent routing between SLM and LLM
Routes simple queries to cost-effective models, complex queries to powerful models
"""

import re
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"           # Basic questions, greetings, simple lookups
    MODERATE = "moderate"       # Multi-step reasoning, moderate context
    COMPLEX = "complex"         # Deep analysis, multi-document reasoning
    CRITICAL = "critical"       # High-stakes decisions, requires best model

class ModelTier(Enum):
    """Available model tiers"""
    SLM = "gpt-4o-mini"                    # Small: Fast, cheap, simple queries
    LLM_STANDARD = "gpt-4o"                # Large: Complex reasoning
    LLM_ADVANCED = "gpt-4-turbo-preview"   # Advanced: Critical tasks
    
class ModelRouter:
    """
    Intelligent router that analyzes queries and selects optimal model
    """
    
    def __init__(self):
        self.complexity_keywords = {
            QueryComplexity.SIMPLE: [
                'hello', 'hi', 'hey', 'thanks', 'thank you',
                'what is', 'who is', 'when is', 'where is',
                'yes', 'no', 'ok', 'okay', 'sure',
                'status', 'list', 'show me'
            ],
            QueryComplexity.MODERATE: [
                'explain', 'how does', 'compare', 'difference',
                'analyze', 'summarize', 'why', 'because',
                'steps', 'process', 'procedure'
            ],
            QueryComplexity.COMPLEX: [
                'strategy', 'optimize', 'architect', 'design',
                'evaluate', 'recommend', 'decide', 'plan',
                'integrate', 'troubleshoot', 'debug',
                'comprehensive', 'detailed analysis'
            ],
            QueryComplexity.CRITICAL: [
                'security breach', 'critical incident', 'emergency',
                'compliance violation', 'audit', 'legal',
                'executive decision', 'budget approval'
            ]
        }
        
        # Complexity thresholds
        self.length_thresholds = {
            'simple': 50,      # Less than 50 chars
            'moderate': 150,   # 50-150 chars
            'complex': 300     # 150+ chars
        }
        
        # Model routing map
        self.model_map = {
            QueryComplexity.SIMPLE: ModelTier.SLM,
            QueryComplexity.MODERATE: ModelTier.SLM,
            QueryComplexity.COMPLEX: ModelTier.LLM_STANDARD,
            QueryComplexity.CRITICAL: ModelTier.LLM_ADVANCED
        }
        
        # Performance tracking
        self.routing_stats = {
            'simple': 0,
            'moderate': 0,
            'complex': 0,
            'critical': 0
        }
    
    def analyze_query_complexity(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryComplexity:
        """
        Analyze query complexity using multiple heuristics
        
        Args:
            query: User query text
            context: Optional context (user role, history, etc.)
            
        Returns:
            QueryComplexity enum
        """
        query_lower = query.lower()
        
        # 1. Check for critical keywords first
        for keyword in self.complexity_keywords[QueryComplexity.CRITICAL]:
            if keyword in query_lower:
                logger.info(f"Critical query detected: '{keyword}' in query")
                return QueryComplexity.CRITICAL
        
        # 2. Check for complex keywords
        complex_count = sum(1 for kw in self.complexity_keywords[QueryComplexity.COMPLEX] 
                          if kw in query_lower)
        if complex_count >= 2:
            logger.info(f"Complex query detected: {complex_count} complex keywords")
            return QueryComplexity.COMPLEX
        
        # 3. Check query length
        if len(query) > self.length_thresholds['complex']:
            return QueryComplexity.COMPLEX
        
        # 4. Check for moderate complexity
        moderate_count = sum(1 for kw in self.complexity_keywords[QueryComplexity.MODERATE] 
                           if kw in query_lower)
        if moderate_count >= 1 or len(query) > self.length_thresholds['moderate']:
            return QueryComplexity.MODERATE
        
        # 5. Check for multiple questions
        if query.count('?') > 1:
            return QueryComplexity.MODERATE
        
        # 6. Check context-based complexity
        if context:
            # If user has executive role, use better models
            if context.get('role') in ['ceo', 'senior_manager']:
                if len(query) > self.length_thresholds['simple']:
                    return QueryComplexity.COMPLEX
            
            # If part of ongoing conversation, may need context
            if context.get('conversation_length', 0) > 3:
                return QueryComplexity.MODERATE
        
        # 7. Default to simple
        return QueryComplexity.SIMPLE
    
    def route_to_model(self, query: str, context: Optional[Dict[str, Any]] = None, 
                      force_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Route query to appropriate model
        
        Args:
            query: User query
            context: Optional context
            force_model: Force specific model (for testing)
            
        Returns:
            Dict with model selection and metadata
        """
        if force_model:
            return {
                'model': force_model,
                'complexity': 'forced',
                'reason': 'Manual override'
            }
        
        # Analyze complexity
        complexity = self.analyze_query_complexity(query, context)
        
        # Get model for complexity
        model_tier = self.model_map[complexity]
        
        # Update stats
        self.routing_stats[complexity.value] += 1
        
        # Calculate estimated cost savings
        cost_multiplier = self._get_cost_multiplier(model_tier)
        
        routing_decision = {
            'model': model_tier.value,
            'complexity': complexity.value,
            'reason': self._get_routing_reason(complexity, query),
            'estimated_cost_multiplier': cost_multiplier,
            'query_length': len(query)
        }
        
        logger.info(f"Routing decision: {routing_decision}")
        return routing_decision
    
    def _get_routing_reason(self, complexity: QueryComplexity, query: str) -> str:
        """Generate human-readable routing reason"""
        reasons = {
            QueryComplexity.SIMPLE: f"Simple query ({len(query)} chars) - using cost-effective SLM",
            QueryComplexity.MODERATE: f"Moderate complexity ({len(query)} chars) - using SLM with enhanced context",
            QueryComplexity.COMPLEX: f"Complex reasoning required ({len(query)} chars) - using LLM",
            QueryComplexity.CRITICAL: "Critical query - using most capable model"
        }
        return reasons.get(complexity, "Unknown complexity")
    
    def _get_cost_multiplier(self, model_tier: ModelTier) -> float:
        """
        Estimate cost multiplier relative to base SLM
        Based on approximate OpenAI pricing
        """
        multipliers = {
            ModelTier.SLM: 1.0,              # Base cost
            ModelTier.LLM_STANDARD: 15.0,    # ~15x more expensive
            ModelTier.LLM_ADVANCED: 30.0     # ~30x more expensive
        }
        return multipliers.get(model_tier, 1.0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get routing performance statistics"""
        total = sum(self.routing_stats.values())
        if total == 0:
            return {'error': 'No queries processed yet'}
        
        # Calculate percentages
        percentages = {
            complexity: (count / total * 100)
            for complexity, count in self.routing_stats.items()
        }
        
        # Estimate cost savings (assuming all queries used LLM)
        slm_queries = self.routing_stats['simple'] + self.routing_stats['moderate']
        estimated_savings = (slm_queries * 14.0)  # 14x cost difference saved
        
        return {
            'total_queries': total,
            'distribution': self.routing_stats,
            'distribution_percentage': percentages,
            'slm_usage_percent': (slm_queries / total * 100),
            'estimated_cost_savings_multiplier': estimated_savings,
            'message': f"{slm_queries}/{total} queries handled by SLM, saving ~{estimated_savings:.1f}x in costs"
        }
    
    def optimize_for_tenant(self, tenant_config: Dict[str, Any]) -> None:
        """
        Customize routing logic for specific tenant needs
        
        Args:
            tenant_config: Tenant-specific configuration
        """
        # Adjust thresholds based on tenant preferences
        if tenant_config.get('prefer_quality'):
            # Lower threshold for complex routing
            self.model_map[QueryComplexity.MODERATE] = ModelTier.LLM_STANDARD
        
        if tenant_config.get('prefer_cost'):
            # Higher threshold, keep more queries on SLM
            self.model_map[QueryComplexity.COMPLEX] = ModelTier.SLM
        
        if tenant_config.get('industry') == 'finance':
            # Financial sector needs better models for accuracy
            self.model_map[QueryComplexity.MODERATE] = ModelTier.LLM_STANDARD
        
        logger.info(f"Router optimized for tenant: {tenant_config.get('tenant_id')}")


class CascadingModelRouter(ModelRouter):
    """
    Advanced router that can cascade queries from SLM to LLM
    if confidence is low or response quality is poor
    """
    
    def __init__(self):
        super().__init__()
        self.cascade_threshold = 0.6  # Confidence threshold for cascading
        self.cascade_count = 0
    
    async def route_with_cascade(self, query: str, initial_response: str, 
                                 confidence: float, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Decide whether to cascade to better model based on response quality
        
        Args:
            query: Original query
            initial_response: Response from initial model
            confidence: Confidence score (0-1)
            context: Optional context
            
        Returns:
            Cascade decision
        """
        should_cascade = False
        reason = ""
        
        # Check confidence threshold
        if confidence < self.cascade_threshold:
            should_cascade = True
            reason = f"Low confidence ({confidence:.2f} < {self.cascade_threshold})"
        
        # Check for uncertainty phrases in response
        uncertainty_phrases = [
            "i'm not sure", "i don't know", "unclear", 
            "may or may not", "possibly", "perhaps"
        ]
        if any(phrase in initial_response.lower() for phrase in uncertainty_phrases):
            should_cascade = True
            reason = "Uncertainty detected in response"
        
        # Check response length (very short may indicate inability to answer)
        if len(initial_response) < 50:
            should_cascade = True
            reason = "Response too brief, may need better model"
        
        if should_cascade:
            self.cascade_count += 1
            logger.warning(f"Cascading query to better model: {reason}")
            
            # Get next tier model
            current_complexity = self.analyze_query_complexity(query, context)
            next_tier = self._get_next_tier(current_complexity)
            
            return {
                'should_cascade': True,
                'reason': reason,
                'next_model': next_tier.value,
                'cascade_count': self.cascade_count
            }
        
        return {
            'should_cascade': False,
            'reason': 'Response quality acceptable'
        }
    
    def _get_next_tier(self, current_complexity: QueryComplexity) -> ModelTier:
        """Get next higher tier model"""
        upgrade_map = {
            QueryComplexity.SIMPLE: ModelTier.LLM_STANDARD,
            QueryComplexity.MODERATE: ModelTier.LLM_STANDARD,
            QueryComplexity.COMPLEX: ModelTier.LLM_ADVANCED,
            QueryComplexity.CRITICAL: ModelTier.LLM_ADVANCED
        }
        return upgrade_map.get(current_complexity, ModelTier.LLM_STANDARD)
