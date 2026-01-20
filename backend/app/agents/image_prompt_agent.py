import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


class ImagePromptAgent:
    """
    Generates a realistic image prompt for news thumbnails.

    Goals:
    - Prompt must stick ONLY to the topic (no unrelated creative drift)
    - Keep prompt simple, topic-focused, wide/establishing style
    - Prevent deformed humans/limbs and artifacts using strong negative_prompt
    - prompt length <= 1024 characters
    """

    MAX_PROMPT_LEN = 1024
    MAX_NEGATIVE_LEN = 1024

    ALLOWED_CATEGORIES = {
        "News",
        "Science",
        "Tech",
        "Market",
        "Lifestyle",
        "Health",
        "Sports",
        "Entertainment",
        "Explainers",
    }

    # Strong negatives to prevent weird generations
    BASE_NEGATIVE = (
        "deformed, extra limbs, "
        "abnormal fingers, long neck, distorted face, "
        "blurry, low quality, low resolution, noisy, jpeg artifacts, watermark, caption, "
        "cartoon, anime, illustration, 3d render, plastic look"
    )

    # Only used when humans are NOT allowed
    HUMAN_BLOCK = "people, person, human, face, hands, fingers, crowd"

    def __init__(self, openai_model: str = None, grok_model: str = None):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        self.xai_client = OpenAI(
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )

        self.openai_model = openai_model or os.environ.get(
            "OPENAI_PROMPT_MODEL", "gpt-4o-mini"
        )
        self.grok_model = grok_model or os.environ.get("XAI_PROMPT_MODEL", "grok-4")

    def run(self, topic: str, category: str = None) -> dict:
        topic = (topic or "").strip()
        if not topic:
            return {
                "prompt": "wide realistic establishing shot, documentary style, 16:9",
                "negative_prompt": self.BASE_NEGATIVE[: self.MAX_NEGATIVE_LEN],
                "humans_allowed": False,
                "provider": "fallback-default",
                "error": "empty topic",
            }

        category = category if category in self.ALLOWED_CATEGORIES else None

        # Humans allowed only if topic explicitly implies it
        allow_humans = any(
            w in topic.lower()
            for w in [
                "celebrity",
                "actor",
                "actress",
                "player",
                "team",
                "protest",
                "rally",
                "crowd",
                "people",
                "fans",
            ]
        )

        system = (
            "You generate realistic image prompts for news thumbnails.\n"
            "STRICT RULES:\n"
            "- The prompt must represent ONLY the given topic.\n"
            "- Do NOT add unrelated objects, locations, characters, or fantasy elements.\n"
            "- Keep it realistic and documentary style.\n"
            "Return ONLY valid JSON. No markdown. No extra text."
        )

        # Keep prompt instructions minimal
        user = f"""
Topic: {topic}
Category: {category or "General"}

Return JSON only:
{{
  "prompt": "ONE short realistic image prompt that visually represents ONLY the topic. Use wide establishing shot, 16:9, documentary style.",
  "negative_prompt": "string"
}}
""".strip()

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        def normalize(data: dict, provider: str) -> dict:
            prompt = (data.get("prompt") or "").strip()
            neg = (data.get("negative_prompt") or "").strip()

            # Enforce max prompt length
            prompt = prompt[: self.MAX_PROMPT_LEN].strip()

            # Merge negatives
            negative_parts = [self.BASE_NEGATIVE, neg]
            negative = ", ".join([p for p in negative_parts if p]).strip(", ").strip()

            if not allow_humans:
                negative = f"{self.HUMAN_BLOCK}, {negative}".strip(", ")

            negative = negative[: self.MAX_NEGATIVE_LEN].strip()

            return {
                "prompt": prompt,
                "negative_prompt": negative,
                "humans_allowed": allow_humans,
                "provider": provider,
            }

        # ── Try OpenAI first ──
        try:
            resp = self.openai_client.chat.completions.create(
                model=self.openai_model,
                temperature=0.1,  # low = stays on topic
                max_tokens=220,
                messages=messages,
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            return normalize(data, "openai")

        except (OpenAIError, json.JSONDecodeError, Exception) as e:
            print(
                f"⚠️ OpenAI prompt generation failed: {type(e).__name__} → fallback to Grok"
            )

        # ── Fallback to Grok ──
        try:
            resp = self.xai_client.chat.completions.create(
                model=self.grok_model,
                temperature=0.1,
                max_tokens=220,
                messages=messages,
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            return normalize(data, "xai-grok")

        except Exception as e:
            fallback_prompt = (
                f"wide realistic establishing shot of {topic}, documentary style, 16:9"
            )[: self.MAX_PROMPT_LEN].strip()

            fallback_negative = self.BASE_NEGATIVE
            if not allow_humans:
                fallback_negative = f"{self.HUMAN_BLOCK}, {fallback_negative}"

            return {
                "prompt": fallback_prompt,
                "negative_prompt": fallback_negative[: self.MAX_NEGATIVE_LEN],
                "humans_allowed": allow_humans,
                "provider": "fallback-default",
                "error": str(e)[:120],
            }
