from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
import os
import json
import re
import logging
from datetime import datetime
from config import APP_TEMPLATES, PLATFORM_SETTINGS

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Path to the output directory where ads are stored
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../output')

def get_images_for_ad(ad_file):
    """Retrieve image files associated with a specific ad by reading the JSON file."""
    ad_path = os.path.join(OUTPUT_DIR, ad_file)
    
    if not os.path.exists(ad_path):
        logging.debug(f"Ad file {ad_file} does not exist")
        return [], {}
    
    images = []
    platform_images = {}
    
    try:
        with open(ad_path, 'r') as f:
            ad_data = json.load(f)
        
        # Check each platform for image_path
        for platform, platform_data in ad_data.items():
            platform_images[platform] = False  # Initialize as no image
            
            if 'image_path' in platform_data:
                image_path = platform_data['image_path']
                
                # Extract just the filename from the path
                if '/' in image_path:
                    image_filename = image_path.split('/')[-1]
                else:
                    image_filename = image_path
                
                # Check if the image file actually exists
                full_image_path = os.path.join(OUTPUT_DIR, image_filename)
                if os.path.exists(full_image_path):
                    images.append(image_filename)
                    platform_images[platform] = True
                    logging.debug(f"Found image for {platform}: {image_filename}")
                else:
                    logging.debug(f"Image not found for {platform}: {image_filename} (path: {full_image_path})")
    
    except Exception as e:
        logging.error(f"Error reading ad file {ad_file}: {e}")
    
    logging.debug(f"Images for {ad_file}: {images}")
    logging.debug(f"Platform images: {platform_images}")
    return images, platform_images

@app.route('/')
def home():
    """Display a list of generated ads with enhanced information."""
    ads = []
    # Get all JSON files
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
    
    # Sort files by the timestamp in filename (format: ads_YYYYMMDD_HHMMSS.json)
    json_files.sort(key=lambda x: x.split('_')[1:3] if len(x.split('_')) >= 3 else ['00000000', '000000'], reverse=True)
    
    # Create list of ads with enhanced information
    for file_name in json_files:
        ad_path = os.path.join(OUTPUT_DIR, file_name)
        try:
            with open(ad_path, 'r') as f:
                ad_data = json.load(f)
            
            # Extract meaningful information
            platforms = list(ad_data.keys())
            app_name = None
            posted_count = 0
            total_platforms = len(platforms)
            creation_date = None
            
            # Get app name from the content - improved extraction based on config.py
            for platform in platforms:
                platform_data = ad_data[platform]
                
                # First try to extract from Play Store URL
                if 'play_store_url' in platform_data:
                    play_store_url = platform_data['play_store_url']
                    if 'darkstories' in play_store_url:
                        app_name = "Dark Stories AI"
                    elif 'illusionofmasteryandroid' in play_store_url:
                        app_name = "Illusion of Mastery"
                    elif 'oneoffive' in play_store_url:
                        app_name = "Terra Nova"
                    elif 'terranovaadventure' in play_store_url:
                        app_name = "Terra Nova"
                
                # If not found from URL, extract from headline and body text
                if not app_name and 'headline' in platform_data:
                    headline = platform_data['headline']
                    body_text = platform_data.get('body_text', '')
                    
                    # Look for specific app names and keywords in content
                    if 'Dark Stories' in headline or 'Dark Stories' in body_text:
                        app_name = "Dark Stories AI"
                    elif 'Terra Nova' in headline or 'Terra Nova' in body_text:
                        app_name = "Terra Nova"
                    elif 'Illusion of Mastery' in headline or 'Illusion of Mastery' in body_text:
                        app_name = "Illusion of Mastery"
                    elif ('Mystery' in headline or 'Mystery' in body_text) and ('AI' in headline or 'AI' in body_text):
                        app_name = "Dark Stories AI"
                    elif 'Space' in headline or 'Galaxy' in body_text or 'Spaceship' in body_text:
                        app_name = "Terra Nova"
                    elif 'Quiz' in headline or 'Quiz' in body_text or 'Knowledge' in body_text:
                        app_name = "Illusion of Mastery"
                    else:
                        # Extract the main subject from headline
                        if ':' in headline:
                            app_name = headline.split(':')[0].strip()
                        elif '!' in headline:
                            app_name = headline.split('!')[0].strip()
                        else:
                            # Take first 3-4 words as app name
                            words = headline.split()
                            app_name = ' '.join(words[:3]) if len(words) >= 3 else headline
                
                if app_name:
                    break
            
            # Count posted platforms
            for platform in platforms:
                if 'post_time' in ad_data[platform]:
                    posted_count += 1
            
            # Extract creation date from filename
            try:
                date_part = file_name.split('_')[1]  # YYYYMMDD
                time_part = file_name.split('_')[2].replace('.json', '')  # HHMMSS
                creation_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            except:
                creation_date = "Unknown"
            
            images, platform_images = get_images_for_ad(file_name)
            
            # Count images per platform
            platform_image_counts = {
                'facebook': 1 if platform_images.get('facebook', False) else 0,
                'instagram': 1 if platform_images.get('instagram', False) else 0,
                'twitter': 1 if platform_images.get('twitter', False) else 0,
                'bluesky': 1 if platform_images.get('bluesky', False) else 0
            }
            
            ads.append({
                "file": file_name,
                "app_name": app_name or "Unknown App",
                "platforms": platforms,
                "posted_count": posted_count,
                "total_platforms": total_platforms,
                "creation_date": creation_date,
                "images": images,
                "image_count": len(images),
                "platform_image_counts": platform_image_counts,
                "is_fully_posted": posted_count == total_platforms,
                "posting_status": f"{posted_count}/{total_platforms} posted"
            })
            
        except Exception as e:
            logging.error(f"Error reading {file_name}: {e}")
            # Fallback to basic info
            images, platform_images = get_images_for_ad(file_name)
            platform_image_counts = {
                'facebook': 1 if platform_images.get('facebook', False) else 0,
                'instagram': 1 if platform_images.get('instagram', False) else 0,
                'twitter': 1 if platform_images.get('twitter', False) else 0,
                'bluesky': 1 if platform_images.get('bluesky', False) else 0
            }
            ads.append({
                "file": file_name,
                "app_name": "Error loading",
                "platforms": [],
                "posted_count": 0,
                "total_platforms": 0,
                "creation_date": "Unknown",
                "images": images,
                "image_count": len(images),
                "platform_image_counts": platform_image_counts,
                "is_fully_posted": False,
                "posting_status": "Error"
            })
    
    return render_template('home.html', ads=ads, total_campaigns=len(ads))

