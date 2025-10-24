"""
Enhanced Web Proxy VPN - Google Docs Edition
Provides access to Google Docs in restricted networks with proxy support
"""

from flask import Flask, render_template, request, redirect, Response, session, jsonify, url_for, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import secrets
import base64
import time
import os
from urllib.parse import urlparse, urljoin, quote_plus
from pathlib import Path
import json

# Import custom modules
from network_checker import NetworkChecker
from crypto_manager import CryptoManager, ProxyConfig, GoogleTokenManager
from google_integration import GoogleDriveManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Initialize managers
crypto_manager = CryptoManager()
proxy_manager = ProxyConfig(crypto_manager)
token_manager = GoogleTokenManager(crypto_manager)
google_manager = GoogleDriveManager(crypto_manager=crypto_manager)

# Store browser sessions
browser_sessions = {}

# Upload directory
UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

# Download directory
DOWNLOAD_DIR = Path('downloads')
DOWNLOAD_DIR.mkdir(exist_ok=True)


def get_chrome_options(use_proxy=False):
    """Configure Chrome options for headless browsing with optional proxy"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Add proxy if configured and enabled
    if use_proxy:
        proxy_config = proxy_manager.get_proxy()
        if proxy_config:
            proxy_type = proxy_config['type']
            host = proxy_config['host']
            port = proxy_config['port']
            username = proxy_config.get('username')
            password = proxy_config.get('password')

            if username and password:
                proxy_str = f"{proxy_type}://{username}:{password}@{host}:{port}"
            else:
                proxy_str = f"{proxy_type}://{host}:{port}"

            chrome_options.add_argument(f'--proxy-server={proxy_str}')

    return chrome_options


def get_browser_session(session_id, use_proxy=False):
    """Get or create a browser session for the user"""
    if session_id not in browser_sessions:
        try:
            chrome_options = get_chrome_options(use_proxy=use_proxy)
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            browser_sessions[session_id] = {
                'driver': driver,
                'last_access': time.time()
            }
        except Exception as e:
            print(f"Error creating browser: {e}")
            return None

    browser_sessions[session_id]['last_access'] = time.time()
    return browser_sessions[session_id]['driver']


def cleanup_old_sessions():
    """Remove browser sessions that haven't been used in 10 minutes"""
    current_time = time.time()
    sessions_to_remove = []

    for session_id, session_data in browser_sessions.items():
        if current_time - session_data['last_access'] > 600:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        try:
            browser_sessions[session_id]['driver'].quit()
        except:
            pass
        del browser_sessions[session_id]


@app.route('/')
def index():
    """Main dashboard"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)

    # Check network status
    proxy_config = proxy_manager.get_proxy_dict()
    checker = NetworkChecker(proxy_config=proxy_config)
    network_status = checker.get_network_status()

    # Check Google authentication
    is_google_auth = google_manager.is_authenticated()

    return render_template('dashboard.html',
                          network_status=network_status,
                          is_google_auth=is_google_auth,
                          proxy_configured=proxy_manager.get_proxy() is not None)


@app.route('/settings')
def settings():
    """Settings page for proxy and configuration"""
    proxy_config = proxy_manager.get_proxy()
    return render_template('settings.html', proxy_config=proxy_config)


@app.route('/api/proxy/save', methods=['POST'])
def save_proxy():
    """Save proxy configuration"""
    data = request.get_json()

    proxy_type = data.get('type', 'socks5')
    host = data.get('host', '')
    port = int(data.get('port', 1080))
    username = data.get('username')
    password = data.get('password')

    if not host:
        return jsonify({'error': 'Host is required'}), 400

    proxy_manager.save_proxy(proxy_type, host, port, username, password)
    return jsonify({'success': True, 'message': 'Proxy configuration saved'})


@app.route('/api/proxy/delete', methods=['POST'])
def delete_proxy():
    """Delete proxy configuration"""
    proxy_manager.delete_proxy()
    return jsonify({'success': True, 'message': 'Proxy configuration deleted'})


@app.route('/api/network/check')
def check_network():
    """Check network connectivity status"""
    proxy_config = proxy_manager.get_proxy_dict()
    checker = NetworkChecker(proxy_config=proxy_config)
    status = checker.get_network_status()
    return jsonify(status)


@app.route('/google-login')
def google_login():
    """Initiate Google OAuth flow"""
    if not os.path.exists('client_secrets.json'):
        return render_template('error.html',
                             error='client_secrets.json not found. Please add your Google OAuth credentials.',
                             url='/')

    try:
        redirect_uri = url_for('oauth2callback', _external=True)
        auth_url = google_manager.get_authorization_url(redirect_uri=redirect_uri)
        return redirect(auth_url)
    except Exception as e:
        return render_template('error.html',
                             error=f'OAuth initialization error: {str(e)}',
                             url='/')


@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback"""
    authorization_response = request.url
    redirect_uri = url_for('oauth2callback', _external=True)

    if google_manager.handle_oauth_callback(authorization_response, redirect_uri=redirect_uri):
        return redirect('/')
    else:
        return render_template('error.html',
                             error='OAuth authentication failed',
                             url='/')


