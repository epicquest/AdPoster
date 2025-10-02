"""
Configuration file for AdPoster
Copy this to config.py and fill in your actual values
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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