# Ollama Debate Chatbot with LiveKit & Cartesia TTS

A debate-focused AI chatbot using Ollama for the LLM backend with LiveKit for real-time audio streaming and Cartesia for high-quality text-to-speech.

## Features

- **Text-based Chat** (`chat_deb.py`): Traditional terminal-based chat interface
- **LiveKit Voice Agent** (`voice_agent.py`): Text input with Cartesia TTS audio output via LiveKit
- Text input via browser or custom client
- AI responses streamed as audio through LiveKit
- Debate-focused AI that challenges arguments and identifies logical fallacies
- High-quality voice synthesis with Cartesia
- Real-time audio streaming with LiveKit

## Architecture

```
User types text → LiveKit Data Channel → Ollama LLM → Cartesia TTS → LiveKit Audio Stream → Browser
```

**Flow:**
1. User sends text message via LiveKit data channel
2. Agent receives message and processes with Ollama
3. AI response is converted to speech with Cartesia TTS
4. Audio is streamed back through LiveKit audio track
5. User hears the response in their browser

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally ([Installation Guide](https://ollama.ai/))
- Ollama model `llama3.2` downloaded: `ollama pull llama3.2`
- LiveKit account and credentials - Get from [LiveKit Cloud](https://cloud.livekit.io/)
- Cartesia API key - Get from [Cartesia](https://cartesia.ai/)

## Installation

### 1. Install Dependencies

```bash
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

### 3. Set up LiveKit

**Option A: Use LiveKit Cloud (Recommended)**
1. Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. Create a new project
3. Copy your WebSocket URL, API Key, and API Secret

**Option B: Self-host LiveKit**
See [LiveKit Self-Hosting Guide](https://docs.livekit.io/home/self-hosting/deployment/)

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

Example `.env` file:
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
CARTESIA_API_KEY=your_cartesia_key
CARTESIA_VOICE_ID=79a125e8-cd45-4c13-8a67-188112f4dd22
```

## Usage

### Option 1: Text-only Chat (No setup needed)

```bash
python chat_deb.py
```

Simple terminal-based chat with no API keys required.

### Option 2: LiveKit Voice Agent (Requires setup)

**Step 1: Start the Agent**

```bash
python voice_agent.py
```

The agent will start and wait for connections.

**Step 2: Connect a Client**

You have several options:

**A. Use the Included HTML Client (Easiest)**

1. Open `client_example.html` in your browser
2. Enter your LiveKit server URL
3. Generate a token (see below) and paste it
4. Click "Connect"
5. Type your messages and hear the AI responses!

**B. Generate a Token**

You need a LiveKit token to connect. Create one using:

```bash
# Install LiveKit CLI
pip install livekit-cli

# Generate token (replace with your credentials)
livekit-cli create-token \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --join --room debate-room \
  --identity user123 \
  --valid-for 24h
```

Or use the [LiveKit Token Generator](https://docs.livekit.io/guides/access-tokens/)

**C. Use LiveKit Meet**

1. Go to https://meet.livekit.io/custom
2. Enter your server URL and token
3. Join the room
4. Use the chat to send text messages

## How It Works

### Text Input → Voice Output Flow

```
Browser Client
    │
    ├─ Send text via data channel ──────────┐
    │                                        │
    │                                        ▼
    │                              [LiveKit Agent]
    │                                        │
    │                                        ├─ Process with Ollama
    │                                        │
    │                                        ├─ Generate TTS with Cartesia
    │                                        │
    │                                        └─ Stream audio ──┐
    │                                                          │
    └─ Receive audio stream ◄─────────────────────────────────┘
```

### Key Components

1. **LiveKit Data Channel**: Sends text messages from client to agent
2. **Ollama LLM**: Processes messages and generates debate responses
3. **Cartesia TTS**: Converts text responses to natural speech
4. **LiveKit Audio Track**: Streams audio back to the client

## Cartesia Voice Options

Available voice IDs (set in `.env` as `CARTESIA_VOICE_ID`):

| Voice ID | Description |
|----------|-------------|
| `79a125e8-cd45-4c13-8a67-188112f4dd22` | Professional male (British) - **Default** |
| `a0e99841-438c-4a64-b679-ae501e7d6091` | Friendly female (American) |
| `421b3369-f63f-4b03-8980-37a44df1d4e8` | Warm female (American) |
| `248be419-c632-4f23-adf1-5324ed7dbf1d` | Conversational male (American) |

Browse more voices: [https://cartesia.ai/voices](https://cartesia.ai/voices)

## Customization

### Change the System Prompt

Edit the `system_prompt` in `voice_agent.py`:

```python
system_prompt = """Your custom prompt here"""
```

### Change the Ollama Model

Modify the model parameter:

```python
ollama_llm = OllamaLLM(system_prompt=system_prompt, model="llama3.1")
```

Available models:
- `llama3.2` (default, 3B parameters)
- `llama3.1` (larger, more capable)
- `mistral` (fast and efficient)
- And more from [Ollama Library](https://ollama.ai/library)

### Change Voice

Update `CARTESIA_VOICE_ID` in `.env` or modify the code:

```python
tts = cartesia.TTS(
    api_key=cartesia_api_key,
    voice="a0e99841-438c-4a64-b679-ae501e7d6091",  # Friendly female
    model="sonic-english",
)
```

## File Structure

```
.
├── chat_deb.py              # Original text-based chatbot
├── chat_with_voice.py       # Local voice output (no LiveKit)
├── voice_agent.py           # LiveKit agent with Cartesia TTS
├── client_example.html      # Web client for testing
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Troubleshooting

### Agent Not Starting

**Check Ollama:**
```bash
curl http://localhost:11434/api/tags
```

**Check Environment Variables:**
```bash
cat .env
```

Make sure all required variables are set.

### Client Can't Connect

1. **Check LiveKit URL**: Make sure it starts with `wss://`
2. **Verify Token**: Token must be valid and not expired
3. **Check Room Name**: Agent and client must use the same room
4. **Firewall**: Ensure ports 7880-7882 are open (if self-hosting)

### No Audio Playing

1. **Check Browser Console**: Look for errors
2. **Check Audio Element**: Audio track should be subscribed
3. **Browser Permissions**: Ensure audio playback is allowed
4. **Check Cartesia Credits**: Verify your Cartesia account has credits

### Cartesia API Errors

- `401 Unauthorized`: Check `CARTESIA_API_KEY` is correct
- `429 Rate Limited`: Slow down requests or upgrade plan
- `402 Payment Required`: Add credits to your account

### Connection Issues

**Self-hosting LiveKit:**
- Verify server is running: `docker ps`
- Check logs: `docker logs livekit`
- Ensure correct ports are exposed

**LiveKit Cloud:**
- Check [LiveKit Status](https://status.livekit.io/)
- Verify API keys in dashboard

## Performance Tips

1. **Lower Latency**: Use smaller Ollama models (`llama3.2:1b`)
2. **Better Quality**: Use larger models (`llama3.1:70b`)
3. **Audio Quality**: Cartesia's `sonic-english` is optimized for speed
4. **Network**: Use a stable connection for best audio streaming

## API Costs

### Cartesia TTS
- Pay-as-you-go pricing
- ~$0.015 per 1000 characters
- Free tier available
- [Pricing Details](https://cartesia.ai/pricing)

### LiveKit
- Free tier: 50 GB traffic/month
- Pay-as-you-go after that
- [Pricing Details](https://livekit.io/pricing)

### Ollama
- **Free!** Runs locally
- No API costs

## Example Session

**In Terminal:**
```bash
$ python voice_agent.py
INFO:root:Starting LiveKit agent with Cartesia TTS...
INFO:root:Connecting to room...
INFO:root:Participant connected: user123
INFO:root:Cartesia TTS initialized with voice: 79a125e8-cd45-4c13-8a67-188112f4dd22
INFO:root:Audio track published
INFO:root:Agent is ready and listening for messages...
```

**In Browser:**
```
User: I think artificial intelligence will solve all of humanity's problems.

AI: [Spoken aloud] That's an overly optimistic claim that commits the 
fallacy of hasty generalization. While AI has potential to address 
certain challenges, claiming it will solve "all" problems ignores 
several critical factors...
```

## Advanced Usage

### Custom Client

Build your own client using LiveKit SDKs:

```javascript
import { Room, DataPacket } from 'livekit-client';

const room = new Room();
await room.connect(wsUrl, token);

// Send text message
const encoder = new TextEncoder();
const data = encoder.encode('Hello AI');
await room.localParticipant.publishData(data, {
  reliable: true,
  topic: 'chat'
});

// Receive audio
room.on('trackSubscribed', (track) => {
  if (track.kind === 'audio') {
    const audioElement = track.attach();
    document.body.appendChild(audioElement);
  }
});
```

### Multiple Participants

The agent can handle multiple participants in the same room. Each participant can send messages and hear responses.

### Custom Audio Processing

Modify the `synthesize_and_stream` function to add effects or processing:

```python
async def synthesize_and_stream(text, tts, audio_source):
    async for audio_chunk in tts.synthesize(text):
        # Add custom processing here
        await audio_source.capture_frame(audio_chunk)
```

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Python SDK](https://docs.livekit.io/client-sdk-python/)
- [Cartesia API Docs](https://docs.cartesia.ai/)
- [Cartesia Voice Library](https://cartesia.ai/voices)

## FAQ

**Q: Can I use this without the browser client?**  
A: Yes! You can send messages via the LiveKit CLI or build a custom client.

**Q: Does this work on mobile?**  
A: Yes! The HTML client works on mobile browsers. You can also build native apps with LiveKit SDKs.

**Q: Can I add voice input (STT)?**  
A: Yes! You can extend the agent to accept audio input and use a service like Deepgram or Whisper for STT.

**Q: How many concurrent users can this handle?**  
A: Depends on your server resources. Each user processes through Ollama sequentially.

**Q: Can I deploy this to production?**  
A: Yes! Deploy the agent to a server and ensure Ollama and LiveKit are properly configured.

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!
