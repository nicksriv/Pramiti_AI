#!/usr/bin/env python3
"""
Test OAuth Integration in Agent Chat
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8084"

def test_oauth_chat():
    """Test OAuth authentication through chat interface"""
    
    print("=" * 70)
    print("TESTING OAUTH INTEGRATION IN AGENT CHAT")
    print("=" * 70)
    
    # Test 1: General authentication request
    print("\n📝 Test 1: User says 'I want to connect my Microsoft account'")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/user-chat",
        json={
            "message": "I want to connect my Microsoft account",
            "user_id": "test-user-001"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"🤖 Agent: {data.get('agent')}")
        print(f"📨 Response:\n{data.get('response')}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    sleep(1)
    
    # Test 2: Provide email address
    print("\n📝 Test 2: User provides email 'My email is john.doe@company.com'")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/user-chat",
        json={
            "message": "My email is john.doe@company.com",
            "user_id": "test-user-001"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"🤖 Agent: {data.get('agent')}")
        print(f"📨 Response:\n{data.get('response')}\n")
        
        # Check if authorization URL was generated
        if "http" in data.get('response', ''):
            print("🔗 Authorization URL detected in response!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    sleep(1)
    
    # Test 3: Direct request with email
    print("\n📝 Test 3: User says 'Connect Outlook for jane@company.com'")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/user-chat",
        json={
            "message": "Connect Outlook for jane@company.com",
            "user_id": "test-user-002"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"🤖 Agent: {data.get('agent')}")
        print(f"📨 Response:\n{data.get('response')}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    sleep(1)
    
    # Test 4: Google authentication
    print("\n📝 Test 4: User says 'I want to login with Google'")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/user-chat",
        json={
            "message": "I want to login with Google",
            "user_id": "test-user-003"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"🤖 Agent: {data.get('agent')}")
        print(f"📨 Response:\n{data.get('response')}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    sleep(1)
    
    # Test 5: Help request
    print("\n📝 Test 5: User asks for help 'How do I authenticate?'")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/user-chat",
        json={
            "message": "How do I authenticate?",
            "user_id": "test-user-004"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"🤖 Agent: {data.get('agent')}")
        print(f"📨 Response:\n{data.get('response')}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    print("\nWaiting for API server to be ready...")
    sleep(2)
    
    try:
        test_oauth_chat()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("   Please make sure the server is running on http://localhost:8084")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
