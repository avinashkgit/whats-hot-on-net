import requests
import os
import time
from io import BytesIO
from PIL import Image, ImageEnhance
import cloudinary
import cloudinary.uploader
from datetime import datetime, timezone
from dotenv import load_dotenv
import certifi

load_dotenv()

# xAI Image Generation Endpoint (stable as of Jan 2026)
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
    def run(self, topic: str, retries: int = 2) -> str:
        """
        Generate a realistic news-style environmental/documentary photo using xAI Aurora,
        process lightly, upload to Cloudinary and return the permanent URL.
        """
        # Ultra-realistic documentary prompt - optimized for wide scenes & zero humans
        positive_prompt = f"""
        Wide establishing shot, long environmental scene, pure breaking news / documentary photograph of {topic}, 
        focus exclusively on objects, setting, atmosphere, aftermath, scattered items, equipment, displays, 
        ingredients, stadium setup, stage elements — story told through environment only

        Shot on location Canon EOS R5 Mark II or Sony A1 II, 24-28mm wide-angle lens, f/8–f/11 deep DoF, 
        tack-sharp across entire frame, natural perspective with mild wide-angle character

        Strictly available light, authentic time-of-day lighting, real shadows/highlights, imperfect color balance, 
        subtle organic grain like scanned film, maximum photorealistic detail, RAW look

        ABSOLUTELY NO: people, humans, figures, silhouettes, bodies, faces, crowds, any human presence whatsoever, 
        text, watermark, logo, signature, plastic surfaces, perfect symmetry, glamour/studio lighting, 
        artificial bokeh, HDR, over-sharpening, AI smoothness, beauty filters, close-ups, portraits — 
        100% environment/objects as sole subject, maximum documentary realism
        """

        payload = {
            "model": "grok-2-image-1212",  # Current stable & versioned model name (Jan 2026)
            "prompt": positive_prompt.strip(),
            "n": 1,
            "response_format": "url",  # returns temporary URL (expires ~1h)
        }

        attempt = 0
        while attempt < retries:
            try:
                response = requests.post(
                    XAI_URL,
                    headers=XAI_HEADERS,
                    json=payload,
                    timeout=120,
                    verify=certifi.where(),
                )
                response.raise_for_status()
                break

            except requests.HTTPError as e:
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = 10 * (2 ** attempt)  # exponential backoff
                    print(f"xAI rate limit/server error → retry in {wait}s (attempt {attempt+1}/{retries})")
                    time.sleep(wait)
                    attempt += 1
                    continue
                raise RuntimeError(f"xAI API error {response.status_code}: {response.text}") from e

            except requests.RequestException as e:
                raise RuntimeError(f"xAI request failed: {str(e)}") from e

        else:
            raise RuntimeError("Max retries exceeded for xAI image generation")

        # Parse temporary image URL
        try:
            data = response.json()
            image_url = data["data"][0]["url"]
        except Exception as e:
            raise RuntimeError("Failed to extract image URL from xAI response") from e

        # Download
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()

        # Process
        image = Image.open(BytesIO(img_response.content)).convert("RGB")
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.08)  # subtle, natural look

        # Save as high-quality JPEG (better compression & compatibility for news photos)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=93, optimize=True, progressive=True)
        buffer.seek(0)

        # Upload with better naming & tags
        try:
            safe_topic = topic.lower().replace(" ", "_")[:50]  # truncate for safety
            public_id = f"news_{safe_topic}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

            result = cloudinary.uploader.upload(
                buffer,
                folder="ai_news_images",
                public_id=public_id,
                overwrite=False,
                resource_type="image",
                format="jpg",
                quality="auto:good",
                tags=["ai-generated", "photojournalism", "xai-aurora", "documentary"],
            )
            return result["secure_url"]

        except Exception as e:
            raise RuntimeError(f"Cloudinary upload failed: {str(e)}") from e