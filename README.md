# Agentic AI Organization

A sophisticated multi-agent AI system designed for enterprise IT Service Management (ITSM) with hierarchical structure and blockchain-based communication logging.

## 🎯 Project Overview

This autonomous AI organization consists of specialized agents working in a hierarchical structure to handle complex IT service management tasks. The system features:

- **Hierarchical Agent Structure**: Subject Matter Experts → Senior Managers → CEO Agent
- **Blockchain Communication Logging**: Immutable audit trails for all agent interactions
- **ITSM Domain Specialization**: Expert agents for Incident, Problem, and Change Management
- **White-label Ready**: Configurable for different organizations and domains

## 🏗️ Architecture

```
                    ┌─────────────┐
                    │  CEO Agent  │
                    │ (Executive) │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │Senior Manager│
                    │   (ITSM)    │
                    └─────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌─────▼─────┐     ┌────▼────┐
   │Incident │      │ Problem   │     │ Change  │
   │ Agents  │      │ Agents    │     │ Agents  │
   └─────────┘      └───────────┘     └─────────┘
```

## 🛠️ Technology Stack

- **Core Framework**: Python 3.8+, FastAPI, LangChain, CrewAI
- **Blockchain**: Web3.py, Ethereum-compatible networks
- **Database**: PostgreSQL/MongoDB hybrid, SQLAlchemy ORM
- **API**: RESTful API with FastAPI, WebSocket support
- **Frontend**: React.js with TypeScript
- **Message Queue**: Redis for high-performance communication
- **Monitoring**: Prometheus metrics, structured logging

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for frontend)
- Docker and Docker Compose (optional)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/agentic-ai-organization.git
   cd agentic-ai-organization
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```
   
   Or manually:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create configuration
   cp config.example.json config.json
   cp .env.example .env
   ```

3. **Configure the application**
   - Edit `config.json` for organizational settings
   - Update `.env` with your API keys and blockchain configuration

4. **Run the application**
   ```bash
   # Using the run script
   ./run.sh  # On Windows: run.bat
   
   # Or directly
   python main.py
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📊 Features

### Core Capabilities

- **🤖 Multi-Agent System**: Autonomous AI agents with specialized expertise
- **📋 Hierarchical Decision Making**: Escalation workflows with management oversight
- **🔗 Blockchain Audit Trail**: Immutable logging of all agent communications
- **📈 Performance Analytics**: Real-time metrics and historical reporting
- **🔄 Auto-Scaling**: Dynamic agent allocation based on workload

### ITSM Specializations

- **🚨 Incident Management**: Automated incident detection, classification, and resolution
- **🔍 Problem Management**: Root cause analysis and prevention strategies
- **📋 Change Management**: Risk assessment and change approval workflows
- **🎫 Service Request Fulfillment**: Automated handling of standard requests

### Advanced Features

- **🧠 Machine Learning Integration**: Continuous learning from interactions
- **🔒 Security & Compliance**: Role-based access control and audit compliance
- **🌐 Multi-Tenant Architecture**: Support for multiple organizations
- **📱 Mobile-Ready API**: Full mobile application support
- **🔌 Integration Framework**: Connect with existing ITSM tools

## 🎛️ Configuration

### Basic Configuration (`config.json`)

```json
{
  "organization": {
    "name": "Your Organization Name",
    "domain": "itsm",
    "version": "1.0.0"
  },
  "blockchain": {
    "network": "ethereum",
    "provider_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
  },
  "agents": {
    "max_concurrent": 50,
    "escalation_timeout": 300
  }
}
```

### Environment Variables (`.env`)

```bash
# API Configuration
API_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/agenticai

# Blockchain
BLOCKCHAIN_PRIVATE_KEY=your-private-key
INFURA_PROJECT_ID=your-infura-project-id

# External APIs
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## 🏃‍♂️ Usage Examples

### Starting the Organization

```python
from main import AgenticAIOrganization

# Initialize the organization
org = AgenticAIOrganization("config.json")
org.initialize_organization()

# Start processing
org.start()
```

### Creating a Test Incident

```python
# Create and escalate an incident
org.create_test_scenario()
```

### Generating Reports

```python
# Generate executive dashboard
org.generate_reports()
```

### API Integration

