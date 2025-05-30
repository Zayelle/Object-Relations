import sqlite3
import pytest
from pathlib import Path

from projectlib.db.connection import get_connection
from projectlib.db.seed import seed
from projectlib.models.articles import Article
from projectlib.models.author import Author
from projectlib.models.magazine import Magazine

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    db_file = tmp_path / "articles.db"
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_file))
    def get_conn_override():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        return conn
    monkeypatch.setattr("projectlib.db.connection.get_connection", get_conn_override)

    sql = (Path(__file__).parent.parent / "projectlib/db/schema.sql").read_text()
    conn = get_conn_override()
    conn.executescript(sql)
    conn.close()
    seed()
    yield

def test_create_and_find_article():
    bob = Author("Bob Builder")
    bob.save()
    time = Magazine.find_by_name("Time")
    art = Article("Building Blocks", bob.id, time.id)
    art.save()
    fetched = Article.find_by_id(art.id)
    assert fetched.title == "Building Blocks"

def test_find_by_title_and_relations():
    results = Article.find_by_title("Pride and Prejudice")
    assert len(results) == 1
    art = results[0]
    assert art.author().name == "Jane Austen"
    assert art.magazine().name == "Nature"

def test_find_by_author_and_magazine():
    alice = Author.find_by_name("Alice Walker")
    by_author = Article.find_by_author(alice)
    assert any(a.title == "Science Fiction Today" for a in by_author)
    vogue = Magazine.find_by_name("Vogue")
    by_mag = Article.find_by_magazine(vogue)
    assert any(a.title == "The Color Purple" for a in by_mag)
