from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests 
from bs4 import BeautifulSoup

# --- SETUP ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- HOME PAGE ---
@app.route('/')
def home():
    return "✅ The Server is Running! You can now use the Wheel."

def scrape_site(url):
    print(f"🕵️‍♂️ Attempting to scrape: {url}")

    # 1. Clean the URL (Remove tracking junk)
    if "?" in url:
        url = url.split("?")[0]

    try:
        # 2. THE IMPERSONATION (The Magic Fix)
        response = cffi_requests.get(
            url, 
            impersonate="chrome110", 
            timeout=10
        )

        if response.status_code != 200:
            print(f"❌ Server returned status: {response.status_code}")
            return None

        # 3. PARSE HTML
        soup = BeautifulSoup(response.text, "html.parser")
        title = ""

        # STRATEGY A: META TAGS
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            title = meta_title["content"]
        
        # STRATEGY B: FLIPKART
        if not title:
            flipkart_h1 = soup.find("span", {"class": "B_NuCI"})
            if flipkart_h1:
                title = flipkart_h1.get_text()
            else:
                h1 = soup.find("h1")
                if h1:
                    title = h1.get_text()

        # STRATEGY C: AMAZON
        if not title:
            amazon_span = soup.find("span", {"id": "productTitle"})
            if amazon_span:
                title = amazon_span.get_text()

        # STRATEGY D: PAGE TITLE
        if not title and soup.title:
            title = soup.title.string

        # 4. CLEANUP
        if title:
            clean_title = title.split("(")[0].split("|")[0]
            clean_title = clean_title.replace("Online at Best Price", "")
            return clean_title.strip()[:35]
            
        return None

    except Exception as e:
        print(f"❌ Error scraping: {e}")
        return None

@app.route('/get-title', methods=['POST'])
def get_title_api():
    data = request.json
    user_url = data.get('url')

    if not user_url:
        return jsonify({"error": "No URL provided"}), 400

    product_name = scrape_site(user_url)

    if product_name:
        return jsonify({"title": product_name})
    else:
        return jsonify({"error": "Could not find product name. Try Again."}), 500

# --- RUN SERVER ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
