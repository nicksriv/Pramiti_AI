#!/usr/bin/env python3
"""
Interactive script to set up OpenAI API key in .env file
"""

import os
import sys
from pathlib import Path

def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    
    print("\n" + "="*60)
    print("🤖 Pramiti AI - OpenAI API Key Setup")
    print("="*60 + "\n")
    
    # Check if .env file exists
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Creating .env file from .env.example...\n")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file\n")
        else:
            print("❌ .env.example not found! Cannot create .env file.")
            return False
    
    # Read current .env content
    with open(".env", "r") as f:
        env_content = f.read()
    
    # Check if API key is already set
    if "OPENAI_API_KEY=" in env_content:
        current_key = None
        for line in env_content.split("\n"):
            if line.startswith("OPENAI_API_KEY="):
                current_key = line.split("=", 1)[1].strip()
                break
        
        if current_key and current_key != "your_openai_api_key_here":
            print(f"ℹ️  Current API key: {current_key[:8]}...{current_key[-4:] if len(current_key) > 12 else ''}\n")
            print("Options:")
            print("  1. Keep current key")
            print("  2. Replace with new key")
            choice = input("\nYour choice (1/2): ").strip()
            
            if choice == "1":
                print("\n✅ Keeping current API key")
                print("\n💡 To test your setup, run: python3 api_server.py")
                return True
    
    # Get API key from user
    print("\n📋 To get your OpenAI API key:")
    print("   1. Go to: https://platform.openai.com/api-keys")
    print("   2. Sign in or create an account")
    print("   3. Click 'Create new secret key'")
    print("   4. Copy the key (starts with 'sk-')\n")
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided. Setup cancelled.")
        return False
    
    if not api_key.startswith("sk-"):
        print("\n⚠️  Warning: OpenAI API keys typically start with 'sk-'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Setup cancelled.")
            return False
    
    # Update .env file
    updated_content = env_content.replace(
        "OPENAI_API_KEY=your_openai_api_key_here",
        f"OPENAI_API_KEY={api_key}"
    )
    
    # If the key was already set but different, replace it
    if "OPENAI_API_KEY=" in env_content and "your_openai_api_key_here" not in env_content:
        lines = []
        for line in env_content.split("\n"):
            if line.startswith("OPENAI_API_KEY="):
                lines.append(f"OPENAI_API_KEY={api_key}")
            else:
                lines.append(line)
        updated_content = "\n".join(lines)
    
    # Write updated .env file
    with open(".env", "w") as f:
        f.write(updated_content)
    
    print("\n✅ OpenAI API key successfully configured!")
    print("\n" + "="*60)
    print("🚀 Next Steps:")
    print("="*60)
    print("\n1. Start the API server:")
    print("   python3 api_server.py")
    print("\n2. Open the dashboard in your browser:")
    print("   http://localhost:8084/openai-dashboard.html")
    print("\n3. Start chatting with AI agents!")
    print("\n💡 The agents will now use OpenAI to generate intelligent responses.")
    print("💡 All conversations are logged to blockchain for audit trails.")
    print("\n")
    
    return True

def verify_setup():
    """Verify that the setup is correct"""
    
    print("\n🔍 Verifying setup...\n")
    
    # Check .env file
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set or invalid")
        return False
    
    print(f"✅ OPENAI_API_KEY is set: {api_key[:8]}...{api_key[-4:]}")
    
    # Try to import required packages
    try:
        import openai
        print("✅ openai package is installed")
    except ImportError:
        print("❌ openai package not installed. Run: pip install openai")
        return False
    
    try:
        import fastapi
        print("✅ fastapi package is installed")
    except ImportError:
        print("❌ fastapi package not installed. Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ Setup verification complete!")
    print("   You're ready to start the API server.\n")
    
    return True

if __name__ == "__main__":
    try:
        if setup_openai_key():
            verify_setup()
        else:
            print("\n❌ Setup failed. Please try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
