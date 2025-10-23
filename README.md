# Web Proxy VPN

A simple web-based proxy that allows you to bypass network restrictions and access websites.

## Features

- 🔓 **Bypass Network Restrictions** - Access blocked websites
- 🌐 **Universal Access** - Works with most websites
- ⚡ **Fast & Secure** - Direct proxy connection
- 🎨 **Clean Interface** - Beautiful, easy-to-use design
- 🚫 **No Logging** - Your privacy is protected
- 📝 **POST Support** - Forms and login pages work
- 🍪 **Cookie Forwarding** - Maintains sessions properly

## How to Use

1. Visit the proxy homepage
2. Enter any URL you want to access (e.g., `youtube.com`, `reddit.com`)
3. Click "Browse Securely"
4. The website will load through the proxy

## ⚠️ Important Notes

**Works Best With:**
- News sites (BBC, CNN, etc.)
- Social media (Twitter, Reddit, etc.)
- Video sites (YouTube, Vimeo, etc.)
- Wiki sites (Wikipedia, etc.)
- Most regular websites

**Limited Support For:**
- Gmail/Google services (heavy JavaScript & security)
- Banking sites (security restrictions)
- Sites with complex authentication
- Some single-page applications

**Why Gmail May Not Work:**
Gmail uses advanced JavaScript, AJAX requests, and security measures that are difficult to proxy. For email access, consider using simpler webmail services or the Gmail basic HTML view.

## Deploy to Vercel

1. Push this code to GitHub
2. Import the project in Vercel
3. Deploy!

No environment variables needed - it just works!

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

## How It Works

- All requests go through your server
- Links are rewritten to route through the proxy
- Network restrictions are bypassed
- Works like a VPN but through your browser
