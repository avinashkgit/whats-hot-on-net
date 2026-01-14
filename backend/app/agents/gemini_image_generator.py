import os
import io
import base64
from datetime import datetime
from dotenv import load_dotenv

# Core libraries
from PIL import Image
import cloudinary
import cloudinary.uploader
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
import google.api_core.exceptions

load_dotenv()

# --- Cloudinary Configuration ---
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# --- Gemini API Configuration ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiImageAgent:
    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        wait=wait_random_exponential(multiplier=1, max=60), # Wait up to 60s
        stop=stop_after_attempt(5) # Give up after 5 tries
    )
    def run(self, topic: str):
        prompt = f"""
            Realistic editorial news photo about "{topic}",
            natural lighting, documentary photography style,
            true-to-life colors, candid composition,
            high detail, no text, no watermark.
        """

        try:
            # 1. Use the standard GenerativeModel with the Imagen model ID
            # This is the most compatible way to access image generation
            model = genai.GenerativeModel("gemini-2.5-flash-image")

            # 2. Generate the image
            # In this SDK version, we use generate_content
            response = model.generate_content(
                prompt
            )

            # 3. Extract the image from the response
            # Gemini returns images as part of the candidates
            if not response.candidates or not response.candidates[0].content.parts:
                raise RuntimeError("No image generated in the response.")

            # Look for the blob data in the response parts
            image_part = response.candidates[0].content.parts[0]

            if hasattr(image_part, "inline_data"):
                image_bytes = io.BytesIO(image_part.inline_data.data)
            else:
                # Some versions return it as a direct attribute
                image_bytes = io.BytesIO(image_part.blob.data)

            image = Image.open(image_bytes).convert("RGB")

        except Exception as e:
            raise RuntimeError(f"Gemini API error during image generation: {e}") from e

        # --- Image Processing and Upload ---
        try:
            # Prepare buffer for Cloudinary
            upload_buffer = io.BytesIO()
            image.save(upload_buffer, format="PNG")
            upload_buffer.seek(0)

            # Generate a clean filename
            clean_topic = "".join(
                c for c in topic if c.isalnum() or c in (" ", "_")
            ).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            public_id = f"article_{clean_topic.replace(' ', '_')}_{timestamp}"

            # 4. Upload to Cloudinary
            result = cloudinary.uploader.upload(
                upload_buffer,
                folder="ai_articles",
                public_id=public_id,
                overwrite=True,
            )

            return result["secure_url"]

        except Exception as e:
            raise RuntimeError(f"Cloudinary upload failed: {e}") from e


# Example Usage:
# agent = GeminiImageAgent()
# url = agent.run("renewable energy in urban cities")
# print(f"Image uploaded to: {url}")
