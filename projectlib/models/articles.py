from projectlib.db.connection import get_connection

class Article:
    def __init__(self, title, author_id, magazine_id, id=None):
        self.id = id
        self.title = title
        self.author_id = author_id
        self.magazine_id = magazine_id

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id:
            cur.execute(
                "UPDATE articles SET title = ?, author_id = ?, magazine_id = ? WHERE id = ?;",
                (self.title, self.author_id, self.magazine_id, self.id)
            )
        else:
            cur.execute(
                "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?);",
                (self.title, self.author_id, self.magazine_id)
            )
            self.id = cur.lastrowid
        conn.commit()
        conn.close()
        return self

    @classmethod
    def find_by_id(cls, art_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE id = ?;", (art_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(row["title"], row["author_id"], row["magazine_id"], row["id"])
        return None

    @classmethod
    def find_by_title(cls, title):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE title = ?;", (title,))
        rows = cur.fetchall()
        conn.close()
        return [cls(r["title"], r["author_id"], r["magazine_id"], r["id"]) for r in rows]

    @classmethod
    def find_by_author(cls, author):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE author_id = ?;", (author.id,))
        rows = cur.fetchall()
        conn.close()
        return [cls(r["title"], r["author_id"], r["magazine_id"], r["id"]) for r in rows]

    @classmethod
    def find_by_magazine(cls, magazine):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE magazine_id = ?;", (magazine.id,))
        rows = cur.fetchall()
        conn.close()
        return [cls(r["title"], r["author_id"], r["magazine_id"], r["id"]) for r in rows]

    def author(self):
        from projectlib.models.author import Author
        return Author.find_by_id(self.author_id)

    def magazine(self):
        from projectlib.models.magazine import Magazine
        return Magazine.find_by_id(self.magazine_id)