```bash
# Create an incident via API
curl -X POST "http://localhost:8000/api/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Performance Issue",
    "severity": "high",
    "description": "Users reporting slow response times"
  }'

# Get organization status
curl "http://localhost:8000/api/status"
```

## 📊 Monitoring & Analytics

### Real-time Dashboard

Access the web dashboard at `http://localhost:8000/dashboard` to view:

- Agent performance metrics
- Active incidents and escalations
- Communication flow visualization
- Blockchain transaction history

### Key Metrics

- **Response Time**: Average time from incident creation to first response
- **Resolution Rate**: Percentage of issues resolved without escalation
- **Escalation Patterns**: Analysis of when and why escalations occur
- **Agent Utilization**: Workload distribution across agents

## 🔧 Development

### Project Structure

```
agentic-ai-organization/
├── core/                   # Core framework components
│   ├── base_agent.py      # Base agent class and protocols
│   ├── blockchain_logger.py # Blockchain integration
│   └── communication_orchestrator.py # Message routing
├── agents/                 # Specialized agent implementations
│   ├── itsm_agents.py     # ITSM domain agents
│   └── management_agents.py # Manager and CEO agents
├── api/                    # REST API endpoints
├── web/                    # Frontend application
├── tests/                  # Test suites
├── docs/                   # Documentation
├── config.json            # Configuration file
├── requirements.txt        # Python dependencies
└── main.py                # Application entry point
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=agents --cov-report=html

# Run specific test suite
pytest tests/test_agents.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy core/ agents/
```

## 🚀 Deployment

### Production Deployment

1. **Prepare environment**
   ```bash
   # Set production environment
   export ENVIRONMENT=production
   
   # Update configuration
   cp config.production.json config.json
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Setup monitoring**
   ```bash
   # Deploy monitoring stack
   docker-compose -f monitoring/docker-compose.yml up -d
   ```

### Scaling Considerations

- **Horizontal Scaling**: Add more agent instances behind a load balancer
- **Database Optimization**: Use connection pooling and read replicas
- **Cache Layer**: Implement Redis for frequently accessed data
- **Message Queue**: Use RabbitMQ or Apache Kafka for high-throughput scenarios

## 🔐 Security

### Authentication & Authorization

- JWT-based authentication for API access
- Role-based access control (RBAC) for different user types
- API rate limiting and request validation

### Data Protection

- Encryption at rest and in transit
- PII data anonymization in logs
- Secure blockchain key management
- Regular security audits and vulnerability scanning

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📚 Documentation

- **[API Reference](docs/api.md)**: Complete API documentation
- **[Agent Development Guide](docs/agents.md)**: Creating custom agents
- **[Blockchain Integration](docs/blockchain.md)**: Blockchain setup and configuration
- **[Deployment Guide](docs/deployment.md)**: Production deployment instructions
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## 🐛 Troubleshooting

### Common Issues

1. **Blockchain Connection Failed**
   - Check your `BLOCKCHAIN_PROVIDER_URL` in `.env`
   - Ensure your Infura/Alchemy project is active
   - Verify network connectivity

2. **Agent Not Responding**
   - Check agent queue sizes in the dashboard
   - Review agent logs for errors
   - Restart the communication orchestrator

3. **Database Connection Error**
   - Verify `DATABASE_URL` configuration
   - Ensure database server is running
   - Check network connectivity and credentials

## 🚧 Roadmap

### Version 1.1 (Q1 2024)
- [ ] Enhanced ML model integration
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Kubernetes deployment support

### Version 1.2 (Q2 2024)
- [ ] Multi-language agent support
- [ ] Advanced workflow automation
- [ ] Integration with major ITSM platforms
- [ ] Performance optimization

### Version 2.0 (Q3 2024)
- [ ] Complete white-label solution
- [ ] Advanced AI model fine-tuning
- [ ] Enterprise SSO integration
- [ ] Advanced compliance features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For the agent framework foundation
- **CrewAI**: For multi-agent coordination patterns
- **FastAPI**: For the robust API framework
- **Web3.py**: For blockchain integration capabilities

## 📞 Support

- **Documentation**: [https://docs.agentciaiorg.com](https://docs.agentciaiorg.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/agentic-ai-organization/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/agentic-ai-organization/discussions)
- **Email**: support@agentciaiorg.com

---

**Built with ❤️ for the future of autonomous AI organizations**