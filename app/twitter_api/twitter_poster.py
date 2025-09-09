import os
import tweepy
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")

class TwitterPoster:
    def __init__(self,
                access_token: str = TWITTER_ACCESS_TOKEN,
                access_token_secret: str = TWITTER_ACCESS_TOKEN_SECRET,
                api_key: str = TWITTER_API_KEY,
                api_key_secret: str = TWITTER_API_KEY_SECRET):

        # Tweepy client for Twitter API v2 endpoints (for posting tweets)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Tweepy API for Twitter API v1.1 endpoints (for media upload)
        # auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
        # self.api = tweepy.API(auth)


    def _post_image_and_tweet(self, image_path, message, reply_message=None, app_url: str | None = None):
        media_id = self.upload_image(image_path)
        tweet_id = self.post_tweet_with_image(message, media_id)

        if reply_message is None and app_url:
            reply_message = f"Get the app on Google Play: {app_url}"

        if reply_message:
            self.reply_to_tweet(tweet_id, reply_message)

        return tweet_id

    def upload_image(self, image_path):
        """
        Uploads an image to Twitter using v1.1 endpoint (via Tweepy API).
        """
        try:
            # The tweepy.API object handles the OAuth1 logic internally
            media = self.api.media_upload(image_path)
            media_id = media.media_id_string
            print(f"Image uploaded successfully. Media ID: {media_id}")
            return media_id
        except tweepy.errors.TweepyException as e:
            print(f"Error uploading image: {e}")
            raise

    def post_tweet_with_image(self, message, media_id=None):
        """
        Posts a tweet with optional media using v2 endpoint (via Tweepy Client).
        """
        try:
            if media_id:
                # The tweepy.Client handles the media_ids list correctly
                response = self.client.create_tweet(text=message, media_ids=[media_id])
            else:
                response = self.client.create_tweet(text=message)

            tweet_id = response.data["id"]
            print(f"Tweet posted successfully. Tweet ID: {tweet_id}")
            return tweet_id
        except tweepy.errors.TweepyException as e:
            print(f"Error posting tweet: {e}")
            raise

    def reply_to_tweet(self, tweet_id, message):
        """
        Replies to an existing tweet using v2 endpoint.
        """
        try:
            response = self.client.create_tweet(
                text=message,
                in_reply_to_tweet_id=tweet_id
            )
            reply_id = response.data["id"]
            print(f"Reply posted successfully. Reply ID: {reply_id}")
            return reply_id
        except tweepy.errors.TweepyException as e:
            print(f"Error replying to tweet: {e}")
            raise

    def post_text_and_link(self, message: str, app_url: Optional[str] = None):
        """
        Posts a text-only tweet, with an optional URL appended to the message.
        """
        full_message = message
        if app_url:
            # You can add the URL directly to the message. Twitter will
            # automatically shorten it and handle the rich media preview.
            full_message = f"{message}\n\n{app_url}"

        # tweet_id = self._post_tweet(full_message)
        tweet_id = self._post_tweet(message=message)

        return tweet_id

    def _post_tweet(self, message: str):
        """
        Posts a text-only tweet using v2 endpoint (via Tweepy Client).
        """
        try:
            # The tweepy.Client handles the text-only tweet perfectly.
            response = self.client.create_tweet(text=message)

            tweet_id = response.data["id"]
            print(f"Tweet posted successfully. Tweet ID: {tweet_id}")
            return tweet_id
        except tweepy.errors.TweepyException as e:
            print(f"Error posting tweet: {e}")
            raise