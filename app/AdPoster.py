
import io
import os

from .imagekit_api.imagekit_upload_image import ImageKitUploader
from .facebook_api.facebook_poster import FacebookPoster
from .twitter_api.twitter_poster import TwitterPoster
from .blue_sky_api.blue_sky_poster import BlueskyPoster
from .instagram_api.instagram_poster import InstagramPoster
from .PosterGenerator import AdContent, AppInfo, PosterGenerator

from .config import APP_TEMPLATES, GOOGLE_API_KEY, IMAGE_AI_MODEL

class AdPoster:
    """Main AdPoster class for generating social media ads"""

    def __init__(self):
        pass

    def post_ad(self, platform: str, image_path: str, body_text: str, app_url: str):
        """Post ad to specified platform"""
        import logging
        
        logging.info(f"AdPoster.post_ad() called - Platform: {platform}")
        logging.info(f"Parameters: image_path={image_path}, body_text_length={len(body_text) if body_text else 0}, app_url={app_url}")
        
        try:
            if platform == "facebook":
                logging.info("Initializing FacebookPoster...")
                poster = FacebookPoster()
                logging.info(f"Calling FacebookPoster.post_image_and_comment() with image: {image_path}")
                result = poster.post_image_and_comment(image_path, body_text, app_url=app_url)
                logging.info(f"Facebook posting result: {result}")
                
            elif platform == "twitter":
                logging.info("Initializing TwitterPoster...")
                poster = TwitterPoster()
                logging.info(f"Calling TwitterPoster.post_text_and_link() with text: {body_text[:50]}...")
                result = poster.post_text_and_link(body_text, app_url)
                logging.info(f"Twitter posting result: {result}")
                
            elif platform == "bluesky":
                logging.info("Initializing BlueskyPoster...")
                poster = BlueskyPoster()
                logging.info(f"Calling BlueskyPoster.post_image() with image: {image_path}")
                result = poster.post_image(image_path, body_text, app_url)
                logging.info(f"BlueSky posting result: {result}")
                
            elif platform == "instagram":
                logging.info("Initializing InstagramPoster and ImageKitUploader...")
                poster = InstagramPoster()
                uploader = ImageKitUploader()
                
                logging.info(f"Uploading image to ImageKit: {image_path}")
                uploaded_url = uploader.upload_image(image_path, "uploaded_image.jpg", tags=["ads", "upload"])
                
                if uploaded_url:
                    logging.info(f"Image uploaded successfully to ImageKit. URL: {uploaded_url}")
                    result = poster.post_image(uploaded_url, body_text)
                    logging.info(f"Instagram posting result: {result}")
                else:
                    error_msg = "Image upload to ImageKit failed"
                    logging.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Unsupported platform: {platform}"
                logging.error(error_msg)
                raise ValueError(error_msg)
                
            logging.info(f"Successfully completed posting to {platform}")
            
        except Exception as e:
            error_msg = f"Error posting to {platform}: {str(e)}"
            logging.error(error_msg)
            logging.error(f"Exception type: {type(e).__name__}")
            logging.error(f"Exception details: {repr(e)}")
            # Re-raise the exception so the web interface can handle it
            raise e
        
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
        if not GOOGLE_API_KEY:
            print("Please set your GOOGLE_API_KEY in configuration")
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
    # app_info: AppInfo = AppInfo(**APP_TEMPLATES['game_terra_nova'])
    # app_info: AppInfo = AppInfo(**APP_TEMPLATES['illusion_of_mastery'])
    app_info: AppInfo = AppInfo(**APP_TEMPLATES['dark_stories'])

    # Generate ads for multiple platforms
    platforms = ["facebook", "instagram", "twitter", "bluesky"]
    # platforms = ["facebook", "instagram", "bluesky"]
    # platforms = [ "bluesky"]
   # platforms = [ "twitter"]
    #  platforms = [ "instagram"]
    # platforms = [ "facebook"]
    poster = AdPoster()
    # poster.generate_and_post(app_info, platforms, generate_images=True)
    poster.generate_ads(app_info, platforms)

if __name__ == "__main__":
    main()