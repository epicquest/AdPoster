
import json
import os

from imagekit_api.imagekit_upload_image import ImageKitUploader
from imgbb_api.imgbb_upload_image import upload_to_imgbb
from instagram_api.instagram_poster import InstagramPoster



iposter = InstagramPoster()
ads_json_path = "output/ads_20250909_155354.json"

with open(ads_json_path, "r") as f:
    ads_data = json.load(f)

body_text = ads_data.get("instagram", {}).get("body_text")
image_path = ads_data.get("instagram", {}).get("image_path")
if (not image_path) or (not os.path.exists(image_path)):
    print("No valid image path found for Iinstagram post.")
    exit(1)
# link = upload_to_imgbb(image_path)
#link="https://i.ibb.co/xKdmZGcY/ads-20250902-175015.png"
# link="https://www.dafont.com/img/illustration/k/e/keep_calm.png"
# link="https://ik.imagekit.io/z9w2fm5s2/uploaded_image_hKt38txoz.jpg"
# iposter.post_image(link, body_text)
uploader = ImageKitUploader()
uploaded_url = uploader.upload_image(image_path, "uploaded_image.jpg", tags=["ads", "upload"])
if uploaded_url:
    print("Image uploaded successfully. URL:", uploaded_url)
    iposter.post_image(uploaded_url, body_text)
else:
    print("Image upload failed.")
