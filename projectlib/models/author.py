from projectlib.db.connection import get_connection

class Author:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id:
            cur.execute("UPDATE authors SET name = ? WHERE id = ?;", (self.name, self.id))
        else:
            cur.execute("INSERT INTO authors (name) VALUES (?);", (self.name,))
            self.id = cur.lastrowid
        conn.commit()
        conn.close()
        return self

    @classmethod
    def find_by_id(cls, author_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM authors WHERE id = ?;", (author_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(row["name"], row["id"])
        return None

    @classmethod
    def find_by_name(cls, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM authors WHERE name = ?;", (name,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(row["name"], row["id"])
        return None

    def articles(self):
        from projectlib.models.articles import Article
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE author_id = ?;", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Article(r["title"], r["author_id"], r["magazine_id"], r["id"]) for r in rows]

    def magazines(self):
        from projectlib.models.magazine import Magazine
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT m.* FROM magazines m JOIN articles a ON m.id = a.magazine_id WHERE a.author_id = ?;",
            (self.id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [Magazine(r["name"], r["category"], r["id"]) for r in rows]

    def add_article(self, magazine, title):
        from projectlib.models.articles import Article
        art = Article(title, self.id, magazine.id)
        art.save()
        return art

    def topic_areas(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT m.category FROM magazines m JOIN articles a ON m.id = a.magazine_id WHERE a.author_id = ?;",
            (self.id,)
        )
        cats = [r["category"] for r in cur.fetchall()]
        conn.close()
        return cats
