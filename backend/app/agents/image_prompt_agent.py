import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

# Primary client: OpenAI
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Fallback client: xAI Grok
xai_client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

BASE_NEGATIVE = (
    "people, human, face, hands, fingers, extra limbs, deformed, blurry, low quality, "
    "text, logo, watermark, cartoon, anime, 3d render, plastic look"
)

MAX_PROMPT = 320

def get_thumbnail_prompt(topic: str, category: str = None) -> dict:
    """
    Returns cinematic thumbnail prompt parameters with OpenAI → Grok fallback
    """
    topic = (topic or "").strip()
    category = category if category in {
        "News", "Science", "Tech", "Market", "Lifestyle",
        "Health", "Sports", "Entertainment", "Explainers"
    } else None

    allow_humans = any(w in topic.lower() for w in [
        "celebrity", "actor", "actress", "player", "protest", "rally", "people", "crowd"
    ])

    scene_hints = {
        "Science": "research lab, observatory, scientific instruments",
        "Tech": "circuit board macro, data center, futuristic tech",
        "Market": "financial district skyline, stock exchange building",
        "Health": "modern hospital exterior, medical lab",
        "Sports": "empty stadium, floodlights, sports arena",
        "Entertainment": "cinema hall, concert stage, theater",
        "Lifestyle": "modern minimal interior, calm city street, travel landscape",
        None: "wide cinematic landscape or cityscape, establishing shot, documentary mood"
    }
    scene = scene_hints.get(category, scene_hints[None])

    system = "You create short cinematic thumbnail prompts for news. Return **only** clean JSON, no extra text."

    user = f"""Topic: {topic}
Category: {category or 'General'}

Create ONE short, strong, realistic cinematic thumbnail prompt.
wide shot • 16:9 • 24mm lens • environment focused • no readable text

Scene vibe: {scene}

Humans: {"allowed" if allow_humans else "NOT allowed - avoid all people completely"}

Return JSON only:
{{
  "prompt": str,
  "negative_prompt": str,
  "aspect_ratio": "16:9",
  "style": "cinematic realistic",
  "humans_allowed": bool
}}""".strip()

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    def normalize(result: dict, provider: str) -> dict:
        prompt = (result.get("prompt") or "").strip()[:MAX_PROMPT]
        neg = result.get("negative_prompt", "").strip()

        negative = f"{BASE_NEGATIVE}, {neg}".strip(", ")

        if not allow_humans and "people" not in negative.lower():
            negative = "people, human, face, crowd, " + negative

        return {
            "prompt": prompt,
            "negative_prompt": negative,
            "aspect_ratio": "16:9",
            "style": "cinematic realistic",
            "humans_allowed": bool(allow_humans),
            "provider": provider,
        }

    # ── Try OpenAI first ──
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # or your preferred model
            temperature=0.3,
            max_tokens=220,
            messages=messages,
            response_format={"type": "json_object"}
        )

        data = json.loads(resp.choices[0].message.content)
        return normalize(data, "openai")

    except (OpenAIError, json.JSONDecodeError, Exception) as e:
        print(f"OpenAI failed: {type(e).__name__} – falling back to Grok...")

    # ── Fallback: xAI Grok ──
    try:
        resp = xai_client.chat.completions.create(
            model="grok-4",           # or "grok-4" if available in 2026
            temperature=0.3,
            max_tokens=220,
            messages=messages,
            response_format={"type": "json_object"}
        )

        data = json.loads(resp.choices[0].message.content)
        return normalize(data, "xai-grok")

    except Exception as fallback_e:
        # Ultimate fallback - safe default
        return {
            "prompt": f"wide cinematic establishing shot of {topic}, documentary style, realistic, 16:9",
            "negative_prompt": BASE_NEGATIVE,
            "aspect_ratio": "16:9",
            "style": "cinematic realistic",
            "humans_allowed": allow_humans,
            "provider": "fallback-default",
            "error": str(fallback_e)[:80]
        }