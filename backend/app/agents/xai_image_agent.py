import requests
import os
import time
from io import BytesIO
from PIL import Image
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
    "Content-Type": "application/json"
}

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class XaiImageAgent:
    def run(self, topic: str):
        # Strong prompt optimized for editorial/news realism (Grok models love detailed prompts)
        positive_prompt = f"""
        Editorial news photograph of {topic}, 
        highly detailed documentary photography, candid real moment captured in the field, 
        natural outdoor/indoor lighting, soft realistic shadows, true-to-life colors and skin tones, 
        sharp focus, professional photojournalism style, shot on professional camera like Canon EOS R5, 
        50mm prime lens at f/2.8, ultra realistic, photorealistic, RAW quality, 8k detail, 
        no text overlays, no watermark, no logo, no signature, no artificial look
        """

        # Optional: negative prompt isn't directly supported, but you can include it in the prompt text
        # Grok usually respects "avoid: blurry, deformed, cartoon..." naturally

        payload = {
            "model": "grok-2-image",          # Current best image model (Flux/Aurora powered)
            "prompt": positive_prompt,
            "n": 1,                            # Number of images (1-10 allowed)
            "response_format": "url"           # Or "b64_json" for base64 data
        }

        response = requests.post(
            XAI_URL,
            headers=XAI_HEADERS,
            json=payload,
            timeout=120,
            verify=certifi.where(),
        )

        if response.status_code != 200:
            error_text = response.text
            raise RuntimeError(
                f"xAI API error {response.status_code}: {error_text}"
            )

        try:
            data = response.json()
            # Response structure: {"created": timestamp, "data": [{"url": "..."}]}
            image_url = data["data"][0]["url"]  # Temporary xAI-hosted URL
        except (KeyError, IndexError) as e:
            raise RuntimeError("Unexpected xAI response format") from e

        # Download the image from xAI's temporary URL
        img_response = requests.get(image_url, timeout=60)
        if img_response.status_code != 200:
            raise RuntimeError("Failed to download generated image from xAI")

        try:
            image = Image.open(BytesIO(img_response.content)).convert("RGB")
        except Exception as e:
            raise RuntimeError("Failed to decode image from xAI") from e

        # Optional subtle post-processing (sharpening)
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.12)

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_articles",
            public_id=f"article_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            overwrite=False,
            format="png",
            quality="auto:good"
        )

        return result["secure_url"]