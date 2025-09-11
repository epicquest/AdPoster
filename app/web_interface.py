from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
import os
import json
import re
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Path to the output directory where ads are stored
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../output')

def get_images_for_ad(ad_file):
    """Retrieve image files associated with a specific ad."""
    base_name = re.sub(r'\.json$', '', ad_file)
    images = []
    for file_name in os.listdir(OUTPUT_DIR):
        if file_name.startswith(base_name) and file_name.endswith(('.png', '.jpg', '.jpeg')):
            images.append(file_name)
    logging.debug(f"Images for {ad_file}: {images}")
    return images

@app.route('/')
def home():
    """Display a list of generated ads with images, sorted by date."""
    ads = []
    # Get all JSON files
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
    
    # Sort files by the timestamp in filename (format: ads_YYYYMMDD_HHMMSS.json)
    json_files.sort(key=lambda x: x.split('_')[1:3] if len(x.split('_')) >= 3 else ['00000000', '000000'], reverse=True)
    
    # Create list of ads with their images
    for file_name in json_files:
        images = get_images_for_ad(file_name)
        ads.append({"file": file_name, "images": images})
    
    return render_template('home.html', ads=ads)

@app.route('/ad/<ad_file>')
def view_ad(ad_file):
    """View details of a specific ad with images."""
    ad_path = os.path.join(OUTPUT_DIR, ad_file)
    if not os.path.exists(ad_path):
        return "Ad not found", 404

    with open(ad_path, 'r') as f:
        ad_data = json.load(f)

    images = get_images_for_ad(ad_file)
    response = make_response(render_template('ad_detail.html', ad=ad_data, ad_file=ad_file, images=images))
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/ad/<ad_file>/confirm', methods=['POST'])
def confirm_ad(ad_file):
    """Mark an ad as confirmed."""
    # Logic to mark the ad as confirmed (e.g., update JSON or database)
    return jsonify({"status": "confirmed", "ad_file": ad_file})

@app.route('/ad/<ad_file>/reject', methods=['POST'])
def reject_ad(ad_file):
    """Mark an ad as rejected."""
    # Logic to mark the ad as rejected (e.g., update JSON or database)
    return jsonify({"status": "rejected", "ad_file": ad_file})

@app.route('/ad/<ad_file>/<platform>/post', methods=['POST'])
def post_ad(ad_file, platform):
    """Handle the 'Post Now' action for a specific platform."""
    ad_path = os.path.join(OUTPUT_DIR, ad_file)
    if not os.path.exists(ad_path):
        return jsonify({"status": "error", "message": "Ad not found"}), 404

    with open(ad_path, 'r') as f:
        ad_data = json.load(f)

    # Add post time to the JSON data
    post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if platform not in ad_data:
        return jsonify({"status": "error", "message": "Platform not found in ad"}), 400

    ad_data[platform]['post_time'] = post_time

    # Save the updated JSON file
    with open(ad_path, 'w') as f:
        json.dump(ad_data, f, indent=4)

    return jsonify({"status": "success", "post_time": post_time, "platform": platform})

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serve files from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
