import os
from dotenv import load_dotenv
from imagekitio.client import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions



load_dotenv()

from ..config import IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT
 

class ImageKitUploader:
    def __init__(self):
        self.imagekit = ImageKit(
            private_key=IMAGEKIT_PRIVATE_KEY,
            public_key=IMAGEKIT_PUBLIC_KEY,
            url_endpoint=IMAGEKIT_URL_ENDPOINT
        )

    def upload_image(self, file_path, file_name, tags=None):
        try:
            with open(file_path, "rb") as file_to_upload:
                options = UploadFileRequestOptions(tags=tags or [])
                upload = self.imagekit.upload_file(
                    file=file_to_upload,
                    file_name=file_name,
                    options=options
                )
            if upload.response_metadata.http_status_code == 200:
                return upload.url
            else:
                print("Upload failed.")
                print(f"Error: {upload.response_metadata.raw}")
                return None
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
