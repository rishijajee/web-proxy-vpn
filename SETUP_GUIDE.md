# 🚀 Google Docs Proxy VPN - Setup Guide

Complete guide for setting up and using the Google Docs Proxy VPN application in restricted networks.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Google OAuth Configuration](#google-oauth-configuration)
4. [Proxy Configuration](#proxy-configuration)
5. [Running the Application](#running-the-application)
6. [Usage Guide](#usage-guide)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System:** Windows, macOS, or Linux
- **Python:** Version 3.8 or higher
- **Chrome/Chromium:** Latest version installed
- **Internet Connection:** Required for initial setup

### Check Python Version

```bash
python --version
# or
python3 --version
```

Should output Python 3.8.x or higher.

### Check Chrome Installation

```bash
# Linux
google-chrome --version

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Windows (in Command Prompt)
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

---

## Installation

### Step 1: Clone or Download the Repository

```bash
cd /path/to/your/projects
git clone https://github.com/rishijajee/web-proxy-vpn.git
cd web-proxy-vpn
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Selenium (browser automation)
- Google API libraries (Drive and Docs access)
- Cryptography (secure credential storage)
- Requests (HTTP client)
- Additional network tools

### Step 4: Verify Installation

```bash
python -c "import flask, selenium, google.auth; print('All dependencies installed successfully!')"
```

---

## Google OAuth Configuration

To access Google Drive and Docs, you need to set up OAuth credentials.

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **NEW PROJECT**
3. Enter project name: `Google Docs Proxy`
4. Click **CREATE**

### Step 2: Enable Required APIs

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Google Drive API**
   - **Google Docs API**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the **OAuth consent screen**:
   - User Type: **External**
   - App name: `Google Docs Proxy`
   - User support email: Your email
   - Developer contact: Your email
   - Click **SAVE AND CONTINUE**
   - Skip scopes (we'll add them programmatically)
   - Add test users (your Gmail address)
   - Click **SAVE AND CONTINUE**

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: `Google Docs Proxy Client`
   - Authorized redirect URIs: Add these URLs:
     ```
     http://localhost:5000/oauth2callback
     http://127.0.0.1:5000/oauth2callback
     ```
   - Click **CREATE**

### Step 4: Download Client Secrets

1. Click the download button (⬇) next to your OAuth client
2. Download the JSON file
3. Rename it to `client_secrets.json`
4. Place it in the project root directory:
   ```
   web-proxy-vpn/
   ├── client_secrets.json  ← Here
   ├── app_google.py
   ├── requirements.txt
   └── ...
   ```

### Step 5: Verify Configuration

The `client_secrets.json` file should look like this:

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:5000/oauth2callback"]
  }
}
```

---

## Proxy Configuration

If you're in a restricted network, configure a proxy to route traffic.

### Proxy Types Supported

1. **SOCKS5** - Most versatile, supports any protocol (Recommended)
2. **HTTP** - Web traffic only
3. **HTTPS** - Secure web traffic only

### Finding a Proxy

**Option 1: Free Public Proxies**
- [Free Proxy List](https://free-proxy-list.net/)
- [SOCKS Proxy List](https://www.socks-proxy.net/)

**Option 2: Commercial Proxy Services**
- Bright Data
- Smartproxy
- Oxylabs
- NordVPN (with SOCKS5 support)

**Option 3: Self-Hosted**
- Set up your own proxy server using Squid or Shadowsocks

### Configuration via Web UI

1. Start the application (see [Running the Application](#running-the-application))
2. Navigate to **Settings** page
3. Fill in the proxy details:
   - **Type:** socks5, http, or https
   - **Host:** proxy.example.com
   - **Port:** 1080 (SOCKS5), 8080 (HTTP), 8443 (HTTPS)
   - **Username:** (optional) your proxy username
   - **Password:** (optional) your proxy password
4. Click **Save Configuration**

### Configuration via Command Line

Alternatively, you can configure the proxy programmatically:

```python
from crypto_manager import CryptoManager, ProxyConfig

crypto = CryptoManager()
proxy_mgr = ProxyConfig(crypto)

# Configure SOCKS5 proxy
proxy_mgr.save_proxy(
    proxy_type='socks5',
    host='proxy.example.com',
    port=1080,
    username='your_username',  # Optional
    password='your_password'   # Optional
)

print("Proxy configured successfully!")
```

---

## Running the Application

### Start the Application

```bash
# Make sure virtual environment is activated
# Then run:
python app_google.py
```

You should see:

```
🚀 Google Docs Proxy VPN Starting...
Features:
  - Network detection
  - SOCKS5/HTTPS proxy support
  - Google OAuth authentication
  - Google Drive file operations
  - Headless browser with interaction

Access at: http://localhost:5000
```

### Access the Dashboard

Open your web browser and navigate to:

```
http://localhost:5000
```

---

## Usage Guide

### 1. First-Time Setup

#### Check Network Status

The dashboard will automatically check if Google services are accessible:
- 🟢 **OPEN** - Direct access available
- 🟡 **RESTRICTED** - Some services blocked
- 🔴 **BLOCKED** - All services blocked (proxy required)

#### Configure Proxy (if needed)

If network status is **RESTRICTED** or **BLOCKED**:
1. Go to **Settings**
2. Configure your proxy details
3. Save configuration
4. Return to dashboard to verify connectivity

#### Login to Google

1. Click **Login with Google** on the dashboard
2. You'll be redirected to Google's consent page
3. Select your Google account
4. Grant permissions:
   - View and manage Google Drive files
   - View and manage Google Docs
5. You'll be redirected back to the dashboard

### 2. Browsing Google Docs

#### Quick Access Links

Use the quick links on the dashboard:
- **Google Docs** - Direct access to docs.google.com
- **Google Drive** - Access your Drive files
- **Gmail** - Check your email

#### Custom URL Access

1. Enter any URL in the **Quick Access** box
2. Click **Go**
3. The page will load through the proxy (if configured)
4. Click **Interact** to type and click on the page

### 3. Managing Google Drive Files

#### Browse Files

1. Click **Browse Drive** on the dashboard
2. View all your Google Drive files
3. Use the search bar to find specific files
4. Click **Open** to view files in browser
5. Click **Download** to save files locally

#### Upload Files

1. Click **Upload Files** on the dashboard
2. Drag and drop a file or click to browse
3. Options:
   - ☑️ **Convert to Google Docs format** (for .docx, .xlsx, .pptx)
   - This allows online editing in Google Docs
4. Click **Upload to Drive**
5. Wait for upload to complete

#### Download Files

**For Google Docs files:**
1. Browse to the file in **Browse Drive**
2. Click **Download ▼** dropdown
3. Select format:
   - **Word (.docx)** - Microsoft Word format
   - **PDF** - Portable Document Format
   - **Text** - Plain text
   - **Excel (.xlsx)** - For spreadsheets
   - **PowerPoint (.pptx)** - For presentations

**For regular files:**
1. Click **Download** button
2. File will be saved to your downloads folder

### 4. Interactive Browser Mode

For complex interactions (login forms, buttons, etc.):

1. Browse to any page
2. Click **Interact** button
3. In interactive mode:
   - **Click** anywhere on the screenshot to simulate clicks
   - **Type** text into focused elements
   - Screenshot updates automatically every 30 seconds
   - Manual refresh available

---

## Troubleshooting

### Common Issues

#### 1. "Chrome/Chromium not found" Error

**Solution:**
- Install Chrome or Chromium browser
- On Linux: `sudo apt install chromium-browser`
- On macOS: Download from [Google Chrome](https://www.google.com/chrome/)
- On Windows: Download from [Google Chrome](https://www.google.com/chrome/)

#### 2. "client_secrets.json not found" Error

**Solution:**
- Ensure `client_secrets.json` is in the project root
- Verify the file is named exactly `client_secrets.json` (not `client_secrets (1).json`)
- Check file permissions (should be readable)

#### 3. OAuth "Access Blocked" Error

**Solution:**
- Go to Google Cloud Console → OAuth consent screen
- Add your email to **Test users**
- Ensure app is in **Testing** mode (not Production)

#### 4. Proxy Connection Failed

**Solution:**
- Verify proxy host and port are correct
- Check if proxy requires authentication
- Test proxy with curl:
  ```bash
  curl -x socks5://username:password@proxy.example.com:1080 https://google.com
  ```
- Try a different proxy server

#### 5. "Network Status: BLOCKED" Even with Proxy

**Solution:**
- Verify proxy credentials are correct
- Check if proxy supports HTTPS connections
- Try using SOCKS5 instead of HTTP proxy
- Test network connectivity:
  ```bash
  python network_checker.py
  ```

#### 6. Google Drive Files Not Loading

**Solution:**
- Re-authenticate with Google (logout and login again)
- Check if tokens are expired (auto-refreshes on next request)
- Verify Google Drive API is enabled in Cloud Console
- Check browser console for API errors

#### 7. Upload Fails with "Upload failed" Error

**Solution:**
- Check file size (Google Drive has limits)
- Verify internet connection is stable
- Check Google Drive storage quota
- Try uploading a smaller file first

### Debug Mode

Run the app in debug mode for detailed error messages:

```bash
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows

python app_google.py
```

### Test Individual Components

#### Test Network Detection

```bash
python network_checker.py
```

#### Test Credential Storage

```bash
python crypto_manager.py
```

#### Test Google Integration

```python
from google_integration import GoogleDriveManager

manager = GoogleDriveManager()
print("Authenticated:", manager.is_authenticated())
```

### Logs Location

Application logs are printed to console. To save logs:

```bash
python app_google.py > app.log 2>&1
```

---

## Security Best Practices

### 1. Protect Credentials

- Never commit `client_secrets.json` to version control
- Keep `.config/` directory private (contains encrypted credentials)
- Use strong proxy passwords

### 2. Encrypted Storage

All credentials are encrypted using Fernet encryption:
- Proxy credentials: `.config/credentials.enc`
- Google tokens: `.config/credentials.enc`
- Encryption key: `.config/secret.key`

**Important:** Backup the `.config/` directory to preserve credentials.

### 3. OAuth Security

- Only grant permissions to your own Google account
- Revoke access anytime at [Google Account Permissions](https://myaccount.google.com/permissions)
- Use test users in OAuth consent screen during development

### 4. Network Security

- Use HTTPS proxies when possible
- Verify proxy provider is trustworthy
- Don't use free proxies for sensitive data

---

## Advanced Configuration

### Custom Port

Run on a different port:

```python
# Edit app_google.py, line ~430
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### Disable Headless Mode

To see browser window (for debugging):

```python
# Edit app_google.py, get_chrome_options() function
# Comment out this line:
# chrome_options.add_argument('--headless')
```

### Increase Session Timeout

Default session timeout is 10 minutes. To change:

```python
# Edit app_google.py, cleanup_old_sessions() function
if current_time - session_data['last_access'] > 1800:  # 30 minutes
```

---

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/rishijajee/web-proxy-vpn/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rishijajee/web-proxy-vpn/discussions)
- **Email:** Contact the maintainer

---

## License

This project is licensed under the MIT License. See LICENSE file for details.
