import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ArticleAgent:
    def run(self, topic: str):
        prompt = f"""
You are a professional news researcher and journalist.

Research and write a comprehensive, fact-based news article about: {topic}

Tone: neutral, objective, and informative
Style: professional newsroom writing
Focus on:
- Background and context
- Key developments and facts
- Why the topic matters
- Possible implications or next steps (without speculation)

Guidelines:
- Avoid opinions, hype, or promotional language
- Use clear, simple language for a global audience
- Ensure logical flow and clarity
- Do not use markdown, emojis, or bullet symbols

Length: approximately 800 words
"""

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        print(response.json())

        content = response.json()["choices"][0]["message"]["content"]

        return {"title": topic, "body": content}
