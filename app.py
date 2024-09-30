from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import urllib.parse
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_tiktok_reviews(place_name, address, place_type):
    # Encode the place name to handle special characters
    encoded_place_name = urllib.parse.quote(place_name)
    encoded_address = urllib.parse.quote(address)
    encoded_type = urllib.parse.quote(place_type)

    # Create a Google search query using the place name
    search_query = f"{encoded_place_name} {encoded_address} {encoded_type} tiktok reviews"
    google_search_url = f"https://www.google.com/search?q={search_query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(google_search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    tiktok_review_links = set()  # Use a set to avoid duplicates
    limit = 4

    for a_tag in soup.find_all('a', href=True):
        if 'tiktok.com' in a_tag['href']:
            # Extract the actual URL from the href
            match = re.search(r"url=(https://www.tiktok.com[^\&]+)", a_tag['href'])
            if match:
                # Decode URL-encoded characters
                url = urllib.parse.unquote(match.group(1))
                # Replace %40 with @ for TikTok usernames
                url = url.replace('%40', '@')

                # Filter out '/discover' links and only include @username links
                if '@' in url and '/discover' not in url:
                    # Clean up the URL, remove query parameters like '?lang=en'
                    clean_url = re.sub(r'(\d+)/.*', r'\1', url)  # Stop at post ID
                    tiktok_review_links.add(clean_url)

        # Stop if we've already found 5 unique links with @username
        if len(tiktok_review_links) >= limit:
            break

    # Convert the set back to a list and return it
    return list(tiktok_review_links)


#INTAGRAM REVIEWS-------------------------------------------------------------------------------------------
def scrape_insta_reviews(place_name, address, place_type):
    # Encode the place name to handle special characters
    encoded_place_name = urllib.parse.quote(place_name)
    encoded_address = urllib.parse.quote(address)
    encoded_type = urllib.parse.quote(place_type)

    # Create a Google search query using the place name
    search_query = f"{encoded_place_name} {encoded_address} {encoded_type} instagram reviews"
    google_search_url = f"https://www.google.com/search?q={search_query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(google_search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    instagram_review_links = set()  # Use a set to avoid duplicates
    limit = 4

    # Normalize place name for comparison (remove spaces, lowercase)
    normalized_place_name = place_name.replace(' ', '').lower()

    # Loop through all <a> tags
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']

        # Check if it's an Instagram link
        if 'instagram.com' in href:
            # Extract the actual URL from the href
            match = re.search(r"url=(https://www.instagram.com[^\&]+)", href)
            if match:
                # Decode URL-encoded characters
                url = urllib.parse.unquote(match.group(1))
                print(url)

                # Keep only links that have /p/ for posts (filter out non-post URLs like profiles)
                if '/p/' in url:
                    # Extract the Instagram username from the URL
                    post_id = url.split('/')[-2]  # Get the second last element
                    print(post_id) 
                    username_match = re.search(r'instagram.com/([^/]+)/', url)
                    if username_match:
                        username = username_match.group(1).replace(' ', '').lower()

                        # Strict match: Skip posts from the place's own account (exact match)
                        if username != normalized_place_name:
                            # Clean URL and remove unnecessary query parameters
                            clean_url = re.sub(r'\?.*', '', url)  # Remove query parameters
                            cleaner_url = "https://www.instagram.com/p/" + post_id
                            instagram_review_links.add(cleaner_url)
                if '/reel/' in url:
                    # Extract the Instagram username from the URL
                    post_id = url.split('/')[-2]  # Get the second last element
                    print(post_id)
                    username_match = re.search(r'instagram.com/([^/]+)/', url)
                    if username_match:
                        username = username_match.group(1).replace(' ', '').lower()

                        # Strict match: Skip posts from the place's own account (exact match)
                        if username != normalized_place_name:
                            # Clean URL and remove unnecessary query parameters
                            clean_url = re.sub(r'\?.*', '', url)  # Remove query parameters
                            cleaner_url = "https://www.instagram.com/reel/" + post_id
                            instagram_review_links.add(cleaner_url)


        # Stop if we've already found 4 unique links
        if len(instagram_review_links) >= limit:
            break

    # Convert the set back to a list and return it
    return list(instagram_review_links)

@app.route('/tiktok-reviews', methods=['GET'])
def scrape_tiktok():
    place_name = request.args.get('place_name')
    address = request.args.get('address')
    place_type = request.args.get('type')
    
    if not place_name or not address or not place_type:
        return jsonify({'error': 'Place name, address, and type are required'}), 400

    tiktok_review_links = scrape_tiktok_reviews(place_name, address, place_type)

    return jsonify({
        'place_name': place_name,
        'tiktok_review_links': tiktok_review_links
    })

@app.route('/insta-reviews', methods=['GET'])
def scrape_insta():
    place_name = request.args.get('place_name')
    address = request.args.get('address')
    place_type = request.args.get('type')
    
    if not place_name or not address or not place_type:
        return jsonify({'error': 'Place name, address, and type are required'}), 400

    instagram_review_links = scrape_insta_reviews(place_name, address, place_type)

    return jsonify({
        'place_name': place_name,
        'instagram_review_links': instagram_review_links
    })

if __name__ == '__main__':
    app.run(debug=True)
