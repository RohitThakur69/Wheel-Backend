from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# --- SETUP ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- THE CHEF (Scraper) ---
@app.route('/')
def home():
    return "✅ The Python Server is Running! You can now use the Wheel."

def scrape_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # STRATEGY 1: Meta Tags (The smartest way)
        # Most sites (Amazon, Flipkart, Youtube) put the clean title in 'og:title'
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            return meta_title["content"].split("(")[0].split("|")[0].strip()[:30]

        # STRATEGY 2: Specific Amazon ID
        amazon_tag = soup.find("span", {"id": "productTitle"})
        if amazon_tag:
            hey=amazon_tag.get_text().split("(")[0].split("|")[0].strip()
            return hey[:30]
            
        # STRATEGY 3: Generic H1 (Flipkart often uses just an H1)
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().split("(")[0].split("|")[0].strip()[:30]

        # STRATEGY 4: Fallback to Page Title
        if soup.title:
            return soup.title.string.split("(")[0].split("|")[0].strip()[:30]

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    

@app.route('/get-title', methods=['POST'])
def get_title_api():
    # 1. Take the order
    data = request.json
    user_url = data.get('url')

    if not user_url:
        return jsonify({"error": "No URL provided"}), 400

    # 2. Send order to Chef
    print(f"Scraping: {user_url}") # Log for debugging
    product_name = scrape_amazon(user_url)

    # 3. Serve the food
    if product_name:
        return jsonify({"title": product_name})
    else:
        return jsonify({"error": "Failed to scrape site"}), 500

# --- RUN SERVER ---
if __name__ == '__main__':
    app.run()
