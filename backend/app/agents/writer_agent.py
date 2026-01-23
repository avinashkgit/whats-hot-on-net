import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError  # ← important: catch OpenAIError
from constants import GPT_MODEL

load_dotenv()

# Primary client (OpenAI)
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Fallback client (xAI Grok) — same interface!
xai_client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

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

        # ── Primary attempt: OpenAI ──
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
                        "strict": True,  # recommended in newer versions
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

            if hasattr(msg, "parsed") and msg.parsed:
                data = msg.parsed
            else:
                data = json.loads(msg.content)

            return {
                "title": data["title"].strip(),
                "summary": data["summary"].strip(),
                "body": data["body"].strip(),
                "category": data["category"],
                "provider": "openai",  # optional: for logging/analytics
            }

        except (OpenAIError, json.JSONDecodeError, KeyError, Exception) as e:
            print(f"OpenAI failed: {e.__class__.__name__} – falling back to Grok...")

        # ── Fallback: xAI Grok ───────────────────────────────────────────────
        # Choose model according to your needs & budget (2026 status)
        # Good options: grok-4, grok-4-fast, grok-4-1-fast-reasoning, etc.
        FALLBACK_MODEL = "grok-4"  # ← change to whatever you have access to

        try:
            response = xai_client.chat.completions.create(
                model=FALLBACK_MODEL,
                temperature=0.3,
                max_tokens=1800,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {  # same schema
                        "name": "news_article",
                        "strict": True,
                        "schema": {  # ← copy the same schema
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

            if hasattr(msg, "parsed") and msg.parsed:
                data = msg.parsed
            else:
                data = json.loads(msg.content)

            return {
                "title": data["title"].strip(),
                "summary": data["summary"].strip(),
                "body": data["body"].strip(),
                "category": data["category"],
                "provider": "xai-grok",
            }

        except Exception as fallback_e:
            raise RuntimeError(
                f"Both OpenAI and xAI fallback failed!\n"
                f"OpenAI: {e}\n"
                f"xAI:    {fallback_e}"
            )
