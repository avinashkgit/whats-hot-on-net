import os
import certifi
from dotenv import load_dotenv
from openai import OpenAI
from gnews import GNews
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from openai import RateLimitError

from constants import XAI_MODEL

# -------------------------------------------------------------------
# Environment & TLS fix (cross-platform safe)
# -------------------------------------------------------------------

load_dotenv()

cert_path = certifi.where()
os.environ["SSL_CERT_FILE"] = cert_path
os.environ["REQUESTS_CA_BUNDLE"] = cert_path
os.environ["CURL_CA_BUNDLE"] = cert_path

# -------------------------------------------------------------------
# Validate API key
# -------------------------------------------------------------------

XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise RuntimeError("XAI_API_KEY not set in environment variables")

# -------------------------------------------------------------------
# Grok (xAI) client
# -------------------------------------------------------------------

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)


class ArticleAgent:
    """
    Media-grade article writer.

    Responsibilities:
    - Fetch latest verified context from Google News
    - Build a strict fact brief
    - Use Grok ONLY for writing
    - Prevent hallucinations and speculation
    """

    def __init__(self):
        self.google_news = GNews(
            language="en",
            country="US",
            max_results=5,
            period="1d"  # last 24 hours
        )

    # ---------------------------------------------------------------
    # Fetch latest news
    # ---------------------------------------------------------------

    def _fetch_news(self, topic: str):
        return self.google_news.get_news(topic)

    # ---------------------------------------------------------------
    # Build fact brief (hallucination guard)
    # ---------------------------------------------------------------

    def _build_fact_brief(self, news_items, topic: str):
        if not news_items:
            # Newsroom-safe fallback (NO hallucination)
            return f"""
No directly matching articles were found in the last 24 hours.

Topic:
{topic}

Instruction:
Write a factual background-based article.
Clearly state that recent developments are limited or unavailable.
Do NOT speculate or invent new events.
"""

        brief_parts = []
        for i, n in enumerate(news_items, 1):
            brief_parts.append(
                f"""
Source {i}:
Title: {n.get('title')}
Publisher: {n.get('publisher', {}).get('title')}
Published: {n.get('published date')}
Summary: {n.get('description')}
"""
            )

        return "\n".join(brief_parts)

    # ---------------------------------------------------------------
    # Grok call with retry (free-tier safe)
    # ---------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(min=5, max=60),
        stop=stop_after_attempt(5),
    )
    def _grok_write(self, prompt: str):
        return client.chat.completions.create(
            model=XAI_MODEL,
            input=prompt,
            temperature=0.3,
            max_output_tokens=1200,
        )

    # ---------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------

    def run(self, topic: str):
        """
        Generates a professional, neutral, fact-based news article body.
        Returns ONLY article content (no title, no headings).
        """

        # 1. Fetch latest facts
        news_items = self._fetch_news(topic)

        # 2. Build fact brief (anti-hallucination)
        fact_brief = self._build_fact_brief(news_items, topic)

        # 3. Journalist-grade writing prompt
        prompt = f"""
You are a professional international news journalist.

Write a comprehensive, neutral, fact-based news article
for a global audience about the topic below.

STRICT RULES:
- Use ONLY the facts provided
- Do NOT add or infer information
- Do NOT speculate or predict
- Do NOT invent names, numbers, or timelines
- If details are missing, clearly state they are unavailable
- Write in continuous paragraphs
- No headings, titles, bullet points, summaries, or labels

TOPIC:
{topic}

FACT BRIEF:
{fact_brief}
"""

        try:
            response = self._grok_write(prompt)
        except Exception as e:
            raise RuntimeError(f"Grok article generation failed: {e}")

        body = response.output_text.strip()

        if not body:
            raise RuntimeError("Grok returned empty article content")

        return {
            "title": topic,
            "body": body,
        }
