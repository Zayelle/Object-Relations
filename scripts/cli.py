#!/usr/bin/env python3
import cmd
from lib.models.author import Author
from lib.models.magazine import Magazine
from lib.models.article import Article
from lib.db.connection import get_connection
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MagazineCLI(cmd.Cmd):
    prompt = '(magazine_db) '
    
    def do_top_publisher(self, arg):
        """Display the magazine with the most articles"""
        magazine = Magazine.top_publisher()
        if magazine:
            print(f"Top publisher: {magazine.name} with {getattr(magazine, 'article_count', '?')} articles")
        else:
            print("No magazines found")

    def do_find_author(self, name):
        """Find authors by name (partial match)"""
        if not name.strip():
            print("Please provide a name to search for.")
            return
        authors = Author.find_by_name(name)
        if not authors:
            print("No authors found.")
            return
        for idx, author in enumerate(authors, 1):
            print(f"{idx}. {author.name} (ID: {author.id})")

    def do_author_stats(self, author_id):
        """Show statistics for an author"""
        try:
            author = Author.find_by_id(int(author_id))
            if not author:
                print("Author not found")
                return
            
            print(f"\nAuthor: {author.name} (ID: {author.id})")
            print(f"Articles written: {len(author.articles())}")
            print(f"Magazines contributed to: {len(author.magazines())}")
            print(f"Topic areas: {', '.join(author.topic_areas())}")
        except ValueError:
            print("Please provide a valid author ID")

    def do_magazine_articles(self, magazine_id):
        """List articles in a magazine"""
        try:
            magazine = Magazine.find_by_id(int(magazine_id))
            if not magazine:
                print("Magazine not found")
                return
            
            print(f"\nArticles in {magazine.name}:")
            articles = magazine.articles()
            if not articles:
                print("No articles found in this magazine.")
                return
            for idx, article in enumerate(articles, 1):
                print(f"{idx}. {article.title} (by {article.author.name})")
        except ValueError:
            print("Please provide a valid magazine ID")

    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
        return True

def main():
    print("Magazine Database CLI")
    print("Type 'help' for commands\n")
    MagazineCLI().cmdloop()

if __name__ == '__main__':
    main()