from lib.db.connection import get_connection
from typing import TypeVar, Type, Dict, Any, List, Optional
import logging
from dataclasses import dataclass

T = TypeVar('T', bound='BaseModel')

logger = logging.getLogger(__name__)

@dataclass
class BaseModel:
    """Base class with common SQL operations"""

    @classmethod
    def _execute_query(cls, query: str, params: tuple = (), conn=None):
        """Safe query execution with injection protection"""
        should_close = False
        if conn is None:
            conn = get_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor
        except Exception as e:
            logger.error(f"Query failed: {query[:50]}... - {str(e)}")
            raise
        finally:
            if should_close:
                conn.close()

    @classmethod
    def _fetch_one(cls, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Safe fetch one with injection protection"""
        try:
            cursor = cls._execute_query(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Fetch one failed: {str(e)}")
            raise

    @classmethod
    def _fetch_all(cls, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Safe fetch all with injection protection"""
        try:
            cursor = cls._execute_query(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Fetch all failed: {str(e)}")
            raise

    @classmethod
    def _row_to_model(cls: Type[T], row: Dict[str, Any]) -> T:
        """Convert DB row to model instance"""
        raise NotImplementedError

    @classmethod
    def _validate_fields(cls, **kwargs) -> None:
        """Validate model fields"""
        raise NotImplementedError