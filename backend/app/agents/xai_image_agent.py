import requests
import os
import time
from io import BytesIO
from PIL import Image, ImageEnhance
import cloudinary
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
import certifi

load_dotenv()

# xAI Image Generation Endpoint (January 2026)
XAI_URL = "https://api.x.ai/v1/images/generations"

XAI_HEADERS = {
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
    "Content-Type": "application/json",
}

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class XaiImageAgent:
    def run(self, topic: str) -> str:
        """
        Generate a realistic news-style photo using xAI's image model,
        process it lightly, upload to Cloudinary and return the final URL.

        Returns:
            str: Secure Cloudinary URL of the uploaded image
        """
        # Highly optimized prompt for documentary/photojournalism realism (Aurora excels with this style)
        positive_prompt = f"""
        Wide establishing shot / long wide shot / environmental scene, genuine breaking news / documentary photograph of {topic}, focusing entirely on objects, setting, environment and aftermath, detailed scene description e.g. scattered items / equipment / displays / ingredients / stadium / stage setup, real world photojournalism style, caught in the moment, observed not directed, story told through things and context only

        Shot on location with Canon EOS R5 Mark II / Sony A1 II, 24mm or 28mm wide-angle lens, f/5.6–f/11 for deep depth of field, sharp focus throughout the scene, natural lens character and slight edge distortion

        Available light only, realistic lighting conditions matching the time of day or atmosphere, authentic shadows, highlights, true-to-life color balance, subtle imperfect white balance

        RAW quality, maximum realistic detail, subtle organic film-like grain, no digital smoothness or artificial perfection

        STRICTLY NO: text, watermark, logo, signature, people, humans, figures, silhouettes, bodies, faces, crowds, pedestrians, any human presence, plastic surfaces, perfect symmetry, glamour lighting, studio look, artificial bokeh, over-sharpening, HDR look, AI smoothness, beauty effects, close-up, portrait, headshot, tight crop — maximum documentary realism, environment/objects as the sole subject
        """

        payload = {
            "model": "grok-2-image-1212",  # Fixed: This is the correct & stable model name in Jan 2026
            "prompt": positive_prompt,
            "n": 1,
            "response_format": "url",
        }

        # Generate image with xAI
        try:
            response = requests.post(
                XAI_URL,
                headers=XAI_HEADERS,
                json=payload,
                timeout=120,
                verify=certifi.where(),
            )
            response.raise_for_status()  # Raises exception for 4xx/5xx
        except requests.RequestException as e:
            raise RuntimeError(f"xAI API request failed: {str(e)}") from e

        if response.status_code != 200:
            error_text = response.text
            raise RuntimeError(f"xAI API error {response.status_code}: {error_text}")

        # Parse response
        try:
            data = response.json()
            if "data" not in data or not data["data"] or "url" not in data["data"][0]:
                raise RuntimeError(
                    "Unexpected xAI response format - no image URL found"
                )
            image_url = data["data"][0][
                "url"
            ]  # Temporary xAI-hosted URL (usually expires in ~1h)
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError("Failed to parse xAI image URL from response") from e

        # Download the generated image
        try:
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download image from xAI: {str(e)}") from e

        # Open and process image
        try:
            image = Image.open(BytesIO(img_response.content)).convert("RGB")

            # Very light sharpening (photojournalism usually looks best subtle)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.08)  # Reduced from 1.12 → more natural
        except Exception as e:
            raise RuntimeError(f"Failed to process image: {str(e)}") from e

        # Prepare buffer for upload (save as high-quality JPEG - better for photos)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=92, optimize=True, progressive=True)
        buffer.seek(0)

        # Upload to Cloudinary with meaningful naming
        try:
            public_id = f"news_{topic.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            result = cloudinary.uploader.upload(
                buffer,
                folder="ai_news_images",
                public_id=public_id,
                overwrite=False,
                resource_type="image",
                format="jpg",
                quality="auto:good",
                tags=["ai-generated", "photojournalism", "xai-aurora"],
            )

            return result["secure_url"]

        except Exception as e:
            raise RuntimeError(f"Cloudinary upload failed: {str(e)}") from e
