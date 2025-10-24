# 🌐 Google Docs Proxy VPN

**Access Google Docs, Drive, and Gmail from Restricted Networks**

A powerful web application that enables full access to Google services in restricted networks through proxy tunneling, headless browser automation, and Google Drive API integration.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ✨ Features

### 🔍 Network Detection
- **Automatic Detection** - Identifies if Google services are blocked
- **Real-time Status** - Shows which services are accessible
- **Smart Routing** - Automatically uses proxy when needed

### 🔧 Proxy & VPN Support
- **SOCKS5 Support** - Most versatile proxy protocol
- **HTTP/HTTPS Proxies** - Standard web proxies
- **Automatic Switching** - Seamless proxy activation
- **Secure Credentials** - Encrypted storage with Fernet encryption

### 🔐 Google OAuth Integration
- **Full Google Drive Access** - Browse, upload, download files
- **Google Docs Support** - View and edit documents online
- **Secure Authentication** - OAuth 2.0 with token refresh
- **Session Management** - Persistent login across sessions

### 📁 File Operations
- **Upload to Drive** - Drag-and-drop file upload
- **Download Files** - Multiple format support (PDF, DOCX, XLSX)
- **Format Conversion** - Convert Google Docs to Office formats
- **Batch Operations** - Upload/download multiple files

### 🌐 Browser Automation
- **Headless Chrome** - Full JavaScript execution
- **Interactive Mode** - Click and type on web pages
- **Screenshot Capture** - Visual preview of pages
- **Session Persistence** - Maintains login state

### 🛡️ Security & Privacy
- **Encrypted Storage** - All credentials encrypted at rest
- **No Logging** - Your browsing data is not stored
- **Secure OAuth** - Industry-standard authentication
- **Session Isolation** - Each user gets isolated browser session

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/rishijajee/web-proxy-vpn.git
cd web-proxy-vpn

# Install dependencies
pip install -r requirements.txt
```

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Drive API** and **Google Docs API**
4. Create OAuth credentials (Web application)
5. Add redirect URI: `http://localhost:5000/oauth2callback`
6. Download `client_secrets.json` and place in project root

### 3. Run Application

```bash
python app_google.py
```

Visit: **http://localhost:5000**

### 4. Configure Proxy (Optional)

If you're in a restricted network:
1. Go to **Settings** page
2. Enter proxy details (SOCKS5/HTTP/HTTPS)
3. Save configuration
4. Proxy will be used automatically

---

## 📖 Full Documentation

**For detailed setup and usage instructions, see:**
- [**SETUP_GUIDE.md**](SETUP_GUIDE.md) - Complete installation and configuration guide

---

## 🎯 Use Cases

### 1. School/University Networks
- Access Google Docs for assignments
- Submit homework through Drive
- Collaborate on group projects

### 2. Corporate Networks
- Access personal Google Drive
- Edit documents remotely
- Download files for offline work

### 3. Country-Level Restrictions
- Route through proxy to access Google
- Maintain productivity with Docs
- Sync files with Drive

### 4. Public Wi-Fi
- Secure access through proxy
- Browse Google services safely
- Upload/download files securely

---

## 📊 Comparison with Original Version

| Feature | Original App | Google Docs Edition |
|---------|--------------|---------------------|
| Basic Proxy | ✅ | ✅ |
| Headless Browser | ✅ | ✅ |
| Network Detection | ❌ | ✅ |
| Proxy Tunneling | ❌ | ✅ SOCKS5/HTTP/HTTPS |
| Google OAuth | ❌ | ✅ Full OAuth 2.0 |
| Drive Integration | ❌ | ✅ Complete API |
| File Upload | ❌ | ✅ Drag & Drop |
| File Download | ❌ | ✅ Multiple Formats |
| Credential Encryption | ❌ | ✅ Fernet Encryption |
| Dashboard UI | ❌ | ✅ Status Dashboard |
| Settings Page | ❌ | ✅ Full Configuration |

---

## 🏗️ Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Flask Application               │
│  ┌──────────────────────────────────┐  │
│  │      Dashboard (app_google.py)    │  │
│  └──────────────────────────────────┘  │
│           │         │         │          │
│           ▼         ▼         ▼          │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│    │ Network │ │  Proxy  │ │ Google  │ │
│    │ Checker │ │ Manager │ │   API   │ │
│    └─────────┘ └─────────┘ └─────────┘ │
│           │         │         │          │
└───────────┼─────────┼─────────┼──────────┘
            ▼         ▼         ▼
     ┌──────────┐ ┌──────┐ ┌──────────┐
     │  Google  │ │ SOCKS│ │  Google  │
     │ Services │ │Proxy │ │   Drive  │
     └──────────┘ └──────┘ └──────────┘