@app.route('/google-logout')
def google_logout():
    """Logout from Google"""
    token_manager.delete_tokens()
    return redirect('/')


@app.route('/drive')
def drive_browser():
    """Browse Google Drive files"""
    if not google_manager.is_authenticated():
        return redirect('/google-login')

    if not google_manager.initialize_services():
        return render_template('error.html',
                             error='Failed to initialize Google services',
                             url='/')

    query = request.args.get('q')
    files = google_manager.list_files(page_size=50, query=query)

    return render_template('drive.html', files=files, query=query)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Upload file to Google Drive"""
    if not google_manager.is_authenticated():
        return redirect('/google-login')

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save file temporarily
        file_path = UPLOAD_DIR / file.filename
        file.save(file_path)

        # Upload to Google Drive
        convert_to_docs = request.form.get('convert_to_docs') == 'true'
        result = google_manager.upload_file(str(file_path), convert_to_docs=convert_to_docs)

        # Clean up temporary file
        file_path.unlink()

        if result:
            return jsonify({
                'success': True,
                'file_id': result['id'],
                'file_name': result['name'],
                'web_view_link': result.get('webViewLink')
            })
        else:
            return jsonify({'error': 'Upload failed'}), 500

    return render_template('upload.html')


@app.route('/download/<file_id>')
def download_file(file_id):
    """Download file from Google Drive"""
    if not google_manager.is_authenticated():
        return redirect('/google-login')

    export_format = request.args.get('format', 'pdf')

    # Generate unique filename
    output_path = DOWNLOAD_DIR / f"{file_id}.{export_format}"

    if google_manager.download_file(file_id, str(output_path), export_format=export_format):
        return send_file(output_path, as_attachment=True)
    else:
        return render_template('error.html',
                             error='Download failed',
                             url='/drive')


@app.route('/browse', methods=['POST', 'GET'])
def browse():
    """Handle URL submission and redirect to proxy"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
    else:
        url = request.args.get('url', '').strip()

    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if url:
        return redirect(f'/proxy?url={url}')

    return redirect('/')


