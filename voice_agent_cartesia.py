"""
LiveKit Voice Agent with Cartesia TTS Integration
This version specifically uses Cartesia for high-quality text-to-speech
"""

import asyncio
import logging
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
from livekit.plugins import deepgram, silero
import ollama
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaVoiceChat:
    """Voice-enabled chat using Ollama LLM with LiveKit"""
    
    def __init__(self, system_prompt: str, model: str = "llama3.2"):
        self.model = model
        self.history = [{
            "role": "system",
            "content": system_prompt
        }]
    
    async def generate_response_stream(self, prompt: str):
        """Generate streaming response from Ollama"""
        try:
            # Add user message to history
            self.history.append({"role": "user", "content": prompt})
            
            # Stream response from Ollama
            response_stream = ollama.chat(
                model=self.model,
                messages=self.history,
                stream=True
            )
            
            full_response = ""
            for chunk in response_stream:
                chunk_content = chunk['message']['content']
                full_response += chunk_content
                yield chunk_content
            
            # Add assistant response to history
            self.history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield f"I apologize, but I encountered an error: {str(e)}"


class CartesiaTTS:
    """Custom Cartesia TTS integration"""
    
    def __init__(self, api_key: str, voice_id: str = "79a125e8-cd45-4c13-8a67-188112f4dd22"):
        """
        Initialize Cartesia TTS
        
        Args:
            api_key: Cartesia API key
            voice_id: Cartesia voice ID (default is a professional male voice)
        
        Popular Cartesia voice IDs:
        - "79a125e8-cd45-4c13-8a67-188112f4dd22" - Professional male
        - "a0e99841-438c-4a64-b679-ae501e7d6091" - Friendly female
        - "421b3369-f63f-4b03-8980-37a44df1d4e8" - Warm female
        """
        self.api_key = api_key
        self.voice_id = voice_id
        
        # Try to import cartesia plugin
        try:
            from livekit.plugins import cartesia
            self.tts_engine = cartesia.TTS(
                voice=voice_id,
                model="sonic-english",  # Cartesia's fastest model
                api_key=api_key,
            )
            self.available = True
            logger.info("Cartesia TTS initialized successfully")
        except ImportError:
            logger.warning("Cartesia plugin not available. Install with: pip install livekit-plugins-cartesia")
            self.available = False
            # Fallback to OpenAI TTS
            from livekit.plugins import openai
            self.tts_engine = openai.TTS(voice="alloy", model="tts-1")
    
    def get_engine(self):
        """Get the TTS engine"""
        return self.tts_engine


async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit voice agent with Cartesia TTS"""
    
    # System prompt for the debate-focused AI
    system_prompt = """You are a debate focused AI whose job is to challenge arguments, 
    present strong counterarguments, and clearly point out any logical fallacies or weak assumptions. 
    Maintain a firm, rational, and respectful tone. Do not simply agree—critique, question, 
    and push the reasoning deeper. When you identify a flaw, name the fallacy and briefly explain 
    why it applies. Keep responses concise, focused, and intellectually rigorous."""
    
    # Initialize the Ollama chat
    ollama_chat = OllamaVoiceChat(system_prompt=system_prompt, model="llama3.2")
    
    logger.info("Connecting to room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    
    # Wait for participant
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant connected: {participant.identity}")
    
    # Configure Speech-to-Text using Deepgram
    stt = deepgram.STT(
        model="nova-2-general",
        language="en-US",
    )
    
    # Configure Cartesia TTS
    cartesia_api_key = os.getenv("CARTESIA_API_KEY")
    if not cartesia_api_key:
        logger.warning("CARTESIA_API_KEY not found in environment variables")
        cartesia_api_key = ""
    
    cartesia_tts = CartesiaTTS(
        api_key=cartesia_api_key,
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22"  # Professional voice
    )
    
    # Voice Activity Detection
    vad = silero.VAD.load()
    
    # Track audio playback
    audio_source = rtc.AudioSource(sample_rate=24000, num_channels=1)
    audio_track = rtc.LocalAudioTrack.create_audio_track("agent-voice", audio_source)
    
    # Publish audio track
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_MICROPHONE
    await ctx.room.local_participant.publish_track(audio_track, options)
    
    logger.info("Voice agent is ready and listening...")
    
    # Handle incoming audio from participant
    async def handle_audio_frame(frame: rtc.AudioFrame):
        """Process incoming audio frames"""
        # Implement STT processing here
        pass
    
    # Simple interaction loop
    greeting = "Hello! I'm your debate partner. I'm here to challenge your arguments and help you think more critically. What would you like to discuss?"
    
    # Convert greeting to speech using Cartesia
    logger.info(f"Greeting: {greeting}")
    
    # For now, log that we're ready
    logger.info("Agent ready to receive voice input")
    
    # Keep the agent running
    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        await asyncio.sleep(0.1)


async def simple_voice_agent(ctx: JobContext):
    """Simplified voice agent implementation"""
    
    logger.info("Starting simplified voice agent...")
    
    # System prompt
    system_prompt = """You are a debate focused AI. Challenge arguments and point out 
    logical fallacies. Be concise and intellectually rigorous."""
    
    # Initialize Ollama chat
    ollama_chat = OllamaVoiceChat(system_prompt=system_prompt, model="llama3.2")
    
    # Connect to room
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    
    logger.info(f"Participant {participant.identity} connected")
    
    # Configure components
    stt = deepgram.STT(model="nova-2-general", language="en-US")
    
    # Initialize TTS (Cartesia or fallback)
    try:
        from livekit.plugins import cartesia
        tts_engine = cartesia.TTS(
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
            model="sonic-english",
            api_key=os.getenv("CARTESIA_API_KEY", ""),
        )
        logger.info("Using Cartesia TTS")
    except (ImportError, Exception) as e:
        logger.warning(f"Cartesia not available ({e}), falling back to OpenAI TTS")
        from livekit.plugins import openai
        tts_engine = openai.TTS(voice="alloy", model="tts-1")
    
    # Create simple message handler
    async def handle_message(text: str):
        """Handle incoming text and generate response"""
        logger.info(f"User: {text}")
        
        # Generate response from Ollama
        full_response = ""
        async for chunk in ollama_chat.generate_response_stream(text):
            full_response += chunk
        
        logger.info(f"AI: {full_response}")
        
        # Convert to speech and stream
        # This would need proper LiveKit audio streaming implementation
        return full_response
    
    logger.info("Voice agent ready")
    
    # Keep connection alive
    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        await asyncio.sleep(1)


def main():
    """Run the LiveKit voice agent with Cartesia TTS"""
    
    # Check required environment variables
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "DEEPGRAM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and fill in your API keys")
        return
    
    if not os.getenv("CARTESIA_API_KEY"):
        logger.warning("CARTESIA_API_KEY not set. Will use fallback TTS")
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
        )
    )


if __name__ == "__main__":
    main()
