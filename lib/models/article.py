from lib.db.connection import get_connection
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from lib.models.author import Author
    from lib.models.magazine import Magazine

logger = logging.getLogger(__name__)

@dataclass
class Article:
    id: Optional[int]
    title: str
    content: str
    author_id: int
    magazine_id: int
    published_at: Optional[str] = None

    def __post_init__(self):
        """Validate article data on initialization"""
        self._validate_fields()

    def _validate_fields(self):
        """Centralized field validation logic"""
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Article title must be a non-empty string")
        if len(self.title) > 255:
            raise ValueError("Article title cannot exceed 255 characters")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Article content must be a non-empty string")
        if not isinstance(self.author_id, int) or self.author_id <= 0:
            raise ValueError("Author ID must be a positive integer")
        if not isinstance(self.magazine_id, int) or self.magazine_id <= 0:
            raise ValueError("Magazine ID must be a positive integer")

    def save(self) -> bool:
        """Persist article to database, returns success status"""
        try:
            with get_connection() as conn:
                if self.id is None:
                    return self._create_article(conn)
                return self._update_article(conn)
        except Exception as e:
            logger.error(f"Failed to save article {self.id}: {str(e)}")
            raise

    def _create_article(self, conn) -> bool:
        """Handle new article creation"""
        cursor = conn.execute(
            """INSERT INTO articles 
            (title, content, author_id, magazine_id) 
            VALUES (?, ?, ?, ?) 
            RETURNING id, published_at""",
            (self.title, self.content, self.author_id, self.magazine_id)
        )
        result = cursor.fetchone()
        self.id = result['id']
        self.published_at = result['published_at']
        logger.info(f"Created new article ID {self.id}")
        return True

    def _update_article(self, conn) -> bool:
        """Handle existing article updates"""
        conn.execute(
            """UPDATE articles SET 
            title = ?, content = ?, 
            author_id = ?, magazine_id = ? 
            WHERE id = ?""",
            (self.title, self.content, self.author_id, self.magazine_id, self.id)
        )
        logger.info(f"Updated article ID {self.id}")
        return True

    @classmethod
    def find_by_id(cls, article_id: int) -> Optional['Article']:
        """Find single article by ID with error handling"""
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM articles WHERE id = ?", 
                    (article_id,)
                ).fetchone()
                return cls._row_to_article(row) if row else None
        except Exception as e:
            logger.error(f"Error finding article {article_id}: {str(e)}")
            raise

    @classmethod
    def find_by_title(cls, title: str, exact: bool = False) -> List['Article']:
        """Find articles by title with flexible matching"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM articles WHERE title = ?" if exact else "SELECT * FROM articles WHERE title LIKE ?"
                param = title if exact else f"%{title}%"
                rows = conn.execute(query, (param,)).fetchall()
                return [cls._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding articles by title '{title}': {str(e)}")
            raise

    @classmethod
    def find_by_author(cls, author_id: int, limit: Optional[int] = None) -> List['Article']:
        """Find articles by author with optional pagination"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM articles WHERE author_id = ?" + (" LIMIT ?" if limit else "")
                params = (author_id, limit) if limit else (author_id,)
                rows = conn.execute(query, params).fetchall()
                return [cls._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding articles by author {author_id}: {str(e)}")
            raise

    @classmethod
    def find_by_magazine(cls, magazine_id: int, limit: Optional[int] = None) -> List['Article']:
        """Find articles by magazine with optional pagination"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM articles WHERE magazine_id = ?" + (" LIMIT ?" if limit else "")
                params = (magazine_id, limit) if limit else (magazine_id,)
                rows = conn.execute(query, params).fetchall()
                return [cls._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding articles by magazine {magazine_id}: {str(e)}")
            raise

    @classmethod
    def recent_articles(cls, days: int = 30, limit: int = 10) -> List['Article']:
        """Find recently published articles"""
        try:
            with get_connection() as conn:
                cutoff_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                rows = conn.execute(
                    """SELECT * FROM articles 
                    WHERE published_at >= datetime(?, ?) 
                    ORDER BY published_at DESC 
                    LIMIT ?""",
                    (cutoff_date, f'-{days} days', limit)
                ).fetchall()
                return [cls._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding recent articles: {str(e)}")
            raise

    @property
    def author(self) -> 'Author':
        """Get the author of this article"""
        from lib.models.author import Author
        return Author.find_by_id(self.author_id)

    @property
    def magazine(self) -> 'Magazine':
        """Get the magazine this article belongs to"""
        from lib.models.magazine import Magazine
        return Magazine.find_by_id(self.magazine_id)

    @classmethod
    def _row_to_article(cls, row: Dict[str, Any]) -> 'Article':
        """Convert database row to Article instance"""
        return cls(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author_id=row['author_id'],
            magazine_id=row['magazine_id'],
            published_at=row['published_at']
        )

    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert instance to dictionary, optionally with relationships"""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'published_at': self.published_at,
            'author_id': self.author_id,
            'magazine_id': self.magazine_id
        }
        if include_relationships:
            data['author'] = self.author.to_dict() if self.author else None
            data['magazine'] = self.magazine.to_dict() if self.magazine else None
        return data

    @classmethod
    def find_most_prolific_author(cls) -> Optional['Author']:
        """Find the author who has written the most articles"""
        from lib.models.author import Author
        try:
            with get_connection() as conn:
                row = conn.execute(
                    """SELECT a.* FROM authors a
                    JOIN (
                        SELECT author_id, COUNT(*) as article_count
                        FROM articles
                        GROUP BY author_id
                        ORDER BY article_count DESC
                        LIMIT 1
                    ) ac ON a.id = ac.author_id"""
                ).fetchone()
                return Author._row_to_author(row) if row else None
        except Exception as e:
            logger.error(f"Error finding most prolific author: {str(e)}")
            raise