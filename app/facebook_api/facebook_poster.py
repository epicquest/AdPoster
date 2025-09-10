import requests
from dotenv import load_dotenv
import os

load_dotenv()

PAGE_ID = os.getenv('FB_PAGE_ID')
ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')

class FacebookPoster:
    def __init__(self, page_id=PAGE_ID, access_token=ACCESS_TOKEN):
        self.page_id = page_id
        self.access_token = access_token


    def post_image_and_comment(self, image_path: str|None, message, comment_message = None, app_url: str|None = None):
        post_id = self.post_image(image_path, message)

        if comment_message is None:
            if app_url:
                comment_message = f"Get the app on Google Play: {app_url}"
        
        if comment_message:
            comment_id = self.post_comment(post_id, comment_message)

    def post_image(self, image_path: str|None, message):
        """
        Posts an image and text to the Facebook page.
        Returns the ID of the new post.
        """
        if image_path is None or not os.path.exists(image_path):
            # No media file, post just the text
            post_url = f'https://graph.facebook.com/v23.0/{self.page_id}/feed'
            post_payload = {
                'access_token': self.access_token,
                'message': message
            }
        else:
            # Step 1: Upload the image and get its ID
            with open(image_path, 'rb') as img:
                files = {
                    'source': img,
                }
                upload_payload = {
                    'access_token': self.access_token,
                    'published': 'false'
                }
                upload_url = f'https://graph.facebook.com/v23.0/{self.page_id}/photos'
                response = requests.post(upload_url, files=files, data=upload_payload)
                response.raise_for_status()
                photo_id = response.json()['id']
                print(f"Image uploaded successfully. Photo ID: {photo_id}")

            # Step 2: Create the main post with the uploaded image
            post_url = f'https://graph.facebook.com/v23.0/{self.page_id}/feed'
            post_payload = {
                'access_token': self.access_token,
                'message': message,
                'attached_media': [{'media_fbid': photo_id}]
            }
        post_response = requests.post(post_url, json=post_payload)
        post_response.raise_for_status()
        post_id = post_response.json()['id']
        print(f"Post created successfully. Post ID: {post_id}")

        return post_id

    def post_comment(self, post_id, comment_message):
        """
        Posts a comment to a specified Facebook post.
        Returns the ID of the new comment.
        """
        comment_url = f'https://graph.facebook.com/v23.0/{post_id}/comments'
        comment_payload = {
            'access_token': self.access_token,
            'message': comment_message
        }
        comment_response = requests.post(comment_url, json=comment_payload)
        comment_response.raise_for_status()
        comment_result = comment_response.json()
        print(f"Comment posted successfully. Comment ID: {comment_result['id']}")

        return comment_result['id']