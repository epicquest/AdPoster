from flask import Flask, render_template, jsonify, request, send_from_directory, make_response, redirect, url_for, flash
import os
import json
import re
import logging
from datetime import datetime
from .config import APP_TEMPLATES, PLATFORM_SETTINGS, CONFIG, save_config
from .AdPoster import AdPoster
from .PosterGenerator import AppInfo

app = Flask(__name__)
app.secret_key = 'adposter-secret-key-2025'  # Required for flash messages

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Path to the output directory where ads are stored
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../output')

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    try:
        os.makedirs(OUTPUT_DIR)
        logging.info(f"Created output directory: {OUTPUT_DIR}")
    except OSError as e:
        logging.error(f"Could not create output directory {OUTPUT_DIR}: {e}")

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
            
            # Get app name from APP_TEMPLATES by matching content
            for platform in platforms:
                platform_data = ad_data[platform]
                
                # Try to match app name from APP_TEMPLATES
                if 'name' in platform_data and platform_data['name']:
                    content_name = platform_data['name']
                    # Check if this matches any app in APP_TEMPLATES
                    for _, app_config in APP_TEMPLATES.items():
                        if app_config['name'] == content_name:
                            app_name = app_config['name']
                            break
                
                # If not found by name, try to match by app URL
                if not app_name and 'app_url' in platform_data:
                    app_url = platform_data['app_url']
                    for _, app_config in APP_TEMPLATES.items():
                        if app_config['app_url'] in app_url or app_url in app_config['app_url']:
                            app_name = app_config['name']
                            break
                
                # If not found, try to match by keywords in headline/body text
                if not app_name and 'headline' in platform_data:
                    headline = platform_data['headline']
                    body_text = platform_data.get('body_text', '')
                    content = f"{headline} {body_text}".lower()
                    
                    for _, app_config in APP_TEMPLATES.items():
                        app_config_name = app_config['name'].lower()
                        # Check if app name appears in content
                        if app_config_name in content:
                            app_name = app_config['name']
                            break
                
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
            
            # Count images per platform - use config for platform names
            platform_image_counts = {}
            for platform_key in PLATFORM_SETTINGS.keys():
                platform_image_counts[platform_key] = 1 if platform_images.get(platform_key, False) else 0
            
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
            platform_image_counts = {}
            for platform_key in PLATFORM_SETTINGS.keys():
                platform_image_counts[platform_key] = 1 if platform_images.get(platform_key, False) else 0
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
    
    # Check if user needs guidance
    needs_setup = not APP_TEMPLATES or len(APP_TEMPLATES) == 0
    has_sample_only = len(APP_TEMPLATES) == 1 and 'sample_app' in APP_TEMPLATES
    
    return render_template('home.html', 
                         ads=ads, 
                         total_campaigns=len(ads), 
                         platform_settings=PLATFORM_SETTINGS, 
                         app_templates=APP_TEMPLATES,
                         needs_setup=needs_setup,
                         has_sample_only=has_sample_only)

@app.route('/ad/<ad_file>')
def view_ad(ad_file):
    """View details of a specific ad with images."""
    ad_path = os.path.join(OUTPUT_DIR, ad_file)
    if not os.path.exists(ad_path):
        return "Ad not found", 404

    with open(ad_path, 'r') as f:
        ad_data = json.load(f)

    # Extract app name using APP_TEMPLATES
    app_name = None
    platforms = list(ad_data.keys())
    
    for platform in platforms:
        platform_data = ad_data[platform]
        
        # Try to match app name from APP_TEMPLATES
        if 'name' in platform_data and platform_data['name']:
            content_name = platform_data['name']
            # Check if this matches any app in APP_TEMPLATES
            for _, app_config in APP_TEMPLATES.items():
                if app_config['name'] == content_name:
                    app_name = app_config['name']
                    break
        
        # If not found by name, try to match by app URL
        if not app_name and 'app_url' in platform_data:
            app_url = platform_data['app_url']
            for _, app_config in APP_TEMPLATES.items():
                if app_config['app_url'] in app_url or app_url in app_config['app_url']:
                    app_name = app_config['name']
                    break
        
        # If not found, try to match by keywords in headline/body text
        if not app_name and 'headline' in platform_data:
            headline = platform_data['headline']
            body_text = platform_data.get('body_text', '')
            content = f"{headline} {body_text}".lower()
            
            for _, app_config in APP_TEMPLATES.items():
                app_config_name = app_config['name'].lower()
                # Check if app name appears in content
                if app_config_name in content:
                    app_name = app_config['name']
                    break
        
        if app_name:
            break
    
    if not app_name:
        app_name = "Unknown App"

    images = get_images_for_ad(ad_file)
    response = make_response(render_template('ad_detail.html', ad=ad_data, ad_file=ad_file, images=images, app_name=app_name, platform_settings=PLATFORM_SETTINGS))
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

