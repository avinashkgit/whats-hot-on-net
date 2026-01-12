import os
from io import BytesIO
from PIL import Image
import cloudinary
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import base64
import certifi # Note: certifi is not needed for the google-genai SDK
import io

load_dotenv()

# --- Cloudinary Configuration (Remains the same) ---
cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)

# --- Gemini API Configuration ---
# The SDK automatically looks for the GEMINI_API_KEY env var
# If you prefer to set it explicitly in code:
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])


class GeminiImageAgent:
    def run(self, topic: str):
        prompt = f"""
            Realistic editorial news photo about "{topic}",
            natural lighting, documentary photography style,
            true-to-life colors, candid composition,
            high detail, no text, no watermark.
        """
        
        # --- Gemini Image Generation Logic ---
        try:
            model_name = "gemini-2.5-flash-image-preview-05-20"
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "image/png",
                    "image_config": {
                        "aspect_ratio": "16:9" # Use 16:9 for an editorial feel
                    }
                }
            )

            # Extract the base64 encoded image data from the response
            image_data = None
            for part in response.parts:
                if hasattr(part, 'inline_data'):
                    image_data = base64.b64decode(part.inline_data.data)
                    break
            
            if image_data is None:
                 raise RuntimeError("Gemini API failed to return image data.")

        except Exception as e:
            # Catching potential API errors, quota limits, etc.
            raise RuntimeError(f"Gemini API error during image generation: {e}") from e


        # --- Image Processing and Upload (Remains the same logic) ---
        try:
            # Safe image decode using BytesIO for the raw data
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
        except Exception as e:
            raise RuntimeError("Failed to decode image from Gemini response") from e

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        result = cloudinary.uploader.upload(
            buffer,
            folder="ai_articles",
            # Use topic in the public_id to help identify it later
            public_id=f"article_{topic.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            overwrite=False,
        )

        return result["secure_url"]

