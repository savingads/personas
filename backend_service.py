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
import openvpn_api
import logging
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def connect_vpn(region):
    logging.debug(f'Connecting to VPN server in region: {region}')
    vpn = openvpn_api.VPN('127.0.0.1', 7505)
    try:
        vpn.connect()
        vpn.login('username', 'password')  # Replace with actual credentials
        vpn.set_config(f'/path/to/{region}.ovpn')  # Replace with actual path to .ovpn file for the region
        vpn.start()
        time.sleep(5)  # Give some time for the VPN to establish the connection
        logging.debug('VPN connection established')
    except Exception as e:
        logging.error(f'Failed to connect to VPN: {e}')
        return False
    return True

def disconnect_vpn():
    logging.debug('Disconnecting VPN')
    vpn = openvpn_api.VPN('127.0.0.1', 7505)
    try:
        vpn.connect()
        vpn.stop()
        logging.debug('VPN disconnected')
    except Exception as e:
        logging.error(f'Failed to disconnect VPN: {e}')

def get_driver(browser, accept_language):
    logging.debug(f'Initializing WebDriver for browser: {browser}')
    if browser == 'chrome':
        options = ChromeOptions()
        options.add_argument(f'--lang={accept_language}')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "acceptLanguage": accept_language
        })
        return driver
    elif browser == 'firefox':
        options = FirefoxOptions()
        options.set_preference('intl.accept_languages', accept_language)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.execute_script(f"Object.defineProperty(navigator, 'language', {{get: function() {{return '{accept_language}';}}}});")
        return driver
    elif browser == 'safari':
        # Safari does not support setting Accept-Language header via WebDriver
        return webdriver.Safari(service=SafariService())
    elif browser == 'edge':
        options = EdgeOptions()
        options.add_argument(f'--lang={accept_language}')
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
    if not connect_vpn(region):
        return jsonify({'status': 'error', 'message': 'Failed to connect to VPN'}), 500
    
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

if __name__ == '__main__':
    app.run(debug=True)
