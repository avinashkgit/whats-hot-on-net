import requests, os, time
from io import BytesIO
from PIL import Image
import cloudinary
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
import certifi

load_dotenv()

HF_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)


class ImageAgent:
    def run(self, topic: str):
        prompt = f"""
            Realistic editorial news photo about "{topic}",
            natural lighting, documentary photography style,
            true-to-life colors, candid composition,
            high detail, no text, no watermark.
        """

        response = requests.post(
            HF_URL,
            headers=HF_HEADERS,
            json={"inputs": prompt},
            timeout=120,
            verify=certifi.where(),
        )

        # 1️⃣ HTTP-level validation
        if response.status_code != 200:
            raise RuntimeError(
                f"HuggingFace HTTP {response.status_code}: {response.text}"
            )

        # 2️⃣ Content-Type check
        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            data = response.json()

            # Model warming up → wait & retry
            if isinstance(data, dict) and "estimated_time" in data:
                wait = int(data.get("estimated_time", 15))
                time.sleep(wait + 2)
                return self.run(topic)

            # Any other JSON = error
            raise RuntimeError(f"HuggingFace JSON error: {data}")

        # 3️⃣ Safe image decode
        try:
            image = Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            raise RuntimeError("Failed to decode image from HuggingFace") from e

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_articles",
            public_id=f"article_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            overwrite=False,
        )

        return result["secure_url"]
