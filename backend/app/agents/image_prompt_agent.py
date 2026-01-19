import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from constants import GPT_MODEL

load_dotenv()

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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

# ✅ Strong default negatives (stable + consistent)
BASE_NEGATIVE_PROMPT = """
people, human, crowd, face, faces, portrait, selfie, close-up,
hands, fingers, extra fingers, extra limbs, deformed body, mutated, distorted anatomy,
cartoon, anime, illustration, CGI, 3D render, plastic look,
text, caption, subtitles, watermark, logo, signature, branding, poster,
low quality, blurry, grainy, noise, jpeg artifacts, oversaturated,
weird objects, floating objects, duplicated objects, broken geometry
""".strip()


def category_scene_hint(topic: str, category: str | None) -> str:
    """
    Adds category-aware environment guidance.
    We avoid "people doing X" scenes because that creates weird humans.
    """
    t = (topic or "").lower()

    if category == "Science":
        return "scientific environment: observatory, lab equipment, telescope, research facility, satellites, clean futuristic infrastructure"
    if category == "Tech":
        return "technology environment: modern data center, server racks, circuit boards, AI-themed abstract light trails, futuristic city skyline"
    if category == "Market":
        return "finance environment: city financial district skyline, stock market screens (unreadable), modern corporate buildings, trading floor wide shot"
    if category == "Health":
        return "health environment: hospital exterior, ambulance bay, medical lab, pharmacy shelves (no readable labels), clean sterile lighting"
    if category == "Sports":
        return "sports environment: stadium wide shot, floodlights, empty field/court, sports equipment in foreground, dramatic sky"
    if category == "Entertainment":
        return "entertainment environment: cinema hall wide shot, stage lighting, concert venue, red carpet area without people"
    if category == "Lifestyle":
        return "lifestyle environment: city street, café exterior, modern home interior wide shot, travel landscape, minimal objects"
    if category == "Explainers":
        return "neutral explainer environment: abstract newsroom set, modern studio, minimal clean background, symbolic objects related to topic"

    # Auto-detect fallback hints from topic keywords
    if any(x in t for x in ["train", "rail", "metro", "station"]):
        return "transport environment: railway tracks, station platforms, signal lights, maintenance equipment, wide perspective"
    if any(x in t for x in ["war", "attack", "conflict", "missile"]):
        return "serious news environment: distant skyline, smoke in background, military vehicles far away, dramatic clouds (no people visible)"
    if any(x in t for x in ["flood", "storm", "earthquake", "disaster"]):
        return "disaster environment: wide landscape, damaged roads/buildings, emergency lights far away, dramatic weather (no people visible)"

    return "news environment: realistic cityscape, infrastructure, landscape, weather, wide establishing shot"


class ImagePromptAgent:
    def run(self, topic: str, category: str = None):
        """
        Returns scenic image prompt for article thumbnail generation.

        Output JSON:
        {
          "prompt": "...",
          "negative_prompt": "...",
          "aspect_ratio": "16:9",
          "style": "cinematic realistic",
          "humans_allowed": false
        }
        """

        # Normalize category
        if category and category not in ALLOWED_CATEGORIES:
            category = None

        # ✅ Default: disallow humans (prevents weird people)
        humans_allowed = False

        # If topic clearly requires humans, allow them (rare)
        # You can tune this list based on your website needs.
        topic_l = (topic or "").lower()
        if any(x in topic_l for x in ["election rally", "celebrity", "actor", "player interview", "protest", "crowd"]):
            humans_allowed = True

        scene_hint = category_scene_hint(topic, category)

        system_message = (
            "You are an Image Prompt Writer Agent for a news/articles website.\n"
            "You write prompts for image generation models (FLUX / Gemini / Grok).\n"
            "Your job: produce a single clean, scenic, wide cinematic thumbnail prompt.\n"
            "Avoid humans unless explicitly allowed.\n"
            "Return STRICT JSON only. No markdown. No extra text.\n"
        )

        user_message = f"""
Create ONE best prompt for a news/blog thumbnail image.

TOPIC:
{topic}

CATEGORY:
{category or "Auto-detect"}

SCENE HINT:
{scene_hint}

GOAL:
A wide scenic cinematic realistic photojournalism image that represents the topic clearly.

HARD RULES:
- Aspect ratio must be 16:9 landscape
- Establishing shot, wide-angle lens, 24mm, deep depth of field
- No close-up portraits, no faces
- No text/logos/watermarks
- Keep it realistic and clean (no surreal artifacts)

HUMANS POLICY:
- humans_allowed = {str(humans_allowed).lower()}
- If humans_allowed is false: the scene must contain NO people at all

OUTPUT JSON FIELDS:
- prompt: single line prompt
- negative_prompt: a strong comma-separated list
- aspect_ratio: "16:9"
- style: "cinematic realistic"
- humans_allowed: true/false
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
            # Ensure stable output
            prompt = data["prompt"].strip().replace("\n", " ")
            style = data["style"].strip()
            aspect_ratio = data["aspect_ratio"].strip()

            # ✅ Force our baseline negatives (LLM can add more, but can't remove these)
            model_negative = (data.get("negative_prompt") or "").strip()
            combined_negative = f"{BASE_NEGATIVE_PROMPT}, {model_negative}".strip(", ").strip()

            # Small safety: if humans not allowed, ensure human terms exist in negative
            if not data.get("humans_allowed", False):
                if "people" not in combined_negative.lower():
                    combined_negative = "people, human, crowd, face, " + combined_negative

            return {
                "prompt": prompt,
                "negative_prompt": combined_negative,
                "aspect_ratio": aspect_ratio if aspect_ratio else "16:9",
                "style": style if style else "cinematic realistic",
                "humans_allowed": bool(data.get("humans_allowed", False)),
                "provider": provider,
            }

        # ── Primary: OpenAI ─────────────────────────────────────────────────────
        try:
            response = openai_client.chat.completions.create(
                model=GPT_MODEL,
                temperature=0.25,  # lower = more consistent
                max_tokens=450,
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

        # ── Fallback: xAI Grok ─────────────────────────────────────────────────
        FALLBACK_MODEL = "grok-4"
        try:
            response = xai_client.chat.completions.create(
                model=FALLBACK_MODEL,
                temperature=0.25,
                max_tokens=450,
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
