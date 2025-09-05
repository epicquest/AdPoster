
import json
import os

from facebook_api.facebook_poster import FacebookPoster


#https://graph.facebook.com/v23.0/me/accounts?access_token={your-user-access-token}

fposter = FacebookPoster()
ads_json_path = "output/ads_20250905_181928.json"

with open(ads_json_path, "r") as f:
    ads_data = json.load(f)

body_text = ads_data.get("facebook", {}).get("body_text", "Check out our new ad!")

image_path = ads_data.get("facebook", {}).get("image_path")

play_store_url = ads_data.get("facebook", {}).get("play_store_url")
if (not image_path) or (not os.path.exists(image_path)):
    print("No valid image path found for Facebook post.")
    exit(1)
# fposter.post_image(image_path, body_text)
fposter.post_image_and_comment(image_path, body_text, app_url=play_store_url)