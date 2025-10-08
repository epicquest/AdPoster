import base64
import hashlib
import os
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

import requests

from ..config import TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET

# Load from config
CLIENT_ID = TWITTER_CLIENT_ID
CLIENT_SECRET = TWITTER_CLIENT_SECRET  # only needed if you use client_secret_post
REDIRECT_URI = "http://127.0.0.1:8000/callback"
SCOPES = "tweet.read tweet.write users.read offline.access"

# Step 1: Generate code verifier + challenge
code_verifier = secrets.token_urlsafe(100)[:128]
code_challenge = (
    base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
    .rstrip(b"=")
    .decode("utf-8")
)

# Step 2: Build authorization URL
auth_url = "https://twitter.com/i/oauth2/authorize?" + urlencode(
    {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "random_state_123",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
)

print("👉 Open this URL in your browser and log in:\n")
print(auth_url, "\n")


# Step 3: Simple web server to catch callback
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "/callback" in self.path:
            query = self.path.split("?", 1)[-1]
            params = dict(qc.split("=") for qc in query.split("&"))
            auth_code = params.get("code")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")

            # Step 4: Exchange code for token
            token_url = "https://api.twitter.com/2/oauth2/token"
            data = {
                "client_id": CLIENT_ID,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
                "client_secret": CLIENT_SECRET,
            }

            response = requests.post(token_url, data=data)
            print("\n🔑 Token response:")
            print(response.json())

            # Save tokens
            with open("twitter_tokens.json", "w") as f:
                f.write(response.text)

            os._exit(0)


httpd = HTTPServer(("127.0.0.1", 8000), Handler)
httpd.serve_forever()
