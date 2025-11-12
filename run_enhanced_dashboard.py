#!/usr/bin/env python3
"""
Enhanced Web Dashboard Startup Script
Agentic AI Organization System
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from api.enhanced_web_api import create_enhanced_app
    import uvicorn
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install requirements: pip install -r api/requirements.txt")
    sys.exit(1)

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(project_root / "logs" / "enhanced_dashboard.log")
        ]
    )

async def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Agentic AI Organization Dashboard")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    try:
        # Create enhanced FastAPI application
        logger.info("Creating enhanced FastAPI application...")
        app, dashboard = create_enhanced_app()
        
        # Initialize agent system
        logger.info("Initializing agent system...")
        await dashboard.initialize_agent_system()
        
        print("\n✅ Enhanced Dashboard initialized successfully!")
        print(f"📁 Project root: {project_root}")
        print(f"🌐 Web interface: http://127.0.0.1:8000")
        print(f"📊 API docs: http://127.0.0.1:8000/docs")
        print(f"🔌 WebSocket: ws://127.0.0.1:8000/ws")
        print(f"💬 Chat WebSocket: ws://127.0.0.1:8000/ws/chat")
        print("\n🎯 Available Features:")
        print("   • Agent Management (CRUD operations)")
        print("   • Organization Hierarchy Builder")
        print("   • Agent Chat Interface")
        print("   • User Chatbot")
        print("   • Real-time WebSocket Updates")
        print("   • Blockchain Communication Logging")
        
        print("\n🛠️  API Endpoints:")
        print("   • GET  /api/v1/agents - List all agents")
        print("   • POST /api/v1/agents - Create new agent")
        print("   • PUT  /api/v1/agents/{id} - Update agent")
        print("   • DEL  /api/v1/agents/{id} - Delete agent")
        print("   • POST /api/v1/agents/{id}/chat - Chat with agent")
        print("   • POST /api/v1/userbot/chat - Chat with organization bot")
        print("   • GET  /api/v1/hierarchy - Get organization structure")
        print("   • POST /api/v1/hierarchy - Save hierarchy changes")
        
        print(f"\n📝 Logs: {logs_dir / 'enhanced_dashboard.log'}")
        print("\n🔥 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the server
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=True,  # Enable auto-reload during development
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced Dashboard...")
        print("\n👋 Enhanced Dashboard stopped gracefully")
        
    except Exception as e:
        logger.error(f"Failed to start Enhanced Dashboard: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies verified")
    except ImportError:
        print("❌ Missing dependencies. Please run:")
        print("   pip install -r api/requirements.txt")
        sys.exit(1)
    
    # Run the application
    asyncio.run(main())