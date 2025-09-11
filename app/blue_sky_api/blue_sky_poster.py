import grapheme
import requests
import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()

BLUESKY_HANDLE = os.getenv("BSKY_HANDLE")  
BLUESKY_PASSWORD = os.getenv("BSKY_PASSWORD") 

# Configure logging for BlueskyPoster
logger = logging.getLogger(__name__)


class BlueskyPoster:
    def __init__(self, handle=BLUESKY_HANDLE, password=BLUESKY_PASSWORD):
        self.handle = handle
        self.password = password
        self.session = None
        logger.info(f"BlueskyPoster initialized with handle: {self.handle}")

    def login(self):
        """Authenticate and get session tokens"""
        logger.info(f"Attempting to login to BlueSky with handle: {self.handle}")
        
        if not self.handle or not self.password:
            error_msg = f"Missing BlueSky credentials - Handle: {bool(self.handle)}, Password: {bool(self.password)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            response = requests.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={"identifier": self.handle, "password": self.password},
                timeout=30
            )
            
            logger.info(f"Login response status: {response.status_code}")
            logger.debug(f"Login response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            self.session = response.json()
            
            logger.info("Successfully logged in to BlueSky")
            logger.debug(f"Session DID: {self.session.get('did', 'N/A')}")
            
            return self.session
            
        except requests.exceptions.Timeout:
            error_msg = "Login request timed out (30s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error during login: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error during login: {response.status_code} - {response.text if 'response' in locals() else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during login: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def upload_image(self, image_path):
        """Upload an image and return the blob reference"""
        logger.info(f"Attempting to upload image: {image_path}")
        
        if not self.session:
            logger.error("No active session for image upload")
            raise Exception("Not logged in. Call login() first.")

        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Get file size
        file_size = os.path.getsize(image_path)
        logger.info(f"Image file size: {file_size} bytes")
        
        try:
            with open(image_path, "rb") as img:
                image_data = img.read()
                logger.debug(f"Read {len(image_data)} bytes from image file")
                
                # Determine content type based on file extension
                if image_path.lower().endswith('.png'):
                    content_type = "image/png"
                elif image_path.lower().endswith(('.jpg', '.jpeg')):
                    content_type = "image/jpeg"
                else:
                    content_type = "image/jpeg"  # default
                
                headers = {
                    "Authorization": f"Bearer {self.session['accessJwt']}",
                    "Content-Type": content_type,
                }
                
                logger.info(f"Uploading image with content-type: {content_type}")
                
                response = requests.post(
                    "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                    headers=headers,
                    data=image_data,
                    timeout=60  # 60 second timeout for image upload
                )
                
                logger.info(f"Image upload response status: {response.status_code}")
                logger.debug(f"Image upload response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                upload_result = response.json()
                
                logger.info("Image uploaded successfully to BlueSky")
                logger.debug(f"Upload result: {upload_result}")
                
                return upload_result["blob"]
                
        except requests.exceptions.Timeout:
            error_msg = "Image upload timed out (60s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error during image upload: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error during image upload: {response.status_code} - {response.text if 'response' in locals() else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during image upload: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_image(self, image_path, message, app_url: str|None = None):
        """Post a skeet with image + text + url (optional)"""
        logger.info(f"Starting BlueSky post creation with image: {image_path}")
        logger.info(f"Message length: {len(message)}, App URL: {app_url}")
        
        try:
            if not self.session:
                logger.info("No active session, attempting login...")
                self.login()

            # Check the grapheme length and truncate if necessary
            original_message = message
            if grapheme.length(message) > 150:
                # Truncate and add an ellipsis to show it was shortened
                message = grapheme.slice(message, end=150) + "..."
                logger.info(f"Message truncated from {grapheme.length(original_message)} to {grapheme.length(message)} characters")
                
            if app_url:
                message = f"{message} {app_url}"
                logger.info(f"Final message with URL: {len(message)} characters")

            logger.info("Uploading image to BlueSky...")
            blob = self.upload_image(image_path)
            
            now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
            logger.debug(f"Post timestamp: {now}")

            # Corrected payload structure: repo, collection, and record are top-level keys
            payload = {
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": {
                    "$type": "app.bsky.feed.post",
                    "text": message,
                    "createdAt": now,
                    "embed": {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            {
                                "alt": "Ad image",  # accessibility text
                                "image": blob,
                            }
                        ],
                    },
                },
            }

            logger.info("Creating BlueSky post...")
            logger.debug(f"Post payload: {payload}")

            response = requests.post(
                "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {self.session['accessJwt']}"},
                json=payload,
                timeout=30
            )
            
            logger.info(f"Post creation response status: {response.status_code}")
            logger.debug(f"Post creation response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            post_result = response.json()
            
            logger.info(f"Post created successfully on BlueSky: {post_result}")
            print(f"Post created successfully. : {post_result}")
            
            return post_result
            
        except requests.exceptions.Timeout:
            error_msg = "Post creation timed out (30s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error during post creation: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error during post creation: {response.status_code} - {response.text if 'response' in locals() else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during post creation: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

