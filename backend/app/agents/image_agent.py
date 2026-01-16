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
        # Short, strong prompt focused on landscape (≈480-520 chars)
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
                width=1344,  # Most reliable landscape size for FLUX
                height=768,
                num_inference_steps=20,
                guidance_scale=5.5,  # Better prompt adherence
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

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
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
            ],
        )

        return result["secure_url"]
