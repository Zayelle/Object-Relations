from projectlib.db.connection import get_connection

def seed():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM articles;")
    cur.execute("DELETE FROM authors;")
    cur.execute("DELETE FROM magazines;")
    authors = ['Alice Walker', 'Mark Twain', 'Jane Austen']
    for name in authors:
        cur.execute("INSERT INTO authors (name) VALUES (?);", (name,))
    mags = [
        ('Nature', 'Science'),
        ('Time', 'News'),
        ('Vogue', 'Fashion'),
    ]
    for name, category in mags:
        cur.execute(
            "INSERT INTO magazines (name, category) VALUES (?, ?);",
            (name, category)
        )
    cur.execute("SELECT id, name FROM authors;")
    author_ids = {row['name']: row['id'] for row in cur.fetchall()}
    cur.execute("SELECT id, name FROM magazines;")
    mag_ids = {row['name']: row['id'] for row in cur.fetchall()}
    articles = [
        ('The Color Purple', 'Alice Walker', 'Vogue'),
        ('Adventures of Huckleberry Finn', 'Mark Twain', 'Time'),
        ('Pride and Prejudice', 'Jane Austen', 'Nature'),
        ('Science Fiction Today', 'Alice Walker', 'Nature'),
        ('Fashion Through the Ages', 'Jane Austen', 'Vogue'),
    ]
    for title, author, magazine in articles:
        cur.execute(
            "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?);",
            (title, author_ids[author], mag_ids[magazine])
        )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed()
