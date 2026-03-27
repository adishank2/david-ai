# David AI Assistant 🤖

David is a secure, local-first, voice-activated AI assistant for Windows. It controls your OS, manages tasks, and converses naturally—all while keeping your data private.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 🚀 Key Features

### ⚡ Optimized Performance
- **10x Faster Wake Word:** Uses tiny Whisper model for instant "Hey David" detection.
- **Smart Caching:** Common responses are cached for 0-latency replies.
- **Memory Efficient:** Models loaded intelligently to save RAM.

### 🔒 Privacy & Security
- **Local Processing:** Runs locally using Ollama (phi3/llama3) and Whisper.
- **Security Hardening:** Command validation, file path whitelisting, and audit logging.
- **Privacy First:** Your voice data never leaves your machine.

### 💪 Power Features
- **Custom Shortcuts:** "Work mode", "Focus mode", and create your own.
- **Pattern Recognition:** Remembers your habits and makes proactive suggestions.
- **Context Awareness:** Remembers previous conversations and context.

### 🗣️ Natural Interaction
- **Conversational:** Friendly, human-like personality.
- **WhatsApp Integration:** Send messages hands-free.
- **Music Playback:** Play local music files by voice.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/David.git
   cd David
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv david-env
   david-env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama:**
   - Download from [ollama.com](https://ollama.com)
   - Pull the model: `ollama pull phi3` (or `llama3`)

5. **Install FFMPEG:**
   - Required for audio processing. [Download here](https://ffmpeg.org/download.html).

---

## 🎮 Quick Start

1. **Activate environment:**
   ```bash
   david-env\Scripts\activate
   ```

2. **Run David:**
   ```bash
   python main.py
   ```

3. **Say "Hey David":**
   - *"Open Chrome"*
   - *"Play music by Queen"*
   - *"Send WhatsApp to Mom saying hello"*
   - *"Work mode"*

---

## 📚 Documentation

- [**Troubleshooting Guide**](file:///C:/Users/Adish/.gemini/antigravity/brain/8f686cbb-679b-4832-90ee-0217142327dd/troubleshooting.md) - Solutions for microphone, TTS, and other issues.
- [**Security Guide**](file:///C:/Users/Adish/.gemini/antigravity/brain/8f686cbb-679b-4832-90ee-0217142327dd/security_guide.md) - Details on security features and audit logs.
- [**Power Features**](file:///C:/Users/Adish/.gemini/antigravity/brain/8f686cbb-679b-4832-90ee-0217142327dd/power_features_guide.md) - How to use shortcuts and patterns.
- [**Walkthrough**](file:///C:/Users/Adish/.gemini/antigravity/brain/8f686cbb-679b-4832-90ee-0217142327dd/walkthrough.md) - Full development history and features.

---

## ⚙️ Configuration

Edit `core/config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `WAKE_WORD` | "hey david" | The phrase to activate assistant |
| `RECORDING_DURATION` | 5 | Seconds to listen after wake word |
| `MODEL_NAME` | "phi3" | Ollama model to use |
| `FILE_OPS_ALLOWED_DIRS` | Docs, Downloads | Whitelisted directories |

**Contacts & Shortcuts:**
- `contacts.json`: Add WhatsApp contacts
- `shortcuts.json`: Create custom voice shortcuts

---

## 🧪 Testing

Run internal tests to verify system health:

```bash
# Test Microphone
python test_microphone.py

# Test Performance
python test_performance.py
```

---

## 🤝 Contributing

Contributions are welcome! Please read the security guidelines before submitting pull requests.

## 📄 License

MIT License - see `LICENSE` for details.