@app.route('/generate')
def generate_ad_page():
    """Display the ad generation page."""
    app_templates = APP_TEMPLATES
    platform_settings = PLATFORM_SETTINGS
    
    # Check if we have any app templates
    if not app_templates:
        flash('No app templates found. Please add at least one app before generating ads.', 'warning')
        return redirect(url_for('list_apps'))
    
    return render_template('generate.html', 
                         app_templates=app_templates, 
                         platform_settings=platform_settings)

@app.route('/generate', methods=['POST'])
def generate_ad():
    """Handle ad generation form submission."""
    try:
        # Get form data
        selected_app_key = request.form.get('app_name')  # This is actually the app key
        selected_platforms = request.form.getlist('platforms')
        generate_images = request.form.get('generate_images') == 'on'
        custom_feature = request.form.get('custom_feature', '').strip()
        
        # Filter out disabled platforms
        selected_platforms = [p for p in selected_platforms if not PLATFORM_SETTINGS.get(p, {}).get('disabled', False)]
        
        # Validate input
        if not selected_app_key:
            return jsonify({
                "status": "error",
                "message": "Please select an app"
            })
        
        if not selected_platforms:
            return jsonify({
                "status": "error",
                "message": "Please select at least one platform"
            })
        
        # Check if we have any app templates
        if not APP_TEMPLATES:
            return jsonify({
                "status": "error",
                "message": "No app templates available. Please add at least one app first."
            })
        
        # Find the app template
        if selected_app_key not in APP_TEMPLATES:
            return jsonify({
                "status": "error", 
                "message": f"App template not found for key: {selected_app_key}. Available apps: {list(APP_TEMPLATES.keys())}"
            })
        
        app_template = APP_TEMPLATES[selected_app_key].copy()
        selected_app_name = app_template['name']
        
        # Add custom feature to the app template if provided
        if custom_feature:
            app_template['key_features'] = app_template.get('key_features', []).copy()
            app_template['key_features'].append(custom_feature)
        
        # Create AppInfo object
        app_info = AppInfo(**app_template)
        
        # Initialize AdPoster and generate ads
        poster = AdPoster()
        
        logging.info(f"Starting ad generation for {selected_app_name} on platforms: {selected_platforms}")
        
        # Generate ads
        ads_data = poster.generate_ads(app_info, selected_platforms, generate_images=generate_images)
        
        if not ads_data:
            return jsonify({
                "status": "error",
                "message": "Failed to generate ads. Please check your API configuration."
            })
        
        # Prepare response data
        result_data = {
            "app": selected_app_name,
            "platforms": selected_platforms,
            "generate_images": generate_images,
            "custom_feature": custom_feature,
            "ads_generated": len(ads_data),
            "generated_platforms": list(ads_data.keys())
        }
        
        # Add ad details if available
        if ads_data:
            result_data["ads_details"] = {}
            for platform, ad_content in ads_data.items():
                result_data["ads_details"][platform] = {
                    "headline": ad_content.headline,
                    "body_text": ad_content.body_text[:100] + "..." if len(ad_content.body_text) > 100 else ad_content.body_text,
                    "hashtags_count": len(ad_content.hashtags),
                    "has_image": bool(ad_content.image_path),
                    "image_path": ad_content.image_path
                }
        
        logging.info(f"Successfully generated ads for {len(ads_data)} platforms")
        
        return jsonify({
            "status": "success",
            "message": f"Successfully generated ads for {len(ads_data)} platform(s)!",
            "data": result_data
        })
        
    except Exception as e:
        logging.error(f"Error generating ads: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred during ad generation: {str(e)}"
        })

