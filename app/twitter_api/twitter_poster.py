import os
import tweepy
import logging
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")

# Configure logging for TwitterPoster
logger = logging.getLogger(__name__)

class TwitterPoster:
    def __init__(self,
                access_token: str = TWITTER_ACCESS_TOKEN,
                access_token_secret: str = TWITTER_ACCESS_TOKEN_SECRET,
                api_key: str = TWITTER_API_KEY,
                api_key_secret: str = TWITTER_API_KEY_SECRET):

        logger.info(f"TwitterPoster initializing with credentials - API Key: {bool(api_key)}, Access Token: {bool(access_token)}")
        
        if not all([access_token, access_token_secret, api_key, api_key_secret]):
            error_msg = f"Missing Twitter credentials - API Key: {bool(api_key)}, API Secret: {bool(api_key_secret)}, Access Token: {bool(access_token)}, Access Secret: {bool(access_token_secret)}"
            logger.error(error_msg)
            raise Exception(error_msg)

        try:
            # Tweepy client for Twitter API v2 endpoints (for posting tweets)
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_key_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Tweepy API for Twitter API v1.1 endpoints (for media upload)
            auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
            self.api = tweepy.API(auth)
            
            logger.info("TwitterPoster initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize Twitter API clients: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


    def _post_image_and_tweet(self, image_path, message, reply_message=None, app_url: str | None = None):
        logger.info(f"Starting Twitter image post - Image: {image_path}, Message length: {len(message) if message else 0}")
        
        try:
            media_id = self.upload_image(image_path)
            tweet_id = self.post_tweet_with_image(message, media_id)

            if reply_message is None and app_url:
                reply_message = f"Get the app on Google Play: {app_url}"

            if reply_message:
                logger.info("Adding reply to Twitter tweet...")
                self.reply_to_tweet(tweet_id, reply_message)

            return tweet_id
            
        except Exception as e:
            error_msg = f"Error in Twitter _post_image_and_tweet: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def upload_image(self, image_path):
        """
        Uploads an image to Twitter using v1.1 endpoint (via Tweepy API).
        """
        logger.info(f"Uploading image to Twitter: {image_path}")
        
        if not os.path.exists(image_path):
            error_msg = f"Twitter image file not found: {image_path}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Check file size
        file_size = os.path.getsize(image_path)
        logger.info(f"Twitter image file size: {file_size} bytes")
        
        try:
            # The tweepy.API object handles the OAuth1 logic internally
            logger.info("Making Twitter media upload request...")
            media = self.api.media_upload(image_path)
            media_id = media.media_id_string
            logger.info(f"Twitter image uploaded successfully. Media ID: {media_id}")
            print(f"Image uploaded successfully. Media ID: {media_id}")
            return media_id
            
        except tweepy.errors.TweepyException as e:
            error_msg = f"Twitter image upload error: {str(e)}"
            logger.error(error_msg)
            print(f"Error uploading image: {e}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Twitter image upload error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_tweet_with_image(self, message, media_id=None):
        """
        Posts a tweet with optional media using v2 endpoint (via Tweepy Client).
        """
        logger.info(f"Creating Twitter tweet with image - Message length: {len(message) if message else 0}, Has media: {bool(media_id)}")
        
        try:
            logger.info("Making Twitter tweet creation request...")
            if media_id:
                # The tweepy.Client handles the media_ids list correctly
                response = self.client.create_tweet(text=message, media_ids=[media_id])
            else:
                response = self.client.create_tweet(text=message)

            tweet_id = response.data["id"]
            logger.info(f"Twitter tweet posted successfully. Tweet ID: {tweet_id}")
            print(f"Tweet posted successfully. Tweet ID: {tweet_id}")
            return tweet_id
            
        except tweepy.errors.TweepyException as e:
            error_msg = f"Twitter tweet creation error: {str(e)}"
            logger.error(error_msg)
            print(f"Error posting tweet: {e}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Twitter tweet creation error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def reply_to_tweet(self, tweet_id, message):
        """
        Replies to an existing tweet using v2 endpoint.
        """
        logger.info(f"Creating Twitter reply to tweet {tweet_id}, message length: {len(message)}")
        
        try:
            logger.info("Making Twitter reply request...")
            response = self.client.create_tweet(
                text=message,
                in_reply_to_tweet_id=tweet_id
            )
            reply_id = response.data["id"]
            logger.info(f"Twitter reply posted successfully. Reply ID: {reply_id}")
            print(f"Reply posted successfully. Reply ID: {reply_id}")
            return reply_id
            
        except tweepy.errors.TweepyException as e:
            error_msg = f"Twitter reply creation error: {str(e)}"
            logger.error(error_msg)
            print(f"Error replying to tweet: {e}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Twitter reply error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_text_and_link(self, message: str, app_url: Optional[str] = None):
        """
        Posts a text-only tweet, with an optional URL appended to the message.
        """
        logger.info(f"Creating Twitter text post - Message length: {len(message)}, Has app URL: {bool(app_url)}")
        
        try:
            full_message = message
            if app_url:
                # You can add the URL directly to the message. Twitter will
                # automatically shorten it and handle the rich media preview.
                full_message = f"{message}\n\n{app_url}"
                logger.info(f"Added app URL to Twitter message, final length: {len(full_message)}")

            # Use the message with URL for posting
            tweet_id = self._post_tweet(message=full_message)

            return tweet_id
            
        except Exception as e:
            error_msg = f"Error in Twitter post_text_and_link: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _post_tweet(self, message: str):
        """
        Posts a text-only tweet using v2 endpoint (via Tweepy Client).
        """
        logger.info(f"Creating Twitter text-only tweet - Message length: {len(message)}")
        
        try:
            # The tweepy.Client handles the text-only tweet perfectly.
            logger.info("Making Twitter text tweet request...")
            response = self.client.create_tweet(text=message)

            tweet_id = response.data["id"]
            logger.info(f"Twitter text tweet posted successfully. Tweet ID: {tweet_id}")
            print(f"Tweet posted successfully. Tweet ID: {tweet_id}")
            return tweet_id
            
        except tweepy.errors.TweepyException as e:
            error_msg = f"Twitter text tweet error: {str(e)}"
            logger.error(error_msg)
            print(f"Error posting tweet: {e}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Twitter text tweet error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)