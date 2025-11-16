"""
LiveKit Voice Agent with Ollama LLM and Cartesia TTS
Text input -> Ollama processing -> Cartesia TTS -> LiveKit audio output
"""

import asyncio
import logging
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import cartesia
import ollama
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaLLM:
    """Ollama LLM integration for debate-focused chat"""
    
    def __init__(self, system_prompt: str, model: str = "llama3.2"):
        self.model = model
        self.history = [{
            "role": "system",
            "content": system_prompt
        }]
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: User's text input
            
        Returns:
            AI's response text
        """
        try:
            # Add user message to history
            self.history.append({"role": "user", "content": prompt})
            
            logger.info(f"User: {prompt}")
            
            # Get response from Ollama (streaming)
            response_stream = ollama.chat(
                model=self.model,
                messages=self.history,
                stream=True
            )
            
            full_response = ""
            for chunk in response_stream:
                chunk_content = chunk['message']['content']
                full_response += chunk_content
            
            # Add assistant response to history
            self.history.append({"role": "assistant", "content": full_response})
            
            logger.info(f"AI: {full_response[:100]}...")
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"


async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit agent"""
    
    # System prompt for the debate-focused AI
    system_prompt = """You are a debate focused AI whose job is to challenge arguments, 
    present strong counterarguments, and clearly point out any logical fallacies or weak assumptions. 
    Maintain a firm, rational, and respectful tone. Do not simply agree—critique, question, 
    and push the reasoning deeper. When you identify a flaw, name the fallacy and briefly explain 
    why it applies. Keep responses concise, focused, and intellectually rigorous."""
    
    # Initialize Ollama LLM
    ollama_llm = OllamaLLM(system_prompt=system_prompt, model="llama3.2")
    
    logger.info("Connecting to room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.SUBSCRIBE_NONE)
    
    # Wait for participant
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant connected: {participant.identity}")
    
    # Initialize Cartesia TTS
    cartesia_api_key = os.getenv("CARTESIA_API_KEY")
    cartesia_voice_id = os.getenv("CARTESIA_VOICE_ID", "79a125e8-cd45-4c13-8a67-188112f4dd22")
    
    if not cartesia_api_key:
        logger.error("CARTESIA_API_KEY not found in environment variables")
        return
    
    tts = cartesia.TTS(
        api_key=cartesia_api_key,
        voice=cartesia_voice_id,
        model="sonic-english",
    )
    
    logger.info(f"Cartesia TTS initialized with voice: {cartesia_voice_id}")
    
    # Create audio source for streaming
    audio_source = rtc.AudioSource(sample_rate=24000, num_channels=1)
    audio_track = rtc.LocalAudioTrack.create_audio_track("agent-voice", audio_source)
    
    # Publish audio track
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_MICROPHONE
    await ctx.room.local_participant.publish_track(audio_track, options)
    
    logger.info("Audio track published")
    
    # Send greeting
    greeting = "Hello! I'm your debate partner. Send me a message and I'll challenge your arguments with critical analysis. What would you like to discuss?"
    
    # Convert greeting to speech and stream
    await synthesize_and_stream(greeting, tts, audio_source)
    
    # Send greeting as data message too
    await ctx.room.local_participant.publish_data(
        greeting.encode('utf-8'),
        topic="chat"
    )
    
    # Listen for data messages (text input from participant)
    @ctx.room.on("data_received")
    async def on_data_received(data: rtc.DataPacket):
        """Handle incoming text messages"""
        if data.topic == "chat":
            try:
                user_message = data.data.decode('utf-8')
                logger.info(f"Received message: {user_message}")
                
                # Generate response from Ollama
                ai_response = await ollama_llm.generate_response(user_message)
                
                # Send response as data (for text display)
                await ctx.room.local_participant.publish_data(
                    ai_response.encode('utf-8'),
                    topic="chat"
                )
                
                # Convert to speech and stream audio
                await synthesize_and_stream(ai_response, tts, audio_source)
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    
    logger.info("Agent is ready and listening for messages...")
    
    # Keep the agent running
    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        await asyncio.sleep(0.1)


async def synthesize_and_stream(text: str, tts: cartesia.TTS, audio_source: rtc.AudioSource):
    """
    Synthesize text to speech using Cartesia and stream to LiveKit
    
    Args:
        text: Text to synthesize
        tts: Cartesia TTS instance
        audio_source: LiveKit audio source to stream to
    """
    try:
        logger.info(f"Synthesizing speech: {text[:50]}...")
        
        # Synthesize speech with Cartesia
        async for audio_chunk in tts.synthesize(text):
            # Stream audio chunk to LiveKit
            await audio_source.capture_frame(audio_chunk)
        
        logger.info("Speech synthesis complete")
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")


def main():
    """Run the LiveKit agent"""
    
    # Check required environment variables
    required_vars = {
        "LIVEKIT_URL": "LiveKit server URL",
        "LIVEKIT_API_KEY": "LiveKit API key",
        "LIVEKIT_API_SECRET": "LiveKit API secret",
        "CARTESIA_API_KEY": "Cartesia API key for TTS"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("\nPlease copy .env.example to .env and fill in your API keys")
        return
    
    logger.info("Starting LiveKit agent with Cartesia TTS...")
    
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
