
import json
import os
from blue_sky_api.blue_sky_poster import BlueskyPoster


poster = BlueskyPoster()
 
# image_path = "output/ads_facebook_20250904_170441.png"
ads_json_path = "output/ads_20250909_160647.json"


with open(ads_json_path, "r") as f:
    ads_data = json.load(f)

body_text = ads_data.get("bluesky", {}).get("body_text")
image_path = ads_data.get("bluesky", {}).get("image_path")
play_store_url = ads_data.get("bluesky", {}).get("play_store_url")
if (not image_path) or (not os.path.exists(image_path)):
    print("No valid image path found for Bluesky post.")
    exit(1)
result = poster.post_image(image_path, body_text, play_store_url)
print(result)
