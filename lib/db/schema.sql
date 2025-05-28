-- lib/db/schema.sql
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE CHECK(length(name) > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS magazines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE CHECK(length(name) > 0),
    category VARCHAR(255) NOT NULL CHECK(length(category) > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL CHECK(length(title) > 0),
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    magazine_id INTEGER NOT NULL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    FOREIGN KEY (magazine_id) REFERENCES magazines(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_articles_magazine_id ON articles(magazine_id);
CREATE INDEX IF NOT EXISTS idx_articles_author_id ON articles(author_id);
CREATE INDEX IF NOT EXISTS idx_magazines_category ON magazines(category);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);

-- For top_publisher() optimization
CREATE INDEX IF NOT EXISTS idx_article_counts ON articles(magazine_id, id);

COMMIT;