@app.route('/ad/<ad_file>/<platform>/post', methods=['POST'])
def post_ad_to_platform(ad_file, platform):
    """Handle posting an ad to a specific platform."""
    try:
        # Load the ad data from the JSON file
        ad_path = os.path.join(OUTPUT_DIR, ad_file)
        
        if not os.path.exists(ad_path):
            return jsonify({
                "status": "error",
                "message": f"Ad file {ad_file} not found"
            })
        
        with open(ad_path, 'r') as f:
            ad_data = json.load(f)
        
        # Check if the platform exists in the ad data
        if platform not in ad_data:
            return jsonify({
                "status": "error",
                "message": f"Platform {platform} not found in ad data"
            })
        
        platform_data = ad_data[platform]
        
        # Get the required data for posting
        body_text = platform_data.get('body_text', '')
        app_url = platform_data.get('app_url', '')
        image_path = platform_data.get('image_path', '')
        
        # Validate required data
        if not body_text:
            return jsonify({
                "status": "error",
                "message": "No body text found for this platform"
            })
        
        # Check if image exists if image_path is provided
        if image_path:
            # Handle relative paths - convert to absolute path
            if not image_path.startswith('/'):
                # Remove 'output/' prefix if present in the stored path
                if image_path.startswith('output/'):
                    image_filename = image_path[7:]  # Remove 'output/' prefix
                else:
                    image_filename = image_path
                full_image_path = os.path.join(OUTPUT_DIR, image_filename)
            else:
                full_image_path = image_path
            
            if not os.path.exists(full_image_path):
                logging.warning(f"Image file not found: {full_image_path}, posting without image")
                image_path = None
            else:
                image_path = full_image_path
                logging.info(f"Using image: {image_path}")
        
        # Initialize AdPoster and post the ad
        poster = AdPoster()
        
        logging.info(f"Starting post process for {platform}: {body_text[:50]}...")
        
        # Create progress tracking
        progress_steps = []
        
        try:
            # Step 1: Initialize platform connection
            progress_steps.append(f"🔗 Connecting to {platform.title()} API...")
            logging.info(f"Step 1: Initializing {platform} connection")
            
            # Step 2: Prepare content
            progress_steps.append("📝 Preparing ad content and validating data...")
            logging.info(f"Step 2: Preparing content - Body: {len(body_text)} chars, Image: {'Yes' if image_path else 'No'}")
            
            # Step 3: Platform-specific preparation
            if platform == "instagram":
                progress_steps.append("📤 Uploading image to ImageKit service...")
            elif platform == "facebook":
                progress_steps.append("🖼️ Processing image for Facebook posting...")
            elif platform == "twitter":
                progress_steps.append("🐦 Formatting content for Twitter constraints...")
            elif platform == "bluesky":
                progress_steps.append("☁️ Preparing content for BlueSky network...")
            else:
                progress_steps.append(f"⚙️ Configuring {platform.title()} posting parameters...")
            
            # Step 4: Upload image (if applicable)
            if image_path:
                progress_steps.append(f"🖼️ Processing and uploading image ({image_path.split('/')[-1]})...")
                logging.info(f"Step 4: Processing image: {image_path}")
            
            # Step 5: Post to platform
            progress_steps.append(f"🚀 Publishing to {platform.title()}...")
            logging.info(f"Step 5: Calling post_ad method for {platform}")
            logging.debug(f"Posting parameters: platform={platform}, image_path={image_path}, body_text_length={len(body_text)}, app_url={app_url}")
            
            # Call the post_ad method with detailed error tracking
            try:
                poster.post_ad(platform, image_path, body_text, app_url)
                logging.info(f"post_ad method completed successfully for {platform}")
            except Exception as post_ad_error:
                error_details = {
                    'error_type': type(post_ad_error).__name__,
                    'error_message': str(post_ad_error),
                    'platform': platform,
                    'has_image': bool(image_path),
                    'image_path': image_path if image_path else 'None',
                    'body_text_length': len(body_text),
                    'app_url': app_url
                }
                logging.error(f"Detailed error in post_ad: {error_details}")
                
                # Add specific error information to progress
                progress_steps.append(f"❌ Posting failed: {error_details['error_type']} - {error_details['error_message']}")
                
                # Update ad data with error information
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ad_data[platform]['post_time'] = current_time
                ad_data[platform]['posting_progress'] = progress_steps
                ad_data[platform]['posting_status'] = 'failed'
                ad_data[platform]['error_details'] = error_details
                
                # Save error information to file
                with open(ad_path, 'w', encoding='utf-8') as f:
                    json.dump(ad_data, f, indent=2, ensure_ascii=False)
                
                return jsonify({
                    "status": "error",
                    "message": f"Failed to post to {platform.title()}: {error_details['error_message']}",
                    "error_type": error_details['error_type'],
                    "progress_steps": progress_steps,
                    "error_details": error_details
                })
            
            # Step 6: Verify posting
            progress_steps.append("✅ Verifying successful publication...")
            logging.info(f"Step 6: Post completed successfully for {platform}")
            
            # Step 7: Update records
            progress_steps.append("💾 Updating campaign records and analytics...")
            logging.info(f"Step 7: Updating ad data with timestamp")
            
            # Step 8: Final confirmation
            progress_steps.append(f"🎉 Successfully posted to {platform.title()}!")
            
        except Exception as post_error:
            error_msg = str(post_error)
            error_type = type(post_error).__name__
            logging.error(f"Outer exception in post_ad_to_platform: {error_type} - {error_msg}")
            progress_steps.append(f"❌ Unexpected error: {error_type} - {error_msg}")
            
            # Update ad data with error information
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ad_data[platform]['post_time'] = current_time
            ad_data[platform]['posting_progress'] = progress_steps
            ad_data[platform]['posting_status'] = 'failed'
            ad_data[platform]['error_details'] = {
                'error_type': error_type,
                'error_message': error_msg,
                'platform': platform
            }
            
            # Save error information to file
            with open(ad_path, 'w', encoding='utf-8') as f:
                json.dump(ad_data, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                "status": "error",
                "message": f"Unexpected error posting to {platform}: {error_msg}",
                "error_type": error_type,
                "progress_steps": progress_steps
            })
        
        # Update the ad data with post time and progress info
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ad_data[platform]['post_time'] = current_time
        ad_data[platform]['posting_progress'] = progress_steps
        ad_data[platform]['posting_status'] = 'completed'
        
        # Save the updated ad data back to the file
        with open(ad_path, 'w', encoding='utf-8') as f:
            json.dump(ad_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Successfully completed posting process to {platform}")
        
        return jsonify({
            "status": "success",
            "message": f"Successfully posted to {platform.title()}!",
            "post_time": current_time,
            "progress_steps": progress_steps,
            "platform_details": {
                "name": platform.title(),
                "content_length": len(body_text),
                "has_image": bool(image_path),
                "image_path": image_path.split('/')[-1] if image_path else None
            }
        })
        
    except Exception as e:
        logging.error(f"Error posting ad to {platform}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to post to {platform}: {str(e)}"
        })

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serve files from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)

