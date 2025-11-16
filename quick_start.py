"""
Quick Start Example: Minimal LiveKit Voice Agent with Cartesia TTS
This is a simplified version for quick testing and understanding the core concepts.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    required = {
        "LIVEKIT_URL": "LiveKit server URL (e.g., wss://your-project.livekit.cloud)",
        "LIVEKIT_API_KEY": "LiveKit API key",
        "LIVEKIT_API_SECRET": "LiveKit API secret",
        "DEEPGRAM_API_KEY": "Deepgram API key for speech-to-text",
    }
    
    optional = {
        "CARTESIA_API_KEY": "Cartesia API key for TTS (will fallback to OpenAI)",
        "OPENAI_API_KEY": "OpenAI API key (fallback for TTS)",
    }
    
    print("=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)
    
    missing_required = []
    for var, description in required.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: Set")
        else:
            print(f"✗ {var}: MISSING - {description}")
            missing_required.append(var)
    
    print("\nOptional:")
    for var, description in optional.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: Set")
        else:
            print(f"○ {var}: Not set - {description}")
    
    print("=" * 60)
    
    if missing_required:
        print("\n❌ MISSING REQUIRED VARIABLES:")
        for var in missing_required:
            print(f"   - {var}")
        print("\nPlease create a .env file with these variables.")
        print("See .env.example for a template.\n")
        return False
    
    print("\n✓ All required environment variables are set!")
    return True


async def test_ollama_connection():
    """Test connection to Ollama"""
    print("\n" + "=" * 60)
    print("TESTING OLLAMA CONNECTION")
    print("=" * 60)
    
    try:
        import ollama
        
        # Try to list models
        models = ollama.list()
        print("✓ Successfully connected to Ollama")
        print(f"\nAvailable models: {len(models['models'])}")
        
        # Check if llama3.2 is available
        model_names = [m['name'] for m in models['models']]
        if any('llama3.2' in name for name in model_names):
            print("✓ llama3.2 model is available")
        else:
            print("⚠ llama3.2 model not found. Run: ollama pull llama3.2")
            print(f"Available models: {', '.join(model_names[:5])}")
        
        # Test a simple chat
        print("\nTesting chat generation...")
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': 'Say "test successful" in 3 words'}]
        )
        print(f"✓ Chat test: {response['message']['content']}")
        
        return True
        
    except ImportError:
        print("✗ Ollama package not installed. Run: pip install ollama")
        return False
    except Exception as e:
        print(f"✗ Error connecting to Ollama: {str(e)}")
        print("\nMake sure Ollama is running:")
        print("  - macOS/Windows: Start the Ollama app")
        print("  - Linux: systemctl start ollama")
        return False


def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Text-based Chat (No setup required):
   $ python chat_deb.py

2. Voice Agent (Requires API keys):
   a. Copy .env.example to .env
      $ cp .env.example .env
   
   b. Fill in your API keys in .env
      - Get LiveKit keys: https://cloud.livekit.io/
      - Get Deepgram key: https://console.deepgram.com/
      - Get Cartesia key: https://cartesia.ai/
   
   c. Run the voice agent:
      $ python voice_agent_cartesia.py
   
   d. Connect a client to your LiveKit room:
      - Use LiveKit Meet: https://meet.livekit.io/custom
      - Or build a custom client with LiveKit SDKs

3. Read the full documentation:
   $ cat README.md

For detailed setup instructions, see README.md
""")


async def main():
    """Main function"""
    print("\n🎙️  LIVEKIT VOICE AGENT - QUICK START CHECK\n")
    
    # Check environment
    env_ok = check_environment()
    
    # Test Ollama
    ollama_ok = await test_ollama_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if ollama_ok:
        print("✓ Text-based chat is ready to use")
        print("  Run: python chat_deb.py")
    else:
        print("✗ Text-based chat needs Ollama setup")
    
    if env_ok and ollama_ok:
        print("✓ Voice agent is ready to use")
        print("  Run: python voice_agent_cartesia.py")
    else:
        print("✗ Voice agent needs additional setup")
    
    print_next_steps()


if __name__ == "__main__":
    asyncio.run(main())
