import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


class ImagePromptAgent:
    """
    Takes a topic + category and generates a SHORT cinematic image prompt
    that can be directly passed to ImageAgent.run(prompt=...).

    Output format:
    {
        "prompt": "...",
        "negative_prompt": "...",
        "humans_allowed": bool,
        "provider": "openai" | "xai-grok" | "fallback-default"
    }
    """

    MAX_PROMPT_LEN = 320

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

    BASE_NEGATIVE = (
        "people, human, face, hands, fingers, extra limbs, deformed, blurry, low quality, "
        "text, logo, watermark, caption, cartoon, anime, 3d render, plastic look"
    )

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
                "prompt": "wide cinematic establishing shot, documentary style, realistic, 16:9",
                "negative_prompt": self.BASE_NEGATIVE,
                "humans_allowed": False,
                "provider": "fallback-default",
                "error": "empty topic",
            }

        category = category if category in self.ALLOWED_CATEGORIES else None

        allow_humans = any(
            w in topic.lower()
            for w in [
                "celebrity",
                "actor",
                "actress",
                "player",
                "protest",
                "rally",
                "people",
                "crowd",
            ]
        )

        scene_hints = {
            "Science": "research lab, observatory, scientific instruments",
            "Tech": "circuit board macro, data center, futuristic tech",
            "Market": "financial district skyline, stock exchange building",
            "Health": "modern hospital exterior, medical lab",
            "Sports": "empty stadium, floodlights, sports arena",
            "Entertainment": "cinema hall, concert stage, theater",
            "Lifestyle": "modern minimal interior, calm city street, travel landscape",
            None: "wide cinematic landscape or cityscape, establishing shot, documentary mood",
        }
        scene = scene_hints.get(category, scene_hints[None])

        system = (
            "You generate short cinematic realistic image prompts for news thumbnails. "
            "Return ONLY valid JSON. No markdown. No extra text."
        )

        user = f"""
Topic: {topic}
Category: {category or "General"}

Goal:
- Create ONE cinematic, realistic, news-thumbnail image prompt.
- Must be usable directly as an image generation prompt.
- 16:9 landscape, wide establishing shot, 24mm lens look.
- Environment-focused (NOT close-up).
- No readable text anywhere.

Scene vibe hints: {scene}

Humans: {"allowed" if allow_humans else "NOT allowed (avoid people completely)"}

Return JSON only:
{{
  "prompt": "string",
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

            prompt = prompt[: self.MAX_PROMPT_LEN].strip()

            negative = f"{self.BASE_NEGATIVE}, {neg}".strip(", ")

            if not allow_humans and "people" not in negative.lower():
                negative = "people, human, face, crowd, " + negative

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
                temperature=0.3,
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
                temperature=0.3,
                max_tokens=220,
                messages=messages,
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            return normalize(data, "xai-grok")

        except Exception as e:
            return {
                "prompt": f"wide cinematic establishing shot of {topic}, documentary style, realistic, 16:9",
                "negative_prompt": self.BASE_NEGATIVE,
                "humans_allowed": allow_humans,
                "provider": "fallback-default",
                "error": str(e)[:120],
            }
