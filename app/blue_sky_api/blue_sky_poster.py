import grapheme
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BLUESKY_HANDLE = os.getenv("BSKY_HANDLE")  
BLUESKY_PASSWORD = os.getenv("BSKY_PASSWORD") 


class BlueskyPoster:
    def __init__(self, handle=BLUESKY_HANDLE, password=BLUESKY_PASSWORD):
        self.handle = handle
        self.password = password
        self.session = None

    def login(self):
        """Authenticate and get session tokens"""
        response = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.password},
        )
        response.raise_for_status()
        self.session = response.json()
        return self.session

    def upload_image(self, image_path):
        """Upload an image and return the blob reference"""
        if not self.session:
            raise Exception("Not logged in. Call login() first.")

        with open(image_path, "rb") as img:
            headers = {
                "Authorization": f"Bearer {self.session['accessJwt']}",
                "Content-Type": "image/jpeg",  # or "image/png"
            }
            response = requests.post(
                "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                headers=headers,
                data=img.read(),
            )
            response.raise_for_status()
            return response.json()["blob"]

    def post_image(self, image_path, message, app_url: str|None = None):
        """Post a skeet with image + text + url (optional)"""
        if not self.session:
            self.login()

        # Check the grapheme length and truncate if necessary
        if grapheme.length(message) > 150:
            # Truncate and add an ellipsis to show it was shortened
            message = grapheme.slice(message, end=150) + "..."
            
        if app_url:
            message = f"{message} {app_url}"

        blob = self.upload_image(image_path)

        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

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

        response = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {self.session['accessJwt']}"},
            json=payload,  
        )
        response.raise_for_status()
        return response.json()

