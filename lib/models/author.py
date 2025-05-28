from lib.db.connection import get_connection
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from lib.models.article import Article
    from lib.models.magazine import Magazine

logger = logging.getLogger(__name__)

@dataclass
class Author:
    id: Optional[int]
    name: str
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validate author data on initialization"""
        self._validate_name()

    def _validate_name(self):
        """Centralized name validation logic"""
        if not isinstance(self.name, str):
            raise TypeError("Author name must be a string")
        if not self.name.strip():
            raise ValueError("Author name cannot be blank")
        if len(self.name) > 255:
            raise ValueError("Author name cannot exceed 255 characters")

    def save(self) -> bool:
        """Persist author to database, returns success status"""
        try:
            with get_connection() as conn:
                if self.id is None:
                    return self._create_author(conn)
                return self._update_author(conn)
        except Exception as e:
            logger.error(f"Failed to save author {self.id}: {str(e)}")
            raise

    def _create_author(self, conn) -> bool:
        """Handle new author creation"""
        cursor = conn.execute(
            "INSERT INTO authors (name) VALUES (?) RETURNING id, created_at",
            (self.name,)
        )
        result = cursor.fetchone()
        self.id = result['id']
        self.created_at = result['created_at']
        logger.info(f"Created new author ID {self.id}")
        return True

    def _update_author(self, conn) -> bool:
        """Handle existing author updates"""
        conn.execute(
            "UPDATE authors SET name = ? WHERE id = ?",
            (self.name, self.id)
        )
        logger.info(f"Updated author ID {self.id}")
        return True

    @classmethod
    def find_by_id(cls, author_id: int) -> Optional['Author']:
        """Find single author by ID with error handling"""
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM authors WHERE id = ?", 
                    (author_id,)
                ).fetchone()
                return cls._row_to_author(row) if row else None
        except Exception as e:
            logger.error(f"Error finding author {author_id}: {str(e)}")
            raise

    @classmethod
    def find_by_name(cls, name: str, exact: bool = False) -> List['Author']:
        """Find authors by name with flexible matching"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM authors WHERE name = ?" if exact else "SELECT * FROM authors WHERE name LIKE ?"
                param = name if exact else f"%{name}%"
                rows = conn.execute(query, (param,)).fetchall()
                return [cls._row_to_author(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding authors by name '{name}': {str(e)}")
            raise

    def articles(self, limit: Optional[int] = None) -> List['Article']:
        """Get author's articles with optional pagination"""
        from lib.models.article import Article
        try:
            with get_connection() as conn:
                query = "SELECT * FROM articles WHERE author_id = ?" + (" LIMIT ?" if limit else "")
                params = (self.id, limit) if limit else (self.id,)
                rows = conn.execute(query, params).fetchall()
                return [Article._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching articles for author {self.id}: {str(e)}")
            raise

    def magazines(self) -> List['Magazine']:
        """Get distinct magazines author has written for"""
        from lib.models.magazine import Magazine
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT DISTINCT m.* FROM magazines m
                    JOIN articles a ON m.id = a.magazine_id
                    WHERE a.author_id = ?""",
                    (self.id,)
                ).fetchall()
                return [Magazine._row_to_magazine(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching magazines for author {self.id}: {str(e)}")
            raise

    @classmethod
    def _row_to_author(cls, row: Dict[str, Any]) -> 'Author':
        """Convert database row to Author instance"""
        return cls(
            id=row['id'],
            name=row['name'],
            created_at=row['created_at']
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'article_count': len(self.articles()),
            'magazine_count': len(self.magazines())
        }