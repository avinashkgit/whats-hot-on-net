import requests
import os
from dotenv import load_dotenv
load_dotenv()

class ArticleAgent:
    def run(self, topic: str):
        prompt = f"""
        Write a professional news article about: {topic}
        Tone: neutral, informative
        Length: 800 words
        """

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        print(response.json())

        content = response.json()["choices"][0]["message"]["content"]

        return {
            "title": topic,
            "body": content
        }
