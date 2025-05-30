import code
from projectlib.db.seed import seed
from projectlib.db.connection import get_connection
from projectlib.models.author import Author
from projectlib.models.magazine import Magazine
from projectlib.models.articles import Article

if __name__ == "__main__":
    seed()
    banner = (
        "Interactive shell ready!\n"
        "Available objects:\n"
        "  get_connection\n"
        "  Author\n"
        "  Magazine\n"
        "  Article\n\n"
        "Examples:\n"
        "  >>> alice = Author.find_by_name('Alice Walker')\n"
        "  >>> alice.articles()\n"
        "  >>> mag = Magazine.find_by_name('Time')\n"
        "  >>> mag.article_titles()\n"
    )
    code.interact(banner=banner, local={
        "get_connection": get_connection,
        "Author": Author,
        "Magazine": Magazine,
        "Article": Article
    })
