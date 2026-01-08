import os
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
            "Do not speculate or add external information."
        )

        user_message = f"""
Write a comprehensive news article about:

{topic}

Use ONLY the context below.

CONTEXT:
{context}

Rules:
- Neutral tone
- No bullet points
- No headings
- Continuous paragraphs
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

        body = response.choices[0].message.content.strip()
        if not body:
            raise RuntimeError("Empty article")

        return {"title": topic, "body": body}
