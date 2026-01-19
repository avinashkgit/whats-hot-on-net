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

# ✅ Keep these SHORT because image providers have strict prompt limits
BASE_NEGATIVE_PROMPT = (
    "people, human, crowd, face, portrait, hands, fingers, extra limbs, "
    "deformed, distorted, mutated, blurry, low quality, noise, jpeg artifacts, "
    "text, logo, watermark, caption, signature, branding, "
    "cartoon, anime, cgi, 3d render, plastic look"
)

# Hard limits to prevent 1024 prompt errors downstream
MAX_PROMPT_LEN = 320
MAX_NEGATIVE_LEN = 260


def category_scene_hint(topic: str, category: str | None) -> str:
    t = (topic or "").lower()

    if category == "Science":
        return "observatory, telescope, research lab, satellites, scientific instruments"
    if category == "Tech":
        return "data center, server racks, circuit board macro, futuristic skyline"
    if category == "Market":
        return "financial district skyline, trading screens (no readable text), corporate buildings"
    if category == "Health":
        return "hospital exterior, medical lab, ambulance bay, sterile lighting"
    if category == "Sports":
        return "stadium wide shot, floodlights, empty field, sports equipment foreground"
    if category == "Entertainment":
        return "cinema hall wide shot, stage lights, concert venue, empty red carpet"
    if category == "Lifestyle":
        return "city street, travel landscape, modern minimal interior, calm environment"
    if category == "Explainers":
        return "modern newsroom set, neutral studio, symbolic objects related to topic"

    if any(x in t for x in ["train", "rail", "metro", "station"]):
        return "railway tracks, station platform, signal lights, wide perspective"
    if any(x in t for x in ["flood", "storm", "earthquake", "disaster"]):
        return "wide landscape, dramatic weather, damaged infrastructure, no people visible"
    if any(x in t for x in ["war", "attack", "conflict", "missile"]):
        return "distant skyline, smoke far away, dramatic clouds, no people visible"

    return "realistic cityscape or landscape, wide establishing shot, documentary mood"


class ImagePromptAgent:
    def run(self, topic: str, category: str = None):
        """
        Output JSON:
        {
          "prompt": "...",
          "negative_prompt": "...",
          "aspect_ratio": "16:9",
          "style": "cinematic realistic",
          "humans_allowed": false
        }
        """

        if category and category not in ALLOWED_CATEGORIES:
            category = None

        # ✅ Default: no humans (prevents weird people)
        humans_allowed = False

        topic_l = (topic or "").lower()
        if any(x in topic_l for x in ["celebrity", "actor", "actress", "player", "protest", "rally"]):
            humans_allowed = True

        scene_hint = category_scene_hint(topic, category)

        system_message = (
            "You generate short, scenic prompts for news thumbnail images.\n"
            "Return STRICT JSON only.\n"
            "Keep prompt short and cinematic.\n"
            "Avoid humans unless humans_allowed is true.\n"
        )

        user_message = f"""
TOPIC: {topic}
CATEGORY: {category or "Auto"}

Generate ONE short cinematic realistic thumbnail prompt.

Must include:
- 16:9 landscape
- wide establishing shot, 24mm
- environment-focused
- no readable text

Scene inspiration: {scene_hint}

Humans allowed: {str(humans_allowed).lower()}

Return JSON with:
prompt, negative_prompt, aspect_ratio, style, humans_allowed
""".strip()

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
                    "humans_allowed": {"type": "boolean"},
                },
                "required": ["prompt", "negative_prompt", "aspect_ratio", "style", "humans_allowed"],
            },
        }

        def normalize_output(data: dict, provider: str):
            prompt = (data.get("prompt") or "").strip().replace("\n", " ")
            neg = (data.get("negative_prompt") or "").strip().replace("\n", " ")

            # Force short prompt
            if len(prompt) > MAX_PROMPT_LEN:
                prompt = prompt[:MAX_PROMPT_LEN].rsplit(" ", 1)[0]

            # Always enforce our base negatives
            combined_neg = f"{BASE_NEGATIVE_PROMPT}, {neg}".strip(", ").strip()

            if len(combined_neg) > MAX_NEGATIVE_LEN:
                combined_neg = combined_neg[:MAX_NEGATIVE_LEN].rsplit(",", 1)[0]

            # If humans not allowed, ensure human negatives exist
            humans_allowed_out = bool(data.get("humans_allowed", False))
            if not humans_allowed_out and "people" not in combined_neg.lower():
                combined_neg = "people, human, face, " + combined_neg

            return {
                "prompt": prompt,
                "negative_prompt": combined_neg,
                "aspect_ratio": "16:9",
                "style": "cinematic realistic",
                "humans_allowed": humans_allowed_out,
                "provider": provider,
            }

        # ── Primary attempt: OpenAI ──
        try:
            response = openai_client.chat.completions.create(
                model=GPT_MODEL,
                temperature=0.25,
                max_tokens=300,
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

            return normalize_output(data, "openai")

        except (OpenAIError, json.JSONDecodeError, KeyError, Exception) as e:
            print(f"OpenAI failed: {e.__class__.__name__} – falling back to Grok...")

        # ── Fallback: xAI Grok ──
        FALLBACK_MODEL = "grok-4"
        try:
            response = xai_client.chat.completions.create(
                model=FALLBACK_MODEL,
                temperature=0.25,
                max_tokens=300,
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

            return normalize_output(data, "xai-grok")

        except Exception as fallback_e:
            raise RuntimeError(
                f"Both OpenAI and xAI fallback failed!\n"
                f"OpenAI: {e}\n"
                f"xAI:    {fallback_e}"
            )
