"""
Advanced Web Proxy VPN - With Headless Browser Support
Handles complex JavaScript sites like Gmail using Selenium
"""

from flask import Flask, render_template, request, redirect, Response, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import secrets
import base64
import time
import os
from urllib.parse import urlparse, urljoin
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Store browser sessions
browser_sessions = {}

def get_chrome_options():
    """Configure Chrome options for headless browsing"""
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
    return chrome_options


def get_browser_session(session_id):
    """Get or create a browser session for the user"""
    if session_id not in browser_sessions:
        try:
            chrome_options = get_chrome_options()
            driver = webdriver.Chrome(options=chrome_options)
            # Hide the fact that we're using Selenium
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            browser_sessions[session_id] = {
                'driver': driver,
                'last_access': time.time()
            }
        except Exception as e:
            print(f"Error creating browser: {e}")
            return None

    # Update last access time
    browser_sessions[session_id]['last_access'] = time.time()
    return browser_sessions[session_id]['driver']


def cleanup_old_sessions():
    """Remove browser sessions that haven't been used in 10 minutes"""
    current_time = time.time()
    sessions_to_remove = []

    for session_id, session_data in browser_sessions.items():
        if current_time - session_data['last_access'] > 600:  # 10 minutes
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        try:
            browser_sessions[session_id]['driver'].quit()
        except:
            pass
        del browser_sessions[session_id]


@app.route('/')
def index():
    """Main page with URL input"""
    # Initialize session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    return render_template('index_advanced.html')


@app.route('/browse', methods=['POST', 'GET'])
def browse():
    """Handle URL submission and redirect to proxy"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
    else:
        url = request.args.get('url', '').strip()

    # Add https:// if no protocol specified
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

    # Ensure session ID exists
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)

    session_id = session['session_id']

    # Cleanup old sessions periodically
    cleanup_old_sessions()

    try:
        # Get browser for this session
        driver = get_browser_session(session_id)

        if not driver:
            return render_template('error.html',
                                 error='Failed to initialize browser. Chrome/Chromium may not be installed.',
                                 url=target_url)

        # Navigate to the URL
        driver.get(target_url)

        # Wait for page to load (max 10 seconds)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            pass  # Continue anyway if timeout

        # Get the page source after JavaScript execution
        page_source = driver.page_source

        # Get the current URL (might have changed due to redirects)
        current_url = driver.current_url

        # Take a screenshot
        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        # Create an interactive HTML page with screenshot and iframe
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Proxy - {current_url}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }}
                .proxy-banner {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background: #1a73e8;
                    color: white;
                    padding: 10px 20px;
                    z-index: 9999;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }}
                .proxy-banner-content {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .proxy-info {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 14px;
                }}
                .proxy-controls {{
                    display: flex;
                    gap: 10px;
                }}
                .proxy-btn {{
                    background: white;
                    color: #1a73e8;
                    padding: 5px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-size: 14px;
                    border: none;
                    cursor: pointer;
                }}
                .proxy-btn:hover {{
                    background: #f0f0f0;
                }}
                .content-area {{
                    margin-top: 50px;
                    padding: 20px;
                }}
                .screenshot {{
                    max-width: 100%;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .interaction-form {{
                    background: #f9f9f9;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .interaction-form input {{
                    padding: 8px;
                    margin: 5px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }}
                .interaction-form button {{
                    padding: 8px 20px;
                    background: #1a73e8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                .info {{
                    background: #e3f2fd;
                    padding: 10px;
                    margin: 10px 0;
                    border-left: 4px solid #1a73e8;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="proxy-banner">
                <div class="proxy-banner-content">
                    <div class="proxy-info">
                        <span style="font-weight: bold;">🔓 Advanced Proxy Active</span>
                        <span style="opacity: 0.9;">Viewing: {current_url}</span>
                    </div>
                    <div class="proxy-controls">
                        <a href="/interact?url={current_url}" class="proxy-btn">Interact</a>
                        <a href="/" class="proxy-btn">New URL</a>
                    </div>
                </div>
            </div>

            <div class="content-area">
                <div class="info">
                    <strong>📸 Live Screenshot:</strong> The page is being rendered with full JavaScript support.
                    Click "Interact" to type, click, and interact with the page.
                </div>

                <img src="data:image/png;base64,{screenshot_b64}" class="screenshot" alt="Page Screenshot">

                <div class="interaction-form">
                    <h3>Quick Actions</h3>
                    <form action="/interact" method="GET" style="display: inline;">
                        <input type="hidden" name="url" value="{current_url}">
                        <button type="submit">Open Interactive Mode</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        '''

        return Response(html_content, headers={'Content-Type': 'text/html; charset=utf-8'})

    except WebDriverException as e:
        return render_template('error.html',
                             error=f'Browser error: {str(e)}',
                             url=target_url)
    except Exception as e:
        return render_template('error.html',
                             error=str(e),
                             url=target_url)


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

        return {
            'screenshot': screenshot_b64,
            'url': current_url
        }
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

        # Execute JavaScript to click at coordinates
        driver.execute_script(f'''
            var element = document.elementFromPoint({x}, {y});
            if (element) element.click();
        ''')

        time.sleep(1)  # Wait for any page changes

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

        # Find the active element and type into it
        driver.switch_to.active_element.send_keys(text)

        time.sleep(0.5)

        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        return {'screenshot': screenshot_b64, 'url': driver.current_url}
    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    print("🚀 Advanced Web Proxy VPN Starting...")
    print("Using headless browser for full JavaScript support")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
