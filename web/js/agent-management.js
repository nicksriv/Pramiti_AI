class AgentManager {
    constructor() {
        this.agents = new Map();
        this.hierarchy = {
            levels: ['executive', 'manager', 'specialist'],
            structure: new Map()
        };
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.loadDefaultAgents();
    }
    
    initEventListeners() {
        // Add agent form
        const addAgentForm = document.getElementById('add-agent-form');
        if (addAgentForm) {
            addAgentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddAgent(e);
            });
        }
        
        // Agent card actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="edit-agent"]')) {
                const agentId = e.target.dataset.agentId;
                this.editAgent(agentId);
            }
            
            if (e.target.matches('[data-action="chat-agent"]')) {
                const agentId = e.target.dataset.agentId;
                this.startChatWithAgent(agentId);
            }
            
            if (e.target.matches('[data-action="delete-agent"]')) {
                const agentId = e.target.dataset.agentId;
                this.deleteAgent(agentId);
            }
        });
        
        // Hierarchy builder actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="save-hierarchy"]')) {
                this.saveHierarchy();
            }
            
            if (e.target.matches('[data-action="reset-hierarchy"]')) {
                this.resetHierarchy();
            }
        });
        
        // Agent slot interactions
        document.addEventListener('click', (e) => {
            const slot = e.target.closest('.agent-slot');
            if (slot && slot.classList.contains('empty')) {
                this.showAddAgentModal(slot);
            }
        });
    }
    
    loadDefaultAgents() {
        // Load default agent configuration
        const defaultAgents = [
            {
                id: 'ceo',
                name: 'CEO Agent',
                type: 'executive',
                role: 'Chief Executive Officer',
                specialization: 'Strategic Leadership',
                responsibilities: ['Strategic Planning', 'Decision Making', 'Organizational Oversight'],
                capabilities: 'High-level strategic thinking, decision making, and organizational leadership',
                reportsTo: null,
                icon: 'fas fa-crown',
                status: 'online'
            },
            {
                id: 'senior_manager',
                name: 'Senior Manager',
                type: 'manager',
                role: 'ITSM Senior Manager',
                specialization: 'IT Service Management',
                responsibilities: ['Team Coordination', 'Task Assignment', 'Performance Monitoring'],
                capabilities: 'Team management, ITSM processes, and operational coordination',
                reportsTo: 'ceo',
                icon: 'fas fa-user-tie',
                status: 'online'
            },
            {
                id: 'incident_agent',
                name: 'Incident Management Agent',
                type: 'specialist',
                role: 'Incident Management Specialist',
                specialization: 'Incident Response & Resolution',
                responsibilities: ['Incident Detection', 'Response Coordination', 'Resolution Tracking'],
                capabilities: 'Rapid incident response, troubleshooting, and escalation management',
                reportsTo: 'senior_manager',
                icon: 'fas fa-exclamation-triangle',
                status: 'online'
            },
            {
                id: 'problem_agent',
                name: 'Problem Management Agent',
                type: 'specialist',
                role: 'Problem Management Specialist',
                specialization: 'Root Cause Analysis',
                responsibilities: ['Problem Investigation', 'Root Cause Analysis', 'Prevention Strategies'],
                capabilities: 'Deep analytical thinking, pattern recognition, and preventive solution design',
                reportsTo: 'senior_manager',
                icon: 'fas fa-search',
                status: 'online'
            },
            {
                id: 'change_agent',
                name: 'Change Management Agent',
                type: 'specialist',
                role: 'Change Management Specialist',
                specialization: 'Change Implementation',
                responsibilities: ['Change Assessment', 'Risk Evaluation', 'Implementation Planning'],
                capabilities: 'Change impact analysis, risk assessment, and implementation coordination',
                reportsTo: 'senior_manager',
                icon: 'fas fa-cogs',
                status: 'online'
            }
        ];
        
        defaultAgents.forEach(agent => {
            this.agents.set(agent.id, agent);
        });
        
        this.buildHierarchyStructure();
        this.renderAgentsGrid();
    }
    
    handleAddAgent(event) {
        const formData = new FormData(event.target);
        const agentData = {
            id: this.generateAgentId(),
            name: formData.get('name'),
            type: formData.get('type'),
            role: formData.get('role'),
            specialization: formData.get('specialization'),
            responsibilities: formData.get('responsibilities').split('\n').filter(r => r.trim()),
            capabilities: formData.get('capabilities'),
            reportsTo: formData.get('reportsTo') || null,
            icon: formData.get('icon'),
            status: 'online'
        };
        
        // Validate required fields
        if (!agentData.name || !agentData.type) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }
        
        // Add agent to collection
        this.agents.set(agentData.id, agentData);
        
        // Update hierarchy
        this.buildHierarchyStructure();
        
        // Re-render UI
        this.renderAgentsGrid();
        this.renderHierarchy();
        
        // Close modal and reset form
        this.closeModal('add-agent-modal');
        event.target.reset();
        
        // Show success message
        this.showToast(`Agent "${agentData.name}" created successfully!`, 'success');
        
        // Send to backend
        this.saveAgentToBackend(agentData);
    }
    
    editAgent(agentId) {
        const agent = this.agents.get(agentId);
        if (!agent) {
            this.showToast('Agent not found', 'error');
            return;
        }
        
        // Populate form with agent data
        document.getElementById('agent-name').value = agent.name;
        document.getElementById('agent-type').value = agent.type;
        document.getElementById('agent-role').value = agent.role;
        document.getElementById('agent-specialization').value = agent.specialization;
        document.getElementById('agent-responsibilities').value = agent.responsibilities.join('\n');
        document.getElementById('agent-capabilities').value = agent.capabilities;
        document.getElementById('reports-to').value = agent.reportsTo || '';
        document.getElementById('agent-icon').value = agent.icon;
        
        // Change form to edit mode
        const form = document.getElementById('add-agent-form');
        form.dataset.mode = 'edit';
        form.dataset.agentId = agentId;
        
        const modalTitle = document.querySelector('#add-agent-modal .modal-title');
        modalTitle.textContent = 'Edit Agent';
        
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.textContent = 'Update Agent';
        
        // Open modal
        this.openModal('add-agent-modal');
    }
    
    deleteAgent(agentId) {
        const agent = this.agents.get(agentId);
        if (!agent) return;
        
        if (confirm(`Are you sure you want to delete "${agent.name}"?`)) {
            this.agents.delete(agentId);
            this.buildHierarchyStructure();
            this.renderAgentsGrid();
            this.renderHierarchy();
            
            this.showToast(`Agent "${agent.name}" deleted successfully`, 'success');
            
            // Remove from backend
            this.deleteAgentFromBackend(agentId);
        }
    }
    
    startChatWithAgent(agentId) {
        // Switch to chat tab and select agent
        const dashboard = window.dashboard;
        if (dashboard) {
            dashboard.switchTab('chat');
            
            setTimeout(() => {
                const chatManager = window.chatManager;
                if (chatManager) {
                    chatManager.selectAgent(agentId);
                }
            }, 100);
        }
    }
    
    generateAgentId() {
        return 'agent_' + Math.random().toString(36).substr(2, 9);
    }
    
    buildHierarchyStructure() {
        this.hierarchy.structure.clear();
        
        // Group agents by level and reporting structure
        this.agents.forEach(agent => {
            if (!this.hierarchy.structure.has(agent.type)) {
                this.hierarchy.structure.set(agent.type, []);
            }
            this.hierarchy.structure.get(agent.type).push(agent);
        });
    }
    
    renderAgentsGrid() {
        const agentsGrid = document.querySelector('.agents-grid');
        if (!agentsGrid) return;
        
        agentsGrid.innerHTML = '';
        
        this.agents.forEach(agent => {
            const agentCard = this.createAgentCard(agent);
            agentsGrid.appendChild(agentCard);
        });
    }
    
    createAgentCard(agent) {
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.dataset.agentId = agent.id;
        
        const responsibilityTags = agent.responsibilities.map(resp => 
            `<div class="responsibility-tag">${resp}</div>`
        ).join('');
        
        card.innerHTML = `
            <div class="agent-card-header">
                <div class="agent-avatar large">
                    <i class="${agent.icon}"></i>
                </div>
                <div class="agent-badge ${agent.type}">${agent.type}</div>
            </div>
            <div class="agent-card-content">
                <h4>${agent.name}</h4>
                <p class="agent-type">${agent.role}</p>
                <div class="agent-responsibilities">
                    ${responsibilityTags}
                </div>
            </div>
            <div class="agent-card-actions">
                <button class="btn btn-sm btn-outline" data-action="edit-agent" data-agent-id="${agent.id}">
                    <i class="fas fa-edit"></i>
                    Edit
                </button>
                <button class="btn btn-sm btn-primary" data-action="chat-agent" data-agent-id="${agent.id}">
                    <i class="fas fa-comment"></i>
                    Chat
                </button>
                ${agent.type !== 'executive' ? `
                    <button class="btn btn-sm btn-outline btn-danger" data-action="delete-agent" data-agent-id="${agent.id}">
                        <i class="fas fa-trash"></i>
                        Delete
                    </button>
                ` : ''}
            </div>
        `;
        
        return card;
    }
    
    renderHierarchy() {
        const hierarchyContainer = document.querySelector('.hierarchy-builder-container');
        if (!hierarchyContainer) return;
        
        hierarchyContainer.innerHTML = '';
        
        const levels = [
            { key: 'executive', label: 'Executive Level' },
            { key: 'manager', label: 'Management Level' },
            { key: 'specialist', label: 'Specialist Level' }
        ];
        
        levels.forEach((level, index) => {
            const levelDiv = document.createElement('div');
            levelDiv.className = 'hierarchy-level';
            levelDiv.dataset.level = index;
            
            levelDiv.innerHTML = `
                <div class="level-label">${level.label}</div>
                <div class="agent-slots">
                    ${this.renderAgentSlots(level.key)}
                </div>
            `;
            
            hierarchyContainer.appendChild(levelDiv);
        });
    }
    
    renderAgentSlots(levelType) {
        const agentsInLevel = Array.from(this.agents.values()).filter(agent => agent.type === levelType);
        let slots = '';
        
        // Render occupied slots
        agentsInLevel.forEach(agent => {
            slots += `
                <div class="agent-slot occupied" data-agent-id="${agent.id}">
                    <div class="slot-content">
                        <i class="${agent.icon}"></i>
                        <span>${agent.name}</span>
                    </div>
                </div>
            `;
        });
        
        // Add empty slot for adding new agents
        slots += `
            <div class="agent-slot empty" data-level-type="${levelType}">
                <div class="slot-content">
                    <i class="fas fa-plus"></i>
                    <span>Add ${levelType.charAt(0).toUpperCase() + levelType.slice(1)}</span>
                </div>
            </div>
        `;
        
        return slots;
    }
    
    showAddAgentModal(slot) {
        const levelType = slot.dataset.levelType;
        
        // Pre-fill agent type
        document.getElementById('agent-type').value = levelType;
        
        // Set appropriate reports-to based on level
        const reportsToSelect = document.getElementById('reports-to');
        if (levelType === 'manager') {
            reportsToSelect.value = 'ceo';
        } else if (levelType === 'specialist') {
            reportsToSelect.value = 'senior_manager';
        }
        
        this.openModal('add-agent-modal');
    }
    
    saveHierarchy() {
        const hierarchyData = {
            structure: Object.fromEntries(this.hierarchy.structure),
            agents: Object.fromEntries(this.agents)
        };
        
        // Send to backend
        this.saveHierarchyToBackend(hierarchyData);
        
        this.showToast('Hierarchy saved successfully!', 'success');
    }
    
    resetHierarchy() {
        if (confirm('Are you sure you want to reset the hierarchy to default?')) {
            this.agents.clear();
            this.loadDefaultAgents();
            this.renderAgentsGrid();
            this.renderHierarchy();
            
            this.showToast('Hierarchy reset to default configuration', 'info');
        }
    }
    
    // Backend API calls
    async saveAgentToBackend(agentData) {
        try {
            const response = await fetch('/api/v1/agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(agentData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to save agent');
            }
        } catch (error) {
            console.error('Error saving agent:', error);
            this.showToast('Failed to save agent to server', 'error');
        }
    }
    
    async deleteAgentFromBackend(agentId) {
        try {
            const response = await fetch(`/api/v1/agents/${agentId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete agent');
            }
        } catch (error) {
            console.error('Error deleting agent:', error);
        }
    }
    
    async saveHierarchyToBackend(hierarchyData) {
        try {
            const response = await fetch('/api/v1/hierarchy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(hierarchyData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to save hierarchy');
            }
        } catch (error) {
            console.error('Error saving hierarchy:', error);
            this.showToast('Failed to save hierarchy to server', 'error');
        }
    }
    
    // Utility methods
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            
            // Reset form if it's the add agent modal
            if (modalId === 'add-agent-modal') {
                const form = document.getElementById('add-agent-form');
                form.reset();
                form.dataset.mode = 'add';
                delete form.dataset.agentId;
                
                document.querySelector('#add-agent-modal .modal-title').textContent = 'Add New Agent';
                form.querySelector('button[type="submit"]').textContent = 'Create Agent';
            }
        }
    }
    
    showToast(message, type = 'info') {
        if (window.dashboard && window.dashboard.showToast) {
            window.dashboard.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
    
    // Public API
    getAgent(agentId) {
        return this.agents.get(agentId);
    }
    
    getAllAgents() {
        return Array.from(this.agents.values());
    }
    
    getAgentsByType(type) {
        return Array.from(this.agents.values()).filter(agent => agent.type === type);
    }
    
    getHierarchy() {
        return this.hierarchy;
    }
}

// Initialize agent manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.agentManager = new AgentManager();
});