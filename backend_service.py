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
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

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
    
    # Define geolocation coordinates and Accept-Language headers for each region
    region_settings = {
        'North America': {'latitude': 37.7749, 'longitude': -122.4194, 'accept_language': 'en-US'},
        'Europe': {'latitude': 48.8566, 'longitude': 2.3522, 'accept_language': 'fr-FR'},
        'Asia': {'latitude': 35.6895, 'longitude': 139.6917, 'accept_language': 'ja-JP'},
        'South America': {'latitude': -23.5505, 'longitude': -46.6333, 'accept_language': 'pt-BR'},
        'Africa': {'latitude': -1.2921, 'longitude': 36.8219, 'accept_language': 'sw-KE'},
        'Australia': {'latitude': -33.8688, 'longitude': 151.2093, 'accept_language': 'en-AU'}
    }
    
    # Get the settings for the selected region
    settings = region_settings.get(region, {'latitude': 0, 'longitude': 0, 'accept_language': 'en-US'})
    
    driver = get_driver(browser, settings['accept_language'])
    if driver:
        if browser in ['chrome', 'edge']:
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": settings['latitude'],
                "longitude": settings['longitude'],
                "accuracy": 100
            })
        elif browser == 'firefox':
            driver.install_addon('geckodriver', temporary=True)
            driver.execute_script("""
                window.navigator.geolocation.getCurrentPosition = function(success){
                    var position = {"coords" : {
                        "latitude": %(latitude)s,
                        "longitude": %(longitude)s
                    }};
                    success(position);
                }
            """ % settings)
        
        driver.get(url)
        # Add logic to capture screenshot or perform actions
        driver.quit()
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid browser'}), 400

if __name__ == '__main__':
    app.run(debug=True)
