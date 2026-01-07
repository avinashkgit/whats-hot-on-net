import requests, os
from io import BytesIO
from PIL import Image
import cloudinary
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
import certifi

load_dotenv()

HF_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
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
        Cinematic editorial illustration about "{topic}",
        global news style, realistic lighting,
        professional, no text, no watermark
        """

        response = requests.post(
            HF_URL, headers=HF_HEADERS, json={"inputs": prompt}, timeout=120, verify=certifi.where()
        )

        image = Image.open(BytesIO(response.content)).convert("RGB")

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
