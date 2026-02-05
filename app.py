from flask import Flask, request, jsonify
from flask_cors import CORS  # <--- Essential for allowing your site to talk to this server
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- 1. ENABLE CORS ---
# This tells the server: "It's okay to accept requests from any website"
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 2. HOME PAGE ROUTE ---
# This fixes the "Not Found" error. Now you can visit your URL to check if it's alive.
@app.route('/')
def home():
    return "✅ The Python Server is Running! You can now use the Wheel."

# --- 3. YOUR ORIGINAL SCRAPER LOGIC ---
@app.route('/get-title', methods=['POST'])
def get_title():
    # Get JSON data from the request
    data = request.json
    
    # Safety Check: Did they send a URL?
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
    
    url = data['url']
    
    try:
        # We pretend to be a real Chrome browser so websites don't block us
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Download the page
        response = requests.get(url, headers=headers, timeout=10)
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the title tag
        if soup.title:
            return jsonify({'title': soup.title.string.split("(")[0].strip()[:30]})
        else:
            return jsonify({'title': 'No Title Found'})
            
    except Exception as e:
        # If anything crashes (like a bad URL), tell the frontend what happened
        return jsonify({'error': str(e)}), 500

# This part runs the app
if __name__ == '__main__':

    app.run()

