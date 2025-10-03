import requests
import os
import logging

from ..config import FB_PAGE_ID, FB_ACCESS_TOKEN

# Configure logging for FacebookPoster
logger = logging.getLogger(__name__)

class FacebookPoster:
    def __init__(self, page_id=FB_PAGE_ID, access_token=FB_ACCESS_TOKEN):
        self.page_id = page_id
        self.access_token = access_token
        logger.info(f"FacebookPoster initialized with page_id: {bool(self.page_id)}, access_token: {bool(self.access_token)}")


    def post_image_and_comment(self, image_path: str|None, message, comment_message = None, app_url: str|None = None):
        logger.info(f"Starting Facebook post with image: {image_path}, message length: {len(message) if message else 0}")
        
        if not self.page_id or not self.access_token:
            error_msg = f"Missing Facebook credentials - Page ID: {bool(self.page_id)}, Access Token: {bool(self.access_token)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            post_id = self.post_image(image_path, message)
            logger.info(f"Main Facebook post created successfully with ID: {post_id}")

            if comment_message is None:
                if app_url:
                    comment_message = f"Get the app on Google Play: {app_url}"
            
            if comment_message:
                logger.info("Adding comment to Facebook post...")
                comment_id = self.post_comment(post_id, comment_message)
                logger.info(f"Comment added successfully with ID: {comment_id}")
                
            return {"post_id": post_id, "comment_id": comment_id if comment_message else None}
            
        except Exception as e:
            error_msg = f"Error in Facebook post_image_and_comment: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_image(self, image_path: str|None, message):
        """
        Posts an image and text to the Facebook page.
        Returns the ID of the new post.
        """
        logger.info(f"Creating Facebook post - Has image: {bool(image_path)}, Message length: {len(message) if message else 0}")
        
        try:
            if image_path is None or not os.path.exists(image_path):
                # No media file, post just the text
                logger.info("Posting text-only content to Facebook")
                post_url = f'https://graph.facebook.com/v23.0/{self.page_id}/feed'
                post_payload = {
                    'access_token': self.access_token,
                    'message': message
                }
                
                logger.info(f"Making text post request to: {post_url}")
                post_response = requests.post(post_url, json=post_payload, timeout=30)
                
                logger.info(f"Facebook text post response status: {post_response.status_code}")
                post_response.raise_for_status()
                
                post_result = post_response.json()
                post_id = post_result['id']
                logger.info(f"Text post created successfully. Post ID: {post_id}")
                
            else:
                # Step 1: Upload the image and get its ID
                logger.info(f"Uploading image to Facebook: {image_path}")
                
                # Check file size
                file_size = os.path.getsize(image_path)
                logger.info(f"Image file size: {file_size} bytes")
                
                with open(image_path, 'rb') as img:
                    files = {
                        'source': img,
                    }
                    upload_payload = {
                        'access_token': self.access_token,
                        'published': 'false'
                    }
                    upload_url = f'https://graph.facebook.com/v23.0/{self.page_id}/photos'
                    
                    logger.info(f"Uploading image to: {upload_url}")
                    response = requests.post(upload_url, files=files, data=upload_payload, timeout=60)
                    
                    logger.info(f"Facebook image upload response status: {response.status_code}")
                    logger.debug(f"Facebook upload response headers: {dict(response.headers)}")
                    
                    response.raise_for_status()
                    upload_result = response.json()
                    photo_id = upload_result['id']
                    logger.info(f"Image uploaded successfully. Photo ID: {photo_id}")

                # Step 2: Create the main post with the uploaded image
                logger.info("Creating main Facebook post with uploaded image...")
                post_url = f'https://graph.facebook.com/v23.0/{self.page_id}/feed'
                post_payload = {
                    'access_token': self.access_token,
                    'message': message,
                    'attached_media': [{'media_fbid': photo_id}]
                }
                
                logger.info(f"Making post request to: {post_url}")
                post_response = requests.post(post_url, json=post_payload, timeout=30)
                
                logger.info(f"Facebook post response status: {post_response.status_code}")
                post_response.raise_for_status()
                
                post_result = post_response.json()
                post_id = post_result['id']
                logger.info(f"Post created successfully. Post ID: {post_id}")

            return post_id
            
        except requests.exceptions.Timeout:
            error_msg = "Facebook request timed out"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Facebook connection error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"Facebook HTTP error: {post_response.status_code if 'post_response' in locals() else 'Unknown'} - {post_response.text if 'post_response' in locals() else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Facebook posting error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_comment(self, post_id, comment_message):
        """
        Posts a comment to a specified Facebook post.
        Returns the ID of the new comment.
        """
        logger.info(f"Adding comment to Facebook post {post_id}, comment length: {len(comment_message)}")
        
        try:
            comment_url = f'https://graph.facebook.com/v23.0/{post_id}/comments'
            comment_payload = {
                'access_token': self.access_token,
                'message': comment_message
            }
            
            logger.info(f"Making comment request to: {comment_url}")
            comment_response = requests.post(comment_url, json=comment_payload, timeout=30)
            
            logger.info(f"Facebook comment response status: {comment_response.status_code}")
            comment_response.raise_for_status()
            
            comment_result = comment_response.json()
            comment_id = comment_result['id']
            logger.info(f"Comment posted successfully. Comment ID: {comment_id}")

            return comment_id
            
        except requests.exceptions.Timeout:
            error_msg = "Facebook comment request timed out"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Facebook comment connection error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"Facebook comment HTTP error: {comment_response.status_code if 'comment_response' in locals() else 'Unknown'} - {comment_response.text if 'comment_response' in locals() else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Facebook comment error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)