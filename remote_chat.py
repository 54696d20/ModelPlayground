#!/usr/bin/env python3
"""
Remote Chat Client for AWS EC2 Model Playground
Connect to your AI model running on AWS from your local machine
"""

import requests
import json
import time
import sys
from typing import Optional

# Configuration - Update these values
EC2_IP = "YOUR_EC2_IP_HERE"  # Replace with your EC2 instance IP
API_BASE_URL = f"http://{EC2_IP}:8000"
SESSION_ID = f"remote_{int(time.time())}"

class RemoteChatClient:
    def __init__(self, api_url: str, session_id: str):
        self.api_url = api_url
        self.session_id = session_id
        self.conversation_history = []
        
    def check_connection(self) -> bool:
        """Check if the remote API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connected to {self.api_url}")
                print(f"📊 Status: {data['status']}")
                print(f"🤖 Model: {data.get('model_loaded', 'Unknown')}")
                print(f"💻 Device: {data.get('device', 'Unknown')}")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_message(self, message: str, max_tokens: int = 512) -> Optional[str]:
        """Send a message to the remote API"""
        try:
            payload = {
                "message": message,
                "max_tokens": max_tokens,
                "session_id": self.session_id
            }
            
            print("🤔 Thinking...")
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=120  # 2 minute timeout for model inference
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response received")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out. The model might be taking too long to respond.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def list_conversations(self):
        """List all active conversations"""
        try:
            response = requests.get(f"{self.api_url}/conversations", timeout=10)
            if response.status_code == 200:
                conversations = response.json()
                print("\n📋 Active Conversations:")
                for conv_id in conversations:
                    print(f"  - {conv_id}")
            else:
                print("❌ Failed to fetch conversations")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching conversations: {e}")
    
    def clear_conversation(self):
        """Clear the current conversation"""
        try:
            response = requests.delete(f"{self.api_url}/conversations/{self.session_id}", timeout=10)
            if response.status_code == 200:
                print("🗑️ Conversation cleared!")
                self.conversation_history = []
            else:
                print("❌ Failed to clear conversation")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error clearing conversation: {e}")

def main():
    print("🚀 Remote Chat Client for AWS Model Playground")
    print("=" * 50)
    
    # Initialize client
    client = RemoteChatClient(API_BASE_URL, SESSION_ID)
    
    # Check connection
    if not client.check_connection():
        print("\n❌ Cannot connect to remote API. Please check:")
        print("1. Your EC2 instance is running")
        print("2. The IP address is correct")
        print("3. Port 8000 is open in your security group")
        print("4. The API is running on the EC2 instance")
        sys.exit(1)
    
    print(f"\n🤖 Session ID: {SESSION_ID}")
    print("💡 Type 'help' for commands, 'quit' to exit")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\n📖 Available Commands:")
                print("  help          - Show this help")
                print("  quit          - Exit the chat")
                print("  clear         - Clear conversation history")
                print("  sessions      - List active sessions")
                print("  status        - Check API status")
                print("  <message>     - Send a message to the AI")
            elif user_input.lower() == 'clear':
                client.clear_conversation()
                continue
            elif user_input.lower() == 'sessions':
                client.list_conversations()
                continue
            elif user_input.lower() == 'status':
                client.check_connection()
                continue
            
            # Send message to AI
            response = client.send_message(user_input)
            if response:
                print(f"\nAI: {response}")
                client.conversation_history.append(("user", user_input))
                client.conversation_history.append(("ai", response))
            else:
                print("❌ Failed to get response from AI")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 