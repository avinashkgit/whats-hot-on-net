from agents.topic_agent import TopicAgent
from agents.article_agent import ArticleAgent
from agents.image_agent import ImageAgent
from app.db.database import SessionLocal
from app.db.repository import save_article

from dotenv import load_dotenv
load_dotenv()

def run():
    topic = TopicAgent().run()
    article = ArticleAgent().run(topic)
    image_url = ImageAgent().run(topic)

    db = SessionLocal()
    save_article(
        db=db,
        topic=topic,
        title=article["title"],
        body=article["body"],
        image_url=image_url
    )
    db.close()

if __name__ == "__main__":
    run()
