from projectlib.db.connection import get_connection

class Magazine:
    def __init__(self, name, category, id=None):
        self.id = id
        self.name = name
        self.category = category

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id:
            cur.execute("UPDATE magazines SET name = ?, category = ? WHERE id = ?;", (self.name, self.category, self.id))
        else:
            cur.execute("INSERT INTO magazines (name, category) VALUES (?, ?);", (self.name, self.category))
            self.id = cur.lastrowid
        conn.commit()
        conn.close()
        return self

    @classmethod
    def find_by_id(cls, mag_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM magazines WHERE id = ?;", (mag_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(row["name"], row["category"], row["id"])
        return None

    @classmethod
    def find_by_name(cls, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM magazines WHERE name = ?;", (name,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(row["name"], row["category"], row["id"])
        return None

    @classmethod
    def find_by_category(cls, category):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM magazines WHERE category = ?;", (category,))
        rows = cur.fetchall()
        conn.close()
        return [cls(r["name"], r["category"], r["id"]) for r in rows]

    def articles(self):
        from projectlib.models.articles import Article
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE magazine_id = ?;", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Article(r["title"], r["author_id"], r["magazine_id"], r["id"]) for r in rows]

    def contributors(self):
        from projectlib.models.author import Author
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT a.* FROM authors a JOIN articles ar ON a.id = ar.author_id WHERE ar.magazine_id = ?;", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Author(r["name"], r["id"]) for r in rows]

    def article_titles(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title FROM articles WHERE magazine_id = ?;", (self.id,))
        titles = [r["title"] for r in cur.fetchall()]
        conn.close()
        return titles

    def contributing_authors(self):
        from projectlib.models.author import Author
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT a.*, COUNT(ar.id) AS cnt FROM authors a JOIN articles ar ON a.id = ar.author_id WHERE ar.magazine_id = ? GROUP BY a.id HAVING cnt > 2;", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Author(r["name"], r["id"]) for r in rows]
