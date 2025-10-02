"""
Configuration file for AdPoster
Copy this to config.py and fill in your actual values
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file (fallback)
load_dotenv()

# Load configuration from JSON file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'configuration', 'config.json')
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'configuration', 'default_config.json')

def load_config():
    """Load configuration from JSON file, with fallback to environment variables"""
    config = {}

    # Check if config.json exists, if not, create it from default_config.json
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(DEFAULT_CONFIG_FILE):
            try:
                with open(DEFAULT_CONFIG_FILE, 'r') as f:
                    default_config = json.load(f)
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Created {CONFIG_FILE} from {DEFAULT_CONFIG_FILE}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not create config from {DEFAULT_CONFIG_FILE}: {e}")
        else:
            print(f"Warning: Neither {CONFIG_FILE} nor {DEFAULT_CONFIG_FILE} found")

    # Try to load from JSON file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {CONFIG_FILE}: {e}")
            config = {}

    # Fallback to environment variables if not in config
    config.setdefault('ai_model', os.getenv('AI_MODEL_LITE', 'gemini-2.0-flash-lite'))
    config.setdefault('ai_model_lite', os.getenv('AI_MODEL_LITE', 'gemini-2.0-flash-lite'))
    config.setdefault('ai_model_full', os.getenv('AI_MODEL', 'gemini-2.0-flash-001'))
    config.setdefault('ai_model2', os.getenv('AI_MODEL2', 'gemini-2.5-flash-preview-04-17'))
    config.setdefault('google_api_key', os.getenv('GOOGLE_API_KEY', ''))
    config.setdefault('image_ai_model', os.getenv('IMAGE_AI_MODEL', 'gemini-2.0-flash'))
    config.setdefault('reddit_client_id', os.getenv('REDDIT_CLIENT_ID', ''))
    config.setdefault('reddit_client_secret', os.getenv('REDDIT_CLIENT_SECRET', ''))
    config.setdefault('reddit_user_agent', os.getenv('REDDIT_USER_AGENT', 'CommunityResearcher/1.0'))
    config.setdefault('fb_page_id', os.getenv('FB_PAGE_ID', ''))
    config.setdefault('fb_access_token', os.getenv('FB_ACCESS_TOKEN', ''))
    config.setdefault('instagram_app_id', os.getenv('INSTAGRAM_APP_ID', ''))
    config.setdefault('instagram_account_id', os.getenv('INSTAGRAM_ACCOUNT_ID', ''))
    config.setdefault('instagram_access_token', os.getenv('INSTAGRAM_ACCESS_TOKEN', ''))
    config.setdefault('imgbb_api_key', os.getenv('IMGBB_API_KEY', ''))
    config.setdefault('imagekit_public_key', os.getenv('IMAGEKIT_PUBLIC_KEY', ''))
    config.setdefault('imagekit_private_key', os.getenv('IMAGEKIT_PRIVATE_KEY', ''))
    config.setdefault('imagekit_url_endpoint', os.getenv('IMAGEKIT_URL_ENDPOINT', ''))
    config.setdefault('bsky_handle', os.getenv('BSKY_HANDLE', ''))
    config.setdefault('bsky_password', os.getenv('BSKY_PASSWORD', ''))
    config.setdefault('twitter_api_key', os.getenv('TWITTER_API_KEY', ''))
    config.setdefault('twitter_api_key_secret', os.getenv('TWITTER_API_KEY_SECRET', ''))
    config.setdefault('twitter_bearer_token', os.getenv('TWITTER_BEARER_TOKEN', ''))
    config.setdefault('twitter_access_token', os.getenv('TWITTER_ACCESS_TOKEN', ''))
    config.setdefault('twitter_access_token_secret', os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''))
    config.setdefault('twitter_client_id', os.getenv('TWITTER_CLIENT_ID', ''))
    config.setdefault('twitter_client_secret', os.getenv('TWITTER_CLIENT_SECRET', ''))

    return config

# Load configuration
CONFIG = load_config()

# Extract individual config values for backward compatibility
AI_MODEL_LITE = CONFIG['ai_model_lite']
AI_MODEL = CONFIG['ai_model_full']
AI_MODEL2 = CONFIG['ai_model2']
GOOGLE_API_KEY = CONFIG['google_api_key']
IMAGE_AI_MODEL = CONFIG['image_ai_model']
REDDIT_CLIENT_ID = CONFIG['reddit_client_id']
REDDIT_CLIENT_SECRET = CONFIG['reddit_client_secret']
REDDIT_USER_AGENT = CONFIG['reddit_user_agent']
FB_PAGE_ID = CONFIG['fb_page_id']
FB_ACCESS_TOKEN = CONFIG['fb_access_token']
INSTAGRAM_APP_ID = CONFIG['instagram_app_id']
INSTAGRAM_ACCOUNT_ID = CONFIG['instagram_account_id']
INSTAGRAM_ACCESS_TOKEN = CONFIG['instagram_access_token']
IMGBB_API_KEY = CONFIG['imgbb_api_key']
IMAGEKIT_PUBLIC_KEY = CONFIG['imagekit_public_key']
IMAGEKIT_PRIVATE_KEY = CONFIG['imagekit_private_key']
IMAGEKIT_URL_ENDPOINT = CONFIG['imagekit_url_endpoint']
BSKY_HANDLE = CONFIG['bsky_handle']
BSKY_PASSWORD = CONFIG['bsky_password']
TWITTER_API_KEY = CONFIG['twitter_api_key']
TWITTER_API_KEY_SECRET = CONFIG['twitter_api_key_secret']
TWITTER_BEARER_TOKEN = CONFIG['twitter_bearer_token']
TWITTER_ACCESS_TOKEN = CONFIG['twitter_access_token']
TWITTER_ACCESS_TOKEN_SECRET = CONFIG['twitter_access_token_secret']
def save_config(config_data):
    """Save configuration to JSON file"""
    try:
        # Ensure configuration directory exists
        config_dir = os.path.dirname(CONFIG_FILE)
        os.makedirs(config_dir, exist_ok=True)

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


# App Templates - Loaded from JSON files in /input directory
APP_TEMPLATES = {}

input_dir = os.path.join(os.path.dirname(__file__), '..', 'input')
for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        key = filename[:-5]  # remove .json
        with open(os.path.join(input_dir, filename), 'r') as f:
            APP_TEMPLATES[key] = json.load(f)
PLATFORM_SETTINGS = {
    "facebook": {
        "max_chars": 2200,
        "hashtag_limit": 30,
        "optimal_image_size": (1200, 630),
        "aspect_ratio": "16:9",  # Closest to 1200x630
        "tone": "friendly and engaging",
        "style": "clean, vibrant visuals with clear subjects, community-oriented feel",
        "best_practices": [
            "Use short paragraphs and emojis to boost engagement.",
            "Images with people perform better than generic graphics.",
            "Aim for community-focused messaging."
        ]
    },
    "instagram": {
        "max_chars": 2200,
        "hashtag_limit": 30,
        "optimal_image_size": (1080, 1080),
        "aspect_ratio": "1:1",  # Square format
        "tone": "visual and trendy",
        "style": "aesthetic, modern, bold colors, eye-catching composition",
        "best_practices": [
            "Use carousels for higher engagement.",
            "Leverage Stories/Reels for reach.",
            "Keep captions short; let visuals do the talking."
        ]
    },
    "twitter": {
        "max_chars": 280,
        "hashtag_limit": 10,
        "optimal_image_size": (1200, 675),
        "aspect_ratio": "16:9",  # Closest to 1200x675
        "tone": "concise and punchy",
        "style": "minimalistic, high contrast, quick-to-digest imagery",
        "best_practices": [
            "Keep text short and impactful.",
            "Use 1–2 hashtags max for relevance.",
            "Threads work well for storytelling."
        ]
    },
    "linkedin": {
        "max_chars": 3000,
        "hashtag_limit": 20,
        "optimal_image_size": (1200, 627),
        "aspect_ratio": "16:9",  # Closest to 1200x627
        "tone": "professional and informative",
        "style": "corporate, trustworthy, clear visuals with a polished look",
        "best_practices": [
            "Use professional and educational tone.",
            "Include data-driven insights or case studies.",
            "Native documents and carousels drive more reach."
        ]
    },
    "tiktok": {
        "max_chars": 2200,
        "hashtag_limit": 20,
        "optimal_image_size": (1080, 1920),
        "aspect_ratio": "9:16",  # Vertical video format
        "tone": "fun and energetic",
        "style": "dynamic, colorful, high-energy, visually playful",
        "best_practices": [
            "Hook viewers in first 3 seconds.",
            "Use trending sounds and effects.",
            "Keep videos between 10–30 seconds."
        ]
    },
    "bluesky": {
        "max_chars": 200,
        "hashtag_limit": 5,  # Not enforced, hashtags uncommon
        "optimal_image_size": (1200, 675),
        "max_image_filesize_kb": 976,  # Hard limit from API
        "aspect_ratio": "16:9",
        "tone": "casual, authentic, and community-driven",
        "style": "clean, relatable visuals; organic feel; less polished, more 'real'",
        "best_practices": [
            "Keep text under 300 chars — short and conversational.",
            "Avoid heavy hashtag use; plain words are preferred.",
            "Images must be < 976 KB.",
            "Replying and engaging boosts visibility."
        ]
    }
}


# Output Settings
OUTPUT_DIRECTORY = "output"
LOG_LEVEL = "INFO"
SAVE_IMAGES = True
SAVE_JSON = True

# Image Generation Settings
IMAGE_SETTINGS = {
    "default_background_color": "#1a237e",
    "title_color": "#ffffff",
    "accent_color": "#ffc107",
    "cta_color": "#4caf50",
    "default_font_size_title": 48,
    "default_font_size_body": 32
}