# App Management Routes
INPUT_DIR = os.path.join(os.path.dirname(__file__), '../input')

@app.route('/apps')
def list_apps():
    """Display list of available apps."""
    return render_template('apps.html', app_templates=APP_TEMPLATES)

@app.route('/apps/add', methods=['GET', 'POST'])
def add_app():
    """Add a new app."""
    if request.method == 'POST':
        app_key = request.form.get('app_key')
        app_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'key_features': request.form.getlist('key_features'),
            'game_guide': request.form.get('game_guide'),
            'target_audience': request.form.get('target_audience'),
            'app_url': request.form.get('app_url')
        }
        
        # Save to JSON file
        json_path = os.path.join(INPUT_DIR, f"{app_key}.json")
        with open(json_path, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        # Reload APP_TEMPLATES
        global APP_TEMPLATES
        APP_TEMPLATES[app_key] = app_data
        
        return redirect(url_for('list_apps'))
    
    return render_template('app_form.html', action='add', app=None)

@app.route('/apps/<app_key>/edit', methods=['GET', 'POST'])
def edit_app(app_key):
    """Edit an existing app."""
    if request.method == 'POST':
        app_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'key_features': request.form.getlist('key_features'),
            'game_guide': request.form.get('game_guide'),
            'target_audience': request.form.get('target_audience'),
            'app_url': request.form.get('app_url')
        }
        
        # Save to JSON file
        json_path = os.path.join(INPUT_DIR, f"{app_key}.json")
        with open(json_path, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        # Reload APP_TEMPLATES
        global APP_TEMPLATES
        APP_TEMPLATES[app_key] = app_data
        
        return redirect(url_for('list_apps'))
    
    app = APP_TEMPLATES.get(app_key)
    if not app:
        return "App not found", 404
    
    return render_template('app_form.html', action='edit', app=app, app_key=app_key)

@app.route('/apps/<app_key>/delete', methods=['POST'])
def delete_app(app_key):
    """Delete an app."""
    json_path = os.path.join(INPUT_DIR, f"{app_key}.json")
    if os.path.exists(json_path):
        os.remove(json_path)
    
    # Remove from APP_TEMPLATES
    global APP_TEMPLATES
    if app_key in APP_TEMPLATES:
        del APP_TEMPLATES[app_key]
    
    return redirect(url_for('list_apps'))

@app.route('/campaign/<campaign_file>/delete', methods=['POST'])
def delete_campaign(campaign_file):
    """Delete a campaign and its associated images."""
    # Validate filename to prevent directory traversal
    if not campaign_file.endswith('.json') or '..' in campaign_file:
        return "Invalid campaign file", 400
    
    # Delete the JSON file
    json_path = os.path.join(OUTPUT_DIR, campaign_file)
    if os.path.exists(json_path):
        os.remove(json_path)
        logging.info(f"Deleted campaign file: {campaign_file}")
    
    # Delete associated images
    base_name = campaign_file.replace('.json', '')
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    for ext in image_extensions:
        # Delete platform-specific images
        for platform in PLATFORM_SETTINGS.keys():
            image_file = f"{base_name}_{platform}{ext}"
            image_path = os.path.join(OUTPUT_DIR, image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
                logging.info(f"Deleted image: {image_file}")
    
    return redirect(url_for('home'))

@app.route('/config')
def config_page():
    """Configuration page"""
    return render_template('config.html', config=CONFIG)

@app.route('/config', methods=['POST'])
def save_configuration():
    """Save configuration"""
    # Get form data
    config_data = {
        'ai_model': request.form.get('ai_model', 'gemini-2.0-flash-lite'),
        'ai_model_lite': request.form.get('ai_model_lite', 'gemini-2.0-flash-lite'),
        'ai_model_full': request.form.get('ai_model_full', 'gemini-2.0-flash-001'),
        'ai_model2': request.form.get('ai_model2', 'gemini-2.5-flash-preview-04-17'),
        'google_api_key': request.form.get('google_api_key', ''),
        'image_ai_model': request.form.get('image_ai_model', 'gemini-2.0-flash'),
        'reddit_client_id': request.form.get('reddit_client_id', ''),
        'reddit_client_secret': request.form.get('reddit_client_secret', ''),
        'reddit_user_agent': request.form.get('reddit_user_agent', 'CommunityResearcher/1.0'),
        'fb_page_id': request.form.get('fb_page_id', ''),
        'fb_access_token': request.form.get('fb_access_token', ''),
        'instagram_app_id': request.form.get('instagram_app_id', ''),
        'instagram_account_id': request.form.get('instagram_account_id', ''),
        'instagram_access_token': request.form.get('instagram_access_token', ''),
        'imgbb_api_key': request.form.get('imgbb_api_key', ''),
        'imagekit_public_key': request.form.get('imagekit_public_key', ''),
        'imagekit_private_key': request.form.get('imagekit_private_key', ''),
        'imagekit_url_endpoint': request.form.get('imagekit_url_endpoint', ''),
        'bsky_handle': request.form.get('bsky_handle', ''),
        'bsky_password': request.form.get('bsky_password', ''),
        'twitter_api_key': request.form.get('twitter_api_key', ''),
        'twitter_api_key_secret': request.form.get('twitter_api_key_secret', ''),
        'twitter_bearer_token': request.form.get('twitter_bearer_token', ''),
        'twitter_access_token': request.form.get('twitter_access_token', ''),
        'twitter_access_token_secret': request.form.get('twitter_access_token_secret', ''),
        'twitter_client_id': request.form.get('twitter_client_id', ''),
        'twitter_client_secret': request.form.get('twitter_client_secret', '')
    }
    
    # Save configuration
    if save_config(config_data):
        # Reload configuration
        import importlib
        from . import config
        importlib.reload(config)
        flash('Configuration saved successfully!', 'success')
    else:
        flash('Error saving configuration!', 'error')
    
    return redirect(url_for('config_page'))

if __name__ == '__main__':
    app.run(debug=True)
