# 🤖 David AI — Feature Documentation

> **Version:** 2.0.0 | **Platform:** Windows (Local-First) | **Last Updated:** March 2026

---

## ✅ WHAT DAVID CAN DO

### 🧠 AI & Conversation
| Feature | Description | Voice Command Example |
|---|---|---|
| Natural Chat | General-purpose conversational AI powered by Ollama (LLaMA 3.2 / Phi3) | *"Hey David, tell me a joke"* |
| Bilingual Support | Understands and replies in English, Hindi, and Hinglish | *"David, kaise ho?"* |
| Context Memory | Remembers conversation context across exchanges (last 10 turns) | *"What did I just ask you?"* |
| Long-Term Memory | Stores personal facts using vector embeddings (Ollama) | *"My name is Dishank"* → remembers it |
| Learning From Corrections | Detects when user corrects David and stores the correction as high-priority memory | *"No David, actually the capital is Delhi"* |
| Proactive Assistant Mode | Speaks up automatically to warn you about high CPU/RAM usage, low battery, or upcoming meetings | Automatic (Runs in background) |
| Personality System | Randomized, natural-sounding responses (casual & friendly) | Automatic |
| Response Caching | Caches repeated queries for faster responses (1-hour TTL) | Automatic |

### 🎤 Voice & Speech
| Feature | Description | Details |
|---|---|---|
| Speech-to-Text | OpenAI Whisper (base model) — works offline, supports Hindi + English | Auto-detects language |
| Text-to-Speech (Cloud) | Microsoft Edge TTS — high-quality neural voices | English: `en-IN-PrabhatNeural`, Hindi: `hi-IN-MadhurNeural` |
| Text-to-Speech (Local) | PowerShell System.Speech fallback if cloud TTS fails | Automatic failover |
| Voice Activity Detection | Energy-based VAD for continuous listening mode | Configurable |
| Wake Word Detection | Porcupine wake word engine (optional) | Configurable keyword |
| Speech Interruption | Stop David mid-sentence and issue a new command | Via web UI stop button |

### 🖥️ System Control
| Feature | Voice Command | What Happens |
|---|---|---|
| Open Chrome | *"Open Chrome"* / *"Chrome kholo"* | Launches Google Chrome |
| Open Notepad | *"Open Notepad"* | Launches Notepad |
| Open Calculator | *"Open Calculator"* | Launches Calculator |
| Open Desktop | *"Open desktop folder"* | Opens Desktop in Explorer |
| Open Downloads | *"Open downloads"* | Opens Downloads in Explorer |
| Open Documents | *"Open documents"* | Opens Documents in Explorer |
| Volume Up | *"Volume up"* / *"Volume badhao"* | Increases system volume |
| Volume Down | *"Volume down"* / *"Volume kam karo"* | Decreases system volume |
| Mute | *"Mute"* / *"Band karo"* | Mutes system audio |
| Unmute | *"Unmute"* | Unmutes system audio |
| Shutdown | *"Shut down the PC"* | Asks for confirmation → shuts down |

### 🌐 Browser Automation
| Feature | Voice Command | What Happens |
|---|---|---|
| Open Website | *"Open youtube.com"* | Opens URL in default browser |
| Google Search | *"Search Google for Python tutorials"* | Opens Google search results |
| YouTube Search | *"Search YouTube for coding music"* | Opens YouTube search results |
| Close Browser | *"Close the browser"* | Kills Chrome/Firefox/Edge processes |

### 🔍 Web Search (DuckDuckGo)
| Feature | Voice Command | What Happens |
|---|---|---|
| Factual Queries | *"What is machine learning?"* | Searches DuckDuckGo → LLM summarizes results |
| How-to Queries | *"How to make pasta?"* | Fetches top 3 results and generates answer |
| News / Current Events | *"Latest news about AI"* | Searches and summarizes |

### 📅 Calendar & Reminders
| Feature | Voice Command | What Happens |
|---|---|---|
| Create Event | *"Create a meeting tomorrow at 3 PM"* | Saves event with date/time |
| List Events | *"What's on my schedule?"* | Lists upcoming events (next 7 days) |
| Delete Event | *"Delete the team meeting"* | Removes matching event |
| Set Reminder | *"Remind me to call mom at 5 PM"* | Creates a timed reminder |
| Export Calendar | *"Export my calendar"* | Exports all events to `.ics` file (compatible with Google Calendar/Outlook) |
| Import Calendar | *"Sync calendar from Downloads"* | Imports events from a `.ics` file |

