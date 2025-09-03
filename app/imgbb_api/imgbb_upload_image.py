import os
import requests
from dotenv import load_dotenv

load_dotenv()

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

def upload_to_imgbb(image_path) -> str:
    with open(image_path, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
        }
        files = {
            "image": file,
        }
        response = requests.post(url, data=payload, files=files)
        response.raise_for_status()
        return response.json()["data"]["url"]



