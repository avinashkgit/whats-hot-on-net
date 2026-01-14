import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available models that support Image Generation:")
for m in genai.list_models():
    # Looking for 'generate_images' or 'generateContent' with image-capable models
    if 'generateContent' in m.supported_generation_methods or 'generate_images' in m.supported_generation_methods:
        if 'imagen' in m.name.lower() or 'image' in m.name.lower():
            print(f"-> {m.name}")