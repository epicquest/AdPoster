
import json
import os

from facebook_api.facebook_poster import FacebookPoster

#https://graph.facebook.com/v23.0/me/accounts?access_token={your-user-access-token}

fposter = FacebookPoster()
image_path = "output/ads_facebook_20250904_170441.png"
ads_json_path = "output/ads_20250904_170453.json"

with open(ads_json_path, "r") as f:
    ads_data = json.load(f)

body_text = ads_data.get("facebook", {}).get("body_text", "Check out our new ad!")
fposter.post_image(image_path, body_text)