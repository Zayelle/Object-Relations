# Articles Code Challenge

This project models a simple domain of Authors, Articles, and Magazines using raw SQL in Python (without an ORM). You’ll find:

- A **SQLite** database schema for authors, magazines, and articles
- Python **model classes** (`Author`, `Article`, `Magazine`) with methods to save, query, and navigate relationships
- A **seed script** to populate sample data
- A **test suite** powered by `pytest`
- Helper scripts for **schema setup**, **demo queries**, and an **interactive REPL**

---

## Prerequisites

- Python 3.8+
- [Pipenv](https://pipenv.pypa.io) (for virtualenv & dependency management)

---

## Getting Started

1. **Clone the repository**  
   git clone https://github.com/Zayelle/Object-Relations.git

   cd code-challenge

2. **Install dependencies and spawn a shell**
   pipenv install

   pipenv shell

3. **Create the database schema**

   python scripts/setup_db.py

   This reads projectlib/db/schema.sql and creates the three tables in articles.db.

4. **Seed the database with sample data**

   python -c "from projectlib.db.seed import seed; seed()"

   You should see no errors—three authors, three magazines, and five articles will be inserted.

---

## Running the Tests

The project includes a full pytest suite for each model and their relationships.

pytest -q

Successful output should look like: (
......... # 9 tests passing)

## Interactive Debugging

You can launch a REPL with all models pre-loaded:

python -m projectlib.debug   # module-style

