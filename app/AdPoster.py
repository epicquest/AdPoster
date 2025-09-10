
import io
import os

from imagekit_api.imagekit_upload_image import ImageKitUploader
from facebook_api.facebook_poster import FacebookPoster
from twitter_api.twitter_poster import TwitterPoster
from blue_sky_api.blue_sky_poster import BlueskyPoster
from instagram_api.instagram_poster import InstagramPoster
from PosterGenerator import AdContent, AppInfo, PosterGenerator
from dotenv import load_dotenv

from config import APP_TEMPLATES
load_dotenv()

class AdPoster:
    """Main AdPoster class for generating social media ads"""

    def __init__(self):
        pass

    def post_ad(self, platform: str, image_path: str, body_text: str, app_url: str):
        """Post ad to specified platform"""
        if platform == "facebook":
            poster = FacebookPoster()
            poster.post_image_and_comment(image_path, body_text, app_url=app_url)
        elif platform == "twitter":
            poster = TwitterPoster()
            poster.post_text_and_link(body_text, app_url)
        elif platform == "bluesky":
            poster = BlueskyPoster()
            poster.post_image(image_path, body_text, app_url)
        elif platform == "instagram":
            poster = InstagramPoster()
            uploader = ImageKitUploader()
            uploaded_url = uploader.upload_image(image_path, "uploaded_image.jpg", tags=["ads", "upload"])
            if uploaded_url:
                print("Image uploaded successfully. URL:", uploaded_url)
                poster.post_image(uploaded_url, body_text)
            else:
                print("Image upload failed.")

        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
    def post_to_all(self, ads_data: dict[str, AdContent]):
        """Post ads to all specified platforms"""
        for platform, ad_content in ads_data.items():
            image_path = ad_content.image_path
            body_text = ad_content.body_text
            app_url = ad_content.play_store_url
            print(f"Posting to {platform}...")
            if body_text:
                if not image_path or not os.path.exists(image_path):
                    print(f"No valid image path for {platform}, posting without image...")
                  
                self.post_ad(platform, image_path, body_text, app_url)
            else:
                print(f"Missing image or text for {platform}, skipping...")

    def generate_and_post(self, app_info: dict, platforms: list, generate_images=True):
        """Generate ads and post to specified platforms"""

        ads_data : dict[str, AdContent] = self.generate_ads(app_info, platforms, generate_images)
        self.post_to_all(ads_data)
    
    def generate_ads(self, app_info: dict, platforms: list, generate_images=True) -> dict[str, AdContent]:
        """Generate ads for specified platforms and return the data"""
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-api-key-here')
        if GOOGLE_API_KEY == 'your-api-key-here':
            print("Please set your GOOGLE_API_KEY environment variable")
            return {}
        
        poster_generator = PosterGenerator(GOOGLE_API_KEY)
        ads_data: dict[str, AdContent] = poster_generator.generate_multiple_ads(app_info, platforms, generate_images=generate_images)

        # Display previews
        for platform, ad_content in ads_data.items():
            poster_generator.print_ad_preview(ad_content)

        # Save to file
        saved_file = poster_generator.save_ads_to_file(ads_data)
        print(f"All ads saved to: {saved_file}")
         
        return ads_data

def main():
    """Example usage of AdPoster"""
    app_info: AppInfo = AppInfo(**APP_TEMPLATES['game_terra_nova'])
    # app_info: AppInfo = AppInfo(**APP_TEMPLATES['illusion_of_mastery'])

    # Generate ads for multiple platforms
    # platforms = ["facebook", "instagram", "twitter", "linkedin"]
    # platforms = ["facebook", "instagram", "bluesky"]
    # platforms = [ "bluesky"]
    platforms = [ "twitter"]
    #  platforms = [ "instagram"]
    # platforms = [ "facebook"]
    poster = AdPoster()
    poster.generate_and_post(app_info, platforms, generate_images=True)
    # poster.generate_ads(app_info, platforms)

if __name__ == "__main__":
    main()