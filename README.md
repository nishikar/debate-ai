# Ollama Debate Chatbot with Cartesia TTS

A debate-focused AI chatbot using Ollama for the LLM backend, with optional Cartesia text-to-speech integration for voice output.

## Features

- **Text-based Chat** (`chat_deb.py`): Traditional terminal-based chat interface
- **Voice-enabled Chat** (`chat_with_voice.py`): Same chat with Cartesia TTS voice output
- Debate-focused AI that challenges arguments and identifies logical fallacies
- Streaming responses for better user experience
- Chat history loading and persistence
- High-quality voice synthesis with Cartesia

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally ([Installation Guide](https://ollama.ai/))
- Ollama model `llama3.2` downloaded: `ollama pull llama3.2`
- Cartesia API key (for voice output) - Get from [Cartesia](https://cartesia.ai/)

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

### 3. Configure API Key (for voice features)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Cartesia API key
```

Example `.env` file:
```bash
CARTESIA_API_KEY=your_cartesia_api_key_here
CARTESIA_VOICE_ID=79a125e8-cd45-4c13-8a67-188112f4dd22
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
- Type your messages as usual
- AI responses are automatically converted to speech using Cartesia TTS
- Audio is saved to `response.wav` and played automatically
- Same text input interface as the original chat

## Architecture

### Text Chat Flow
```
User Types → Ollama LLM → Streaming Response → Terminal Output
```

### Voice-enabled Chat Flow
```
User Types → Ollama LLM → Streaming Response → Terminal Output
                                              ↓
                                    Cartesia TTS → Audio File → Speaker
```

## Cartesia TTS Details

### Why Cartesia?

Cartesia provides:
- **Ultra-low latency**: Faster than traditional TTS systems
- **High quality**: Natural, human-like voices
- **Streaming support**: Real-time audio generation
- **Multiple voices**: Professional, friendly, warm options
- **Simple API**: Easy REST API integration

### Available Voices

Popular voice IDs (set in `.env` as `CARTESIA_VOICE_ID`):

| Voice ID | Description |
|----------|-------------|
| `79a125e8-cd45-4c13-8a67-188112f4dd22` | Professional male (British) - **Default** |
| `a0e99841-438c-4a64-b679-ae501e7d6091` | Friendly female (American) |
| `421b3369-f63f-4b03-8980-37a44df1d4e8` | Warm female (American) |
| `248be419-c632-4f23-adf1-5324ed7dbf1d` | Conversational male (American) |

Browse all voices at: [https://cartesia.ai/voices](https://cartesia.ai/voices)

### API Details

The implementation uses Cartesia's REST API:
- **Endpoint**: `https://api.cartesia.ai/tts/bytes`
- **Model**: `sonic-english` (fastest model)
- **Output format**: WAV, PCM 16-bit, 44.1kHz
- **Method**: Direct REST API calls (no complex frameworks)

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

In `chat_with_voice.py`, modify the initialization or update your `.env` file:

```python
# In code:
self.tts = CartesiaTTS(
    api_key=cartesia_key,
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"  # Friendly female
)

# Or in .env:
CARTESIA_VOICE_ID=a0e99841-438c-4a64-b679-ae501e7d6091
```

### Disable Voice Output

Set `enable_tts` to `False`:

```python
chat_bot = OllamaChatWithVoice(
    system_prompt=custom_prompt,
    model="llama3.2",
    enable_tts=False  # Disable voice output
)
```

## File Structure

```
.
├── chat_deb.py              # Original text-based chatbot
├── chat_with_voice.py       # Voice-enabled chatbot with Cartesia TTS
├── requirements.txt         # Python dependencies (minimal)
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
2. **Verify Format**: Make sure the key is copied correctly (no extra spaces)
3. **Check API Status**: Visit [Cartesia Status](https://status.cartesia.ai/)
4. **Verify Credit**: Check your account has available credits at [Cartesia Dashboard](https://cartesia.ai/)

Common error responses:
- `401 Unauthorized`: Invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `402 Payment Required`: No credits remaining

### Voice Not Playing

The app tries to auto-play audio using system players:
- **macOS**: Uses `afplay` (built-in)
- **Linux**: Tries `aplay`, `paplay`, `ffplay`, or `mpg123`
- **Windows**: Uses `winsound` (built-in)

If auto-play fails:
1. Check if the audio file `response.wav` was created
2. Manually play the file to verify it works
3. Install a compatible audio player:
   ```bash
   # Linux
   sudo apt-get install alsa-utils  # for aplay
   # or
   sudo apt-get install pulseaudio-utils  # for paplay
   ```

### "No module named 'dotenv'" Error

```bash
pip install python-dotenv
```

### "No module named 'requests'" Error

```bash
pip install requests
```

## Performance Tips

1. **Faster Responses**: Use smaller Ollama models like `llama3.2:1b`
   ```bash
   ollama pull llama3.2:1b
   ```

2. **Better Quality**: Use larger models like `llama3.1:70b` (requires more resources)
   ```bash
   ollama pull llama3.1:70b
   ```

3. **Streaming**: The code uses streaming for both LLM and TTS for lower latency

4. **Audio Quality**: The default 44.1kHz provides high quality. You can adjust in the code if needed.

## API Costs

### Cartesia TTS
- Pay-as-you-go pricing
- Free tier available for testing
- Approximately $0.015 per 1000 characters
- Check latest pricing: [https://cartesia.ai/pricing](https://cartesia.ai/pricing)

### Ollama
- **Free!** Runs locally on your machine
- No API costs
- Only requires local compute resources

## Example Session

```
Chat with llama3.2 (type 'quit' to exit)
🔊 Voice output: ENABLED
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
- [Ollama Model Library](https://ollama.ai/library)
- [Cartesia API Documentation](https://docs.cartesia.ai/)
- [Cartesia Voice Library](https://cartesia.ai/voices)
- [Cartesia Playground](https://play.cartesia.ai/) - Test voices online

## FAQ

**Q: Can I use this without voice output?**  
A: Yes! Use `chat_deb.py` for text-only interaction, or run `chat_with_voice.py` without setting the `CARTESIA_API_KEY`.

**Q: How do I add voice input?**  
A: Voice input (speech-to-text) is not included in this version. You can integrate services like OpenAI Whisper, Google Speech-to-Text, or run Whisper locally.

**Q: Can I use a different TTS provider?**  
A: Yes! Replace the `CartesiaTTS` class with any other TTS provider's API. The structure is simple and modular.

**Q: Does this work offline?**  
A: Ollama runs locally, so the LLM part works offline. However, Cartesia TTS requires internet connection to generate speech.

**Q: Can I save the audio files?**  
A: Yes! Audio is saved as `response.wav` in the current directory. You can modify the filename in the code.

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For issues and questions:
- **Ollama**: https://github.com/ollama/ollama/issues
- **Cartesia**: https://cartesia.ai/support
- **This Project**: Create an issue in this repository
