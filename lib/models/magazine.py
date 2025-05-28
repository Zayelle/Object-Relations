from __future__ import annotations
from lib.db.connection import get_connection
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from lib.models.article import Article
    from lib.models.author import Author

logger = logging.getLogger(__name__)

@dataclass
class Magazine:
    id: Optional[int]
    name: str
    category: str
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validate magazine data on initialization"""
        self._validate_fields()

    def _validate_fields(self):
        """Centralized field validation logic"""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Magazine name must be a non-empty string")
        if len(self.name) > 255:
            raise ValueError("Magazine name cannot exceed 255 characters")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("Category must be a non-empty string")

    def save(self) -> bool:
        """Persist magazine to database, returns success status"""
        try:
            with get_connection() as conn:
                if self.id is None:
                    return self._create_magazine(conn)
                return self._update_magazine(conn)
        except Exception as e:
            logger.error(f"Failed to save magazine {self.id}: {str(e)}")
            raise

    def _create_magazine(self, conn) -> bool:
        """Handle new magazine creation"""
        cursor = conn.execute(
            "INSERT INTO magazines (name, category) VALUES (?, ?) RETURNING id, created_at",
            (self.name, self.category)
        )
        result = cursor.fetchone()
        self.id = result['id']
        self.created_at = result['created_at']
        logger.info(f"Created new magazine ID {self.id}")
        return True

    def _update_magazine(self, conn) -> bool:
        """Handle existing magazine updates"""
        conn.execute(
            "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
            (self.name, self.category, self.id)
        )
        logger.info(f"Updated magazine ID {self.id}")
        return True

    @classmethod
    def find_by_id(cls, magazine_id: int) -> Optional['Magazine']:
        """Find single magazine by ID with error handling"""
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM magazines WHERE id = ?", 
                    (magazine_id,)
                ).fetchone()
                return cls._row_to_magazine(row) if row else None
        except Exception as e:
            logger.error(f"Error finding magazine {magazine_id}: {str(e)}")
            raise

    @classmethod
    def find_by_name(cls, name: str, exact: bool = False) -> List['Magazine']:
        """Find magazines by name with flexible matching"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM magazines WHERE name = ?" if exact else "SELECT * FROM magazines WHERE name LIKE ?"
                param = name if exact else f"%{name}%"
                rows = conn.execute(query, (param,)).fetchall()
                return [cls._row_to_magazine(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding magazines by name '{name}': {str(e)}")
            raise

    @classmethod
    def find_by_category(cls, category: str, exact: bool = False) -> List['Magazine']:
        """Find magazines by category with flexible matching"""
        try:
            with get_connection() as conn:
                query = "SELECT * FROM magazines WHERE category = ?" if exact else "SELECT * FROM magazines WHERE category LIKE ?"
                param = category if exact else f"%{category}%"
                rows = conn.execute(query, (param,)).fetchall()
                return [cls._row_to_magazine(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding magazines by category '{category}': {str(e)}")
            raise

    def articles(self) -> List['Article']:
        """Optimized with ordering by publication date"""
        from lib.models.article import Article
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT * FROM articles 
                    WHERE magazine_id = ? 
                    ORDER BY published_at DESC""",
                    (self.id,)
                ).fetchall()
                return [Article._row_to_article(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching articles for magazine {self.id}: {str(e)}")
            raise

    def contributors(self) -> List['Author']:
        """Get all authors who have written for this magazine"""
        from lib.models.author import Author
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT DISTINCT a.* FROM authors a
                    JOIN articles ar ON a.id = ar.author_id
                    WHERE ar.magazine_id = ?""",
                    (self.id,)
                ).fetchall()
                return [Author._row_to_author(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching contributors for magazine {self.id}: {str(e)}")
            raise

    @classmethod
    def find_popular_magazines(cls, min_authors: int = 2) -> List['Magazine']:
        """Find magazines with articles by at least N different authors"""
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT m.* FROM magazines m
                    JOIN (
                        SELECT magazine_id, COUNT(DISTINCT author_id) as author_count
                        FROM articles
                        GROUP BY magazine_id
                        HAVING author_count >= ?
                    ) ac ON m.id = ac.magazine_id""",
                    (min_authors,)
                ).fetchall()
                return [cls._row_to_magazine(row) for row in rows]
        except Exception as e:
            logger.error(f"Error finding popular magazines: {str(e)}")
            raise

    @classmethod
    def with_article_counts(cls) -> Dict[int, int]:
        """Count the number of articles in each magazine"""
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT magazine_id, COUNT(*) as article_count
                    FROM articles
                    GROUP BY magazine_id"""
                ).fetchall()
                return {row['magazine_id']: row['article_count'] for row in rows}
        except Exception as e:
            logger.error(f"Error counting articles per magazine: {str(e)}")
            raise

    @classmethod
    def _row_to_magazine(cls, row: Dict[str, Any]) -> 'Magazine':
        """Convert database row to Magazine instance"""
        return cls(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            created_at=row['created_at']
        )

    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert instance to dictionary, optionally with relationships"""
        data = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'created_at': self.created_at
        }
        if include_relationships:
            data['article_count'] = len(self.articles())
            data['contributor_count'] = len(self.contributors())
        return data

    def article_titles(self) -> List[str]:
        """Returns list of all article titles in this magazine"""
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT title FROM articles WHERE magazine_id = ?",
                    (self.id,)
                ).fetchall()
                return [row['title'] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching article titles for magazine {self.id}: {str(e)}")
            raise

    def contributing_authors(self, min_articles: int = 2) -> List['Author']:
        """Returns authors with at least N articles in this magazine"""
        from lib.models.author import Author
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT a.* FROM authors a
                    JOIN (
                        SELECT author_id, COUNT(*) as article_count
                        FROM articles
                        WHERE magazine_id = ?
                        GROUP BY author_id
                        HAVING article_count >= ?
                    ) ac ON a.id = ac.author_id""",
                    (self.id, min_articles)
                ).fetchall()
                return [Author._row_to_author(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching contributing authors for magazine {self.id}: {str(e)}")
            raise