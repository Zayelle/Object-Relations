from contextlib import contextmanager
from lib.db.connection import get_connection
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

@contextmanager
def transaction():
    """Atomic transaction context manager"""
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        yield conn
        conn.execute("COMMIT")
        logger.info("Transaction committed")
    except Exception as e:
        conn.execute("ROLLBACK")
        logger.error(f"Transaction rolled back: {str(e)}")
        raise
    finally:
        conn.close()

def add_author_with_articles(author_name: str, articles_data: List[Dict[str, Any]]) -> bool:
    """
    Atomically add an author and their articles.
    articles_data: List of dicts with keys 'title', 'content', 'magazine_id'
    """
    from lib.models.author import Author
    from lib.models.article import Article

    try:
        with transaction() as conn:
            author = Author(id=None, name=author_name)
            author.save(conn=conn)  # author.id is set after save

            for article in articles_data:
                Article(
                    id=None,
                    title=article['title'],
                    content=article['content'],
                    author_id=author.id,
                    magazine_id=article['magazine_id']
                ).save(conn=conn)

            return True
    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
        return False