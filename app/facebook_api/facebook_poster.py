"""
Facebook API poster module.

This module handles posting advertisements to Facebook.
"""

import logging
import os

import requests

from ..config import FB_ACCESS_TOKEN, FB_PAGE_ID

# Configure logging for FacebookPoster
logger = logging.getLogger(__name__)


class FacebookPoster:
    """
    Facebook poster class.

    Handles posting content to Facebook pages.
    """

    def __init__(self, page_id=FB_PAGE_ID, access_token=FB_ACCESS_TOKEN):
        """
        Initialize the Facebook poster.

        Args:
            page_id: Facebook page ID
            access_token: Facebook access token
        """
        self.page_id = page_id
        self.access_token = access_token
        logger.info(
            "FacebookPoster initialized with page_id: %s, access_token: %s",
            bool(self.page_id),
            bool(self.access_token)
        )

    def post_image_and_comment(
        self,
        image_path: str | None,
        message,
        comment_message=None,
        app_url: str | None = None,
    ):
        """
        Post an image and comment to Facebook.

        Args:
            image_path: Path to the image file
            message: Post message
            comment_message: Comment message
            app_url: App URL
        """
        logger.info(
            "Starting Facebook post with image: %s, message length: %s",
            image_path,
            len(message) if message else 0
        )

        if not self.page_id or not self.access_token:
            error_msg = (
                f"Missing Facebook credentials - Page ID: {bool(self.page_id)}, "
                f"Access Token: {bool(self.access_token)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            post_id = self.post_image(image_path, message)
            logger.info("Main Facebook post created successfully with ID: %s", post_id)

            if comment_message is None:
                if app_url:
                    comment_message = f"Get the app on Google Play: {app_url}"

            if comment_message:
                logger.info("Adding comment to Facebook post...")
                comment_id = self.post_comment(post_id, comment_message)
                logger.info("Comment added successfully with ID: %s", comment_id)

            return {
                "post_id": post_id,
                "comment_id": comment_id if comment_message else None,
            }

        except Exception as e:
            error_msg = f"Error in Facebook post_image_and_comment: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def post_image(self, image_path: str | None, message):
        """
        Posts an image and text to the Facebook page.
        Returns the ID of the new post.
        """
        logger.info(
            "Creating Facebook post - Has image: %s, Message length: %s",
            bool(image_path),
            len(message) if message else 0
        )

        try:
            if image_path is None or not os.path.exists(image_path):
                # No media file, post just the text
                logger.info("Posting text-only content to Facebook")
                post_url = f"https://graph.facebook.com/v23.0/{self.page_id}/feed"
                post_payload = {"access_token": self.access_token, "message": message}

                logger.info("Making text post request to: %s", post_url)
                post_response = requests.post(post_url, json=post_payload, timeout=30)

                logger.info(
                    "Facebook text post response status: %s",
                    post_response.status_code
                )
                post_response.raise_for_status()

                post_result = post_response.json()
                post_id = post_result["id"]
                logger.info("Text post created successfully. Post ID: %s", post_id)

            else:
                # Step 1: Upload the image and get its ID
                logger.info("Uploading image to Facebook: %s", image_path)

                # Check file size
                file_size = os.path.getsize(image_path)
                logger.info("Image file size: %s bytes", file_size)

                with open(image_path, "rb") as img:
                    files = {
                        "source": img,
                    }
                    upload_payload = {
                        "access_token": self.access_token,
                        "published": "false",
                    }
                    upload_url = (
                        f"https://graph.facebook.com/v23.0/{self.page_id}/photos"
                    )

                    logger.info("Uploading image to: %s", upload_url)
                    response = requests.post(
                        upload_url, files=files, data=upload_payload, timeout=60
                    )

                    logger.info(
                        "Facebook image upload response status: %s",
                        response.status_code
                    )
                    logger.debug(
                        "Facebook upload response headers: %s",
                        dict(response.headers)
                    )

                    response.raise_for_status()
                    upload_result = response.json()
                    photo_id = upload_result["id"]
                    logger.info("Image uploaded successfully. Photo ID: %s", photo_id)

                # Step 2: Create the main post with the uploaded image
                logger.info("Creating main Facebook post with uploaded image...")
                post_url = f"https://graph.facebook.com/v23.0/{self.page_id}/feed"
                post_payload = {
                    "access_token": self.access_token,
                    "message": message,
                    "attached_media": [{"media_fbid": photo_id}],
                }

                logger.info("Making post request to: %s", post_url)
                post_response = requests.post(post_url, json=post_payload, timeout=30)

                logger.info(
                    "Facebook post response status: %s",
                    post_response.status_code
                )
                post_response.raise_for_status()

                post_result = post_response.json()
                post_id = post_result["id"]
                logger.info("Post created successfully. Post ID: %s", post_id)

            return post_id

        except requests.exceptions.Timeout:
            error_msg = "Facebook request timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.ConnectionError as exc:
            error_msg = f"Facebook connection error: {str(exc)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
        except requests.exceptions.HTTPError as exc:
            error_msg = (
                f"Facebook HTTP error: "
                f"{post_response.status_code if 'post_response' in locals() else 'Unknown'} "
                f"- {post_response.text if 'post_response' in locals() else str(exc)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
        except Exception as exc:
            error_msg = f"Unexpected Facebook posting error: {str(exc)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc

    def post_comment(self, post_id, comment_message):
        """
        Posts a comment to a specified Facebook post.
        Returns the ID of the new comment.
        """
        logger.info(
            "Adding comment to Facebook post %s, comment length: %s",
            post_id,
            len(comment_message)
        )

        try:
            comment_url = f"https://graph.facebook.com/v23.0/{post_id}/comments"
            comment_payload = {
                "access_token": self.access_token,
                "message": comment_message,
            }

            logger.info("Making comment request to: %s", comment_url)
            comment_response = requests.post(
                comment_url, json=comment_payload, timeout=30
            )

            logger.info(
                "Facebook comment response status: %s",
                comment_response.status_code
            )
            comment_response.raise_for_status()

            comment_result = comment_response.json()
            comment_id = comment_result["id"]
            logger.info("Comment posted successfully. Comment ID: %s", comment_id)

            return comment_id

        except requests.exceptions.Timeout:
            error_msg = "Facebook comment request timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.ConnectionError as exc:
            error_msg = f"Facebook comment connection error: {str(exc)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
        except requests.exceptions.HTTPError as exc:
            error_msg = (
                f"Facebook comment HTTP error: "
                f"{comment_response.text if 'comment_response' in locals() else str(exc)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
        except Exception as exc:
            error_msg = f"Unexpected Facebook comment error: {str(exc)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
