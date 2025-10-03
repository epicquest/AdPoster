import os
import tweepy
from typing import Optional
import datetime

from ..config import TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_API_KEY, TWITTER_API_KEY_SECRET

class TwitterPoster:
    def __init__(self,
                 access_token: str = TWITTER_ACCESS_TOKEN,
                 access_token_secret: str = TWITTER_ACCESS_TOKEN_SECRET,
                 api_key: str = TWITTER_API_KEY,
                 api_key_secret: str = TWITTER_API_KEY_SECRET):
        
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

    def post_unique_text_tweet(self, message: str):
        """
        Posts a simple, unique text tweet to test permissions.
        """
        # Add a unique timestamp to avoid duplicate tweet errors
        unique_message = f"{message} (Test at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        
        try:
            print(f"Attempting to post: '{unique_message}'")
            response = self.client.create_tweet(text=unique_message)
            tweet_id = response.data["id"]
            print(f"Tweet posted successfully. Tweet ID: {tweet_id}")
            return tweet_id
        except tweepy.errors.TweepyException as e:
            print(f"Error posting tweet: {e}")
            raise

# Example usage of the final test script:
if __name__ == "__main__":
    poster = TwitterPoster()
    
    body_text = "This is a basic test tweet."
    
    try:
        result_id = poster.post_unique_text_tweet(body_text)
        print(f"Final tweet ID: {result_id}")
    except Exception as e:
        print(f"An error occurred: {e}")