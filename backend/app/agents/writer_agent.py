import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from constants import GPT_MODEL

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class WriterAgent:
    def run(self, topic: str, context: str):
        system_message = (
            "You are a professional international news journalist. "
            "You must write ONLY using the provided context. "
            "Do not speculate or add external information. "
            "You must respond ONLY with valid JSON."
        )

        user_message = f"""
Write a comprehensive news article about the topic below
using ONLY the provided context.

TOPIC:
{topic}

CONTEXT:
{context}

Rules:
- Neutral tone
- No bullet points
- No headings
- No markdown
- No explanations
- Article title should be attractive and crisp
- Keep the article engaging and informative
- Must have Multiple paragraphs
- Return ONLY valid JSON in this exact format:

{{
  "title": "updated article title here",
  "body": "full article text here"
}}
"""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1200,
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON returned:\n{raw_output}") from e

        if not data.get("body"):
            raise RuntimeError("Empty article body")

        return data
