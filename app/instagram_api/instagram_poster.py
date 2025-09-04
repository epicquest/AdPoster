import requests
import os
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')       # Instagram Business Account ID
ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')

class InstagramPoster:
    def __init__(self, ig_user_id=IG_USER_ID, access_token=ACCESS_TOKEN):
        self.ig_user_id = ig_user_id
        self.access_token = access_token

    def post_image(self, image_url, caption):
        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/v23.0/{self.ig_user_id}/media"
        payload = {
            'image_url': image_url,   # must be a public URL
            'caption': caption,
            'access_token': self.access_token
        }
        response = requests.post(create_url, data=payload)
        response.raise_for_status()
        creation_id = response.json()['id']

        # Step 2: Publish media
        publish_url = f"https://graph.facebook.com/v23.0/{self.ig_user_id}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_response.raise_for_status()
        result = publish_response.json()
        print(f"Posting image to Instagram: {result}")
        return result
    
    def post_image_fake(self, image_path, caption):
        print(f"Posting image to Instagram: {image_path}")
        print(f"Caption: {caption}")