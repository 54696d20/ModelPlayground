#!/usr/bin/env python3
"""
Interactive chat script for real-time conversation
"""

import requests
import json
import sys
import uuid

API_BASE_URL = "http://localhost:8000"

def interactive_chat():
    """Interactive chat session"""
    print("🤖 Interactive Chat Session")
    print("=" * 40)
    print("Type 'quit' to exit, 'clear' to start new session")
    print("Type 'sessions' to see active sessions")
    print("-" * 40)
    
    # Generate a unique session ID
    session_id = f"chat_{uuid.uuid4().hex[:8]}"
    print(f"Session ID: {session_id}")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                session_id = f"chat_{uuid.uuid4().hex[:8]}"
                print(f"🔄 New session: {session_id}")
                continue
            elif user_input.lower() == 'sessions':
                try:
                    response = requests.get(f"{API_BASE_URL}/conversations")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"📋 Active sessions: {data['sessions']}")
                        print(f"Total: {data['total_sessions']}")
                    else:
                        print("❌ Error getting sessions")
                except Exception as e:
                    print(f"❌ Error: {e}")
                continue
            elif not user_input:
                continue
            
            # Send message to API
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={
                    "message": user_input,
                    "max_tokens": 200,
                    "session_id": session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"AI: {data['response']}")
                print()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 Welcome to the Interactive Chat!")
    print("This will maintain conversation context throughout your session.")
    print()
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ API is running and ready!")
        else:
            print("❌ API is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the API is running with: docker-compose up -d")
        return
    
    print()
    interactive_chat()

if __name__ == "__main__":
    main() 