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

# ── Hugging Face primary (Juggernaut-XL-v9) ─────────────────────────────────
HF_URL = "https://api-inference.huggingface.co/models/RunDiffusion/Juggernaut-XL-v9"
HF_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('HF_TOKEN')}",
    "Content-Type": "application/json"
}

# ── xAI Grok fallback (Aurora-based) ────────────────────────────────────────
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
        Generate realistic news/documentary photo.
        Primary: Hugging Face Juggernaut-XL-v9
        Fallback: xAI Grok (grok-2-image / Aurora)
        Returns permanent Cloudinary URL.
        """
        # Strong documentary prompt optimized for both engines
        base_prompt = f"""
        Wide establishing shot, genuine breaking news documentary photograph of {topic},
        focus on environment, objects, setting, aftermath — scattered items, equipment, displays,
        stadium/stage setup, ingredients — story told through context only, no people, humans,
        figures, faces, crowds or any human presence whatsoever

        Shot on Canon EOS R5 Mark II, 24-28mm wide lens, f/8-f/11 deep depth of field,
        sharp across frame, natural available light, authentic shadows, true colors,
        subtle organic grain, RAW photorealistic detail, maximum documentary realism

        STRICTLY NO: text, watermark, logo, signature, plastic, symmetry, glamour lighting,
        artificial bokeh, HDR, over-sharpening, AI smoothness, close-ups, portraits
        """

        negative_prompt = """
        blurry, low quality, deformed, extra limbs, bad anatomy, watermark, text, logo,
        cartoon, 3d render, painting, illustration, plastic skin, uncanny valley,
        overexposed, underexposed, grainy, oversaturated, humans, people, faces, crowds
        """

        # ── PRIMARY: Hugging Face Juggernaut ────────────────────────────────────
        print("Trying Hugging Face Juggernaut XL...")
        try:
            payload = {
                "inputs": base_prompt,
                "negative_prompt": negative_prompt,
                "parameters": {
                    "num_inference_steps": 35,
                    "guidance_scale": 6.0,
                    "width": 1024,
                    "height": 1024,
                    "seed": int(time.time() * 1000) % 2147483647
                }
            }

            for attempt in range(3):  # retry on warming / rate-limit
                response = requests.post(
                    HF_URL,
                    headers=HF_HEADERS,
                    json=payload,
                    timeout=180,
                    verify=certifi.where(),
                )

                if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
                    image = Image.open(BytesIO(response.content)).convert("RGB")
                    print("HF Juggernaut succeeded!")
                    return self._process_and_upload(image, topic, "hf-juggernaut")

                elif "estimated_time" in response.text.lower():
                    try:
                        wait = int(response.json().get("estimated_time", 15)) + 5
                        print(f"HF model warming up → waiting {wait}s (attempt {attempt+1}/3)...")
                        time.sleep(wait)
                        continue
                    except:
                        pass

                elif response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(10 * (attempt + 1))
                    continue

                else:
                    print(f"HF error {response.status_code}: {response.text[:200]}")
                    break  # non-retryable → fallback

        except Exception as e:
            print(f"HF failed: {e.__class__.__name__} → falling back to xAI Grok...")

        # ── FALLBACK: xAI Grok (Aurora) ─────────────────────────────────────────
        print("Falling back to xAI Grok image generation...")
        try:
            xai_payload = {
                "model": "grok-2-image",          # Official stable name per xAI docs
                "prompt": base_prompt.strip(),
                "n": 1,
                "response_format": "url"          # temporary URL
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

            # Download temp image
            img_resp = requests.get(temp_url, timeout=45)
            img_resp.raise_for_status()

            image = Image.open(BytesIO(img_resp.content)).convert("RGB")
            print("xAI Grok succeeded!")
            return self._process_and_upload(image, topic, "xai-grok")

        except Exception as e:
            raise RuntimeError(
                f"Critical failure: Both HF Juggernaut and xAI Grok failed!\n"
                f"HF error: {e}"
            ) from e

    def _process_and_upload(self, image: Image.Image, topic: str, provider: str) -> str:
        """Light post-process + Cloudinary upload"""
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.08)  # subtle realism boost

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