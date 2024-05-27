from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)

cache = {
    "result": None,
    "timestamp": 0
}

# Cache duration in seconds (3 hours)
CACHE_DURATION = 10800

def can_wear_shorts():
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    if(os.getenv('ENV') == 'production'):
        service = Service(executable_path=r'/usr/local/bin/chromedriver')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36") # headless fix??
        options.add_argument("--window-size=1920,1080") # headless fix??

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--remote-debugging-port=9222")
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://kanikeenkortebroekaan.nl/")
        
        image_element = driver.find_element(By.CSS_SELECTOR, ".main-image img")
        image_src = image_element.get_attribute("src")

        print(image_src)

        if "yes-man.png" in image_src:
            return True
        elif "no-man.png" in image_src:
            return False
        else:
            raise ValueError("Unexpected image source")
    finally:
        driver.quit()

@app.route('/can-wear-shorts', methods=['GET'])
def api_can_wear_shorts():
    current_time = time.time()
    
    # Check if the cache is still valid
    if cache["result"] is not None and (current_time - cache["timestamp"]) < CACHE_DURATION:
        return jsonify({"can_wear_shorts": cache["result"]})
    
    try:
        result = can_wear_shorts()
        # Update the cache
        cache["result"] = result
        cache["timestamp"] = current_time
        return jsonify({"can_wear_shorts": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
