import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from constants import GPT_MODEL

load_dotenv()

# Primary client (OpenAI)
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Fallback client (xAI Grok)
xai_client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

ALLOWED_CATEGORIES = [
    "News",
    "Science",
    "Tech",
    "Market",
    "Lifestyle",
    "Health",
    "Sports",
    "Entertainment",
    "Explainers",
]


class ImagePromptAgent:
    def run(self, topic: str, category: str = None):
        """
        Returns a scenic image prompt for article thumbnail generation.

        Output JSON:
        {
          "prompt": "...",
          "negative_prompt": "...",
          "aspect_ratio": "16:9",
          "style": "cinematic realistic"
        }
        """

        # Normalize category
        if category and category not in ALLOWED_CATEGORIES:
            category = None

        system_message = (
            "You are an Image Prompt Writer Agent for a news/articles website.\n"
            "Your job is to generate scenic, wide, cinematic prompts suitable for article thumbnails.\n"
            "You must output STRICTLY valid JSON matching the schema.\n"
            "Avoid close-up portraits unless explicitly requested.\n"
        )

        user_message = f"""
        Create a single best image generation prompt for an article.

        TOPIC:
        {topic}

        CATEGORY:
        {category or "Auto-detect from topic"}

        REQUIREMENTS:
        - Scenic and wide (landscape)
        - Cinematic realistic photography style
        - Suitable for a news/blog thumbnail
        - Should visually represent the topic using environment + action
        - Avoid close-up faces and portrait framing

        OUTPUT RULES:
        - Return ONLY JSON
        - The prompt should include camera/framing hints like: wide-angle, 24mm, 16:9, establishing shot
        - Include a strong negative_prompt to prevent close-ups, text, logos, watermarks
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        schema = {
            "name": "image_prompt",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "prompt": {"type": "string"},
                    "negative_prompt": {"type": "string"},
                    "aspect_ratio": {"type": "string"},
                    "style": {"type": "string"},
                },
                "required": ["prompt", "negative_prompt", "aspect_ratio", "style"],
            },
        }

        # ── Primary attempt: OpenAI ──
        try:
            response = openai_client.chat.completions.create(
                model=GPT_MODEL,
                temperature=0.4,
                max_tokens=500,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": schema,
                },
            )

            msg = response.choices[0].message
            data = (
                msg.parsed
                if hasattr(msg, "parsed") and msg.parsed
                else json.loads(msg.content)
            )

            return {
                "prompt": data["prompt"].strip(),
                "negative_prompt": data["negative_prompt"].strip(),
                "aspect_ratio": data["aspect_ratio"].strip(),
                "style": data["style"].strip(),
                "provider": "openai",
            }

        except (OpenAIError, json.JSONDecodeError, KeyError, Exception) as e:
            print(f"OpenAI failed: {e.__class__.__name__} – falling back to Grok...")

        # ── Fallback: xAI Grok ──
        FALLBACK_MODEL = "grok-4"

        try:
            response = xai_client.chat.completions.create(
                model=FALLBACK_MODEL,
                temperature=0.4,
                max_tokens=500,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": schema,
                },
            )

            msg = response.choices[0].message
            data = (
                msg.parsed
                if hasattr(msg, "parsed") and msg.parsed
                else json.loads(msg.content)
            )

            return {
                "prompt": data["prompt"].strip(),
                "negative_prompt": data["negative_prompt"].strip(),
                "aspect_ratio": data["aspect_ratio"].strip(),
                "style": data["style"].strip(),
                "provider": "xai-grok",
            }

        except Exception as fallback_e:
            raise RuntimeError(
                f"Both OpenAI and xAI fallback failed!\n"
                f"OpenAI: {e}\n"
                f"xAI:    {fallback_e}"
            )