```

---

## 📁 Project Structure

```
web-proxy-vpn/
├── app_google.py              # Enhanced Flask app with Google features
├── app.py                     # Original basic proxy
├── app_advanced.py            # Original advanced proxy with Selenium
│
├── network_checker.py         # Network detection module
├── crypto_manager.py          # Credential encryption module
├── google_integration.py      # Google Drive/Docs API module
│
├── templates/
│   ├── dashboard.html         # Main dashboard with status
│   ├── settings.html          # Proxy configuration page
│   ├── drive.html             # Google Drive file browser
│   ├── upload.html            # File upload interface
│   ├── interact.html          # Interactive browser mode
│   ├── index.html             # Original proxy homepage
│   ├── index_advanced.html    # Advanced proxy homepage
│   └── error.html             # Error page
│
├── .config/                   # Encrypted credentials (auto-created)
│   ├── secret.key             # Encryption key
│   └── credentials.enc        # Encrypted credentials
│
├── uploads/                   # Temporary upload directory
├── downloads/                 # Downloaded files
│
├── requirements.txt           # Python dependencies
├── SETUP_GUIDE.md            # Detailed setup instructions
├── README_GOOGLE_DOCS.md     # This file
├── README.md                  # Original README
├── client_secrets.json        # Google OAuth credentials (user-provided)
└── vercel.json                # Vercel deployment config
```

---

## 🔧 Configuration

### Proxy Configuration

Supports multiple proxy types:

**SOCKS5 (Recommended):**
```
Type: socks5
Host: proxy.example.com
Port: 1080
Username: (optional)
Password: (optional)
```

**HTTP/HTTPS:**
```
Type: http or https
Host: proxy.example.com
Port: 8080
Username: (optional)
Password: (optional)
```

### Environment Variables

Optional environment variables:

```bash
# Flask secret key (auto-generated if not set)
export SECRET_KEY="your-secret-key"

# Flask environment
export FLASK_ENV="development"  # or "production"
```

---

## 📸 Screenshots

### Dashboard
Main dashboard showing network status, authentication status, and quick actions.

### Google Drive Browser
Browse all your Google Drive files with search functionality.

### File Upload
Drag-and-drop interface for uploading files to Google Drive.

### Settings Page
Configure proxy settings and view Google OAuth status.

---

## 🧪 Testing

### Test Network Detection

```bash
python network_checker.py
```

Output:
```
Testing Network Connectivity to Google Services...
============================================================

Overall Status: BLOCKED
Message: All Google services are blocked
Timestamp: 2024-01-15T10:30:00

Detailed Results:
------------------------------------------------------------
✗ docs         - https://docs.google.com
  Error: Connection refused or blocked
✗ drive        - https://drive.google.com
  Error: Connection refused or blocked
...
```

### Test Credential Encryption

```bash
python crypto_manager.py
```

### Test Google Integration

```python
from google_integration import GoogleDriveManager

manager = GoogleDriveManager()
if manager.is_authenticated():
    files = manager.list_files(page_size=10)
    for file in files:
        print(f"📄 {file['name']}")
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. Chrome not found**
```bash
# Install Chrome or Chromium
sudo apt install chromium-browser  # Linux
```

**2. OAuth errors**
- Check `client_secrets.json` is in project root
- Verify redirect URI in Google Cloud Console
- Add your email to test users

**3. Proxy connection failed**
- Verify proxy credentials
- Test proxy with curl
- Try SOCKS5 instead of HTTP

**4. Network still blocked**
- Verify proxy is working
- Check proxy supports HTTPS
- Try different proxy server

For detailed troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting).

---

## 🚀 Deployment

### Local Development

```bash
python app_google.py
```

### Production (Linux Server)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_google:app
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y chromium chromium-driver

# Copy application
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run application
CMD ["python", "app_google.py"]
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is intended for:
- Educational purposes
- Accessing your own Google account in restricted networks
- Legitimate use cases where network access is limited

**Please use responsibly and comply with:**
- Your organization's acceptable use policy
- Local laws and regulations
- Google's Terms of Service

The authors are not responsible for misuse of this software.

---

## 🙏 Acknowledgments

- **Flask** - Web framework
- **Selenium** - Browser automation
- **Google APIs** - Drive and Docs integration
- **Cryptography** - Secure credential storage

---

## 📧 Contact

- **GitHub Issues:** [Report bugs or request features](https://github.com/rishijajee/web-proxy-vpn/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/rishijajee/web-proxy-vpn/discussions)

---

## 🔗 Links

- [Setup Guide](SETUP_GUIDE.md)
- [Google Cloud Console](https://console.cloud.google.com)
- [Google Drive API Docs](https://developers.google.com/drive)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Made with ❤️ for unrestricted access to Google services**