@app.route('/proxy')
def proxy():
    """Proxy the requested URL using headless browser"""
    target_url = request.args.get('url', '')

    if not target_url:
        return redirect('/')

    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)

    session_id = session['session_id']
    cleanup_old_sessions()

    # Determine if proxy should be used
    use_proxy = proxy_manager.get_proxy() is not None

    try:
        driver = get_browser_session(session_id, use_proxy=use_proxy)

        if not driver:
            return render_template('error.html',
                                 error='Failed to initialize browser. Chrome/Chromium may not be installed.',
                                 url=target_url)

        driver.get(target_url)

        try:
            from selenium.webdriver.support.ui import WebDriverWait
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except:
            pass

        current_url = driver.current_url
        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Proxy - {current_url}</title>
            <style>
                body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
                .proxy-banner {{
                    position: fixed; top: 0; left: 0; right: 0;
                    background: #1a73e8; color: white; padding: 10px 20px;
                    z-index: 9999; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }}
                .proxy-banner-content {{
                    display: flex; align-items: center; justify-content: space-between;
                    max-width: 1200px; margin: 0 auto;
                }}
                .proxy-info {{ display: flex; align-items: center; gap: 10px; font-size: 14px; }}
                .proxy-controls {{ display: flex; gap: 10px; }}
                .proxy-btn {{
                    background: white; color: #1a73e8; padding: 5px 15px;
                    border-radius: 4px; text-decoration: none; font-size: 14px;
                    border: none; cursor: pointer;
                }}
                .proxy-btn:hover {{ background: #f0f0f0; }}
                .content-area {{ margin-top: 50px; padding: 20px; }}
                .screenshot {{
                    max-width: 100%; border: 1px solid #ddd;
                    border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .info {{
                    background: #e3f2fd; padding: 10px; margin: 10px 0;
                    border-left: 4px solid #1a73e8; border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="proxy-banner">
                <div class="proxy-banner-content">
                    <div class="proxy-info">
                        <span style="font-weight: bold;">🔓 Proxy Active{' (via Proxy)' if use_proxy else ''}</span>
                        <span style="opacity: 0.9;">Viewing: {current_url}</span>
                    </div>
                    <div class="proxy-controls">
                        <a href="/interact?url={current_url}" class="proxy-btn">Interact</a>
                        <a href="/" class="proxy-btn">Dashboard</a>
                    </div>
                </div>
            </div>
            <div class="content-area">
                <div class="info">
                    <strong>📸 Live Screenshot:</strong> Page rendered with full JavaScript support.
                    Click "Interact" to type, click, and interact with the page.
                </div>
                <img src="data:image/png;base64,{screenshot_b64}" class="screenshot" alt="Page Screenshot">
            </div>
        </body>
        </html>
        '''

        return Response(html_content, headers={'Content-Type': 'text/html; charset=utf-8'})

    except Exception as e:
        return render_template('error.html', error=str(e), url=target_url)


@app.route('/interact')
def interact():
    """Interactive mode for complex sites"""
    target_url = request.args.get('url', '')
    if not target_url:
        return redirect('/')
    return render_template('interact.html', url=target_url)


@app.route('/api/screenshot')
def api_screenshot():
    """Get current screenshot"""
    if 'session_id' not in session:
        return {'error': 'No session'}, 400

    session_id = session['session_id']
    driver = browser_sessions.get(session_id, {}).get('driver')

    if not driver:
        return {'error': 'No browser session'}, 400

    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        current_url = driver.current_url

        return {'screenshot': screenshot_b64, 'url': current_url}
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/click', methods=['POST'])
def api_click():
    """Click at coordinates"""
    if 'session_id' not in session:
        return {'error': 'No session'}, 400

    session_id = session['session_id']
    driver = browser_sessions.get(session_id, {}).get('driver')

    if not driver:
        return {'error': 'No browser session'}, 400

    try:
        data = request.get_json()
        x = data.get('x', 0)
        y = data.get('y', 0)

        driver.execute_script(f'''
            var element = document.elementFromPoint({x}, {y});
            if (element) element.click();
        ''')

        time.sleep(1)

        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        return {'screenshot': screenshot_b64, 'url': driver.current_url}
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/type', methods=['POST'])
def api_type():
    """Type text into focused element"""
    if 'session_id' not in session:
        return {'error': 'No session'}, 400

    session_id = session['session_id']
    driver = browser_sessions.get(session_id, {}).get('driver')

    if not driver:
        return {'error': 'No browser session'}, 400

    try:
        data = request.get_json()
        text = data.get('text', '')

        driver.switch_to.active_element.send_keys(text)
        time.sleep(0.5)

        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        return {'screenshot': screenshot_b64, 'url': driver.current_url}
    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    print("🚀 Google Docs Proxy VPN Starting...")
    print("Features:")
    print("  - Network detection")
    print("  - SOCKS5/HTTPS proxy support")
    print("  - Google OAuth authentication")
    print("  - Google Drive file operations")
    print("  - Headless browser with interaction")
    print("\nAccess at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
