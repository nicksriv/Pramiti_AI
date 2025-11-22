"""
Role-Based Access Control (RBAC) System
Provides server-side authorization for API endpoints
"""

from enum import Enum
from typing import List, Optional, Callable, Dict, Set
from functools import wraps
from fastapi import HTTPException, Header, status
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in hierarchical order (lowest to highest privilege)"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Permission(str, Enum):
    """Granular permissions for different operations"""
    # Dashboard & Analytics
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_KPI = "view_kpi"
    
    # Agent Management
    VIEW_AGENTS = "view_agents"
    CREATE_AGENTS = "create_agents"
    UPDATE_AGENTS = "update_agents"
    DELETE_AGENTS = "delete_agents"
    ENABLE_DISABLE_AGENTS = "enable_disable_agents"
    
    # Chat & Communication
    CHAT_WITH_AGENTS = "chat_with_agents"
    CHAT_WITH_USER_BOT = "chat_with_user_bot"
    CHAT_WITH_RAG = "chat_with_rag"
    VIEW_CHAT_HISTORY = "view_chat_history"
    VIEW_COMMUNICATIONS = "view_communications"
    
    # Blockchain & Audit
    VIEW_BLOCKCHAIN = "view_blockchain"
    VIEW_BLOCKCHAIN_LOGS = "view_blockchain_logs"
    VIEW_AUDIT_TRAIL = "view_audit_trail"
    
    # Organization Management
    VIEW_ORGANIZATIONS = "view_organizations"
    CREATE_ORGANIZATIONS = "create_organizations"
    UPDATE_ORGANIZATIONS = "update_organizations"
    DELETE_ORGANIZATIONS = "delete_organizations"
    
    # Hierarchy Management
    VIEW_HIERARCHY = "view_hierarchy"
    MODIFY_HIERARCHY = "modify_hierarchy"
    
    # Role Management
    VIEW_ROLES = "view_roles"
    CREATE_ROLES = "create_roles"
    UPDATE_ROLES = "update_roles"
    DELETE_ROLES = "delete_roles"
    ASSIGN_ROLES = "assign_roles"
    
    # Connector Management
    VIEW_CONNECTORS = "view_connectors"
    CREATE_CONNECTORS = "create_connectors"
    UPDATE_CONNECTORS = "update_connectors"
    DELETE_CONNECTORS = "delete_connectors"
    AUTHORIZE_CONNECTORS = "authorize_connectors"
    MANAGE_CONNECTORS = "manage_connectors"
    
    # Ticket Management
    VIEW_TICKETS = "view_tickets"
    CREATE_TICKETS = "create_tickets"
    UPDATE_TICKETS = "update_tickets"
    DELETE_TICKETS = "delete_tickets"
    ASSIGN_TICKETS = "assign_tickets"
    
    # Data & Archives
    VIEW_ARCHIVES = "view_archives"
    CREATE_ARCHIVES = "create_archives"
    DELETE_ARCHIVES = "delete_archives"
    MANAGE_ARCHIVES = "manage_archives"
    EXPORT_DATA = "export_data"
    
    # OAuth & Authentication
    SETUP_OAUTH = "setup_oauth"
    
    # Knowledge Base & RAG
    VIEW_KNOWLEDGE_BASE = "view_knowledge_base"
    SUBMIT_FEEDBACK = "submit_feedback"
    
    # Settings
    VIEW_SETTINGS = "view_settings"
    UPDATE_SETTINGS = "update_settings"
    
    # RAG Knowledge Base
    VIEW_RAG_STATS = "view_rag_stats"
    SUBMIT_RAG_FEEDBACK = "submit_rag_feedback"
    MANAGE_RAG_KB = "manage_rag_kb"


# Role-Permission Matrix
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.USER: {
        # Users can only chat and view their own data
        Permission.CHAT_WITH_USER_BOT,
        Permission.CHAT_WITH_RAG,
        Permission.SUBMIT_FEEDBACK,
        Permission.VIEW_RAG_STATS,
        Permission.CREATE_TICKETS,
        Permission.VIEW_TICKETS,  # Only their own
        Permission.VIEW_CHAT_HISTORY,  # Only their own
    },
    
    Role.ADMIN: {
        # Admins have most permissions except super_admin-only features
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_KPI,
        
        Permission.VIEW_AGENTS,
        Permission.CREATE_AGENTS,
        Permission.UPDATE_AGENTS,
        Permission.DELETE_AGENTS,
        Permission.ENABLE_DISABLE_AGENTS,
        
        Permission.CHAT_WITH_AGENTS,
        Permission.CHAT_WITH_USER_BOT,
        Permission.CHAT_WITH_RAG,
        Permission.VIEW_CHAT_HISTORY,
        Permission.VIEW_COMMUNICATIONS,
        
        Permission.VIEW_BLOCKCHAIN,
        Permission.VIEW_BLOCKCHAIN_LOGS,
        Permission.VIEW_AUDIT_TRAIL,
        
        Permission.VIEW_ROLES,
        Permission.CREATE_ROLES,
        Permission.UPDATE_ROLES,
        
        Permission.VIEW_CONNECTORS,
        Permission.CREATE_CONNECTORS,
        Permission.UPDATE_CONNECTORS,
        Permission.DELETE_CONNECTORS,
        Permission.AUTHORIZE_CONNECTORS,
        Permission.MANAGE_CONNECTORS,
        
        Permission.VIEW_TICKETS,
        Permission.CREATE_TICKETS,
        Permission.UPDATE_TICKETS,
        Permission.DELETE_TICKETS,
        Permission.ASSIGN_TICKETS,
        
        Permission.VIEW_ARCHIVES,
        Permission.CREATE_ARCHIVES,
        Permission.MANAGE_ARCHIVES,
        Permission.EXPORT_DATA,
        
        Permission.VIEW_KNOWLEDGE_BASE,
        Permission.SUBMIT_FEEDBACK,
        
        Permission.VIEW_SETTINGS,
        Permission.UPDATE_SETTINGS,
        
        Permission.VIEW_RAG_STATS,
        Permission.SUBMIT_RAG_FEEDBACK,
        Permission.MANAGE_RAG_KB,
    },
    
    Role.SUPER_ADMIN: set(Permission),  # Super admins have ALL permissions
}


