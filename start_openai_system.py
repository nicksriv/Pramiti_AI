#!/usr/bin/env python3
"""
Startup script for Pramiti AI Organization with OpenAI Integration
Starts the API server and opens the web interface
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'openai',
        'fastapi', 
        'uvicorn',
        'python-dotenv',
        'web3'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        
        # Copy from .env.example if it exists
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("📄 Created .env file from .env.example")
        else:
            # Create basic .env file
            env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration  
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Application Configuration
APP_NAME=Pramiti AI Organization
DEBUG=true
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print("📄 Created basic .env file")
    
    # Load and check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured!")
        print("📝 Please edit .env file and add your OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
        print("")
        
        choice = input("Continue without OpenAI? (y/N): ").strip().lower()
        if choice != 'y':
            print("🛑 Startup cancelled. Please configure your OpenAI API key first.")
            return False
        else:
            print("⚠️  Starting without OpenAI integration (blockchain logging will still work)")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Pramiti AI Organization API server...")
    
    # Check if port 8084 is available
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', 8084)) == 0:
            print("⚠️  Port 8084 is already in use. Trying to stop existing server...")
            # Try to kill existing server
            try:
                subprocess.run(['pkill', '-f', 'uvicorn.*api_server'], check=False)
                time.sleep(2)
            except:
                pass
    
    # Start the server
    try:
        server_process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        print("⏳ Waiting for server to start...")
        
        # Wait for server to be ready
        for _ in range(30):  # Wait up to 30 seconds
            try:
                import urllib.request
                response = urllib.request.urlopen('http://localhost:8084/')
                if response.getcode() == 200:
                    print("✅ API server is running!")
                    break
            except:
                time.sleep(1)
        else:
            print("❌ Server failed to start properly")
            return None
        
        return server_process
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def open_web_interface():
    """Open the web interface in browser"""
    print("🌐 Opening web interface...")
    
    # Try to open the OpenAI-powered dashboard first
    urls_to_try = [
        'http://localhost:8084/static/openai-dashboard.html',
        'http://localhost:8084/static/chatbot-dashboard.html',
        'http://localhost:8084/'
    ]
    
    for url in urls_to_try:
        try:
            import urllib.request
            response = urllib.request.urlopen(url)
            if response.getcode() == 200:
                webbrowser.open(url)
                print(f"✅ Opened: {url}")
                return True
        except:
            continue
    
    print("⚠️  Could not open web interface automatically")
    print("🌐 Please visit: http://localhost:8084/static/openai-dashboard.html")
    return False

def main():
    """Main startup function"""
    print("🤖 Pramiti AI Organization - OpenAI Integration Startup")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check requirements
    print("📋 Checking requirements...")
    if not check_requirements():
        print("❌ Requirements check failed")
        return 1
    
    # Check environment
    print("🔧 Checking environment...")
    if not check_environment():
        print("❌ Environment check failed")
        return 1
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start API server")
        return 1
    
    # Open web interface
    time.sleep(2)  # Give server a moment
    open_web_interface()
    
    print("")
    print("🎉 Pramiti AI Organization is running!")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:8084/static/openai-dashboard.html")
    print("📊 API Documentation: http://localhost:8084/docs")  
    print("🔗 Blockchain Status: http://localhost:8084/blockchain/status")
    print("🤖 Agent Chat: Available in web interface")
    print("")
    print("💡 Features:")
    print("   ✅ OpenAI-powered AI agents")
    print("   ✅ Blockchain logging for audit trails")
    print("   ✅ Real-time chat interface")
    print("   ✅ Agent management and monitoring")
    print("   ✅ Compliance reporting")
    print("")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Keep server running
        server_process.wait()
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")
    
    return 0

if __name__ == "__main__":
    exit(main())