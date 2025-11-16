import asyncio
import logging
from typing import Annotated
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
from livekit.plugins import openai, deepgram, silero
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


async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit voice agent"""
    
    # System prompt for the debate-focused AI
    system_prompt = """You are a debate focused AI whose job is to challenge arguments, 
    present strong counterarguments, and clearly point out any logical fallacies or weak assumptions. 
    Maintain a firm, rational, and respectful tone. Do not simply agree—critique, question, 
    and push the reasoning deeper. When you identify a flaw, name the fallacy and briefly explain 
    why it applies. Keep responses concise, focused, and intellectually rigorous."""
    
    # Initialize the Ollama chat
    ollama_chat = OllamaVoiceChat(system_prompt=system_prompt, model="llama3.2")
    
    # Initialize LiveKit components
    initial_ctx = agents.llm.ChatContext().append(
        role="system",
        text=system_prompt,
    )
    
    logger.info("Connecting to room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    
    # Create participant for the agent
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant connected: {participant.identity}")
    
    # Configure Speech-to-Text (STT) using Deepgram
    stt = deepgram.STT(
        model="nova-2-general",
        language="en-US",
    )
    
    # Configure Text-to-Speech (TTS) - Using OpenAI TTS as Cartesia plugin needs specific setup
    # You can replace this with Cartesia TTS once you have the plugin configured
    tts_engine = openai.TTS(
        voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
        model="tts-1",
    )
    
    # Alternative: If you have Cartesia configured, use this instead:
    # from livekit.plugins import cartesia
    # tts_engine = cartesia.TTS(
    #     voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # Cartesia voice ID
    #     model="sonic-english",
    # )
    
    # Create the assistant with voice capabilities
    assistant = agents.VoiceAssistant(
        vad=silero.VAD.load(),  # Voice Activity Detection
        stt=stt,
        llm=openai.LLM(model="gpt-4"),  # Placeholder for coordination
        tts=tts_engine,
        chat_ctx=initial_ctx,
    )
    
    # Custom function to handle Ollama responses
    async def _on_user_speech(assistant: agents.VoiceAssistant, speech: str):
        """Handle user speech and generate Ollama response"""
        logger.info(f"User said: {speech}")
        
        # Generate response from Ollama
        full_response = ""
        async for chunk in ollama_chat.generate_response_stream(speech):
            full_response += chunk
        
        logger.info(f"AI response: {full_response}")
        
        # Send response to TTS
        await assistant.say(full_response, allow_interruptions=True)
    
    # Override the assistant's speech handler
    assistant.on("user_speech_committed", _on_user_speech)
    
    # Start the assistant
    assistant.start(ctx.room, participant)
    
    # Greet the user
    await assistant.say(
        "Hello! I'm your debate partner. I'm here to challenge your arguments "
        "and help you think more critically. What would you like to discuss?",
        allow_interruptions=True
    )
    
    logger.info("Voice agent is ready and listening...")


async def request_fnc(req: agents.llm.FunctionCallContext) -> None:
    """Handle function calls from the LLM"""
    logger.info(f"Function call requested: {req.function_name}")
    # Add custom function handling here if needed


def main():
    """Run the LiveKit voice agent"""
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
