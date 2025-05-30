import sqlite3
import pytest
from pathlib import Path

from projectlib.db.connection import get_connection
from projectlib.db.seed import seed
from projectlib.models.author import Author
from projectlib.models.articles import Article
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

def test_create_and_find_author():
    new = Author("Ernest Hemingway")
    assert new.id is None
    new.save()
    assert isinstance(new.id, int)

    fetched = Author.find_by_id(new.id)
    assert fetched.name == "Ernest Hemingway"

    same = Author.find_by_name("Ernest Hemingway")
    assert same.id == new.id

def test_articles_magazines_topics():
    alice = Author.find_by_name("Alice Walker")
    titles = {a.title for a in alice.articles()}
    assert "The Color Purple" in titles
    assert "Science Fiction Today" in titles

    mags = {m.name for m in alice.magazines()}
    assert mags == {"Vogue", "Nature"}

    topics = set(alice.topic_areas())
    assert topics == {"Fashion", "Science"}

def test_add_article():
    mag = Magazine.find_by_name("Time")
    bob = Author("Bob Builder")
    bob.save()
    art = bob.add_article(mag, "Building 101")
    assert art.id is not None

    reloaded = Author.find_by_id(bob.id)
    titles = {a.title for a in reloaded.articles()}
    assert "Building 101" in titles
