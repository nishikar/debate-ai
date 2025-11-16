"""
Ollama Chat with Cartesia TTS
Text input with voice output using Cartesia text-to-speech
"""

import ollama
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CartesiaTTS:
    """Simple Cartesia TTS integration"""
    
    def __init__(self, api_key: str, voice_id: str = "79a125e8-cd45-4c13-8a67-188112f4dd22"):
        """
        Initialize Cartesia TTS
        
        Popular voice IDs:
        - "79a125e8-cd45-4c13-8a67-188112f4dd22" - Professional male (British)
        - "a0e99841-438c-4a64-b679-ae501e7d6091" - Friendly female (American)
        - "421b3369-f63f-4b03-8980-37a44df1d4e8" - Warm female (American)
        - "248be419-c632-4f23-adf1-5324ed7dbf1d" - Conversational male (American)
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.cartesia.ai/tts/bytes"
        
    def text_to_speech(self, text: str, output_file: str = "output.wav"):
        """
        Convert text to speech and save as audio file
        
        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
        
        Returns:
            Path to the saved audio file, or None if failed
        """
        headers = {
            "X-API-Key": self.api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model_id": "sonic-english",
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": self.voice_id
            },
            "output_format": {
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 44100
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return output_file
            else:
                print(f"Error from Cartesia API: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return None


class OllamaChatWithVoice:
    """Ollama chat with voice output capabilities"""
    
    def __init__(self, system_prompt, model="llama3.2", enable_tts=True):
        self.model = model
        self.history = [{
            "role": "system",
            "content": system_prompt
        }]
        self.enable_tts = enable_tts
        
        # Initialize TTS if enabled
        if self.enable_tts:
            cartesia_key = os.getenv("CARTESIA_API_KEY")
            if cartesia_key:
                self.tts = CartesiaTTS(
                    api_key=cartesia_key,
                    voice_id=os.getenv("CARTESIA_VOICE_ID", "79a125e8-cd45-4c13-8a67-188112f4dd22")
                )
                print("✓ Cartesia TTS enabled")
            else:
                print("⚠ CARTESIA_API_KEY not found. TTS disabled.")
                self.enable_tts = False

    def generate_response(self, prompt):
        try:
            # Using stream=True for streaming responses
            response_stream = ollama.chat(
                model=self.model,
                messages=self.history + [{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Initialize full response content
            full_response = ""
            print(f"\n{self.model}: ", end="", flush=True)
            
            # Process the stream
            for chunk in response_stream:
                chunk_content = chunk['message']['content']
                print(chunk_content, end="", flush=True)
                full_response += chunk_content
                
            print()  # New line after response
            
            # Convert to speech if TTS is enabled
            if self.enable_tts and full_response:
                print("🔊 Generating speech...", end="", flush=True)
                audio_file = self.tts.text_to_speech(full_response, "response.wav")
                if audio_file:
                    print(f" Saved to {audio_file}")
                    self._play_audio(audio_file)
                else:
                    print(" Failed")
            
            return full_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _play_audio(self, audio_file):
        """Play audio file using available system player"""
        import platform
        import subprocess
        
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_file], check=True)
            elif system == "Linux":
                # Try multiple players
                players = ["aplay", "paplay", "ffplay", "mpg123"]
                for player in players:
                    try:
                        subprocess.run([player, audio_file], check=True, stderr=subprocess.DEVNULL)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif system == "Windows":
                import winsound
                winsound.PlaySound(audio_file, winsound.SND_FILENAME)
            else:
                print(f"  (Auto-play not supported on {system}. Please play {audio_file} manually)")
        except Exception as e:
            print(f"  (Could not auto-play: {e})")

    def load_chat_history(self, filename):
        """Load chat history from a text file"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            # Preserve system prompt
            system_prompt = self.history[0]
            self.history = [system_prompt]
            
            current_message = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("You: "):
                    if current_message:
                        self.history.append({
                            "role": "assistant",
                            "content": current_message.strip()
                        })
                    current_message = line[5:]
                    self.history.append({
                        "role": "user",
                        "content": current_message.strip()
                    })
                    current_message = ""
                elif line.startswith(f"{self.model}: "):
                    if current_message:
                        self.history.append({
                            "role": "user",
                            "content": current_message.strip()
                        })
                    current_message = line[len(f"{self.model}: "):]
                    
            if current_message:
                self.history.append({
                    "role": "assistant",
                    "content": current_message.strip()
                })
                
            print(f"Chat history loaded from {filename}")
            return True
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            return False

    def chat(self):
        print(f"Chat with {self.model} (type 'quit' to exit)")
        if self.enable_tts:
            print("🔊 Voice output: ENABLED")
        print("-" * 50)

        # Ask user if they want to load previous chat history
        load_history = input("Would you like to load previous chat history? (y/n): ").strip().lower()
        if load_history == 'y':
            filename = input("Enter the path to your chat history text file: ").strip()
            self.load_chat_history(filename)

        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("\nGoodbye!")
                break
            
            if user_input:
                self.history.append({"role": "user", "content": user_input})
                response = self.generate_response(user_input)
                self.history.append({"role": "assistant", "content": response})


def main():
    # Check for Cartesia API key
    if not os.getenv("CARTESIA_API_KEY"):
        print("\n⚠️  Warning: CARTESIA_API_KEY not found in environment variables")
        print("TTS will be disabled. To enable voice output:")
        print("1. Create a .env file")
        print("2. Add: CARTESIA_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://cartesia.ai/\n")
    
    # Custom system prompt
    custom_prompt = """You are a debate focused AI whose job is to challenge my arguments, present strong counterarguments, and clearly point out any logical fallacies or weak assumptions. Maintain a firm, rational, and respectful tone. Do not simply agree—critique, question, and push the reasoning deeper. When you identify a flaw, name the fallacy and briefly explain why it applies. Keep responses concise, focused, and intellectually rigorous. Always maintain confidentiality and respect throughout our conversations."""
    
    # Create chatbot with voice capabilities
    chat_bot = OllamaChatWithVoice(
        system_prompt=custom_prompt,
        model="llama3.2",
        enable_tts=True  # Enable text-to-speech
    )
    chat_bot.chat()


if __name__ == "__main__":
    main()
