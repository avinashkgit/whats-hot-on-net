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
from huggingface_hub.errors import HfHubHTTPError   # ← this is the correct location
load_dotenv()

# Hugging Face Inference Client (new unified way - Jan 2026)
HF_CLIENT = InferenceClient(
    api_key=os.environ.get("HF_TOKEN"),
    # provider="auto",           # default: auto-select best provider
    # provider="fal-ai",         # or force fast provider like fal-ai / replicate / together
)

# xAI fallback (your existing setup)
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
    def run(self, topic: str) -> str:
        """
        Primary: Hugging Face Inference Providers (FLUX.1-schnell for fast photoreal news-style)
        Fallback: xAI Grok (Aurora)
        Returns permanent Cloudinary URL.
        """
        # Optimized prompt for documentary/news realism (works great on FLUX)
        prompt = f"""
        Wide establishing shot, genuine breaking news documentary photograph of {topic},
        focus exclusively on environment, objects, setting, aftermath — scattered items, equipment,
        stadium setup, stage elements — story told through context only, no people, humans,
        figures, faces, crowds or any human presence whatsoever

        Shot on Canon EOS R5 Mark II, 24-28mm wide lens, f/8-f/11 deep DoF, sharp across frame,
        natural available light, authentic shadows/highlights, true colors, subtle organic grain,
        RAW photorealistic detail, maximum documentary realism

        STRICTLY NO: text, watermark, logo, signature, plastic, symmetry, glamour lighting,
        artificial bokeh, HDR, over-sharpening, AI smoothness, close-ups, portraits
        """

        negative_prompt = """
        blurry, low quality, deformed, extra limbs, bad anatomy, watermark, text, logo,
        cartoon, 3d render, painting, illustration, plastic skin, uncanny valley,
        overexposed, underexposed, grainy, oversaturated, humans, people, faces, crowds
        """

        # ── PRIMARY: Hugging Face Inference Providers ───────────────────────────────
        print("Trying Hugging Face Inference Providers (FLUX.1-schnell)...")
        try:
            image = HF_CLIENT.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell",  # fast & excellent photorealism
                # negative_prompt=negative_prompt,     # some providers support it
                width=1024,
                height=1024,
                num_inference_steps=20,               # fast mode: 4-20 steps
                guidance_scale=6.0,
            )
            print("HF FLUX succeeded!")
            return self._process_and_upload(image, topic, "hf-flux")

        except (HfHubHTTPError, InferenceTimeoutError, Exception) as e:
            print(f"HF failed: {e.__class__.__name__} - {str(e)} → falling back to xAI...")

        # ── FALLBACK: xAI Grok ──────────────────────────────────────────────────────
        print("Falling back to xAI Grok...")
        try:
            xai_payload = {
                "model": "grok-2-image",  # or "grok-2-image-1212" if you prefer versioned
                "prompt": prompt,
                "n": 1,
                "response_format": "url"
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
            return self._process_and_upload(image, topic, "xai-grok")

        except Exception as e:
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