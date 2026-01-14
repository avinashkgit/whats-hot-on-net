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

# Using a top-tier realistic SDXL model in 2026 (Juggernaut XL Ragnarok)
# HF_URL = "https://router.huggingface.co/hf-inference/models/RunDiffusion/Juggernaut-XL-v9"   # ← previous very good version
HF_URL = "https://api-inference.huggingface.co/models/RunDiffusion/Juggernaut-XL-v9"  # Most stable public endpoint
# Alternative (newer Ragnarok variant if available): stablediffusionapi/juggernaut-xl or community uploads

HF_HEADERS = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    "Content-Type": "application/json"
}

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class ImageAgent:
    def run(self, topic: str):
        # ── Very strong realistic/editorial prompt ───────────────────────────────
        positive_prompt = f"""
        Editorial news photograph of {topic}, 
        highly detailed documentary photography, candid real moment, natural lighting, 
        soft natural shadows, realistic skin texture, true-to-life colors, sharp focus, 
        professional photojournalism style, shot on Canon EOS R5, 50mm lens, f/2.8, 
        8k resolution, ultra realistic, photorealistic, RAW photo, no text, no watermark, 
        no logo, no signature, no cartoon
        """

        # ── Very important: strong negative prompt prevents common artifacts ──────
        negative_prompt = """
        blurry, low quality, worst quality, bad anatomy, deformed, mutated hands, 
        extra limbs, poorly drawn face, bad proportions, watermark, text, logo, 
        signature, cartoon, 3d render, painting, illustration, plastic skin, 
        doll, uncanny valley, overexposed, underexposed, jpeg artifacts, grainy, 
        oversaturated, low contrast, amateur photo
        """

        payload = {
            "inputs": positive_prompt,
            "negative_prompt": negative_prompt,
            "parameters": {
                "num_inference_steps": 35,          # 30-40 is sweet spot for realism
                "guidance_scale": 6.0,              # 5.0-7.0 → lower = more natural
                "width": 1024,
                "height": 1024,
                "seed": int(time.time() * 1000) % 2147483647  # random but reproducible-ish
            }
        }

        response = requests.post(
            HF_URL,
            headers=HF_HEADERS,
            json=payload,
            timeout=180,                        # increased timeout - Juggernaut is heavier
            verify=certifi.where(),
        )

        # 1️⃣ HTTP-level validation
        if response.status_code != 200:
            error_text = response.text
            if "estimated_time" in error_text:  # Model warming up
                try:
                    data = response.json()
                    wait = int(data.get("estimated_time", 20))
                    print(f"Model warming up → waiting {wait+5}s...")
                    time.sleep(wait + 5)
                    return self.run(topic)  # retry
                except:
                    pass
            raise RuntimeError(
                f"HuggingFace API error {response.status_code}: {error_text}"
            )

        # 2️⃣ Check content type (should be image)
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            try:
                error_data = response.json()
                raise RuntimeError(f"HuggingFace returned JSON instead of image: {error_data}")
            except:
                raise RuntimeError("Unexpected response - not an image")

        # 3️⃣ Safe image decode
        try:
            image = Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            raise RuntimeError("Failed to decode image from HuggingFace API") from e

        # Optional: slight sharpening / quality boost (very light)
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.15)  # subtle improvement

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_articles",
            public_id=f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            overwrite=False,
            format="png",
            quality="auto:good"
        )

        return result["secure_url"]