@app.route('/ad/<ad_file>')
def view_ad(ad_file):
    """View details of a specific ad with images."""
    ad_path = os.path.join(OUTPUT_DIR, ad_file)
    if not os.path.exists(ad_path):
        return "Ad not found", 404

    with open(ad_path, 'r') as f:
        ad_data = json.load(f)

    # Extract app name using the same logic as the home page
    app_name = None
    platforms = list(ad_data.keys())
    
    for platform in platforms:
        platform_data = ad_data[platform]
        
        # First try to extract from Play Store URL
        if 'play_store_url' in platform_data:
            play_store_url = platform_data['play_store_url']
            if 'darkstories' in play_store_url:
                app_name = "Dark Stories AI"
            elif 'illusionofmasteryandroid' in play_store_url:
                app_name = "Illusion of Mastery"
            elif 'oneoffive' in play_store_url:
                app_name = "Terra Nova"
            elif 'terranovaadventure' in play_store_url:
                app_name = "Terra Nova"
        
        # If not found from URL, extract from headline and body text
        if not app_name and 'headline' in platform_data:
            headline = platform_data['headline']
            body_text = platform_data.get('body_text', '')
            
            # Look for specific app names and keywords in content
            if 'Dark Stories' in headline or 'Dark Stories' in body_text:
                app_name = "Dark Stories AI"
            elif 'Terra Nova' in headline or 'Terra Nova' in body_text:
                app_name = "Terra Nova"
            elif 'Illusion of Mastery' in headline or 'Illusion of Mastery' in body_text:
                app_name = "Illusion of Mastery"
            elif ('Mystery' in headline or 'Mystery' in body_text) and ('AI' in headline or 'AI' in body_text):
                app_name = "Dark Stories AI"
            elif 'Space' in headline or 'Galaxy' in body_text or 'Spaceship' in body_text:
                app_name = "Terra Nova"
            elif 'Quiz' in headline or 'Quiz' in body_text or 'Knowledge' in body_text:
                app_name = "Illusion of Mastery"
            else:
                # Extract the main subject from headline
                if ':' in headline:
                    app_name = headline.split(':')[0].strip()
                elif '!' in headline:
                    app_name = headline.split('!')[0].strip()
                else:
                    # Take first 3-4 words as app name
                    words = headline.split()
                    app_name = ' '.join(words[:3]) if len(words) >= 3 else headline
        
        if app_name:
            break
    
    if not app_name:
        app_name = "Unknown App"

    images = get_images_for_ad(ad_file)
    response = make_response(render_template('ad_detail.html', ad=ad_data, ad_file=ad_file, images=images, app_name=app_name))
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

@app.route('/generate')
def generate_ad_page():
    """Display the ad generation page."""
    app_templates = APP_TEMPLATES
    platform_settings = PLATFORM_SETTINGS
    return render_template('generate.html', 
                         app_templates=app_templates, 
                         platform_settings=platform_settings)

@app.route('/generate', methods=['POST'])
def generate_ad():
    """Handle ad generation form submission."""
    # Get form data
    selected_app = request.form.get('app_name')
    selected_platforms = request.form.getlist('platforms')
    generate_images = request.form.get('generate_images') == 'on'
    custom_feature = request.form.get('custom_feature', '').strip()
    
    # For now, this is a fake implementation
    # In the future, this would call the actual ad generation logic
    result = {
        "status": "success",
        "message": "Ad generation is not yet implemented",
        "data": {
            "app": selected_app,
            "platforms": selected_platforms,
            "generate_images": generate_images,
            "custom_feature": custom_feature
        }
    }
    
    return jsonify(result)

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serve files from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
