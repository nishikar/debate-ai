# Ollama Debate Chatbot with Cartesia TTS

A debate-focused AI chatbot using Ollama for the LLM backend, with optional Cartesia text-to-speech integration for voice output.

## Features

- **Text-based Chat** (`chat_deb.py`): Traditional terminal-based chat interface
- **Voice-enabled Chat** (`chat_with_voice.py`): Same chat with Cartesia TTS voice output
- **Speech-to-Text**: Optional voice input using OpenAI Whisper
- Debate-focused AI that challenges arguments and identifies logical fallacies
- Streaming responses for better user experience
- Chat history loading and persistence
- High-quality voice synthesis with Cartesia

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally ([Installation Guide](https://ollama.ai/))
- Ollama model `llama3.2` downloaded: `ollama pull llama3.2`
- Cartesia API key (for voice output) - Get from [Cartesia](https://cartesia.ai/)
- OpenAI API key (optional, only for voice input) - Get from [OpenAI](https://platform.openai.com/)

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

### 3. Configure API Keys (for voice features)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Cartesia API key
```

Example `.env` file:
```bash
CARTESIA_API_KEY=your_cartesia_api_key_here
CARTESIA_VOICE_ID=79a125e8-cd45-4c13-8a67-188112f4dd22
OPENAI_API_KEY=your_openai_key_here  # Optional, for voice input
```

## Usage

### Option 1: Text-only Chat (No API key needed)

```bash
python chat_deb.py
```

Features:
- Type your messages and press Enter
- Type `quit` to exit
- Option to load previous chat history from a text file

### Option 2: Chat with Voice Output (Requires Cartesia API key)

```bash
python chat_with_voice.py
```

Features:
- Same text chat interface
- AI responses are automatically converted to speech using Cartesia TTS
- Audio is saved to `response.wav` and played automatically
- Type `voice` to transcribe an audio file (requires OpenAI API key)

## Architecture

### Text Chat Flow
```
User Input → Ollama LLM → Streaming Response → Terminal Output
```

### Voice-enabled Chat Flow
```
User Input → Ollama LLM → Streaming Response → Terminal Output
                                              ↓
                                    Cartesia TTS → Audio File → Speaker
```

### Voice Input Flow (Optional)
```
Audio File → OpenAI Whisper STT → Text → Ollama LLM → Cartesia TTS → Audio Output
```

## Cartesia TTS Details

### Why Cartesia?

Cartesia provides:
- **Ultra-low latency**: Faster than traditional TTS systems
- **High quality**: Natural, human-like voices
- **Streaming support**: Real-time audio generation
- **Multiple voices**: Professional, friendly, warm options

### Available Voices

Popular voice IDs (set in `.env` as `CARTESIA_VOICE_ID`):

| Voice ID | Description |
|----------|-------------|
| `79a125e8-cd45-4c13-8a67-188112f4dd22` | Professional male (British) - Default |
| `a0e99841-438c-4a64-b679-ae501e7d6091` | Friendly female (American) |
| `421b3369-f63f-4b03-8980-37a44df1d4e8` | Warm female (American) |
| `248be419-c632-4f23-adf1-5324ed7dbf1d` | Conversational male (American) |

Browse all voices at: [https://cartesia.ai/voices](https://cartesia.ai/voices)

### API Usage

The implementation uses Cartesia's REST API:
- Endpoint: `https://api.cartesia.ai/tts/bytes`
- Model: `sonic-english` (fastest model)
- Output format: WAV, PCM 16-bit, 44.1kHz

## Speech-to-Text (STT) Options

**Note**: Cartesia is a TTS (text-to-speech) provider and does not offer STT services.

For voice input, the implementation uses **OpenAI Whisper API**:

### Why Whisper?

- Industry-leading accuracy
- Supports 50+ languages
- Fast transcription
- Easy API integration

### Alternative STT Options

If you prefer not to use OpenAI, you can integrate:

1. **Local Whisper** (Free, runs on your machine)
```bash
pip install openai-whisper
```

2. **Google Speech-to-Text** (Paid)
3. **AssemblyAI** (Paid, good quality)
4. **Deepgram** (Paid, very fast)

To add a different STT provider, modify the `WhisperSTT` class in `chat_with_voice.py`.

## Customization

### Change the System Prompt

Edit the `custom_prompt` variable in `chat_deb.py` or `chat_with_voice.py`:

```python
custom_prompt = """Your custom system prompt here"""
```

### Change the Ollama Model

Modify the `model` parameter:

```python
chat_bot = OllamaChatWithVoice(
    system_prompt=custom_prompt,
    model="llama3.2"  # Change to any Ollama model
)
```

Available models (after pulling with `ollama pull <model>`):
- `llama3.2` (default, 3B parameters)
- `llama3.1` (larger, more capable)
- `mistral` (fast and efficient)
- `codellama` (for coding tasks)
- And many more from [Ollama Library](https://ollama.ai/library)

### Change Voice Settings

In `chat_with_voice.py`, modify the initialization:

```python
self.tts = CartesiaTTS(
    api_key=cartesia_key,
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"  # Friendly female
)
```

### Disable Voice Features

Set `enable_tts` and `enable_stt` to `False`:

```python
chat_bot = OllamaChatWithVoice(
    system_prompt=custom_prompt,
    model="llama3.2",
    enable_tts=False,  # Disable voice output
    enable_stt=False   # Disable voice input
)
```

## File Structure

```
.
├── chat_deb.py              # Original text-based chatbot
├── chat_with_voice.py       # Voice-enabled chatbot with Cartesia TTS
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Troubleshooting

### Ollama Connection Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
# On macOS/Windows: restart the Ollama app
# On Linux with systemd:
systemctl restart ollama
```

### Cartesia API Error

1. **Check API Key**: Ensure `CARTESIA_API_KEY` is set correctly in `.env`
2. **Check API Status**: Visit [Cartesia Status](https://status.cartesia.ai/)
3. **Verify Credit**: Check your account has available credits

### Voice Not Playing

The app tries to auto-play audio using system players:
- **macOS**: Uses `afplay`
- **Linux**: Tries `aplay`, `paplay`, `ffplay`, or `mpg123`
- **Windows**: Uses `winsound`

If auto-play fails, manually play the `response.wav` file.

### OpenAI Whisper Error (Voice Input)

1. **Check API Key**: Ensure `OPENAI_API_KEY` is set in `.env`
2. **Check Audio Format**: Whisper supports MP3, MP4, WAV, M4A, WEBM, etc.
3. **Check File Size**: Max file size is 25MB

### "No module named 'dotenv'" Error

```bash
pip install python-dotenv
```

## Performance Tips

1. **Faster Responses**: Use smaller Ollama models like `llama3.2:1b`
2. **Better Quality**: Use larger models like `llama3.1:70b` (requires more resources)
3. **Streaming**: The code uses streaming for both LLM and TTS for lower latency

## API Costs

### Cartesia TTS
- Pay-as-you-go pricing
- Free tier available
- Check latest pricing: [https://cartesia.ai/pricing](https://cartesia.ai/pricing)

### OpenAI Whisper (Optional, for STT)
- $0.006 per minute of audio
- Check latest pricing: [https://openai.com/pricing](https://openai.com/pricing)

### Ollama
- **Free!** Runs locally on your machine
- No API costs

## Example Session

```
Chat with llama3.2 (type 'quit' to exit)
🔊 Voice output: ENABLED
🎤 Voice input: Type 'voice' to transcribe an audio file
--------------------------------------------------
Would you like to load previous chat history? (y/n): n

You: I think artificial intelligence will solve all of humanity's problems.

llama3.2: That's an overly optimistic claim that commits the fallacy of 
hasty generalization. While AI has potential to address certain challenges, 
claiming it will solve "all" problems ignores several critical factors:

1. AI cannot address fundamental human issues like empathy, ethics, or 
   meaning - these require human wisdom.
2. Many problems are social, political, or cultural and require human 
   consensus and cooperation, not just technical solutions.
3. AI itself introduces new problems: bias, job displacement, privacy 
   concerns, and potential misuse.

Your argument also assumes technological determinism - that technology 
alone drives progress, ignoring human agency and choice. Can you clarify 
what specific problems you think AI will solve, and why other approaches 
wouldn't work?

🔊 Generating speech... Saved to response.wav
[Audio plays automatically]

You: quit
Goodbye!
```

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Cartesia API Documentation](https://docs.cartesia.ai/)
- [Cartesia Voice Library](https://cartesia.ai/voices)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!
