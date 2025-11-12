#!/usr/bin/env python3
"""
Setup script for Agentic AI Organization
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📥 Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    try:
        # Upgrade pip first
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("You can try installing manually with:")
        print(f"   {python_path} -m pip install -r requirements.txt")
        return False

def create_config_file():
    """Create configuration file"""
    config_path = Path("config.json")
    
    if config_path.exists():
        print("✅ Configuration file already exists")
        return True
    
    print("⚙️ Creating configuration file...")
    
    config = {
        "organization": {
            "name": "Agentic AI ITSM Organization",
            "description": "AI-powered ITSM organization with hierarchical agent structure",
            "domain": "itsm",
            "version": "1.0.0"
        },
        "agents": {
            "ceo": {
                "name": "Executive AI Director",
                "id": "ceo-001"
            },
            "senior_managers": [
                {
                    "name": "ITSM Operations Manager",
                    "id": "sm-itsm-001",
                    "specialization": "ITSM Operations",
                    "team_size": 6
                }
            ],
            "sme_agents": [
                {
                    "name": "Incident Response Specialist",
                    "id": "sme-incident-001",
                    "specialization": "incident_management",
                    "manager_id": "sm-itsm-001"
                },
                {
                    "name": "Incident Analysis Expert",
                    "id": "sme-incident-002",
                    "specialization": "incident_management",
                    "manager_id": "sm-itsm-001"
                },
                {
                    "name": "Problem Resolution Specialist",
                    "id": "sme-problem-001",
                    "specialization": "problem_management",
                    "manager_id": "sm-itsm-001"
                },
                {
                    "name": "Problem Analysis Expert",
                    "id": "sme-problem-002",
                    "specialization": "problem_management",
                    "manager_id": "sm-itsm-001"
                },
                {
                    "name": "Change Coordinator",
                    "id": "sme-change-001",
                    "specialization": "change_management",
                    "manager_id": "sm-itsm-001"
                },
                {
                    "name": "Change Approval Specialist",
                    "id": "sme-change-002",
                    "specialization": "change_management",
                    "manager_id": "sm-itsm-001"
                }
            ]
        },
        "blockchain": {
            "network": "development",
            "provider_url": "http://localhost:8545",
            "contract_address": "0x0000000000000000000000000000000000000000",
            "gas_limit": 500000,
            "gas_price": "20000000000"
        },
        "database": {
            "type": "sqlite",
            "url": "sqlite:///./agentic_ai_org.db",
            "echo": False
        },
        "api": {
            "host": "127.0.0.1",
            "port": 8000,
            "debug": True,
            "reload": True
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/agentic_ai_org.log"
        },
        "performance": {
            "max_queue_size": 100,
            "processing_timeout": 300,
            "conversation_cleanup_hours": 24,
            "max_concurrent_agents": 50
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "reports", 
        "data",
        "tests",
        "docs"
    ]
    
    print("📁 Creating directories...")
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {directory}/")
        else:
            print(f"   ✓ Exists: {directory}/")

def create_env_file():
    """Create environment file"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ Environment file already exists")
        return True
    
    print("🔐 Creating environment file...")
    
    env_content = """# Agentic AI Organization Environment Variables

# Development/Production Mode
ENVIRONMENT=development

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
API_SECRET_KEY=change-this-secret-key-in-production

# Database Configuration
DATABASE_URL=sqlite:///./agentic_ai_org.db

# Blockchain Configuration
BLOCKCHAIN_NETWORK=development
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
BLOCKCHAIN_PRIVATE_KEY=your-private-key-here
BLOCKCHAIN_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

# External APIs (Optional - for advanced AI features)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agentic_ai_org.log

# Performance Settings
MAX_QUEUE_SIZE=100
PROCESSING_TIMEOUT=300
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ Environment file created")
        print("⚠️  Remember to update the API keys and secrets in .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def create_run_scripts():
    """Create convenient run scripts"""
    print("📜 Creating run scripts...")
    
    # Unix/Linux/macOS script
    run_script_unix = """#!/bin/bash
# Agentic AI Organization - Run Script

echo "🤖 Starting Agentic AI Organization..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the main application
python main.py

echo "👋 Goodbye!"
"""
    
    # Windows script
    run_script_windows = """@echo off
REM Agentic AI Organization - Run Script

echo 🤖 Starting Agentic AI Organization...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Run the main application
python main.py

echo 👋 Goodbye!
pause
"""
    
    try:
        # Unix script
        with open("run.sh", 'w') as f:
            f.write(run_script_unix)
        os.chmod("run.sh", 0o755)  # Make executable
        
        # Windows script
        with open("run.bat", 'w') as f:
            f.write(run_script_windows)
        
        print("✅ Run scripts created")
        print("   • Unix/macOS: ./run.sh")
        print("   • Windows: run.bat")
        return True
    except Exception as e:
        print(f"❌ Failed to create run scripts: {e}")
        return False

def create_init_files():
    """Create __init__.py files for proper Python imports"""
    print("📄 Creating __init__.py files...")
    
    init_files = [
        "core/__init__.py",
        "agents/__init__.py", 
        "api/__init__.py",
        "web/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        
        # Create directory if it doesn't exist
        init_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py file
        if not init_path.exists():
            with open(init_path, 'w') as f:
                f.write('"""Agentic AI Organization module"""\n')
            print(f"   ✅ Created: {init_file}")

def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Review and update configuration in config.json")
    print("2. Update API keys and secrets in .env file (if using external APIs)")
    print("3. Run the application:")
    
    if os.name == 'nt':
        print("   • Windows: double-click run.bat or run 'run.bat' in terminal")
    else:
        print("   • Unix/macOS: run './run.sh' in terminal")
    
    print("   • Or manually: activate venv and run 'python main.py'")
    
    print("\n📚 Documentation:")
    print("• README.md - Project overview and architecture")
    print("• docs/ - Additional documentation (when available)")
    
    print("\n🔧 Development:")
    print("• Logs will be saved to logs/")
    print("• Reports will be generated in reports/")
    print("• Configuration can be modified in config.json")
    
    print("\n🧪 Getting Started:")
    print("1. Run the application")
    print("2. Choose option '2' to create a test scenario")
    print("3. Choose option '3' to generate reports")
    print("4. Explore the blockchain logging and agent communication!")
    
    print("\n🆘 Need Help?")
    print("• Check the README.md for troubleshooting")
    print("• Review the code documentation in the source files")
    print("• All dependencies are installed in the 'venv' virtual environment")

def main():
    """Main setup function"""
    print("🚀 Agentic AI Organization Setup")
    print("=" * 40)
    print("Setting up your autonomous AI organization...")
    print()
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Setup failed at virtual environment creation")
        sys.exit(1)
    
    # Install dependencies
    print("\n⏳ This may take a few minutes...")
    if not install_dependencies():
        print("\n⚠️ Setup completed with warnings - dependencies may not be fully installed")
        print("You can complete the installation manually later")
    
    # Create configuration
    if not create_config_file():
        print("\n❌ Setup failed at configuration creation") 
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create environment file
    if not create_env_file():
        print("\n❌ Setup failed at environment file creation")
        sys.exit(1)
    
    # Create run scripts
    if not create_run_scripts():
        print("\n❌ Setup failed at run script creation")
        sys.exit(1)
    
    # Create __init__.py files
    create_init_files()
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main()