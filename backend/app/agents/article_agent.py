import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class ArticleAgent:
    def run(self, topic: str):
        """
        Generates a professional, fact-based news article body
        for the given topic. Returns ONLY article content.
        """

        system_message = (
            "You are a professional international news journalist. "
            "You write neutral, fact-based articles for a global audience. "
            "You never include headings, titles, prompts, or instructions "
            "in your output."
        )

        user_message = (
            f"Write a comprehensive news article about the following topic:\n\n"
            f"{topic}\n\n"
            "The article should provide background, key developments, "
            "and explain why the topic matters. "
            "Maintain a neutral and objective tone throughout. "
            "Use clear, professional language suitable for a global readership. "
            "Write in continuous paragraphs without bullet points or formatting. "
            "Do not include a title, summary, or conclusion label."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.35,
                max_tokens=1200,
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI Article generation failed: {e}")

        content = response.choices[0].message.content.strip()

        if not content:
            raise RuntimeError("OpenAI returned empty article content")

        return {
            "title": topic,
            "body": content,
        }
