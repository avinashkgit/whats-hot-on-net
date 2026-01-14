import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from constants import GPT_MODEL

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ALLOWED_CATEGORIES = [
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
- Body must be between 800 and 1000 words
- If unable to reach 800 words from context, expand logically WITHOUT adding new facts

CATEGORY RULE:
Choose EXACTLY ONE category from this list:
{", ".join(ALLOWED_CATEGORIES)}
"""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            temperature=0.3,
            max_tokens=1800,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "news_article",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear and engaging article title",
                            },
                            "summary": {
                                "type": "string",
                                "description": "2–3 sentence concise summary",
                            },
                            "body": {
                                "type": "string",
                                "description": "500-600 word article body in multiple paragraphs",
                            },
                            "category": {"type": "string", "enum": ALLOWED_CATEGORIES},
                        },
                        "required": ["title", "summary", "body", "category"],
                    },
                },
            },
        )

        msg = response.choices[0].message

        if hasattr(msg, "parsed") and msg.parsed is not None:
            data = msg.parsed
        else:
            data = json.loads(msg.content)

        return {
            "title": data["title"].strip(),
            "summary": data["summary"].strip(),
            "body": data["body"].strip(),
            "category": data["category"],
        }
