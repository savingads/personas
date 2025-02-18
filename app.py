from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def index():
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Australia']
    return render_template('index.html', regions=regions)

@app.route('/select_region', methods=['POST'])
def select_region():
    selected_region = request.form['region']
    url = request.form['url']
    
    # Define geolocation coordinates for each region
    geolocations = {
        'North America': {'latitude': 37.7749, 'longitude': -122.4194},  # Example: San Francisco, USA
        'Europe': {'latitude': 48.8566, 'longitude': 2.3522},  # Example: Paris, France
        'Asia': {'latitude': 35.6895, 'longitude': 139.6917},  # Example: Tokyo, Japan
        'South America': {'latitude': -23.5505, 'longitude': -46.6333},  # Example: São Paulo, Brazil
        'Africa': {'latitude': -1.2921, 'longitude': 36.8219},  # Example: Nairobi, Kenya
        'Australia': {'latitude': -33.8688, 'longitude': 151.2093}  # Example: Sydney, Australia
    }
    
    # Get the geolocation for the selected region
    geolocation = geolocations.get(selected_region, {'latitude': 0, 'longitude': 0})
    
    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1
    })
    
    # Initialize Selenium WebDriver with Chrome options
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
    # Set geolocation
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": geolocation['latitude'],
        "longitude": geolocation['longitude'],
        "accuracy": 100
    })
    
    # Open the URL
    driver.get(url)
    
    return f"Selected region: {selected_region}. URL opened in browser with geolocation set."

if __name__ == '__main__':
    app.run(debug=True)
