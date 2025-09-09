#!/usr/bin/env python3
"""
AdPoster - Social Media Ad Generator for Android Apps
Generates promotional content using Google Gemini AI
"""
import io
import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
from google import genai
from google.genai import types

from config import APP_TEMPLATES, PLATFORM_SETTINGS
from google_api.ads_image_generator import AdImageGenerator
from dotenv import load_dotenv
load_dotenv()


@dataclass
class AppInfo:
    """Android app information structure"""
    name: str
    description: str
    category: str
    key_features: List[str]
    game_guide: str
    target_audience: str
    play_store_url: str
    icon_path: Optional[str] = None
    screenshots: Optional[List[str]] = None


@dataclass
class AdContent:
    """Generated ad content structure"""
    platform: str
    play_store_url: str
    headline: str
    body_text: str
    hashtags: List[str]
    call_to_action: str
    suggested_image_description: str
    timestamp: str
    image_path: Optional[str] = None


class AdPoster:
    """Main AdPoster class for generating social media ads"""

    def __init__(self, gemini_api_key: str):
        """Initialize AdPoster with Gemini API key"""
        self.image_ai_model = None
        self.logger = None
        self.model = None
        self.client = None
        self.gemini_api_key = gemini_api_key
        self.setup_gemini()
        self.setup_logging()

        # Create necessary directories
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # Platform-specific configurations
        self.platform_configs = PLATFORM_SETTINGS
        
    def setup_gemini(self):
        """Configure Gemini AI"""
        # genai.configure(api_key=self.gemini_api_key)
        # self.model = genai.GenerativeModel(
        #     model_name=os.getenv("AI_MODEL_LITE"),
        #     generation_config=genai.types.GenerationConfig(
        #         temperature=1.0
        #     )
        # )

        self.client = genai.Client(api_key=self.gemini_api_key)
        self.image_ai_model = os.getenv("IMAGE_AI_MODEL")
        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('adposter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_prompt_first(self, app_info: AppInfo, platform: str) -> str:
        """Create a detailed prompt for Gemini based on app info and platform"""
        config = self.platform_configs.get(platform, {})
        max_chars = config.get("max_chars", 2200)
        hashtag_limit = config.get("hashtag_limit", 20)

        prompt = f"""
        Create a compelling social media ad for {platform} promoting an Android app with the following details:

        App Name: {app_info.name}
        Description: {app_info.description}
        Category: {app_info.category}
        Key Features: {', '.join(app_info.key_features)}
        Target Audience: {app_info.target_audience}
        Play Store URL: {app_info.play_store_url}

        Platform Requirements:
        - Maximum characters: {max_chars}
        - Maximum hashtags: {hashtag_limit}
        - Platform: {platform}

        Please provide:
        1. An attention-grabbing headline (max 60 characters)
        2. Engaging body text that highlights key benefits
        3. Relevant hashtags (max {hashtag_limit})
        4. A strong call-to-action
        5. A description for a suggested promotional image containsing no text or logos

        Format your response as JSON with the following structure:
        {{
            "headline": "Your headline here",
            "body_text": "Your body text here",
            "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
            "call_to_action": "Your CTA here",
            "suggested_image_description": "Description of promotional image"
        }}

        Make the content engaging, benefit-focused, and appropriate for {platform}'s audience.
        """

        return prompt
    
    def create_prompt(self, app_info: AppInfo, platform: str) -> str:
        """Create a detailed prompt for Gemini based on app info and platform"""
        config = self.platform_configs.get(platform, {})
        max_chars = config.get("max_chars", 2200)
        hashtag_limit = config.get("hashtag_limit", 20)

        prompt = f"""
        Create a compelling social media ad for {platform} promoting an Android app with the following details:

        App Name: {app_info.name}
        Description: {app_info.description}
        Category: {app_info.category}
        Key Features: {', '.join(app_info.key_features)}
        Target Audience: {app_info.target_audience}
        Play Store URL: {app_info.play_store_url}
        Game guide: [{app_info.game_guide}]

        Platform Requirements:
        - Maximum characters allowed: {max_chars}
        - Maximum number of hashtags: {hashtag_limit}
        - Platform: {platform}

        Please provide:
        1. An attention-grabbing headline (max 60 characters).
        2. Engaging body text that highlights the app’s key benefits and appeals to the target audience.
        3. Relevant hashtags (max {hashtag_limit}, concise and trending where possible).
        4. A strong, clear call-to-action that encourages immediate engagement (e.g., download, try now, explore).
        5. A suggested promotional image description — **must be a purely visual concept, without any text, logos, or overlays**.

        Format your response as strict JSON with the following structure:
        {{
            "headline": "Your headline here",
            "body_text": "Your body text here",
            "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
            "call_to_action": "Your CTA here",
            "suggested_image_description": "Purely visual description of promotional image, no text or logos"
        }}

        Make the content engaging, benefit-focused, and aligned with what performs best on {platform}.
        """

        return prompt


    def generate_ad_content(self, app_info: AppInfo, platform: str) -> Optional[AdContent]:
        """Generate ad content using Gemini AI"""
        try:
            prompt = self.create_prompt(app_info, platform)
            self.logger.info(f"Generating ad content for {platform}")


            # Access API methods through services on the client object
            response = self.client.models.generate_content( model=self.image_ai_model,
    contents=prompt)

            # response = self.model.generate_content(prompt)
            content_json = None
            try:
                # 1. Access the candidate's content
                candidate = response.candidates[0]
                content = candidate.content

                # 2. Get the markdown-formatted text block
                markdown_text = content.parts[0].text

                # 3. Clean up the markdown and extract the JSON
                # This removes the ```json and ``` markers
                json_string = markdown_text.strip().lstrip("```json\n").rstrip("```")

                # 4. Parse the JSON string
                content_json = json.loads(json_string)

                print(content_json)

            except (AttributeError, IndexError, json.JSONDecodeError) as e:
                print(f"Error parsing the response: {e}")
            # Parse JSON response
            # content_json = json.loads(response.text)
            if content_json:
                ad_content = AdContent(
                    platform=platform,
                    headline=content_json["headline"],
                    body_text=content_json["body_text"],
                    hashtags=content_json["hashtags"],
                    call_to_action=content_json["call_to_action"],
                    suggested_image_description=content_json["suggested_image_description"],
                    timestamp=datetime.now().isoformat(),
                    play_store_url=app_info.play_store_url
                )

                self.logger.info(f"Successfully generated ad content for {platform}")
                return ad_content

        except Exception as e:
            self.logger.error(f"Error generating ad content for {platform}: {str(e)}")
            return None

    def generate_multiple_ads(self, app_info: AppInfo, platforms: List[str], generate_images: bool = True) -> Dict[str, AdContent]:
        """Generate ads for multiple platforms"""
        ads = {}

        for platform in platforms:
            if platform in self.platform_configs:
                ad_content = self.generate_ad_content(app_info, platform)
                if ad_content:
                    if generate_images:
                        ad_content.image_path = self.generate_image_from_text(platform, ad_content.suggested_image_description)
                    ads[platform] = ad_content
            else:
                self.logger.warning(f"Platform {platform} not supported")

        return ads

    def save_ads_to_file(self, ads: Dict[str, AdContent], filename: str = None):
        """Save generated ads to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ads_{timestamp}.json"

        filepath = self.output_dir / filename

        # Convert ads to serializable format
        ads_data = {}
        for platform, ad_content in ads.items():
            ads_data[platform] = {
                "platform": ad_content.platform,
                "headline": ad_content.headline,
                "body_text": ad_content.body_text,
                "hashtags": ad_content.hashtags,
                "call_to_action": ad_content.call_to_action,
                "suggested_image_description": ad_content.suggested_image_description,
                "image_path": ad_content.image_path,
                "timestamp": ad_content.timestamp,
                "play_store_url": ad_content.play_store_url
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(ads_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Ads saved to {filepath}")
        return filepath

    def print_ad_preview(self, ad_content: AdContent):
        """Print a formatted preview of the ad content"""
        print(f"\n{'=' * 50}")
        print(f"Platform: {ad_content.platform.upper()}")
        print(f"{'=' * 50}")
        print(f"Headline: {ad_content.headline}")
        print(f"\nBody Text:")
        print(ad_content.body_text)
        print(f"\nHashtags: {' '.join(ad_content.hashtags)}")
        print(f"\nCall to Action: {ad_content.call_to_action}")
        print(f"\nSuggested Image: {ad_content.suggested_image_description}")
        print(f"\nImage: {ad_content.image_path}")
        print(f"{'=' * 50}\n")

    def generate_image_from_text(self, platform: str, prompt: str) -> str:
        """
        Generates an image from a text prompt using the Gemini API and saves it to a file.

        Args:
            prompt (str): The descriptive text for the image to be generated.
            output_filename (str): The name of the file to save the image to.
        """

        try:
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ads_{platform}_{timestamp}.png"
            # filepath = self.output_dir / filename
            ad_image_generator = AdImageGenerator(self.gemini_api_key)
            image_path = ad_image_generator.generate_image_from_text(platform, prompt, self.output_dir, filename)
            return image_path

        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage
def main():
    """Example usage of AdPoster"""

    # You'll need to get your Gemini API key from Google AI Studio
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-api-key-here')

    if GOOGLE_API_KEY == 'your-api-key-here':
        print("Please set your GOOGLE_API_KEY environment variable")
        return

    # Create AdPoster instance
    ad_poster = AdPoster(GOOGLE_API_KEY)

    # Example app information
    # app_info: AppInfo = AppInfo(**APP_TEMPLATES['game_terra_nova'])
    app_info: AppInfo = AppInfo(**APP_TEMPLATES['illusion_of_mastery'])

    # Generate ads for multiple platforms
   # platforms = ["facebook", "instagram", "twitter", "linkedin"]
    # platforms = ["facebook", "instagram", "bluesky"]
    #platforms = [ "bluesky"]
    platforms = [ "twitter"]
    ads = ad_poster.generate_multiple_ads(app_info, platforms, generate_images=False)

    # Display previews
    for platform, ad_content in ads.items():
        ad_poster.print_ad_preview(ad_content)

    # Save to file
    saved_file = ad_poster.save_ads_to_file(ads)
    print(f"All ads saved to: {saved_file}")

if __name__ == "__main__":
    main()