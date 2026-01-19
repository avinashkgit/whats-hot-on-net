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

# New unified Google GenAI SDK (replaces deprecated google.generativeai)
from google import genai
from google.genai import types

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

# ── Google Gemini (new SDK) ───────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-image")

genai_client = None
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)

# ── Cloudinary ────────────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class ImageAgent:
    def run(
        self,
        prompt: str,
        negative_prompt: str = "",
        topic: str = "news",
        humans_allowed: bool = False,
    ) -> tuple[str, str]:
        """
        Generates landscape news-style image.
        Priority order:
        1) Hugging Face - FLUX.1-schnell
        2) Google Gemini (new SDK)
        3) xAI Grok
        """

        # ⚠️ Hard limit safety (xAI errors above 1024 chars)
        MAX_PROMPT_LEN = 950

        base_blocklist = [
            "text",
            "logo",
            "watermark",
            "caption",
            "branding",
            "blurry",
            "low quality",
            "jpeg artifacts",
            "noise",
            "distorted",
            "duplicate",
            "floating objects",
            "cartoon",
            "anime",
            "cgi",
            "3d render",
            "extra limbs",
            "extra fingers",
            "deformed anatomy",
        ]

        if not humans_allowed:
            base_blocklist += ["people", "human", "crowd", "face", "portrait", "hands"]

        # Keep negative short
        incoming_neg = ", ".join(
            [x.strip() for x in (negative_prompt or "").split(",") if x.strip()]
        )
        if len(incoming_neg) > 180:
            incoming_neg = incoming_neg[:180].rsplit(",", 1)[0]

        # Short rules (single-line to save tokens)
        hard_rules = (
            "16:9 landscape, wide establishing shot, 24mm, cinematic realistic photojournalism, "
            "environment-focused, no close-up, no readable text."
        )
        humans_rule = (
            "EMPTY SCENE, no humans." if not humans_allowed else "No close-up faces."
        )

        final_prompt = (
            f"{prompt.strip()} | {hard_rules} | {humans_rule} | "
            f"avoid: {', '.join(base_blocklist)}"
        )

        if incoming_neg:
            final_prompt += f", {incoming_neg}"

        final_prompt = final_prompt.strip()

        # Final trim to avoid 1024 overflow
        if len(final_prompt) > MAX_PROMPT_LEN:
            final_prompt = final_prompt[:MAX_PROMPT_LEN].rsplit(" ", 1)[0]

        print("🖼️ Final image prompt length:", len(final_prompt))

        # ── 1) PRIMARY: Hugging Face - FLUX.1-schnell ──────────────────────────
        print("Trying Hugging Face Inference (FLUX.1-schnell)...")
        try:
            image = HF_CLIENT.text_to_image(
                prompt=final_prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=1344,
                height=768,
                num_inference_steps=26,
                guidance_scale=7.0,
            )
            print("✅ HF FLUX succeeded!")
            url = self._process_and_upload(image, topic, "hf-flux")
            return url, "black-forest-labs/FLUX.1-schnell"

        except (HfHubHTTPError, InferenceTimeoutError, Exception) as e:
            print(f"❌ HF failed: {e.__class__.__name__} - {str(e)} → trying Gemini...")

        # ── 2) FALLBACK: Google Gemini (new SDK) ───────────────────────────────
        if genai_client:
            print(f"Trying Google Gemini ({GEMINI_MODEL})...")
            try:
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[final_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio="16:9"),
                    ),
                )

                image = response.candidates[0].content.parts[0].as_image()

                print("✅ Gemini succeeded!")
                url = self._process_and_upload(image, topic, "gemini")
                return url, f"Google Gemini ({GEMINI_MODEL})"

            except Exception as gemini_e:
                print(f"❌ Gemini failed: {gemini_e} → falling back to xAI...")

        else:
            print("⚠️ GEMINI_API_KEY not set → skipping Gemini, trying xAI...")

        # ── 3) FINAL FALLBACK: xAI Grok ─────────────────────────────────────────
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
            print("✅ xAI Grok succeeded!")
            url = self._process_and_upload(image, topic, "xai-grok")
            return url, "xAI Grok (grok-2-image-1212)"

        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", "N/A")
            text = getattr(getattr(e, "response", None), "text", str(e))
            print("xAI Status:", status)
            print("xAI Details:", text)
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
        # ✅ Always enforce strict 16:9 crop/resize (prevents stretching weirdness)
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
