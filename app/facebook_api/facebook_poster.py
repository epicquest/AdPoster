import requests
from dotenv import load_dotenv
import os

load_dotenv()

PAGE_ID = os.getenv('FB_PAGE_ID')
ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')

class FacebookPoster:
    def __init__(self, page_id = PAGE_ID, access_token = ACCESS_TOKEN):
        self.page_id = page_id
        self.access_token = access_token


    def post_image_fake(self, image_path, message):
        print(f"Posting image to Facebook: {image_path}")
        print(f"Message: {message}")

    def post_image(self, image_path, message):
        with open(image_path, 'rb') as img:
            files = {
                'source': img,
            }
            payload = {
                'access_token': self.access_token,
                'published': 'false'
            }
            upload_url = f'https://graph.facebook.com/v23.0/{self.page_id}/photos'
            response = requests.post(upload_url, files=files, data=payload)
            response.raise_for_status()
            photo_id = response.json()['id']

        post_url = f'https://graph.facebook.com/v23.0/{self.page_id}/feed'
        post_payload = {
            'access_token': self.access_token,
            'message': message,
            'attached_media': [{'media_fbid': photo_id}]
        }
        post_response = requests.post(post_url, json=post_payload)
        post_response.raise_for_status()
        result = post_response.json()
        print(f"Posting image to Facebook: {result}")
        return result