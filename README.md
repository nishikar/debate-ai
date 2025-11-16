# Ollama Debate Chatbot with LiveKit Voice Agent

This project provides both text-based and voice-enabled AI debate chatbots using Ollama for the LLM backend, with optional LiveKit integration for real-time voice conversations using Cartesia TTS.

## Features

- **Text-based Chat** (`chat_deb.py`): Traditional terminal-based chat interface
- **Voice-enabled Agent** (`voice_agent_cartesia.py`): Real-time voice conversations using LiveKit and Cartesia TTS
- Debate-focused AI that challenges arguments and identifies logical fallacies
- Streaming responses for better user experience
- Chat history loading and persistence

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally ([Installation Guide](https://ollama.ai/))
- Ollama model `llama3.2` downloaded: `ollama pull llama3.2`

## Installation

### 1. Clone and Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set up Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull the required model
ollama pull llama3.2

# Verify Ollama is running
ollama list
```

### 3. Configure Environment Variables (for Voice Agent)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

Required API keys for voice agent:
- **LiveKit**: Get from [LiveKit Cloud](https://cloud.livekit.io/)
  - `LIVEKIT_URL`: Your LiveKit server URL
  - `LIVEKIT_API_KEY`: Your API key
  - `LIVEKIT_API_SECRET`: Your API secret
  
- **Deepgram**: Get from [Deepgram Console](https://console.deepgram.com/)
  - `DEEPGRAM_API_KEY`: For speech-to-text

- **Cartesia**: Get from [Cartesia](https://cartesia.ai/)
  - `CARTESIA_API_KEY`: For high-quality text-to-speech

- **OpenAI** (optional fallback): Get from [OpenAI Platform](https://platform.openai.com/)
  - `OPENAI_API_KEY`: Fallback TTS if Cartesia is not available

## Usage

### Text-based Chat

Run the original terminal-based chatbot:

```bash
python chat_deb.py
```

Features:
- Type your messages and press Enter
- Type `quit` to exit
- Option to load previous chat history from a text file

### Voice-enabled Chat (LiveKit + Cartesia TTS)

Run the voice-enabled agent:

```bash
python voice_agent_cartesia.py
```

This will:
1. Connect to your LiveKit server
2. Wait for a participant to join the room
3. Listen for voice input using Deepgram STT
4. Process input through Ollama LLM
5. Convert responses to speech using Cartesia TTS
6. Stream audio back to the participant

## Architecture

### Text-based Chat Flow
```
User Input → Ollama LLM → Streaming Response → Terminal Output
```

### Voice-enabled Chat Flow
```
User Voice → Deepgram STT → Ollama LLM → Cartesia TTS → Audio Output
```

## File Structure

```
.
├── chat_deb.py                  # Original text-based chatbot
├── voice_agent.py               # LiveKit voice agent (OpenAI TTS)
├── voice_agent_cartesia.py      # LiveKit voice agent (Cartesia TTS)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Customization

### Change the System Prompt

Edit the `system_prompt` variable in any of the Python files:

```python
custom_prompt = """Your custom system prompt here"""
```

### Change the Ollama Model

Modify the `model` parameter:

```python
chat_bot = OllamaChat(
    system_prompt=custom_prompt,
    model="llama3.2"  # Change to any Ollama model
)
```

Available models (after pulling with `ollama pull <model>`):
- `llama3.2` (default)
- `llama3.1`
- `mistral`
- `codellama`
- And many more from [Ollama Library](https://ollama.ai/library)

### Change Cartesia Voice

In `voice_agent_cartesia.py`, modify the `voice_id`:

```python
cartesia_tts = CartesiaTTS(
    api_key=cartesia_api_key,
    voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22"  # Change this
)
```

Popular Cartesia voices:
- `79a125e8-cd45-4c13-8a67-188112f4dd22` - Professional male
- `a0e99841-438c-4a64-b679-ae501e7d6091` - Friendly female
- `421b3369-f63f-4b03-8980-37a44df1d4e8` - Warm female

Visit [Cartesia Voice Library](https://cartesia.ai/voices) for more options.

## LiveKit Setup

### Option 1: Use LiveKit Cloud (Easiest)

1. Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. Create a new project
3. Copy your API key, secret, and WebSocket URL to `.env`

### Option 2: Self-host LiveKit Server

```bash
# Using Docker
docker run -d \
  --name livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -v $PWD/livekit.yaml:/livekit.yaml \
  livekit/livekit-server \
  --config /livekit.yaml
```

See [LiveKit Deployment Guide](https://docs.livekit.io/realtime/self-hosting/deployment/) for details.

## Connecting to the Voice Agent

### Using LiveKit Web Example

1. Get a participant token from your LiveKit dashboard
2. Use the LiveKit example frontend: https://meet.livekit.io/custom
3. Enter your LiveKit URL and token
4. Join the room and start speaking!

### Using Custom Client

You can build custom clients using LiveKit SDKs:
- [JavaScript/TypeScript SDK](https://docs.livekit.io/client-sdk-js/)
- [React SDK](https://docs.livekit.io/client-sdk-react/)
- [Swift SDK](https://docs.livekit.io/client-sdk-swift/)
- [Android SDK](https://docs.livekit.io/client-sdk-android/)

## Troubleshooting

### Ollama Connection Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
# On macOS/Linux: restart the Ollama app
# On Linux with systemd:
systemctl restart ollama
```

### Voice Agent Not Working

1. **Check API Keys**: Ensure all required API keys are set in `.env`
2. **Check LiveKit Connection**: Verify `LIVEKIT_URL` is correct
3. **Check Deepgram**: Verify `DEEPGRAM_API_KEY` is valid
4. **Check Cartesia**: Verify `CARTESIA_API_KEY` is valid

### Cartesia Plugin Not Found

If you get an import error for Cartesia:

```bash
# Install the Cartesia plugin separately
pip install livekit-plugins-cartesia

# Or use the fallback to OpenAI TTS (set OPENAI_API_KEY)
```

### Audio Quality Issues

- Increase sample rate in `AudioSource` (default: 24000 Hz)
- Try different Cartesia voices
- Check network bandwidth and latency

## Performance Tips

1. **Faster Response Times**: Use smaller Ollama models like `llama3.2:1b`
2. **Better Quality**: Use larger models like `llama3.1:70b` (requires more resources)
3. **Streaming**: The code uses streaming for both LLM and TTS for lower latency

## Development

### Adding New Features

The code is modular and easy to extend:

- **Add custom LLM providers**: Modify the `generate_response_stream` method
- **Add different TTS providers**: Create new TTS wrapper classes
- **Add custom STT**: Replace Deepgram with other providers
- **Add function calling**: Implement custom functions in the agent

### Testing

```bash
# Test text chat locally
python chat_deb.py

# Test voice agent (requires LiveKit setup)
python voice_agent_cartesia.py
```

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Cartesia API Documentation](https://docs.cartesia.ai/)
- [Deepgram API Documentation](https://developers.deepgram.com/)

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
- Ollama: https://github.com/ollama/ollama/issues
- LiveKit: https://github.com/livekit/livekit/issues
- Cartesia: https://cartesia.ai/support

## Contributing

Feel free to submit issues and enhancement requests!
