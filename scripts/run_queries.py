import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from projectlib.db.seed import seed
from projectlib.db.connection import get_connection
from projectlib.models.author import Author
from projectlib.models.magazine import Magazine
from projectlib.models.articles import Article

def main():
    seed()

    print("\n=== All Authors and Their Articles ===")
    conn = get_connection()
    for row in conn.execute("SELECT * FROM authors"):
        author = Author(row["name"], row["id"])
        titles = [a.title for a in author.articles()]
        print(f"- {author.name}: {titles}")
    conn.close()

    print("\n=== All Magazines and Their Contributors ===")
    conn = get_connection()
    for row in conn.execute("SELECT * FROM magazines"):
        mag = Magazine(row["name"], row["category"], row["id"])
        contribs = [a.name for a in mag.contributors()]
        print(f"- {mag.name} ({mag.category}): {contribs}")
    conn.close()

    print("\n=== Sample Article Lookup ===")
    art = Article.find_by_title("Pride and Prejudice")[0]
    print(f"Article '{art.title}' written by {art.author().name} for {art.magazine().name}")

if __name__ == "__main__":
    main()
