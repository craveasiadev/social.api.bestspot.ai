from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import urllib.parse
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_social_media(place_name, address, place_type):
    # Encode the parameters to handle special characters
    encoded_place_name = urllib.parse.quote(place_name)
    encoded_address = urllib.parse.quote(address)
    encoded_type = urllib.parse.quote(place_type)

    # Create a specific search query using place name, address, and type
    search_query = f"{encoded_place_name} {encoded_address} {encoded_type} social media instagram tiktok"
    google_search_url = f"https://www.google.com/search?q={search_query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(google_search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    # Look for both 'a' tags and any other relevant tags in the search results
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            # Clean the link
            if 'url=' in href:
                real_url = href.split('url=')[1].split('&')[0]
                real_url = urllib.parse.unquote(real_url)
                print(f"Checking URL: {real_url}")

                
                # Check if the URL contains keywords related to the place name or type
                # Using a more lenient regex to match multi-word names
                keywords = place_name.lower().split()
                place_pattern = "|".join([re.escape(word) for word in keywords])
                type_pattern = re.escape(place_type.lower())
                
                # Create a combined regex pattern for place name and type
                pattern = f'({place_pattern}|{type_pattern})'
                print(f"URL Pattern: {pattern}")
                
                # Check for Facebook and Instagram URLs
                if re.search(pattern, real_url, re.IGNORECASE):
                    links.append(real_url)

    # Remove duplicates and prioritize main links
    social_media_links = {}

    for link in links:
        if "facebook.com" in link:
            if "facebook" not in social_media_links:
                social_media_links["facebook"] = link
        elif "instagram.com" in link:
            if "instagram" not in social_media_links:
                social_media_links["instagram"] = link
        elif "tiktok.com" in link:
            if "tiktok" not in social_media_links:
                social_media_links["tiktok"] = link

    return list(social_media_links.values())

@app.route('/scrape', methods=['GET'])
def scrape():
    place_name = request.args.get('place_name')
    address = request.args.get('address')
    place_type = request.args.get('type')
    
    if not place_name or not address or not place_type:
        return jsonify({'error': 'Place name, address, and type are required'}), 400

    social_links = scrape_social_media(place_name, address, place_type)

    return jsonify({
        'place_name': place_name,
        'social_links': social_links
    })

if __name__ == '__main__':
    app.run(debug=True)
