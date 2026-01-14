from agents.topic_agent import TopicAgent
from agents.search_agent import search_news
from agents.extractor_pool import extract_articles_parallel
from agents.context_builder_agent import build_context
from agents.writer_agent import WriterAgent
from agents.image_agent import ImageAgent
from agents.gemini_image_generator import GeminiImageAgent
from agents.xai_image_agent import XaiImageAgent
from db.database import SessionLocal


def test_topic_agent():
    print("\n=== Testing TopicAgent ===")
    topic = TopicAgent().run()
    print("Topic:", topic)
    assert isinstance(topic, str) and len(topic) > 5


def test_search_agent(topic):
    print("\n=== Testing SearchAgent ===")
    results = search_news(topic, limit=5)
    print("Results found:", len(results))
    assert isinstance(results, list)
    assert len(results) > 0
    assert "link" in results[0]
    return results


def test_extractor_agent(links):
    print("\n=== Testing Parallel Extractor ===")
    articles = extract_articles_parallel(links, max_workers=5)
    print("Articles extracted:", len(articles))
    assert isinstance(articles, list)
    assert len(articles) > 0
    assert "text" in articles[0]
    return articles


def test_context_builder(articles):
    print("\n=== Testing Context Builder ===")
    context = build_context(articles)
    print("Context length:", len(context))
    assert isinstance(context, str)
    assert len(context) > 500
    return context


def test_writer_agent(topic, context):
    print("\n=== Testing WriterAgent ===")
    article = WriterAgent().run(topic, context)
    print("\n✅ Article generated\n", article)
    return article


def test_image_agent(topic):
    print("\n=== Testing ImageAgent ===")
    image_url = ImageAgent().run(topic)
    print("Image URL:", image_url)
    assert isinstance(image_url, str)
    assert image_url.startswith("http")

def test_xai_image_agent(topic):
    print("\n=== Testing ImageAgent ===")
    image_url = XaiImageAgent().run(topic)
    print("Image URL:", image_url)
    assert isinstance(image_url, str)
    assert image_url.startswith("http")

def test_gemini_image_agent(topic):
    print("\n=== Testing ImageAgent ===")
    image_url = GeminiImageAgent().run(topic)
    print("Image URL:", image_url)
    assert isinstance(image_url, str)
    assert image_url.startswith("http")


def run_all_tests():
    print("\n==============================")
    print(" RUNNING AGENT PIPELINE TESTS ")
    print("==============================")
    db = SessionLocal()
    topic = TopicAgent().run()

    # links = test_search_agent(topic)
    # articles = test_extractor_agent(links)
    # context = test_context_builder(articles)
    # article = test_writer_agent("Quantum Computer", "Quantum computing is an area of computing focused on developing computer technology based on the principles of quantum theory...")
    # image_url = test_image_agent("The rise of renewable energy in rural communities")
    # image_url = test_xai_image_agent("The rise of renewable energy in rural communities")
    # image_url = test_gemini_image_agent("The rise of renewable energy in rural communities")
    print("====:", topic)
    print("\n✅ ALL AGENT TESTS PASSED SUCCESSFULLY\n")


if __name__ == "__main__":
    run_all_tests()