### 📂 File Operations
| Feature | Voice Command | What Happens |
|---|---|---|
| Create Folder | *"Create a folder called Projects on Desktop"* | Creates folder |
| Delete File | *"Delete old_file.txt from Downloads"* | Moves to Recycle Bin (safe mode blocks it) |
| Move File | *"Move report.pdf to Documents"* | Moves file |
| Copy File | *"Copy that file to Desktop"* | Copies file |
| List Files | *"Show files in Downloads"* | Lists directory contents |
| Search Files | *"Find all PDF files in Documents"* | Glob-based recursive search |
| File Info | *"How big is that file?"* | Shows size + last modified date |
| Edit File | *"Write 'hello world' to notes.txt on Desktop"* | Creates/overwrites text file content |
| Append to File | *"Add 'buy milk' to my todo list"* | Appends text to existing file |

### 📊 System Monitoring
| Feature | Voice Command | What Happens |
|---|---|---|
| CPU Usage | *"CPU usage?"* / *"Status?"* | Reports current CPU % |
| RAM Usage | *"How much RAM is being used?"* | Reports used/total GB |
| Disk Usage | *"How much storage is left?"* | Reports disk space |
| Battery Status | *"Battery status?"* | Reports % + charging state |
| List Processes | *"What processes are running?"* | Top 5 by CPU usage |
| Kill Process | *"Kill Chrome"* | Terminates matching processes |
| Network Stats | *"Network status?"* | Shows bytes sent/received |

### 👁️ Vision (Screen Analysis)
| Feature | Voice Command | What Happens |
|---|---|---|
| Analyze Screen | *"What is on my screen?"* | Takes screenshot → sends to Ollama vision model |
| Read Screen | *"Read this error"* | Captures and interprets screen content |

### 📸 Screenshots
| Feature | Voice Command | What Happens |
|---|---|---|
| Take Screenshot | *"Take a screenshot"* | Captures screen, saves to Screenshots folder, auto-opens |

### 🎥 Screen Recording
| Feature | Voice Command | What Happens |
|---|---|---|
| Start Recording | *"Start recording"* | Captures screen video at 10 FPS (max 5 minutes) |
| Stop Recording | *"Stop recording"* | Stops capture and saves as .avi video |

### 📋 Clipboard Manager
| Feature | Voice Command | What Happens |
|---|---|---|
| Copy Text | *"Copy this text: hello world"* | Copies to system clipboard |
| Read Clipboard | *"What's in my clipboard?"* | Reads clipboard content aloud |
| Clipboard History | *"Show clipboard history"* | Shows last 10 copied items |
| Clear Clipboard | *"Clear clipboard"* | Empties clipboard |

### 🪟 Window Management
| Feature | Voice Command | What Happens |
|---|---|---|
| List Windows | *"What windows are open?"* | Lists top 10 open windows |
| Switch Window | *"Switch to Chrome"* | Brings window to front |
| Minimize Window | *"Minimize Notepad"* | Minimizes target window |
| Maximize Window | *"Maximize Chrome"* | Maximizes target window |
| Close Window | *"Close Calculator"* | Closes target window |

### ⏰ Timers & Alarms
| Feature | Voice Command | What Happens |
|---|---|---|
| Set Timer | *"Set a timer for 5 minutes"* | Background countdown with audio notification |
| Set Alarm | *"Set an alarm for 2:30 PM"* | Alarm at specific time with beep + TTS alert |
| List Timers | *"What timers are active?"* | Shows all active timers with remaining time |
| Cancel Timer | *"Cancel the pasta timer"* | Cancels a specific timer by label |

### 📧 Email
| Feature | Voice Command | What Happens |
|---|---|---|
| Send Email | *"Send email to user@gmail.com"* | Composes & sends via Gmail SMTP |
| Read Emails | *"Read my emails"* | Fetches latest unread from IMAP |
| Email Count | *"How many emails do I have?"* | Counts unread emails |

### 💬 WhatsApp
| Feature | Voice Command | What Happens |
|---|---|---|
| Send Message | *"Send WhatsApp to Mom saying hello"* | Opens WhatsApp Web and sends message |

### 🎵 Music
| Feature | Voice Command | What Happens |
|---|---|---|
| Play Local Music | *"Play bohemian rhapsody"* | Searches Music/Downloads folders for matching files |
| Play on Spotify | *"Play Faint on Spotify"* | Uses Spotify API (requires Premium for auto-play) |
| Stop Music | *"Stop music"* | Stops local + Spotify playback |
| Next / Previous | *"Next song"* / *"Previous song"* | Spotify skip controls |
| Pause / Resume | *"Pause music"* / *"Resume music"* | Spotify playback controls |

### 📄 Document Reading
| Feature | Voice Command | What Happens |
|---|---|---|
| Read PDF | *"Read report.pdf from Documents"* | Extracts and speaks text from PDF files |
| Read Word Doc | *"Read notes.docx"* | Extracts text from .docx files |
| Read Excel | *"Read spreadsheet.xlsx"* | Reads cell data from Excel files |
| Read Text File | *"Read todo.txt from Desktop"* | Reads any plain text file |
| Summarize Document | *"Summarize report.pdf"* | LLM generates a 2-3 sentence summary |

