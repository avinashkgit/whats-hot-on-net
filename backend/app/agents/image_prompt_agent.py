import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class ImagePromptAgent:
    MAX_PROMPT_LEN = 950

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

    HUMAN_KEYWORDS = [
        "celebrity",
        "actor",
        "actress",
        "singer",
        "politician",
        "protest",
        "rally",
        "election",
        "crowd",
        "people",
        "person",
        "man",
        "woman",
        "child",
        "children",
        "students",
        "workers",
        "fans",
        "public",
        "police",
        "soldiers",
        "refugees",
        "tourists",
        "audience",
        "team",
        "coach",
        "player",
    ]

    def __init__(self, openai_model: str = None, grok_model: str = None):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.xai_client = OpenAI(
            api_key=os.environ.get("XAI_API_KEY"), base_url="https://api.x.ai/v1"
        )

        self.openai_model = openai_model or os.environ.get(
            "OPENAI_PROMPT_MODEL", "gpt-4o-mini"
        )
        self.grok_model = grok_model or os.environ.get("XAI_PROMPT_MODEL", "grok-beta")

    def _topic_allows_humans(self, topic: str) -> bool:
        t = (topic or "").lower()
        for kw in self.HUMAN_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", t):
                return True
        return False

    def run(self, topic: str, category: str | None = None) -> dict:
        topic = (topic or "").strip()[:240]
        if not topic:
            topic = "breaking news"

        category = category if category in self.ALLOWED_CATEGORIES else "News"

        allow_humans = self._topic_allows_humans(topic)

        base_negatives = "cgi, 3d render, plastic, airbrushed, cartoon, text, watermark, logo, blurry, extra limbs"
        if not allow_humans:
            base_negatives = f"people, human, face, portrait, {base_negatives}"

        system_msg = (
            "You are a News Photo Editor. Create a short, highly realistic image prompt for a thumbnail. "
            "Use photography terms like '24mm lens', 'f/8', 'raw photo'. "
            'Return ONLY valid JSON: {"prompt": "...", "negative_prompt": "..."}'
        )

        user_msg = f"""
Topic: {topic}
Category: {category}
Humans: {"Allowed (candid/unposed)" if allow_humans else "STRICTLY FORBIDDEN (empty scene)"}

Requirements:
- 16:9 aspect ratio wide shot
- Documentary / photojournalism style
- Environment-focused
- No text in the image

Return JSON: {{"prompt": "string", "negative_prompt": "string"}}
""".strip()

        def finalize_data(data: dict, provider: str) -> dict:
            p = (data.get("prompt") or "").strip()
            n = (data.get("negative_prompt") or "").strip()

            if not p:
                p = f"wide documentary photo of {topic}"

            full_prompt = f"Shot on 35mm film, raw photo, {p}, 16:9 wide shot, cinematic natural lighting"
            full_negative = f"{base_negatives}"
            if n:
                full_negative = f"{full_negative}, {n}"

            return {
                "prompt": full_prompt[: self.MAX_PROMPT_LEN],
                "negative_prompt": full_negative[:300],
                "provider": provider,
                "topic": topic,
                "category": category,
                "allow_humans": allow_humans,
            }

        # ── Fallback Chain: OpenAI -> Grok -> Static ──
        try:
            resp = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            return finalize_data(json.loads(resp.choices[0].message.content), "openai")
        except Exception:
            try:
                resp = self.xai_client.chat.completions.create(
                    model=self.grok_model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                return finalize_data(
                    json.loads(resp.choices[0].message.content), "xai-grok"
                )
            except Exception:
                return finalize_data(
                    {
                        "prompt": f"wide cinematic documentary photo of {topic}",
                        "negative_prompt": "",
                    },
                    "fallback-static",
                )
