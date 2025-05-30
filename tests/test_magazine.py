import sqlite3
import pytest
from pathlib import Path

from projectlib.db.connection import get_connection
from projectlib.db.seed import seed
from projectlib.models.magazine import Magazine
from projectlib.models.author import Author

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

def test_create_and_find_magazine():
    new = Magazine("Forbes", "Business")
    new.save()
    by_id = Magazine.find_by_id(new.id)
    assert by_id.name == "Forbes"
    by_name = Magazine.find_by_name("Forbes")
    assert by_name.id == new.id
    by_cat = Magazine.find_by_category("Business")
    assert any(m.name == "Forbes" for m in by_cat)

def test_articles_and_contributors():
    vogue = Magazine.find_by_name("Vogue")
    titles = set(vogue.article_titles())
    assert {"The Color Purple", "Fashion Through the Ages"} <= titles
    contribs = {a.name for a in vogue.contributors()}
    assert contribs == {"Alice Walker", "Jane Austen"}

def test_contributing_authors_threshold():
    vogue = Magazine.find_by_name("Vogue")
    alice = Author.find_by_name("Alice Walker")
    alice.add_article(vogue, "Extra 1")
    alice.add_article(vogue, "Extra 2")
    top = {a.name for a in vogue.contributing_authors()}
    assert "Alice Walker" in top
    assert "Jane Austen" not in top
