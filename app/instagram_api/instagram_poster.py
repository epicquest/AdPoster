import logging

import requests

from ..config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

# Configure logging for InstagramPoster
logger = logging.getLogger(__name__)


class InstagramPoster:
    def __init__(
        self, ig_user_id=INSTAGRAM_ACCOUNT_ID, access_token=INSTAGRAM_ACCESS_TOKEN
    ):
        self.ig_user_id = ig_user_id
        self.access_token = access_token
        logger.info(
            f"InstagramPoster initialized with user_id: {bool(self.ig_user_id)}, "
            f"access_token: {bool(self.access_token)}"
        )

    def post_image(self, image_url, caption):
        logger.info(
            f"Starting Instagram post with image URL: {image_url}, "
            f"caption length: {len(caption) if caption else 0}"
        )

        if not self.ig_user_id or not self.access_token:
            error_msg = (
                f"Missing Instagram credentials - User ID: {bool(self.ig_user_id)}, "
                f"Access Token: {bool(self.access_token)}"
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        try:
            # Step 1: Create media container
            logger.info("Creating Instagram media container...")
            create_url = f"https://graph.facebook.com/v23.0/{self.ig_user_id}/media"
            payload = {
                "image_url": image_url,  # must be a public URL
                "caption": caption,
                "access_token": self.access_token,
            }

            logger.info(f"Making media creation request to: {create_url}")
            logger.debug(
                f"Media creation payload: {{'image_url': '{image_url}', "
                f"'caption_length': {len(caption)}, 'access_token': '[HIDDEN]'}}"
            )

            response = requests.post(create_url, data=payload, timeout=30)

            logger.info(
                f"Instagram media creation response status: {response.status_code}"
            )
            logger.debug(
                f"Instagram creation response headers: {dict(response.headers)}"
            )

            response.raise_for_status()
            creation_result = response.json()
            creation_id = creation_result["id"]
            logger.info(f"Media container created successfully with ID: {creation_id}")

            # Step 2: Publish media
            logger.info("Publishing Instagram media...")
            publish_url = (
                f"https://graph.facebook.com/v23.0/{self.ig_user_id}/media_publish"
            )
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token,
            }

            logger.info(f"Making media publish request to: {publish_url}")
            publish_response = requests.post(
                publish_url, data=publish_payload, timeout=30
            )

            logger.info(
                f"Instagram media publish response status: "
                f"{publish_response.status_code}"
            )
            publish_response.raise_for_status()

            result = publish_response.json()
            logger.info(f"Instagram post published successfully: {result}")
            print(f"Posting image to Instagram: {result}")

            return result

        except requests.exceptions.Timeout:
            error_msg = "Instagram request timed out"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Instagram connection error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.HTTPError:
            response_text = ""
            if "response" in locals():
                response_text = response.text
            elif "publish_response" in locals():
                response_text = publish_response.text
            status_code = (
                response.status_code
                if "response" in locals()
                else (
                    publish_response.status_code
                    if "publish_response" in locals()
                    else "Unknown"
                )
            )
            error_msg = f"Instagram HTTP error: {status_code} - {response_text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected Instagram posting error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def post_image_fake(self, image_path, caption):
        logger.info(
            f"FAKE Instagram post - Image: {image_path}, "
            f"Caption length: {len(caption) if caption else 0}"
        )
        print(f"Posting image to Instagram: {image_path}")
        print(f"Caption: {caption}")