class RBACManager:
    """Manages role-based access control"""
    
    def __init__(self):
        self.role_hierarchy = {
            Role.USER: 1,
            Role.ADMIN: 2,
            Role.SUPER_ADMIN: 3
        }
    
    def has_permission(self, user_role: str, required_permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        try:
            role = Role(user_role.lower())
            return required_permission in ROLE_PERMISSIONS.get(role, set())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid role: {user_role}")
            return False
    
    def has_role(self, user_role: str, required_role: Role) -> bool:
        """Check if user role meets minimum required role (hierarchical)"""
        try:
            user_role_enum = Role(user_role.lower())
            return self.role_hierarchy[user_role_enum] >= self.role_hierarchy[required_role]
        except (ValueError, AttributeError, KeyError):
            logger.warning(f"Invalid role comparison: {user_role} vs {required_role}")
            return False
    
    def get_user_permissions(self, user_role: str) -> Set[Permission]:
        """Get all permissions for a role"""
        try:
            role = Role(user_role.lower())
            return ROLE_PERMISSIONS.get(role, set())
        except (ValueError, AttributeError):
            return set()


# Global RBAC manager instance
rbac_manager = RBACManager()


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission for an endpoint
    
    Usage:
        @app.get("/api/v1/agents")
        @require_permission(Permission.VIEW_AGENTS)
        async def get_agents(current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user_role = current_user.get('role', 'user')
            
            if not rbac_manager.has_permission(user_role, permission):
                logger.warning(
                    f"Permission denied: User {current_user.get('user_id')} "
                    f"(role: {user_role}) attempted to access {permission.value}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(min_role: Role):
    """
    Decorator to require a minimum role level for an endpoint
    
    Usage:
        @app.post("/api/v1/organizations")
        @require_role(Role.SUPER_ADMIN)
        async def create_organization(current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user_role = current_user.get('role', 'user')
            
            if not rbac_manager.has_role(user_role, min_role):
                logger.warning(
                    f"Role check failed: User {current_user.get('user_id')} "
                    f"(role: {user_role}) attempted to access {min_role.value}-only endpoint"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role. Required: {min_role.value} or higher"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """
    Decorator to require ANY of the specified permissions
    
    Usage:
        @app.get("/api/v1/data")
        @require_any_permission(Permission.VIEW_AGENTS, Permission.VIEW_ORGANIZATIONS)
        async def get_data(current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user_role = current_user.get('role', 'user')
            
            # Check if user has ANY of the required permissions
            has_access = any(
                rbac_manager.has_permission(user_role, perm)
                for perm in permissions
            )
            
            if not has_access:
                logger.warning(
                    f"Permission denied: User {current_user.get('user_id')} "
                    f"(role: {user_role}) lacks required permissions: {[p.value for p in permissions]}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required one of: {[p.value for p in permissions]}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_resource_ownership(user_id: str, resource_user_id: str, allow_admin: bool = True):
    """
    Helper function to check if user owns a resource or is admin
    
    Args:
        user_id: Current user's ID
        resource_user_id: Owner of the resource
        allow_admin: Whether admins can access regardless of ownership
    
    Returns:
        bool: True if user can access resource
    """
    if user_id == resource_user_id:
        return True
    
    if allow_admin:
        # This would need the actual user object to check role
        # For now, return False - implement in endpoint
        return False
    
    return False


# Audit logging decorator
def audit_action(action: str, resource_type: str):
    """
    Decorator to log user actions for audit trail
    
    Usage:
        @app.delete("/api/v1/agents/{agent_id}")
        @audit_action("delete", "agent")
        async def delete_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user', {})
            
            logger.info(
                f"AUDIT: User {current_user.get('user_id', 'unknown')} "
                f"({current_user.get('role', 'unknown')}) "
                f"performed {action} on {resource_type}"
            )
            
            result = await func(*args, **kwargs)
            
            logger.info(
                f"AUDIT: Action {action} on {resource_type} completed successfully"
            )
            
            return result
        
        return wrapper
    return decorator
