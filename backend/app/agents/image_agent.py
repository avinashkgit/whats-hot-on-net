import os
import time
from io import BytesIO
from PIL import Image, ImageEnhance
import cloudinary
import cloudinary.uploader
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import certifi
from huggingface_hub import InferenceClient, InferenceTimeoutError
from huggingface_hub.errors import HfHubHTTPError

load_dotenv()

# Hugging Face Inference Client
HF_CLIENT = InferenceClient(
    api_key=os.environ.get("HF_TOKEN"),
)

# xAI API setup
XAI_URL = "https://api.x.ai/v1/images/generations"
XAI_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('XAI_API_KEY')}",
    "Content-Type": "application/json",
}

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class ImageAgent:
    def run(self, topic: str) -> tuple[str, str]:
        """
        Generates landscape news-style image.
        Primary: FLUX.1-schnell (Hugging Face)
        Fallback: xAI Grok image generation

        Returns:
            tuple: (permanent_cloudinary_url: str, model_name: str)
        """
        prompt = f"""
        16:9 LANDSCAPE ONLY - horizontal ultra-wide news photograph, {topic},
        wide establishing shot, centered main subject, balanced composition.
        Realistic documentary style: natural setting, everyday details, lived-in textures,
        subtle motion, natural imperfections. Shot on Canon EOS, 24-28mm lens,
        deep DoF, edge-to-edge sharp, natural light, true colors, subtle grain,
        Reuters/AP photorealistic style.
        STRICTLY NO: vertical, square, portrait, close-ups, face focus, glamour lighting,
        artificial bokeh, HDR, oversaturation, text, watermarks, logos, symmetry, AI smoothness.
        """

        print(f"Prompt length: {len(prompt)} characters")

        # ── PRIMARY: Hugging Face - FLUX.1-schnell ────────────────────────────────
        print("Trying Hugging Face Inference (FLUX.1-schnell)...")
        try:
            image = HF_CLIENT.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=1344,
                height=768,
                num_inference_steps=20,
                guidance_scale=5.5,
            )
            print("HF FLUX succeeded!")
            url = self._process_and_upload(image, topic, "hf-flux")
            return url, "black-forest-labs/FLUX.1-schnell"

        except (HfHubHTTPError, InferenceTimeoutError, Exception) as e:
            print(
                f"HF failed: {e.__class__.__name__} - {str(e)} → falling back to xAI..."
            )

        # ── FALLBACK: xAI Grok ────────────────────────────────────────────────────
        print("Falling back to xAI Grok...")
        try:
            xai_payload = {
                "model": "grok-2-image-1212",
                "prompt": prompt,
                "n": 1,
                "response_format": "url",
            }

            response = requests.post(
                XAI_URL,
                headers=XAI_HEADERS,
                json=xai_payload,
                timeout=90,
                verify=certifi.where(),
            )
            response.raise_for_status()

            data = response.json()
            temp_url = data["data"][0]["url"]

            img_resp = requests.get(temp_url, timeout=45)
            img_resp.raise_for_status()

            image = Image.open(BytesIO(img_resp.content)).convert("RGB")
            print("xAI Grok succeeded!")
            url = self._process_and_upload(image, topic, "xai-grok")
            return url, "xAI Grok (grok-2-image-1212)"

        except Exception as e:
            print(
                "xAI Status:",
                e.response.status_code if hasattr(e, "response") else "N/A",
            )
            print("xAI Details:", e.response.text if hasattr(e, "response") else str(e))
            raise RuntimeError(f"Both HF and xAI failed! Last error: {e}") from e

    # ✅ NEW: Force 16:9 landscape crop + resize
    def _to_16_9(self, img: Image.Image, target_w: int = 1344, target_h: int = 768) -> Image.Image:
        """
        Center-crop the image to 16:9 and resize to target resolution.
        This guarantees landscape output even if the model returns square/portrait.
        """
        img = img.convert("RGB")
        w, h = img.size

        target_ratio = target_w / target_h
        current_ratio = w / h

        # If image is wider than 16:9 -> crop width
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))

        # If image is taller than 16:9 -> crop height
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        # Resize to final output size
        img = img.resize((target_w, target_h), Image.LANCZOS)
        return img

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
        # ✅ Force landscape always (even for xAI outputs)
        image = self._to_16_9(image, target_w=1344, target_h=768)

        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.08)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=93, optimize=True, progressive=True)
        buffer.seek(0)

        safe_topic = topic.lower().replace(" ", "_")[:48]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        public_id = f"news_{safe_topic}_{timestamp}_{provider}"

        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_news_images",
            public_id=public_id,
            overwrite=False,
            resource_type="image",
            format="jpg",
            quality="auto:good",
            tags=[
                "ai-generated",
                "photojournalism",
                provider,
                "documentary",
                "landscape",
                "16:9",
            ],
        )

        return result["secure_url"]
