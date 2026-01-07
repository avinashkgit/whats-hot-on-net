import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class TopicAgent:
    def run(self) -> str:
        """
        Returns a single globally trending news topic
        suitable for an AI-written article.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a global news editor selecting topics for an international newsroom. "
                        "Each time you are asked, you must identify ONE currently trending worldwide news topic. "
                        "You should actively vary the type of topic across runs, rotating between areas such as "
                        "geopolitics, global economy, technology, science, climate, public policy, health, or international relations. "
                        "Avoid repeating similar themes unless they clearly dominate global news coverage."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Provide ONE concise, professional global news topic suitable for a full-length article. "
                        "The topic must be factual, timely, and globally relevant. "
                        "Avoid clickbait language, emojis, quotes, or explanations. "
                        "Return only the topic headline."
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=30,
        )

        topic = response.choices[0].message.content.strip()

        # Safety fallback (never return empty)
        if not topic:
            return "Global technology, economic, and geopolitical developments"

        return topic
