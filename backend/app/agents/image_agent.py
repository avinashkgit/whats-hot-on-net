import os
import re
from io import BytesIO
from datetime import datetime, timezone
from PIL import Image, ImageEnhance
import requests
import certifi
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Hugging Face
from huggingface_hub import InferenceClient

# Unified Google GenAI SDK
from google import genai
from google.genai import types

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────

HF_CLIENT = InferenceClient(api_key=os.environ.get("HF_TOKEN"))

XAI_URL = "https://api.x.ai/v1/images/generations"
XAI_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('XAI_API_KEY')}",
    "Content-Type": "application/json",
}

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-image")

genai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)


class ImageAgent:
    def run(self, prompt_data: dict) -> tuple[str, str]:
        prompt = (prompt_data.get("prompt") or "").strip()
        negative = (prompt_data.get("negative_prompt") or "").strip()
        topic = (prompt_data.get("topic") or "news").strip()

        if not prompt:
            prompt = "wide documentary photo, cinematic lighting, 16:9"

        # Keep negatives lightweight for FLUX / general image models
        # (Dumping huge negative lists often hurts quality.)
        if negative:
            final_prompt = f"{prompt}. No text, no watermark, no logo. Avoid: {negative}"
        else:
            final_prompt = f"{prompt}. No text, no watermark, no logo."

        # ── 1) FLUX ──
        try:
            image = HF_CLIENT.text_to_image(
                prompt=final_prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=1344,
                height=768,
                num_inference_steps=4,
                guidance_scale=3.5,
            )
            return self._process_and_upload(image, topic, "hf-flux"), "FLUX.1-schnell"
        except Exception:
            pass

        # ── 2) Gemini ──
        if genai_client:
            try:
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[final_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    ),
                )

                # Extract inline image bytes safely
                parts = response.candidates[0].content.parts
                img_bytes = None

                for part in parts:
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        img_bytes = inline.data
                        break

                if not img_bytes:
                    raise RuntimeError("Gemini returned no inline image bytes")

                image = Image.open(BytesIO(img_bytes)).convert("RGB")

                return (
                    self._process_and_upload(image, topic, "gemini"),
                    f"Gemini ({GEMINI_MODEL})",
                )
            except Exception:
                pass

        # ── 3) FINAL FALLBACK: xAI Grok ──
        print("Falling back to xAI Grok...")
        try:
            xai_payload = {
                "model": "grok-2-image-1212",
                "prompt": final_prompt,
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

            temp_url = response.json()["data"][0]["url"]
            img_resp = requests.get(temp_url, timeout=45)
            img_resp.raise_for_status()

            image = Image.open(BytesIO(img_resp.content)).convert("RGB")
            url = self._process_and_upload(image, topic, "xai-grok")
            return url, "xAI Grok (grok-2-image-1212)"
        except Exception as e:
            raise RuntimeError(f"All providers failed. Last error: {e}")

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.08)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=93, optimize=True, progressive=True)
        buffer.seek(0)

        # safer topic -> slug
        safe_topic = (topic or "news").strip().lower()
        safe_topic = re.sub(r"\s+", "_", safe_topic)
        safe_topic = re.sub(r"[^a-z0-9_]+", "", safe_topic)[:30] or "news"

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
            tags=["ai-generated", "photojournalism", provider, "landscape", "16:9"],
        )

        return result["secure_url"]
