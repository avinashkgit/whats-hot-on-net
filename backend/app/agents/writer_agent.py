import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from google import genai
from google.genai import types
from constants import GPT_MODEL

load_dotenv()

# ── OpenAI (Primary) ─────────────────────────────────────────────
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ── xAI Grok (Secondary) ─────────────────────────────────────────
xai_client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

# ── Gemini (Tertiary) ────────────────────────────────────────────
gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
GEMINI_MODEL = "gemini-2.0-flash"  # Note: ensure model name matches available versions

ALLOWED_CATEGORIES = [
    "Global Affairs",
    "Science",
    "Tech",
    "Business",
    "Lifestyle",
    "Health",
    "Sports",
    "Entertainment",
    "Explainers",
]


class WriterAgent:
    def run(self, topic: str, context: str):
        system_message = (
            "You are a professional international news journalist.\n"
            "You must write using ONLY the provided context.\n"
            "You must NOT invent facts, quotes, or sources.\n"
            "You must output STRICTLY valid JSON that matches the schema.\n"
        )

        user_message = f"""
Write a full-length news article.

TOPIC:
{topic}

CONTEXT (ONLY SOURCE OF TRUTH):
{context}

WRITING RULES:
- Neutral journalistic tone
- Multiple paragraphs
- NO headings
- NO bullet points
- NO markdown
- NO explanations
- Body must be between 500 and 700 words
- Rewrite the title in your own words to make it more catchy, engaging, and reader-friendly while keeping the original meaning

CATEGORY RULE:
Choose EXACTLY ONE category from this list:
{", ".join(ALLOWED_CATEGORIES)}
"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        openai_error = None
        grok_error = None

        # ── 1️⃣ OpenAI ─────────────────────────────────────────────
        try:
            response = openai_client.chat.completions.create(
                model=GPT_MODEL,
                temperature=0.3,
                max_tokens=1800,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "news_article",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "title": {"type": "string"},
                                "summary": {"type": "string"},
                                "body": {"type": "string"},
                                "category": {
                                    "type": "string",
                                    "enum": ALLOWED_CATEGORIES,
                                },
                            },
                            "required": ["title", "summary", "body", "category"],
                        },
                    },
                },
            )

            msg = response.choices[0].message
            data = (
                msg.parsed
                if hasattr(msg, "parsed") and msg.parsed
                else json.loads(msg.content)
            )

            return {
                "title": data["title"].strip(),
                "summary": data["summary"].strip(),
                "body": data["body"].strip(),
                "category": data["category"],
                "provider": "openai",
            }

        except (OpenAIError, json.JSONDecodeError, KeyError, Exception) as e:
            openai_error = e
            print(f"OpenAI failed: {e.__class__.__name__} – falling back to Grok...")

        # ── 2️⃣ xAI Grok ───────────────────────────────────────────
        try:
            response = xai_client.chat.completions.create(
                model="grok-beta", # Update to your specific model identifier
                temperature=0.3,
                max_tokens=1800,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "news_article",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "title": {"type": "string"},
                                "summary": {"type": "string"},
                                "body": {"type": "string"},
                                "category": {
                                    "type": "string",
                                    "enum": ALLOWED_CATEGORIES,
                                },
                            },
                            "required": ["title", "summary", "body", "category"],
                        },
                    },
                },
            )

            msg = response.choices[0].message
            data = json.loads(msg.content)

            return {
                "title": data["title"].strip(),
                "summary": data["summary"].strip(),
                "body": data["body"].strip(),
                "category": data["category"],
                "provider": "xai-grok",
            }

        except Exception as e:
            grok_error = e
            print(f"Grok failed: {e.__class__.__name__} – falling back to Gemini...")

        # ── 3️⃣ Gemini ─────────────────────────────────────────────
        try:
            # Fixing the 'unexpected keyword argument' error
            # 1. Use 'config' instead of 'generation_config'
            # 2. Use 'system_instruction' inside config for cleaner steering
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_message,
                    temperature=0.3,
                    max_output_tokens=1800,
                    response_mime_type="application/json",
                    # Added response_schema to ensure Gemini follows your exact format
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "title": {"type": "STRING"},
                            "summary": {"type": "STRING"},
                            "body": {"type": "STRING"},
                            "category": {
                                "type": "STRING",
                                "enum": ALLOWED_CATEGORIES
                            },
                        },
                        "required": ["title", "summary", "body", "category"],
                    },
                ),
            )

            data = json.loads(response.text)

            return {
                "title": data["title"].strip(),
                "summary": data["summary"].strip(),
                "body": data["body"].strip(),
                "category": data["category"],
                "provider": "gemini",
            }

        except Exception as gemini_error:
            raise RuntimeError(
                "All providers failed!\n"
                f"OpenAI: {openai_error}\n"
                f"Grok:   {grok_error}\n"
                f"Gemini: {gemini_error}"
            )
