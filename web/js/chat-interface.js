class ChatManager {
    constructor() {
        this.currentAgent = null;
        this.conversations = new Map();
        this.websocket = null;
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.initWebSocket();
    }
    
    initEventListeners() {
        // Agent chat
        document.addEventListener('click', (e) => {
            if (e.target.closest('.chat-agent-item')) {
                const agentItem = e.target.closest('.chat-agent-item');
                const agentId = agentItem.dataset.agentId;
                this.selectAgent(agentId);
            }
        });
        
        // Send agent message
        const sendAgentBtn = document.getElementById('send-agent-message');
        const agentInput = document.getElementById('agent-chat-input');
        
        if (sendAgentBtn && agentInput) {
            sendAgentBtn.addEventListener('click', () => this.sendAgentMessage());
            agentInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendAgentMessage();
                }
            });
        }
        
        // User chatbot
        const sendUserbotBtn = document.getElementById('send-userbot-message');
        const userbotInput = document.getElementById('userbot-input');
        
        if (sendUserbotBtn && userbotInput) {
            sendUserbotBtn.addEventListener('click', () => this.sendUserbotMessage());
            userbotInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendUserbotMessage();
                }
            });
        }
        
        // Quick actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quick-action-btn')) {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            }
        });
    }
    
    initWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('Chat WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('Chat WebSocket disconnected');
                // Attempt reconnection
                setTimeout(() => this.initWebSocket(), 3000);
            };
            
        } catch (error) {
            console.error('Failed to initialize chat WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'agent_response':
                this.receiveAgentMessage(data.agentId, data.message, data.timestamp);
                break;
            case 'agent_typing':
                this.showTypingIndicator(data.agentId);
                break;
            case 'agent_stopped_typing':
                this.hideTypingIndicator(data.agentId);
                break;
            case 'userbot_response':
                this.receiveUserbotMessage(data.message, data.timestamp);
                break;
            default:
                console.log('Unknown chat message type:', data.type);
        }
    }
    
    selectAgent(agentId) {
        // Get agent info
        const agent = window.agentManager?.getAgent(agentId);
        if (!agent) {
            console.error('Agent not found:', agentId);
            return;
        }
        
        this.currentAgent = agentId;
        
        // Update UI
        this.updateAgentSelection(agentId);
        this.loadConversation(agentId);
        
        // Clear input and focus
        const input = document.getElementById('agent-chat-input');
        if (input) {
            input.value = '';
            input.focus();
        }
    }
    
    updateAgentSelection(agentId) {
        // Update sidebar selection
        document.querySelectorAll('.chat-agent-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`.chat-agent-item[data-agent-id="${agentId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
    }
    
    loadConversation(agentId) {
        const messagesContainer = document.getElementById('agent-chat-messages');
        if (!messagesContainer) return;
        
        // Get or create conversation
        if (!this.conversations.has(agentId)) {
            this.conversations.set(agentId, []);
            
            // Add welcome message
            const agent = window.agentManager?.getAgent(agentId);
            const welcomeMessage = {
                id: Date.now(),
                type: 'agent',
                agentId: agentId,
                content: this.getWelcomeMessage(agent),
                timestamp: new Date()
            };
            
            this.conversations.get(agentId).push(welcomeMessage);
        }
        
        // Render conversation
        const conversation = this.conversations.get(agentId);
        this.renderConversation(messagesContainer, conversation);
    }
    
    getWelcomeMessage(agent) {
        const welcomeMessages = {
            'ceo': `Hello! I'm the CEO Agent. I can help you with strategic decisions, organizational oversight, and high-level planning. What would you like to discuss?`,
            'senior_manager': `Hi there! I'm the Senior Manager for ITSM operations. I coordinate team activities, assign tasks, and monitor performance. How can I assist you today?`,
            'incident_agent': `Greetings! I'm your Incident Management specialist. I'm here to help with incident detection, response coordination, and resolution tracking. What incident can I help you with?`,
            'problem_agent': `Hello! I'm the Problem Management Agent. I specialize in root cause analysis and developing prevention strategies. What problem would you like me to investigate?`,
            'change_agent': `Hi! I'm your Change Management specialist. I handle change assessments, risk evaluations, and implementation planning. What change are you considering?`
        };
        
        return welcomeMessages[agent?.id] || `Hello! I'm ${agent?.name || 'an AI agent'}. How can I help you today?`;
    }
    
    renderConversation(container, conversation) {
        container.innerHTML = '';
        
        conversation.forEach(message => {
            const messageElement = this.createMessageElement(message);
            container.appendChild(messageElement);
        });
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
    
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.type}`;
        messageDiv.dataset.messageId = message.id;
        
        const agent = window.agentManager?.getAgent(message.agentId);
        const avatarIcon = message.type === 'user' ? 'fas fa-user' : (agent?.icon || 'fas fa-robot');
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${message.content}</div>
                <div class="message-time">${this.formatTime(message.timestamp)}</div>
                ${message.status ? `<div class="message-status ${message.status}">
                    ${message.status === 'sent' ? '✓' : message.status === 'error' ? '✗' : '⏳'}
                </div>` : ''}
            </div>
        `;
        
        return messageDiv;
    }
    
    async sendAgentMessage() {
        const input = document.getElementById('agent-chat-input');
        const saveToBlockchain = document.getElementById('save-to-blockchain')?.checked || false;
        
        if (!input || !input.value.trim() || !this.currentAgent) return;
        
        const message = {
            id: Date.now(),
            type: 'user',
            agentId: this.currentAgent,
            content: input.value.trim(),
            timestamp: new Date(),
            status: 'sending',
            saveToBlockchain: saveToBlockchain
        };
        
        // Add to conversation
        if (!this.conversations.has(this.currentAgent)) {
            this.conversations.set(this.currentAgent, []);
        }
        
        this.conversations.get(this.currentAgent).push(message);
        
        // Update UI
        const messagesContainer = document.getElementById('agent-chat-messages');
        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Clear input
        input.value = '';
        
        try {
            // Send to backend
            const response = await this.sendMessageToAgent(this.currentAgent, message.content, saveToBlockchain);
            
            // Update message status
            message.status = 'sent';
            this.updateMessageStatus(message.id, 'sent');
            
            // Show typing indicator
            this.showTypingIndicator(this.currentAgent);
            
            // Simulate agent response (replace with actual backend response)
            setTimeout(() => {
                this.simulateAgentResponse(this.currentAgent, message.content);
            }, 1000 + Math.random() * 2000);
            
        } catch (error) {
            console.error('Error sending message:', error);
            message.status = 'error';
            this.updateMessageStatus(message.id, 'error');
            
            if (window.dashboard) {
                window.dashboard.showToast('Failed to send message', 'error');
            }
        }
    }
    
    async sendMessageToAgent(agentId, content, saveToBlockchain) {
        const response = await fetch(`/api/v1/agents/${agentId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: content,
                saveToBlockchain: saveToBlockchain,
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        return response.json();
    }
    
    simulateAgentResponse(agentId, userMessage) {
        // Hide typing indicator
        this.hideTypingIndicator(agentId);
        
        // Generate response based on agent and message
        const agent = window.agentManager?.getAgent(agentId);
        const response = this.generateAgentResponse(agent, userMessage);
        
        this.receiveAgentMessage(agentId, response, new Date());
    }
    
    generateAgentResponse(agent, userMessage) {
        const responses = {
            'ceo': [
                "That's an excellent strategic consideration. Let me analyze the organizational impact...",
                "From an executive perspective, we need to consider the broader implications for our organization.",
                "This aligns with our strategic objectives. I'll coordinate with the management team to implement this.",
                "Let me review this decision with the leadership team and provide guidance on the next steps."
            ],
            'senior_manager': [
                "I'll coordinate with my team to address this request efficiently.",
                "This falls under our operational procedures. Let me assign this to the appropriate specialist.",
                "I can see this requires immediate attention. I'll escalate this through proper channels.",
                "Let me check our current workload and prioritize this accordingly."
            ],
            'incident_agent': [
                "I've logged this incident and will begin immediate investigation.",
                "Priority assessment complete. This requires urgent attention based on business impact.",
                "Initiating incident response procedures. I'll coordinate with relevant teams.",
                "I'll track this incident through to resolution and keep you updated on progress."
            ],
            'problem_agent': [
                "Let me conduct a thorough analysis to identify the root cause of this issue.",
                "I'm seeing patterns that suggest this might be related to previous incidents.",
                "This requires deep investigation. I'll analyze historical data for similar issues.",
                "I'll develop a comprehensive solution to prevent this problem from recurring."
            ],
            'change_agent': [
                "I need to assess the risk and impact of this proposed change.",
                "This change will require proper approval workflow before implementation.",
                "Let me evaluate the potential business impact and resource requirements.",
                "I'll coordinate with stakeholders to ensure smooth change implementation."
            ]
        };
        
        const agentResponses = responses[agent?.id] || [
            "I understand your request. Let me process this information.",
            "Thank you for providing this information. I'll handle it appropriately.",
            "I'm analyzing your request and will provide a comprehensive response.",
            "This is within my area of expertise. I'll address this promptly."
        ];
        
        return agentResponses[Math.floor(Math.random() * agentResponses.length)];
    }
    
    receiveAgentMessage(agentId, content, timestamp) {
        const message = {
            id: Date.now(),
            type: 'agent',
            agentId: agentId,
            content: content,
            timestamp: timestamp
        };
        
        // Add to conversation
        if (!this.conversations.has(agentId)) {
            this.conversations.set(agentId, []);
        }
        
        this.conversations.get(agentId).push(message);
        
        // Update UI if this is the current conversation
        if (this.currentAgent === agentId) {
            const messagesContainer = document.getElementById('agent-chat-messages');
            const messageElement = this.createMessageElement(message);
            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    showTypingIndicator(agentId) {
        if (this.currentAgent !== agentId) return;
        
        const messagesContainer = document.getElementById('agent-chat-messages');
        if (!messagesContainer) return;
        
        // Remove existing typing indicator
        const existingIndicator = messagesContainer.querySelector('.typing-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Add new typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-text">Agent is typing</div>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator(agentId) {
        if (this.currentAgent !== agentId) return;
        
        const messagesContainer = document.getElementById('agent-chat-messages');
        const typingIndicator = messagesContainer?.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    updateMessageStatus(messageId, status) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageElement) return;
        
        const statusElement = messageElement.querySelector('.message-status');
        if (statusElement) {
            statusElement.className = `message-status ${status}`;
            statusElement.innerHTML = status === 'sent' ? '✓' : status === 'error' ? '✗' : '⏳';
        }
    }
    
    // User Chatbot Methods
    async sendUserbotMessage() {
        const input = document.getElementById('userbot-input');
        if (!input || !input.value.trim()) return;
        
        const userMessage = input.value.trim();
        
        // Add user message to UI
        this.addUserbotMessage('user', userMessage);
        
        // Clear input
        input.value = '';
        
        try {
            // Send to backend
            const response = await this.sendUserbotRequest(userMessage);
            
            // Add bot response
            setTimeout(() => {
                this.addUserbotMessage('bot', response.message || this.generateUserbotResponse(userMessage));
            }, 1000);
            
        } catch (error) {
            console.error('Error sending userbot message:', error);
            this.addUserbotMessage('bot', "I'm sorry, I'm having trouble processing your request right now. Please try again later.");
        }
    }
    
    async sendUserbotRequest(message) {
        const response = await fetch('/api/v1/userbot/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send userbot message');
        }
        
        return response.json();
    }
    
    generateUserbotResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        if (message.includes('incident') || message.includes('problem') || message.includes('issue')) {
            return "I can help you report an incident. Let me route this to our Incident Management team. Can you provide more details about what's happening?";
        } else if (message.includes('change') || message.includes('modify') || message.includes('update')) {
            return "I understand you want to make a change. Our Change Management team will need to assess this. What type of change are you looking to implement?";
        } else if (message.includes('request') || message.includes('need') || message.includes('want')) {
            return "I can help create a service request for you. What specific service or resource do you need?";
        } else if (message.includes('status') || message.includes('check') || message.includes('update')) {
            return "I can check the status of your requests. Do you have a ticket number, or would you like me to look up your recent requests?";
        } else {
            return "I'm here to help with your IT service needs. I can assist with incident reporting, service requests, change management, and status checks. What would you like to do?";
        }
    }
    
    addUserbotMessage(type, content) {
        const messagesContainer = document.getElementById('userbot-messages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const avatarIcon = type === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    handleQuickAction(action) {
        const quickMessages = {
            'report-incident': "I need to report an incident. There's an issue with our system that needs immediate attention.",
            'service-request': "I'd like to submit a service request. I need access to a new system/resource.",
            'check-status': "Can you check the status of my recent tickets and requests?",
            'ask-question': "I have a question about our IT services and policies."
        };
        
        const message = quickMessages[action];
        if (message) {
            const input = document.getElementById('userbot-input');
            if (input) {
                input.value = message;
                input.focus();
            }
        }
    }
    
    receiveUserbotMessage(content, timestamp) {
        this.addUserbotMessage('bot', content);
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Public API
    selectAgent(agentId) {
        this.selectAgent(agentId);
    }
    
    getCurrentAgent() {
        return this.currentAgent;
    }
    
    getConversation(agentId) {
        return this.conversations.get(agentId) || [];
    }
    
    clearConversation(agentId) {
        this.conversations.delete(agentId);
        if (this.currentAgent === agentId) {
            this.loadConversation(agentId);
        }
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});