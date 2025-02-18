from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import subprocess
import logging
import json
import os
import requests
import webbrowser

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def load_credentials():
    with open(os.path.expanduser('~/nordvpn_credentials.json')) as f:
        return json.load(f)

def connect_vpn():
    logging.debug('Starting OpenVPN connection')
    try:
        result = subprocess.run(
            ['sudo', 'openvpn', '--config', os.path.expanduser('~/nordvpn/ovpn_tcp/jp594.nordvpn.com.tcp.ovpn')],
            check=True,
            capture_output=True,
            text=True
        )
        logging.debug(f'OpenVPN connection started: {result.stdout}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Failed to start OpenVPN: {e.stderr}')
        raise

def start_socks5_proxy():
    logging.debug('Starting SOCKS5 proxy via SSH')
    try:
        # Replace 'user' and 'remote_host' with your SSH username and remote host
        subprocess.Popen(['ssh', '-D', '1080', '-f', '-C', '-q', '-N', 'user@remote_host'])
        logging.debug('SOCKS5 proxy started on port 1080')
    except subprocess.CalledProcessError as e:
        logging.error(f'Failed to start SOCKS5 proxy: {e}')
        raise

def get_driver(browser, accept_language):
    logging.debug(f'Initializing WebDriver for browser: {browser}')
    if browser == 'chrome':
        options = ChromeOptions()
        options.add_argument(f'--lang={accept_language}')
        options.add_argument('--proxy-server=socks5://localhost:1080')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "acceptLanguage": accept_language
        })
        return driver
    elif browser == 'firefox':
        options = FirefoxOptions()
        options.set_preference('intl.accept_languages', accept_language)
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.socks', 'localhost')
        options.set_preference('network.proxy.socks_port', 1080)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.execute_script(f"Object.defineProperty(navigator, 'language', {{get: function() {{return '{accept_language}';}}}});")
        return driver
    elif browser == 'safari':
        # Safari does not support setting Accept-Language header via WebDriver
        return webdriver.Safari(service=SafariService())
    elif browser == 'edge':
        options = EdgeOptions()
        options.add_argument(f'--lang={accept_language}')
        options.add_argument('--proxy-server=socks5://localhost:1080')
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "acceptLanguage": accept_language
        })
        return driver
    else:
        return None

@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    logging.debug(f'Received data: {data}')
    browser = data.get('browser')
    url = data.get('url')
    region = data.get('region')
    
    # Define Accept-Language headers for each region
    region_languages = {
        'North America': 'en-US',
        'Europe': 'fr-FR',
        'Asia': 'ja-JP',
        'South America': 'pt-BR',
        'Africa': 'sw-KE',
        'Australia': 'en-AU'
    }
    
    # Get the Accept-Language header for the selected region
    accept_language = region_languages.get(region, 'en-US')
    
    # Connect to VPN
    connect_vpn()
    
    # Start SOCKS5 proxy
    start_socks5_proxy()
    
    driver = get_driver(browser, accept_language)
    if driver:
        driver.get(url)
        # Add logic to capture screenshot or perform actions
        driver.quit()
        disconnect_vpn()
        return jsonify({'status': 'success'}), 200
    else:
        disconnect_vpn()
        return jsonify({'status': 'error', 'message': 'Invalid browser'}), 400

@app.route('/proxy_request', methods=['POST'])
def proxy_request():
    data = request.json
    url = data.get('url')
    method = data.get('method', 'GET')
    headers = data.get('headers', {})
    payload = data.get('payload', {})
    
    proxies = {
        'http': 'socks5://localhost:1080',
        'https': 'socks5://localhost:1080'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, proxies=proxies)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported method'}), 400
        
        return jsonify({'status': 'success', 'data': response.json()}), 200
    except requests.RequestException as e:
        logging.error(f'Failed to make proxy request: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

def disconnect_vpn():
    logging.debug('Disconnecting VPN')
    try:
        subprocess.run(['nordvpn', 'disconnect'], check=True)
        logging.debug('VPN disconnected')
    except subprocess.CalledProcessError as e:
        logging.error(f'Failed to disconnect VPN: {e}')

if __name__ == '__main__':
    app.run(debug=True)
