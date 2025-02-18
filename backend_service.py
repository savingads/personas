from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def get_driver(browser):
    logging.debug(f'Initializing WebDriver for browser: {browser}')
    if browser == 'chrome':
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == 'firefox':
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif browser == 'safari':
        return webdriver.Safari(service=SafariService())
    elif browser == 'edge':
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    else:
        return None

@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    logging.debug(f'Received data: {data}')
    browser = data.get('browser')
    url = data.get('url')
    
    driver = get_driver(browser)
    if driver:
        driver.get(url)
        # Add logic to capture screenshot or perform actions
        driver.quit()
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid browser'}), 400

if __name__ == '__main__':
    app.run(debug=True)
