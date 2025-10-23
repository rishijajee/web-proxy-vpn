"""
Web Proxy VPN - Bypass Network Restrictions
Access any website through this secure proxy portal
"""

from flask import Flask, render_template, request, redirect, Response
import requests
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

# Disable SSL warnings for proxied requests
requests.packages.urllib3.disable_warnings()


def make_absolute_url(url, base_url):
    """Convert relative URLs to absolute URLs"""
    if url.startswith('//'):
        return 'https:' + url
    elif url.startswith('/'):
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{url}"
    elif not url.startswith(('http://', 'https://')):
        return urljoin(base_url, url)
    return url


def proxy_url(url):
    """Convert external URL to proxied URL through our server"""
    if url.startswith(('http://', 'https://', '//')):
        return f"/proxy?url={url}"
    return url


def rewrite_links(html_content, base_url):
    """Rewrite all links in HTML to go through proxy"""
    # Rewrite href attributes
    html_content = re.sub(
        r'href=["\']([^"\']+)["\']',
        lambda m: f'href="{proxy_url(make_absolute_url(m.group(1), base_url))}"',
        html_content
    )

    # Rewrite src attributes (images, scripts, etc)
    html_content = re.sub(
        r'src=["\']([^"\']+)["\']',
        lambda m: f'src="{proxy_url(make_absolute_url(m.group(1), base_url))}"',
        html_content
    )

    # Rewrite action attributes in forms
    html_content = re.sub(
        r'action=["\']([^"\']+)["\']',
        lambda m: f'action="{proxy_url(make_absolute_url(m.group(1), base_url))}"',
        html_content
    )

    # Rewrite CSS url() references
    html_content = re.sub(
        r'url\(["\']?([^"\')\s]+)["\']?\)',
        lambda m: f'url({proxy_url(make_absolute_url(m.group(1), base_url))})',
        html_content
    )

    # Rewrite JavaScript location redirects
    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    # Rewrite window.location and location.href
    html_content = re.sub(
        r'(window\.location|location\.href)\s*=\s*["\']([^"\']+)["\']',
        lambda m: f'{m.group(1)}="/proxy?url={make_absolute_url(m.group(2), base_url)}"',
        html_content
    )

    return html_content


@app.route('/')
def index():
    """Main page with URL input"""
    return render_template('index.html')


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


@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    """Proxy the requested URL"""
    target_url = request.args.get('url', '')

    if not target_url:
        return redirect('/')

    try:
        # Forward headers from client
        headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'connection', 'content-length', 'content-encoding']:
                headers[key] = value

        # Ensure we have a proper User-Agent
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

        # Make request to target URL (handle both GET and POST)
        if request.method == 'POST':
            response = requests.post(
                target_url,
                data=request.get_data(),
                headers=headers,
                cookies=request.cookies,
                timeout=30,
                allow_redirects=True,
                verify=False
            )
        else:
            response = requests.get(
                target_url,
                headers=headers,
                cookies=request.cookies,
                timeout=30,
                allow_redirects=True,
                verify=False
            )

        content_type = response.headers.get('Content-Type', '')

        # Prepare response headers
        response_headers = {}
        for key, value in response.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                response_headers[key] = value

        # If it's HTML, rewrite links to go through proxy
        if 'text/html' in content_type:
            content = response.text
            content = rewrite_links(content, target_url)

            # Add a banner to show the proxied URL
            banner = f'''
            <div style="position: fixed; top: 0; left: 0; right: 0; background: #1a73e8; color: white; padding: 10px 20px; z-index: 9999; font-family: Arial, sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-weight: bold;">🔓 Proxy Active</span>
                        <span style="opacity: 0.9; font-size: 14px;">Viewing: {target_url}</span>
                    </div>
                    <a href="/" style="background: white; color: #1a73e8; padding: 5px 15px; border-radius: 4px; text-decoration: none; font-size: 14px;">New URL</a>
                </div>
            </div>
            <div style="height: 50px;"></div>
            '''
            content = content.replace('<body', banner + '<body', 1)

            response_headers['Content-Type'] = 'text/html; charset=utf-8'

            # Create response with cookies
            flask_response = Response(content, headers=response_headers)

            # Forward cookies from the proxied site
            for cookie in response.cookies:
                flask_response.set_cookie(
                    cookie.name,
                    cookie.value,
                    max_age=cookie.expires,
                    path=cookie.path or '/',
                    domain=None,  # Don't set domain to allow cookie on our proxy
                    secure=False,
                    httponly=cookie.has_nonstandard_attr('HttpOnly')
                )

            return flask_response
        else:
            # For non-HTML content (images, CSS, JS, etc), pass through as-is
            response_headers['Cache-Control'] = 'public, max-age=3600'
            return Response(
                response.content,
                headers=response_headers
            )

    except requests.exceptions.RequestException as e:
        return render_template('error.html', error=str(e), url=target_url)
    except Exception as e:
        return render_template('error.html', error=str(e), url=target_url)


if __name__ == '__main__':
    print("🔓 Web Proxy VPN Starting...")
    print("Access any blocked website through: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
