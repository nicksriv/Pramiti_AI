class DashboardManager {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.websocket = null;
        this.updateInterval = null;
        this.currentTab = 'dashboard';
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.initWebSocket();
        this.loadInitialData();
        this.startPeriodicUpdates();
        this.initNavigationHighlight();
    }
    
    // Event Listeners
    initEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        // Modal controls
        document.querySelectorAll('[data-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.openModal(modalId);
            });
        });
        
        document.querySelectorAll('.modal-close, .modal-overlay').forEach(element => {
            element.addEventListener('click', (e) => {
                if (e.target === element) {
                    this.closeAllModals();
                }
            });
        });
        
        // Action buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                e.preventDefault();
                const action = e.target.dataset.action;
                this.handleAction(action, e.target);
            }
        });
        
        // Responsive sidebar toggle
        this.initSidebarToggle();
    }
    
    // WebSocket Connection
    initWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.showToast('Connected to real-time updates', 'success');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.showToast('Real-time connection lost', 'error');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.initWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    // Handle WebSocket Messages
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'agent_status_update':
                this.updateAgentStatus(data.payload);
                break;
            case 'communication_log':
                this.addActivityItem(data.payload);
                break;
            case 'queue_update':
                this.updateQueues(data.payload);
                break;
            case 'kpi_update':
                this.updateKPIs(data.payload);
                break;
            case 'system_alert':
                this.showToast(data.payload.message, data.payload.level);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    // API Calls
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API call failed: ${endpoint}`, error);
            this.showToast(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }
    
    // Load Initial Data
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadKPIData(),
                this.loadAgentHierarchy(),
                this.loadActivityFeed(),
                this.loadMessageQueues()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }
    
    // Load KPI Data
    async loadKPIData() {
        try {
            const data = await this.apiCall('/dashboard/kpis');
            this.updateKPIs(data);
        } catch (error) {
            // Fallback to mock data if API is not available
            this.updateKPIs({
                activeAgents: 6,
                activeAgentsChange: 2,
                totalMessages: 1247,
                totalMessagesChange: 23,
                avgResponseTime: 1.2,
                avgResponseTimeChange: -0.3,
                systemUptime: 99.9,
                systemUptimeChange: 0.1
            });
        }
    }
    
    // Update KPIs
    updateKPIs(data) {
        const kpiElements = {
            activeAgents: document.querySelector('[data-kpi="active-agents"]'),
            totalMessages: document.querySelector('[data-kpi="total-messages"]'),
            avgResponseTime: document.querySelector('[data-kpi="avg-response-time"]'),
            systemUptime: document.querySelector('[data-kpi="system-uptime"]')
        };
        
        if (kpiElements.activeAgents && data.activeAgents !== undefined) {
            this.animateNumber(kpiElements.activeAgents, data.activeAgents);
        }
        
        if (kpiElements.totalMessages && data.totalMessages !== undefined) {
            this.animateNumber(kpiElements.totalMessages, data.totalMessages);
        }
        
        if (kpiElements.avgResponseTime && data.avgResponseTime !== undefined) {
            this.animateNumber(kpiElements.avgResponseTime, data.avgResponseTime, 's', 1);
        }
        
        if (kpiElements.systemUptime && data.systemUptime !== undefined) {
            this.animateNumber(kpiElements.systemUptime, data.systemUptime, '%', 1);
        }
    }
    
    // Load Agent Hierarchy
    async loadAgentHierarchy() {
        try {
            const data = await this.apiCall('/agents/hierarchy');
            this.updateAgentHierarchy(data);
        } catch (error) {
            console.log('Using default agent hierarchy');
        }
    }
    
    // Update Agent Status
    updateAgentStatus(data) {
        const agentElement = document.querySelector(`[data-agent-id="${data.agentId}"]`);
        if (agentElement) {
            const statusElement = agentElement.querySelector('.agent-status');
            if (statusElement) {
                statusElement.textContent = data.status;
                statusElement.className = `agent-status ${data.status.toLowerCase()}`;
            }
        }
    }
    
    // Load Activity Feed
    async loadActivityFeed() {
        try {
            const data = await this.apiCall('/communications/recent');
            this.updateActivityFeed(data.communications || []);
        } catch (error) {
            // Mock activity data
            this.updateActivityFeed([
                {
                    id: 1,
                    type: 'communication',
                    title: 'New incident reported',
                    description: 'ITSM Agent received incident INC-2024-001',
                    timestamp: new Date(Date.now() - 5 * 60 * 1000),
                    icon: 'fas fa-exclamation-circle'
                },
                {
                    id: 2,
                    type: 'system',
                    title: 'Agent assignment completed',
                    description: 'Senior Manager assigned task to Problem Management Agent',
                    timestamp: new Date(Date.now() - 15 * 60 * 1000),
                    icon: 'fas fa-user-check'
                }
            ]);
        }
    }
    
    // Update Activity Feed
    updateActivityFeed(activities) {
        const feedElement = document.querySelector('.activity-feed');
        if (!feedElement) return;
        
        feedElement.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon system">
                    <i class="${activity.icon || 'fas fa-info-circle'}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">${this.formatTimeAgo(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }
    
    // Add single activity item
    addActivityItem(activity) {
        const feedElement = document.querySelector('.activity-feed');
        if (!feedElement) return;
        
        const activityHtml = `
            <div class="activity-item">
                <div class="activity-icon system">
                    <i class="${activity.icon || 'fas fa-info-circle'}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">Just now</div>
                </div>
            </div>
        `;
        
        feedElement.insertAdjacentHTML('afterbegin', activityHtml);
        
        // Remove oldest items if more than 10
        const items = feedElement.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
    
    // Load Message Queues
    async loadMessageQueues() {
        try {
            const data = await this.apiCall('/communications/queues');
            this.updateMessageQueues(data.queues || []);
        } catch (error) {
            // Mock queue data
            this.updateMessageQueues([
                { agent: 'CEO Agent', count: 3, status: 'healthy' },
                { agent: 'Senior Manager', count: 7, status: 'healthy' },
                { agent: 'Incident Management', count: 12, status: 'healthy' },
                { agent: 'Problem Management', count: 5, status: 'healthy' },
                { agent: 'Change Management', count: 2, status: 'healthy' }
            ]);
        }
    }
    
    // Update Message Queues
    updateMessageQueues(queues) {
        const queueList = document.querySelector('.queue-list');
        if (!queueList) return;
        
        queueList.innerHTML = queues.map(queue => `
            <div class="queue-item">
                <span class="queue-agent">${queue.agent}</span>
                <div style="display: flex; align-items: center; gap: var(--space-3);">
                    <span class="queue-count">${queue.count}</span>
                    <span class="queue-status ${queue.status}">${queue.status}</span>
                </div>
            </div>
        `).join('');
    }
    
    // Navigation
    switchTab(tabName) {
        // Update navigation state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[data-tab="${tabName}"]`)?.closest('.nav-item');
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
        
        // Update page title
        const titles = {
            dashboard: 'Dashboard Overview',
            agents: 'Agent Management',
            communications: 'Communications Log',
            blockchain: 'Blockchain Audit',
            analytics: 'Analytics & Reports',
            settings: 'System Settings'
        };
        
        const titleElement = document.querySelector('.page-title');
        if (titleElement) {
            titleElement.textContent = titles[tabName] || 'Dashboard';
        }
        
        this.currentTab = tabName;
        this.loadTabContent(tabName);
    }
    
    // Load content for specific tab
    async loadTabContent(tabName) {
        const contentArea = document.querySelector('.dashboard-content');
        
        switch (tabName) {
            case 'dashboard':
                await this.loadDashboardContent();
                break;
            case 'agents':
                await this.loadAgentsContent();
                break;
            case 'communications':
                await this.loadCommunicationsContent();
                break;
            case 'blockchain':
                await this.loadBlockchainContent();
                break;
            case 'analytics':
                await this.loadAnalyticsContent();
                break;
            case 'settings':
                await this.loadSettingsContent();
                break;
        }
    }
    
    // Modal Management
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }
    
    // Action Handlers
    async handleAction(action, element) {
        switch (action) {
            case 'refresh-data':
                await this.refreshAllData();
                break;
            case 'export-logs':
                await this.exportLogs();
                break;
            case 'create-agent':
                this.openModal('agent-modal');
                break;
            case 'system-health':
                await this.checkSystemHealth();
                break;
            case 'emergency-stop':
                await this.emergencyStop();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    // Utility Functions
    animateNumber(element, targetValue, suffix = '', decimals = 0) {
        if (!element) return;
        
        const startValue = parseFloat(element.textContent.replace(/[^\d.-]/g, '')) || 0;
        const increment = (targetValue - startValue) / 30; // 30 frames
        let currentValue = startValue;
        
        const animation = () => {
            currentValue += increment;
            
            if ((increment > 0 && currentValue >= targetValue) || 
                (increment < 0 && currentValue <= targetValue)) {
                element.textContent = targetValue.toFixed(decimals) + suffix;
                return;
            }
            
            element.textContent = currentValue.toFixed(decimals) + suffix;
            requestAnimationFrame(animation);
        };
        
        animation();
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const diffInSeconds = Math.floor((now - past) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }
    
    // Toast Notifications
    showToast(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icons[type] || icons.info}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }
    
    // Sidebar Toggle for Mobile
    initSidebarToggle() {
        const toggleButton = document.createElement('button');
        toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
        toggleButton.className = 'sidebar-toggle btn btn-outline';
        toggleButton.style.cssText = 'position: fixed; top: 20px; left: 20px; z-index: 1001; display: none;';
        
        document.body.appendChild(toggleButton);
        
        // Show toggle button on mobile
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        const handleMediaQuery = (e) => {
            toggleButton.style.display = e.matches ? 'flex' : 'none';
        };
        
        mediaQuery.addListener(handleMediaQuery);
        handleMediaQuery(mediaQuery);
        
        toggleButton.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('open');
        });
    }
    
    // Navigation highlighting
    initNavigationHighlight() {
        // Highlight dashboard by default
        const dashboardNav = document.querySelector('[data-tab="dashboard"]')?.closest('.nav-item');
        if (dashboardNav) {
            dashboardNav.classList.add('active');
        }
    }
    
    // Periodic Updates
    startPeriodicUpdates() {
        // Update KPIs every 30 seconds
        this.updateInterval = setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadKPIData();
            }
        }, 30000);
    }
    
    // Refresh all data
    async refreshAllData() {
        this.showToast('Refreshing data...', 'info');
        
        try {
            await this.loadInitialData();
            this.showToast('Data refreshed successfully', 'success');
        } catch (error) {
            this.showToast('Failed to refresh data', 'error');
        }
    }
    
    // System health check
    async checkSystemHealth() {
        try {
            const health = await this.apiCall('/system/health');
            
            if (health.status === 'healthy') {
                this.showToast('System is running normally', 'success');
            } else {
                this.showToast(`System health: ${health.status}`, 'warning');
            }
        } catch (error) {
            this.showToast('Unable to check system health', 'error');
        }
    }
    
    // Cleanup
    destroy() {
        if (this.websocket) {
            this.websocket.close();
        }
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});

// ESC key to close modals
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && window.dashboard) {
        window.dashboard.closeAllModals();
    }
});