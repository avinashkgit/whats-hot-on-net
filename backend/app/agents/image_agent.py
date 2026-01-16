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
        Generates an image using Hugging Face (FLUX.1-schnell) as primary,
        falls back to xAI Grok (Aurora) if HF fails.

        Returns:
            tuple: (cloudinary_permanent_url: str, generated_by_model: str)
        """
        # Optimized prompt for documentary/news realism
        prompt = f"""
        Ultra-wide horizontal news photograph, strongly landscape 16:9 orientation, wide establishing shot, 
        authentic trending news documentary photo of {topic}, main subject centered with balanced framing and a clear vanishing point. Real-world context: recognizable setting, everyday details, subtle motion in the environment, signs of public attention, lived-in textures, natural imperfections, and small cues that reflect what’s happening without dramatizing it. Shot on Canon EOS R5 Mark II, 24–28mm wide lens, f/8–f/11 deep DoF, edge-to-edge sharp, natural light, realistic shadows/highlights, true colors, subtle grain, photorealistic RAW detail, Reuters/AP editorial style. STRICTLY NO: close-ups, portraits, faces, medium shots, glamour lighting, artificial bokeh, HDR, oversaturation, text, watermarks, logos, perfect symmetry, AI smoothness.
        """

        # ── PRIMARY: Hugging Face Inference (FLUX.1-schnell) ─────────────────────────
        print("Trying Hugging Face Inference (FLUX.1-schnell)...")
        try:
            image = HF_CLIENT.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=1360,
                height=768,
                num_inference_steps=20,
                guidance_scale=6.0,
            )
            print("HF FLUX succeeded!")
            url = self._process_and_upload(image, topic, "hf-flux")
            return url, "black-forest-labs/FLUX.1-schnell"

        except (HfHubHTTPError, InferenceTimeoutError, Exception) as e:
            print(
                f"HF failed: {e.__class__.__name__} - {str(e)} → falling back to xAI..."
            )

        # ── FALLBACK: xAI Grok ──────────────────────────────────────────────────────
        print("Falling back to xAI Grok...")
        try:
            xai_payload = {
                "model": "grok-2-image-1212",  # or "aurora" / latest available model name
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
            return url, "xAI Grok Aurora (grok-2-image-1212)"

        except Exception as e:
            print(
                "xAI Status:",
                e.response.status_code if hasattr(e, "response") else "N/A",
            )
            print("xAI Details:", e.response.text if hasattr(e, "response") else str(e))
            raise RuntimeError(f"Both HF and xAI failed! Error: {e}") from e

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.08)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=93, optimize=True, progressive=True)
        buffer.seek(0)

        safe_topic = topic.lower().replace(" ", "_")[:48]
        public_id = f"news_{safe_topic}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{provider}"

        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_news_images",
            public_id=public_id,
            overwrite=False,
            resource_type="image",
            format="jpg",
            quality="auto:good",
            tags=["ai-generated", "photojournalism", provider, "documentary"],
        )

        return result["secure_url"]
