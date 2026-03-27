# David AI - Advanced Features Guide

## 🚀 New Capabilities

David AI now includes **8 powerful plugins** that transform it into a comprehensive personal assistant and OS controller.

---

## 📋 Plugin Overview

### 1. **Clipboard Manager**
Manage your clipboard with history tracking.

**Commands**:
- "Copy hello world to clipboard"
- "What's in my clipboard?"
- "Show clipboard history"
- "Clear clipboard"

---

### 2. **Screenshot & OCR**
Capture screenshots and extract text from images.

**Commands**:
- "Take a screenshot"
- "Screenshot and read text" (OCR)

**Note**: Screenshots are saved to `Pictures/David_Screenshots/`

---

### 3. **System Monitoring**
Monitor system resources and processes.

**Commands**:
- "What's my CPU usage?"
- "How much RAM is available?"
- "Show disk usage"
- "What's my battery percentage?"
- "List running processes"
- "Kill Chrome process"
- "Show network status"

---

### 4. **File Operations**
Manage files and folders with voice commands.

**Commands**:
- "Create a folder called Projects on Desktop"
- "Delete old file from Downloads"
- "Move file from Downloads to Documents"
- "Copy report from Documents to Desktop"
- "List files in Downloads"
- "Search for PDF files in Documents"
- "Show info for file on Desktop"

**Security**: Only works in allowed directories (Desktop, Downloads, Documents, Pictures)

---

### 5. **Browser Automation**
Control your web browser with voice.

**Commands**:
- "Open website example.com"
- "Search Google for Python tutorials"
- "Search YouTube for machine learning"
- "Close browser"

---

### 6. **Window Control**
Manage application windows.

**Commands**:
- "List all windows"
- "Switch to Chrome"
- "Minimize Notepad"
- "Maximize Chrome"
- "Close Calculator"

---

### 7. **Email Integration**
Send and read emails (requires configuration).

**Commands**:
- "Send email to john@example.com with subject Meeting"
- "Read my latest emails"
- "How many unread emails do I have?"

**Setup**: Add to `.env` file:
```env
EMAIL_ENABLED=true
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)

---

### 8. **Calendar & Reminders**
Manage your schedule and set reminders.

**Commands**:
- "Create a meeting for tomorrow at 2 PM"
- "Remind me to call mom at 5 PM"
- "What's on my schedule today?"
- "List events for next week"
- "Delete meeting"

---

## ⚙️ Configuration

Create or update `.env` file in the project root:

```env
# File Operations
FILE_OPS_ENABLED=true
FILE_OPS_ALLOWED_DIRS=Desktop,Downloads,Documents,Pictures
FILE_OPS_MAX_SIZE_MB=100

# Email (optional)
EMAIL_ENABLED=false
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Calendar
CALENDAR_ENABLED=true

# Browser
BROWSER_ENABLED=true
BROWSER_DEFAULT=chrome

# System Monitoring
SYSTEM_MONITOR_ENABLED=true

# Screenshots
SCREENSHOT_ENABLED=true
SCREENSHOT_OCR_ENABLED=true

# Clipboard
CLIPBOARD_ENABLED=true

# Window Control
WINDOW_CONTROL_ENABLED=true
```

---

## 🔧 Advanced Usage

### Combining Commands
David can understand complex requests:
- "Take a screenshot and copy the text to clipboard"
- "Search Google for Python and open the first result"
- "List my emails and create a reminder to reply"

### File Organization
- "Move all PDFs from Downloads to Documents"
- "Delete files older than 30 days from Downloads"
- "Find all images in Pictures"

### Productivity
- "What's my CPU usage and battery percentage?"
- "Close all Chrome windows and minimize everything"
- "Create a meeting for tomorrow and send email to team"

---

## 🛡️ Security Features

1. **File Operations**: Restricted to allowed directories only
2. **Delete Protection**: Files moved to Recycle Bin (not permanently deleted)
3. **Email**: Credentials stored in `.env` (never in code)
4. **Process Control**: Confirmation for critical operations

---

## 📊 Plugin Status

Check which plugins are loaded:
```bash
# David logs show loaded plugins on startup
2026-02-10 11:30:00 - plugins.manager - INFO - Loaded 9 plugins
```

---

## 🐛 Troubleshooting

### OCR Not Working
Install Tesseract OCR:
1. Download from [tesseract-ocr](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add to system PATH
3. Restart David

### Email Not Sending
1. Verify EMAIL_ADDRESS and EMAIL_PASSWORD in `.env`
2. For Gmail, enable "Less secure app access" or use App Password
3. Check SMTP settings for your email provider

### Window Control Not Working
```bash
pip install pygetwindow
```

### File Operations Denied
Check `FILE_OPS_ALLOWED_DIRS` in config includes the directory you're trying to access.

---

## 💡 Tips & Tricks

1. **Be Specific**: "Open Chrome" works better than "Open browser"
2. **Use Natural Language**: David understands context
3. **Check Logs**: `logs/david_YYYYMMDD.log` for debugging
4. **Combine Features**: Use multiple plugins in one command

---

## 🎯 Example Workflows

### Morning Routine
1. "What's my battery percentage?"
2. "Read my latest emails"
3. "What's on my schedule today?"
4. "Search Google for today's news"

### File Management
1. "List files in Downloads"
2. "Move all PDFs to Documents"
3. "Delete old files from Downloads"
4. "Take a screenshot of my organized Desktop"

### Productivity Boost
1. "Create a meeting for 2 PM tomorrow"
2. "Remind me to prepare presentation at 1 PM"
3. "Send email to team about meeting"
4. "Close all distracting windows"

---

## 📝 Command Reference

See [README.md](README.md) for complete command list and setup instructions.

---

**Made with ❤️ for productivity and automation**
