import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from constants import GPT_MODEL

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


ALLOWED_TOPICS = [
    "Home",
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


class WriterAgent:
    def run(self, topic: str, context: str):
        system_message = (
            "You are a professional international news journalist.\n"
            "You MUST write strictly using the provided context only.\n"
            "You MUST classify the article into ONE allowed topic.\n"
            "You MUST return ONLY valid JSON.\n"
            "You MUST NOT invent facts, sources, or categories.\n"
            "If unsure, choose the closest logical topic.\n"
        )

        user_message = f"""
Write a comprehensive news article using ONLY the provided context.

ORIGINAL TOPIC IDEA:
{topic}

CONTEXT:
{context}

STRICT RULES:
- Neutral journalistic tone
- No bullet points
- No headings
- No markdown
- No explanations
- Multiple paragraphs must
- Engaging but factual
- NO extra text outside JSON

You MUST classify the article into EXACTLY ONE of these topics:
{", ".join(ALLOWED_TOPICS)}

Return ONLY valid JSON in this EXACT format:

{{
  "title": "clear and engaging article title",
  "summary": "2–3 sentence concise summary",
  "body": "full article text in multiple paragraphs",
  "topic": "ONE value from the allowed list"
}}
"""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1400,
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON returned by model:\n{raw_output}") from e

        # =========================
        # VALIDATION (HARD GUARDS)
        # =========================
        if not data.get("title"):
            raise RuntimeError("Missing title")

        if not data.get("summary"):
            raise RuntimeError("Missing summary")

        if not data.get("body"):
            raise RuntimeError("Missing article body")

        topic_value = data.get("topic")

        if topic_value not in ALLOWED_TOPICS:
            raise RuntimeError(
                f"Invalid topic '{topic_value}'. " f"Must be one of {ALLOWED_TOPICS}"
            )

        return {
            "title": data["title"].strip(),
            "summary": data["summary"].strip(),
            "body": data["body"].strip(),
            "topic": topic_value,
        }
