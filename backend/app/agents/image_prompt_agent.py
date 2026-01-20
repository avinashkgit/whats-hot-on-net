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

    # ✅ Ensure prompt length never exceeds 1024 characters
    MAX_PROMPT_LEN = 1024

    # ✅ Optional: also cap negative prompt length (recommended)
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

    BASE_NEGATIVE = (
        "people, human, face, hands, fingers, extra limbs, deformed, blurry, low quality, "
        "watermark, caption, cartoon, anime, 3d render, plastic look, "
        "subtitles, banner"
    )

    CINEMATIC_TAIL = (
        "16:9 wide frame, 24mm lens look, wide establishing shot, deep perspective, "
        "strong foreground-midground-background separation, cinematic lighting, ultra realistic, "
        "documentary style, no readable text"
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
                "negative_prompt": self.BASE_NEGATIVE[: self.MAX_NEGATIVE_LEN],
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

        # ✅ Enhanced cinematic scene hints (environment-focused)
        scene_hints = {
            "Science": (
                "wide cinematic shot inside a high-tech research facility, clean stainless workbenches, "
                "glowing microscopes and spectrometers, glass beakers and lab rigs, subtle blue accent lights, "
                "soft haze for depth, dramatic rim lighting, ultra-real documentary look"
            ),
            "Tech": (
                "wide cinematic establishing shot of futuristic technology environment, server racks in a modern data center, "
                "fiber optic cables, glowing status LEDs, reflections on polished floor, neon blue/purple highlights, "
                "volumetric light beams, high contrast, sleek cyber-modern atmosphere"
            ),
            "Market": (
                "wide cinematic financial district skyline at dusk, tall glass skyscrapers, stock exchange exterior, "
                "city traffic light trails, reflective wet streets, moody clouds, dramatic lighting, "
                "subtle bokeh highlights, documentary realism, global economy vibe"
            ),
            "Lifestyle": (
                "wide cinematic modern lifestyle scene, minimalist interior with soft natural window light, "
                "warm neutral tones, indoor plants, cozy textures, calm city street outside, "
                "travel postcard atmosphere, gentle depth-of-field, peaceful premium editorial look"
            ),
            "Health": (
                "wide cinematic modern hospital exterior or medical research facility, clean white architecture, "
                "ambulance bay lights, sterile medical lab ambiance, clinical blue-white lighting, "
                "subtle fog/haze for depth, high realism, serious documentary mood"
            ),
            "Sports": (
                "wide cinematic empty stadium at night, towering floodlights cutting through light mist, "
                "dramatic shadows on the field, arena architecture in the background, "
                "high contrast, intense atmosphere, epic sports documentary establishing shot"
            ),
            "Entertainment": (
                "wide cinematic concert stage or cinema theater interior, large spotlights and rigging, "
                "smoke haze, glowing LED panels (no readable text), rich warm highlights, "
                "dramatic lighting, glossy reflections, premium showbiz mood"
            ),
            "Explainers": (
                "wide cinematic newsroom-style environment, modern studio set, large abstract screens and light panels "
                "(no readable text), clean professional lighting, subtle depth and reflections, "
                "serious informative documentary tone"
            ),
            "News": (
                "wide cinematic breaking-news atmosphere, city skyline under dramatic storm clouds, "
                "emergency lights in the distance, wet asphalt reflections, "
                "high tension mood, cinematic realism, documentary establishing shot"
            ),
            None: (
                "wide cinematic establishing shot of a real-world cityscape or landscape, "
                "dramatic natural lighting, atmospheric haze, strong depth and scale, "
                "documentary realism, premium news thumbnail mood"
            ),
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
Cinematic style tail: {self.CINEMATIC_TAIL}

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

            # ✅ Append cinematic tail if model didn't include it
            if self.CINEMATIC_TAIL.lower() not in prompt.lower():
                prompt = f"{prompt}, {self.CINEMATIC_TAIL}".strip(", ")

            # ✅ Enforce max prompt length
            prompt = prompt[: self.MAX_PROMPT_LEN].strip()

            # ✅ Merge negatives and enforce max negative length
            negative = f"{self.BASE_NEGATIVE}, {neg}".strip(", ").strip()
            if not allow_humans and "people" not in negative.lower():
                negative = "people, human, face, crowd, " + negative

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
                temperature=0.3,
                max_tokens=260,
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
                max_tokens=260,
                messages=messages,
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            return normalize(data, "xai-grok")

        except Exception as e:
            return {
                "prompt": (
                    f"wide cinematic establishing shot of {topic}, {self.CINEMATIC_TAIL}"
                )[: self.MAX_PROMPT_LEN].strip(),
                "negative_prompt": self.BASE_NEGATIVE[: self.MAX_NEGATIVE_LEN],
                "humans_allowed": allow_humans,
                "provider": "fallback-default",
                "error": str(e)[:120],
            }
