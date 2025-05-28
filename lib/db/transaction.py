from contextlib import contextmanager
from lib.db.connection import get_connection
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

@contextmanager
def transaction():
    """Context manager for database transactions"""
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        yield conn
        conn.execute("COMMIT")
        logger.info("Transaction committed successfully")
    except Exception as e:
        conn.execute("ROLLBACK")
        logger.error(f"Transaction rolled back: {str(e)}")
        raise
    finally:
        conn.close()

def add_author_with_articles(author_name: str, articles_data: List[Dict[str, Any]]) -> bool:
    """
    Add an author and their articles in a single transaction
    :param author_name: Name of the author to create
    :param articles_data: List of dicts with 'title', 'content', and 'magazine_id'
    :return: True if successful, False otherwise
    """
    from lib.models.author import Author
    from lib.models.article import Article
    
    try:
        with transaction() as conn:
            # Create author
            author = Author(id=None, name=author_name)
            cursor = conn.execute(
                "INSERT INTO authors (name) VALUES (?) RETURNING id, created_at",
                (author.name,)
            )
            result = cursor.fetchone()
            author.id = result['id']
            author.created_at = result['created_at']
            
            # Create articles
            for article_data in articles_data:
                Article(
                    id=None,
                    title=article_data['title'],
                    content=article_data.get('content', ''),
                    author_id=author.id,
                    magazine_id=article_data['magazine_id']
                ).save(conn=conn)
            
            return True
    except Exception as e:
        logger.error(f"Failed to create author with articles: {str(e)}")
        return False