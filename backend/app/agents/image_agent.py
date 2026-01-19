import os
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
import google.generativeai as genai  # pip install google-generativeai

load_dotenv()

# ── Hugging Face ──────────────────────────────────────────────────────────────
HF_CLIENT = InferenceClient(
    api_key=os.environ.get("HF_TOKEN"),
)

# ── xAI Grok ──────────────────────────────────────────────────────────────────
XAI_URL = "https://api.x.ai/v1/images/generations"
XAI_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('XAI_API_KEY')}",
    "Content-Type": "application/json",
}

# ── Google Gemini ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = "gemini-2.5-flash-image"  # or "gemini-3-pro-image-preview" if you have access

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class ImageAgent:
    def run(
        self, prompt: str, negative_prompt: str = "", topic: str = "news"
    ) -> tuple[str, str]:
        """
        Generates landscape news-style image.
        Priority order (2026):
        1. Hugging Face - FLUX.1-schnell (fast & free)
        2. Google Gemini - Nano Banana (good quality, limited free tier)
        3. xAI Grok (fallback)
        """

        final_prompt = f"""
16:9 LANDSCAPE ONLY.
{prompt}

Photojournalism requirements:
- wide establishing shot
- cinematic realistic lighting
- environment visible, not close-up
- no text, no logos, no watermark

Negative prompt (if supported):
{negative_prompt}
"""

        print("🖼️ Final image prompt length:", len(final_prompt))

        # ── 1. PRIMARY: Hugging Face - FLUX.1-schnell ─────────────────────────────
        print("Trying Hugging Face Inference (FLUX.1-schnell)...")
        try:
            image = HF_CLIENT.text_to_image(
                prompt=final_prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=1344,
                height=768,
                num_inference_steps=22,
                guidance_scale=6.0,
            )
            print("HF FLUX succeeded!")
            url = self._process_and_upload(image, topic, "hf-flux")
            return url, "black-forest-labs/FLUX.1-schnell"

        except (HfHubHTTPError, InferenceTimeoutError, Exception) as e:
            print(f"HF failed: {e.__class__.__name__} - {str(e)} → trying Gemini...")

        # ── 2. FALLBACK: Google Gemini Nano Banana ────────────────────────────────
        if GEMINI_API_KEY:
            print("Trying Google Gemini (Nano Banana)...")
            try:
                model = genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content(final_prompt)

                # Gemini usually returns inline image data in parts
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_bytes = part.inline_data.data
                        image = Image.open(BytesIO(image_bytes)).convert("RGB")
                        print("Gemini succeeded!")
                        url = self._process_and_upload(image, topic, "gemini-nano-banana")
                        return url, "Google Gemini (Nano Banana)"

                raise ValueError("No image data found in Gemini response")

            except Exception as gemini_e:
                print(f"Gemini failed: {str(gemini_e)} → falling back to xAI...")

        # ── 3. FINAL FALLBACK: xAI Grok ───────────────────────────────────────────
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

            data = response.json()
            temp_url = data["data"][0]["url"]

            img_resp = requests.get(temp_url, timeout=45)
            img_resp.raise_for_status()

            image = Image.open(BytesIO(img_resp.content)).convert("RGB")
            print("xAI Grok succeeded!")
            url = self._process_and_upload(image, topic, "xai-grok")
            return url, "xAI Grok (grok-2-image-1212)"

        except Exception as e:
            print("xAI Status:", getattr(e.response, 'status_code', 'N/A'))
            print("xAI Details:", getattr(e.response, 'text', str(e)))
            raise RuntimeError(f"All providers failed! Last error: {e}") from e

    def _to_16_9(
        self, img: Image.Image, target_w: int = 1344, target_h: int = 768
    ) -> Image.Image:
        img = img.convert("RGB")
        w, h = img.size

        target_ratio = target_w / target_h
        current_ratio = w / h

        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        img = img.resize((target_w, target_h), Image.LANCZOS)
        return img

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
        # Uncomment if you still want strict 16:9 crop/resize
        # image = self._to_16_9(image)

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