### ⚡ Custom Automation
| Feature | Description |
|---|---|
| Custom Actions | Define custom voice-triggered commands in `actions.json` |
| Shell Commands | Run any shell command by voice |
| Script Execution | Launch Python scripts by voice |
| IoT Ready | HTTP action type (planned for smart home control) |

### 🔐 Security & Auth
| Feature | Description |
|---|---|
| User Registration | Email + password with OTP verification |
| OTP via Email | 6-digit code sent to Gmail |
| Login System | Bcrypt-hashed password verification |
| Input Sanitization | All user inputs sanitized before processing |
| Path Validation | File operations restricted to allowed directories |
| Safe Mode | Guardian Mode blocks dangerous file deletions |
| Shutdown Confirmation | Asks for confirmation before shutting down PC |

### 🌐 Web Interface
| Feature | Description |
|---|---|
| React Frontend | Modern UI with 3D animated orb (Three.js) |
| WebSocket | Real-time bidirectional communication |
| REST API | `/command`, `/stop`, `/health`, `/api/status` endpoints |
| Text Input | Type commands in the browser |

---

## ❌ WHAT DAVID CANNOT DO (Current Limitations)

### 🚫 Not Supported
| Limitation | Details |
|---|---|
| No Internet-Free LLM | Requires Ollama running locally (needs the model downloaded) |
| No Multi-User Sessions | Single-user system — no session/token management (JWT) |
| No Voice in Browser | Web mode uses text input only — no in-browser mic recording |
| No Smart Home Control | HTTP action type is defined but not implemented yet |
| No Image Generation | Cannot create or edit images |
| No Multi-Monitor Vision | Screen analysis captures primary monitor only |
| No OCR Without Tesseract | Screenshot OCR requires Tesseract to be installed separately |
| No Mac/Linux Support | Windows-only (PowerShell TTS, nircmd volume, .exe paths) |
| No Cloud Deployment | Designed for local execution — not a cloud SaaS product |
| No Code Execution | Cannot write or run code on behalf of the user |
| No Contact Auto-Import | WhatsApp contacts must be manually added to `contacts.json` |
| No Spotify Free Playback | Spotify auto-play requires Premium — Free users get browser fallback |
| No Multilingual TTS | Hindi TTS uses Devanagari voice; Romanized Hindi cannot be spoken naturally |
| No Offline TTS (High Quality) | Cloud TTS (Edge) needs internet; local fallback is lower quality |
| No App Installation | Cannot install or uninstall software |
| No Database Queries | Cannot query or modify external databases |
| No API Integrations | No Slack, Discord, Telegram, or other messaging platform support |

---

## 🔧 Configuration Quick Reference

| Config | File | Key Variables |
|---|---|---|
| LLM Model | `.env` | `OLLAMA_MODEL=llama3.2` |
| TTS Voice | `.env` | `TTS_ENGINE=cloud`, `TTS_VOICE=en-IN-PrabhatNeural` |
| Email SMTP | `.env` | `EMAIL_ADDRESS`, `EMAIL_PASSWORD` |
| Wake Word | `.env` | `WAKE_WORD_ENABLED=false` |
| Spotify | `core/config.py` | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` |
| WhatsApp Contacts | `contacts.json` | `{"mom": "+91XXXXXXXXXX"}` |
| Custom Automations | `actions.json` | Custom voice-triggered commands |
| Allowed File Dirs | `core/config.py` | `FILE_OPS_ALLOWED_DIRS` |
| Safe Mode | `core/config.py` | `SAFE_MODE=True` (blocks dangerous ops) |

---

## 📊 Plugin Architecture

David uses a **modular plugin system**. All 14 plugins load automatically:

```
plugins/
├── automation.py               → Custom voice-triggered shell commands
├── browser_plugin.py           → Open websites, Google/YouTube search
├── calendar_plugin.py          → Events, reminders, schedule, ICS export/import
├── clipboard_plugin.py         → Copy, paste, clipboard history
├── document_reader_plugin.py   → Read & summarize PDF, Word, Excel, text files
├── email_plugin.py             → Send/read emails via Gmail
├── file_ops.py                 → Create, move, copy, delete, search, EDIT files
├── screenshot_plugin.py        → Take screenshots + OCR
├── screen_recorder_plugin.py   → Record screen to video
├── system_monitor.py           → CPU, RAM, disk, battery, processes
├── timer_plugin.py             → Set timers, alarms, countdowns
├── vision_plugin.py            → AI screen analysis via Ollama vision
├── weather.py                  → Current weather + forecast (wttr.in)
├── window_control.py           → List, switch, minimize, maximize, close windows
```

To add a new plugin: create a `your_plugin.py` in the `plugins/` folder that extends `BasePlugin`. It auto-discovers on startup.

---

*Built by Dishank Agrawal — David AI Assistant v2.0*

