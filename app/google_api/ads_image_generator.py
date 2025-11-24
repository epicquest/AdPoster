import io
from datetime import datetime
from pathlib import Path

import google.genai as genai
from google.genai import types
from PIL import Image

from ..config import PLATFORM_SETTINGS


class AdImageGenerator:
    def __init__(self, api_key: str, model: str = "imagen-4.0-generate-001"):
        self.gemini_api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.gemini_api_key)

    def _compress_image(self, img: Image.Image, max_size_kb: int, filepath: Path):
        """Compress image under the given size limit (KB)."""
        quality = 95
        while quality > 10:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                buffer.seek(0)
                with open(filepath, "wb") as f:
                    f.write(buffer.read())
                return True
            quality -= 5
        return False

    def generate_image_from_text(
        self,
        platform: str,
        prompt: str,
        output_dir: str,
        output_filename: str = None,
    ) -> str:
        """
        Generate a platform-optimized advertisement image.

        Args:
            platform (str): The target platform (must exist in PLATFORM_SETTINGS).
            prompt (str): Base description of the ad image.
            output_dir (str): Directory to save the generated image.
            output_filename (str, optional): Custom filename. Defaults to timestamp.
        """
        try:
            # Get platform-specific settings
            settings = PLATFORM_SETTINGS.get(platform, {})
            aspect_ratio = settings.get("aspect_ratio", "16:9")
            tone = settings.get("tone", "")
            style = settings.get("style", "")
            optimal_size = settings.get("optimal_image_size", None)
            max_filesize_kb = settings.get("max_image_filesize_kb", None)

            # Refine prompt with tone & style
            refined_prompt = (
                f"{prompt}. Style: {style}. Tone: {tone}. "
                f"Modern, high-quality ad creative, visually striking, "
                f"no text, no labels, no captions."
            )

            # Create output directory
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{platform}_ads_{timestamp}.jpg"  # JPEG compressible

            filepath = output_dir / output_filename

            # Generate image with Gemini
            response = self.client.models.generate_images(
                model=self.model,
                prompt=refined_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                ),
            )

            if not response.generated_images:
                print("❌ No image was generated. Try refining your prompt.")
                return None

            # Extract image
            image_data = response.generated_images[0].image.image_bytes
            img = Image.open(io.BytesIO(image_data))

            # Resize to platform optimal size if available
            if optimal_size:
                img = img.resize(optimal_size, Image.LANCZOS)

            # Save with compression if Bluesky or size-limited
            if max_filesize_kb:
                if not self._compress_image(img, max_filesize_kb, filepath):
                    print(f"⚠️ Could not compress image below {max_filesize_kb} KB.")
                    return None
            else:
                img.save(filepath, format="JPEG", quality=95)

            print(f"✅ Success! Image saved at {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"⚠️ Error while generating image: {e}")
            return None
