#!/usr/bin/env python3
"""
Startup script for the Agentic AI Organization Dashboard

This script handles the complete startup process including:
- Environment setup
- Dependency installation  
- Agent system initialization
- Web server startup
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist"""
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    venv_path = project_root / "venv"
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("📦 Installing dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'websockets',
        'langchain',
        'crewai', 
        'web3',
        'sqlalchemy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        return False
    
    print("✅ All required dependencies are available")
    return True

async def initialize_system():
    """Initialize the agent system"""
    print("🤖 Initializing agent system...")
    
    try:
        # Import after dependencies are confirmed available
        from api.web_api import WebDashboardAPI
        
        dashboard = WebDashboardAPI()
        await dashboard.initialize_agent_system()
        print("✅ Agent system initialized successfully")
        return dashboard
        
    except Exception as e:
        print(f"❌ Failed to initialize agent system: {e}")
        return None

def start_web_server(host="127.0.0.1", port=8000):
    """Start the web server"""
    print(f"🚀 Starting web dashboard at http://{host}:{port}")
    
    try:
        # Use uvicorn to run the server
        import uvicorn
        from api.web_api import create_app
        
        app, dashboard = create_app()
        
        # Create startup event
        @app.on_event("startup")
        async def startup():
            await dashboard.initialize_agent_system()
            await dashboard.start_background_tasks()
        
        # Run server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🔄 Starting Agentic AI Organization Dashboard...")
    print("=" * 50)
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Setup virtual environment 
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("\n💡 Tip: Try running the setup manually:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 4: Check dependencies are available
    if not check_dependencies():
        print("🔄 Attempting to install missing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete! Starting dashboard...")
    print("=" * 50)
    
    # Step 5: Parse command line arguments
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
Usage: python start_dashboard.py [host] [port]

Arguments:
    host    Host to bind to (default: 127.0.0.1)
    port    Port to bind to (default: 8000)

Examples:
    python start_dashboard.py                    # Start on localhost:8000
    python start_dashboard.py 0.0.0.0           # Start on all interfaces:8000
    python start_dashboard.py 127.0.0.1 8080    # Start on localhost:8080
            """)
            return
        
        host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[2]}")
            sys.exit(1)
    
    # Step 6: Start the server
    print(f"\n📊 Dashboard will be available at: http://{host}:{port}")
    print("🔗 API documentation will be at: http://{host}:{port}/docs")
    print("\n⚡ Press Ctrl+C to stop the server\n")
    
    try:
        start_web_server(host, port)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()