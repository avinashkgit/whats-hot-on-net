from agents.topic_agent import TopicAgent
from agents.article_agent import ArticleAgent

from dotenv import load_dotenv
load_dotenv()


def test_topic_agent():
    print("=== Testing TopicAgent ===")
    topic = TopicAgent().run()
    print("Topic:", topic)
    print()
    return topic


def test_article_agent(topic: str):
    print("=== Testing ArticleAgent ===")
    article = ArticleAgent().run(topic)

    print("Title:", article["title"])
    print()
    print("Body (first 500 chars):")
    print(article["body"][:500])
    print()
    print("Body length:", len(article["body"]))


if __name__ == "__main__":
    topic = test_topic_agent()
    # test_article_agent(topic)
