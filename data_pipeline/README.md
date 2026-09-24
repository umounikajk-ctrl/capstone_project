# Zepto Data & AI Platform — Data Pipeline

## Module 1 — Data Pipeline

This module implements an end-to-end data pipeline that:

1. Scrapes book catalog data from `books.toscrape.com`
2. Cleans and transforms the scraped data
3. Converts GBP prices to INR using the required fixed project rate
4. Stores the cleaned data in a normalized SQLite database
5. Executes SQL queries for analysis
6. Reads SQL results into pandas
7. Reproduces the SQL JOIN using `pd.merge()`
8. Compares the SQL JOIN and pandas JOIN results
9. Saves the SQL queries and their outputs for submission evidence

---

## 1. Project Objective

The objective of this module is to demonstrate a complete **raw-to-relational data pipeline**:

Web Scraping
     ↓
Raw Data
     ↓
Data Cleaning
     ↓
Data Transformation
     ↓
Currency Conversion
     ↓
SQLite Database
     ↓
SQL Analysis
     ↓
Pandas Validation


The pipeline is implemented entirely in Python and runs without manual copy-pasting of data.

---

## 2. Data Source

The data is collected from:

**Books to Scrape**

https://books.toscrape.com/

Books to Scrape is a public website designed specifically for practicing web scraping.

No login, API key, or paid service is required.

### Categories scraped

The pipeline scrapes all paginated books from the following six categories:

* Travel
* Mystery
* Poetry
* Fantasy
* Music
* Historical Fiction

The assignment requires at least 3 categories and at least 60 books. This implementation uses 6 categories and follows pagination until all books in each selected category have been processed.

---

## 3. Technologies Used

| Technology    | Purpose                                     |
| ------------- | ------------------------------------------- |
| Python        | Main programming language                   |
| Requests      | Download web pages                          |
| BeautifulSoup | Parse HTML                                  |
| pandas        | Data cleaning, transformation, and analysis |
| SQLite        | Relational database                         |
| sqlite3       | Python interface for SQLite                 |
| `urljoin`     | Build URLs for pagination                   |

---

## 4. Installation

### Requirements

Python 3.11 or a compatible Python 3 version is recommended.

Create a virtual environment if desired:   '''python -m venv .venv'''

Activate it on Windows PowerShell:  '''.venv\Scripts\Activate.ps1'''

Install the required packages: '''pip install -r requirements.txt'''


### requirements.txt
---------------------
requests
beautifulsoup4
pandas
---------------------

`os`, `sqlite3`, and `urllib.parse` are part of Python's standard library and do not need to be installed separately.

---

## 5. Running the Pipeline

From the `/data_pipeline` directory, run: '''python data_pipeline.py'''

The script performs the complete pipeline automatically:


Scrape
  ↓
Create DataFrame
  ↓
Clean data
  ↓
Validate data
  ↓
Create SQLite database
  ↓
Insert categories
  ↓
Insert books
  ↓
Run SQL queries
  ↓
Compare SQL JOIN with pandas merge
  ↓
Save query results


No manual data copy-pasting is required.

---

## 6. Web Scraping

The pipeline uses:  '''requests.get()'''


to download each category page.

HTTP status codes are checked using:  '''response.raise_for_status()'''


The HTML is parsed using:  '''BeautifulSoup(response.text, "html.parser")'''


Book records are extracted from:

```html
<article class="product_pod">


For each book, the following raw fields are collected:

* `title`
* `price`
* `star_rating`
* `availability`
* `category`

### Pagination

Each selected category may contain multiple pages.

The pipeline searches for:

```html
<li class="next">
```

and follows the next-page URL using:

```python
urljoin(url, next_link["href"])
```

Pagination continues until there is no next page.

---

## 7. Data Cleaning

### 7.1 Price Cleaning

The original price contains a currency symbol.

The pipeline removes non-numeric characters:

```python
df["price_gbp"] = pd.to_numeric(
    df["price"].str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
)
```

The cleaned column is:  '''price_gbp'''

and is stored as a floating-point value.

Example: £51.77 → 51.77


---

### 7.2 Star Rating Conversion

The website provides ratings as text:

One,
Two,
Three,
Four,
Five


These are converted into integers:
------------------
| Text  | Rating |
|-------|--------|
| One   |      1 |
| Two   |      2 |
| Three |      3 |
| Four  |      4 |
| Five  |      5 |

The mapping is:

rating_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


The final column is: rating


with integer values from 1 to 5.

---

### 7.3 Availability Conversion

The original availability text can contain additional information, for example:
'''In stock (22 available)'''


Therefore, the pipeline uses:

```python
df["in_stock"] = (
    df["availability"]
    .str.contains("In stock", case=False, na=False)
)
```

This converts availability into a Boolean field:

In stock (...)  → True
Out of stock    → False

The final column is:  '''in_stock'''


---

### 7.4 Missing Numeric Values

If a numeric field cannot be parsed, the parsing operation produces `NaN`.

The assignment allows either of two approaches for rows with unparseable numeric fields: median imputation, or dropping the row, provided the choice is stated and justified.

This pipeline uses median imputation, not row-dropping:

Therefore:

```python
df["price_gbp"] = df["price_gbp"].fillna(
    df["price_gbp"].median()
)
```


and:

```python
df["rating"] = df["rating"].fillna(
    df["rating"].median()
).round().astype(int)
```


**Justification:** parsing failures expected from this source are rare formatting edge cases (e.g. an unexpected symbol in a price string), not structurally invalid records. Dropping such rows would unnecessarily shrink the dataset and could reduce category coverage below the required minimum. Imputing with the column median preserves row count and category representation while introducing minimal distortion to the overall price/rating distribution, since only a small number of rows are expected to require it.

This prevents the pipeline from crashing because of an unexpected numeric value, while keeping the handling decision deliberate and documented rather than incidental.

---

## 8. Currency Conversion

The assignment requires a fixed project-defined conversion rate.

### Fixed rate

```text
1 GBP = 105.50 INR
```

This is an artificial project baseline, not a live market exchange rate.

The pipeline calculates:

```python
df["price_inr"] = (
    df["price_gbp"] * 105.50
).round(2)
```

Example:

```text
£10.00 × 105.50 = ₹1,055.00
```

No currency API is required.

---

## 9. Final Dataset

After cleaning and transformation, the main fields are:

| Column      | Description                |
| ----------- | -------------------------- |
| `title`     | Book title                 |
| `category`  | Book category              |
| `price_gbp` | Cleaned GBP price          |
| `rating`    | Numeric rating from 1–5    |
| `in_stock`  | Boolean availability       |
| `price_inr` | INR price using fixed rate |

The original raw columns:

```text
price
star_rating
availability
```

are removed after the cleaned columns are created.

---

## 10. Data Validation

The pipeline checks:

* Total number of books
* Number of categories
* Books per category
* Data types
* Missing values
* Duplicate rows
* Sample cleaned records

Example validation output:

```text
========== DATA VALIDATION ==========

Total books: <number>
Number of categories: 6

Books per category:
--------------------------
category
---------------------------
Fantasy               48
Mystery               32
Historical_fiction    26
Poetry                19
Music                 13
Travel                11
Name: count, dtype: int64

Data types:
-------------------------
title         object
--------------------------
category      object
price_gbp    float64
rating         int64
in_stock        bool
price_inr    float64
dtype: object


Missing values:
---------------------------
title        0
category     0
price_gbp    0
rating       0
in_stock     0
price_inr    0
dtype: int64

Duplicate rows: 0

Sample cleaned data:
                                               title category  price_gbp  \
0                            It's Only the Himalayas   Travel      45.17   
1  Full Moon over Noahâs Ark: An Odyssey to Mou...   Travel      49.43   
2  See America: A Celebration of Our National Par...   Travel      48.87   
3  Vagabonding: An Uncommon Guide to the Art of L...   Travel      36.94   
4                               Under the Tuscan Sun   Travel      37.33   

   rating  in_stock  price_inr  
0       2      True    4765.44  
1       4      True    5214.86  
2       3      True    5155.78  
3       2      True    3897.17  
4       3      True    3938.31  

The assignment requires:
---------------------------------
≥ 60 books
≥ 3 categories
--------------------------------

The pipeline uses six categories and all available pages for those categories.

---

# 11. SQLite Database

The cleaned data is stored in SQLite.

Database file:

Database Name : books.db

The database is not committed as a static, hand-edited file — it is regenerated from scratch on every run of the pipeline script (the existing books.db is deleted first), so the schema and data are always reproducible directly from the scraped source.
---

## 12. Database Schema

The database contains two normalized tables:

┌─────────────────────────┐
│       categories        │
├─────────────────────────┤
│ category_id PK          │
│ category_name UNIQUE    │
└────────────┬────────────┘
             │
             │ 1-to-many
             │
             ▼
┌─────────────────────────┐
│         books           │
├─────────────────────────┤
│ book_id PK              │
│ title                   │
│ price_gbp               │
│ price_inr               │
│ rating                  │
│ in_stock                │
│ category_id FK          │
└─────────────────────────┘

### Categories table

```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
);
```

Columns:

| Column          | Description          |
| --------------- | -------------------- |
| `category_id`   | Primary key          |
| `category_name` | Unique category name |

---

### Books table

```sql
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);
```

Columns:

| Column        | Description                                   |
| ------------- | --------------------------------------------- |
| `book_id`     | Primary key                                   |
| `title`       | Book title                                    |
| `price_gbp`   | GBP price                                     |
| `price_inr`   | Converted INR price                           |
| `rating`      | Rating from 1–5                               |
| `in_stock`    | SQLite representation of Boolean availability |
| `category_id` | Foreign key referencing `categories`          |

The relationship is:

```text
categories.category_id
          │
          │ 1-to-many
          ▼
books.category_id
```

---

# 13. SQL Queries

Six SQL queries are included.

## Query 1 — SELECT + WHERE

Find books with a rating of 5:

```sql
SELECT title, price_gbp, rating
FROM books
WHERE rating = 5;
```

Demonstrates:

* SELECT
* WHERE

---

## Query 2 — ORDER BY + LIMIT

Retrieve books ordered by price:

```sql
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
LIMIT 10
OFFSET 5;
```

Demonstrates:

* ORDER BY
* LIMIT
* OFFSET

---

## Query 3 — DISTINCT

Retrieve unique categories:

```sql
SELECT DISTINCT category_name
FROM categories;
```

Demonstrates:

* DISTINCT

---

## Query 4 — BETWEEN

Find books priced between £20 and £30:

```sql
SELECT title, price_gbp, rating
FROM books
WHERE price_gbp BETWEEN 20 AND 30
ORDER BY price_gbp;
```

Demonstrates:

* BETWEEN
* WHERE
* ORDER BY

---

## Query 5 — GROUP BY + HAVING

Count books by category:

```sql
SELECT
    category_id,
    COUNT(*) AS category_count
FROM books
GROUP BY category_id
HAVING COUNT(*) > 10
ORDER BY category_count DESC;
```

Demonstrates:

* GROUP BY
* COUNT
* HAVING
* ORDER BY

Note: this query returns only categories with more than 10 books. If a given run's category counts fall at or below this threshold (e.g. a smaller category), the result set may legitimately be empty or short — this does not indicate a pipeline error. The actual row counts per category are visible in the Section 10 validation output and in query_results.txt.

---

## Query 6 — JOIN

Join books with their category names:

```sql
SELECT
    b.title,
    c.category_name,
    b.rating,
    b.price_gbp,
    b.price_inr
FROM books AS b
JOIN categories AS c
ON b.category_id = c.category_id
ORDER BY b.rating DESC, b.title ASC
LIMIT 10;
```

Demonstrates:

* INNER JOIN
* Primary key / foreign key relationship
* ORDER BY
* LIMIT

---

# 14. Reading SQL Results with pandas

The pipeline reads SQL results into pandas using:

```python
pd.read_sql()
```

For example:

```python
result1 = pd.read_sql(query1, conn)
```

The JOIN result is also loaded:

```python
sql_join_df = pd.read_sql(join_query, conn)
```

This demonstrates SQL-to-pandas integration.

---

# 15. Reproducing the JOIN with pandas

The same relationship is reproduced without SQL.

First, the two tables are loaded:

```python
books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)
```

Then the JOIN is reproduced using:

```python
pandas_join_df = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)
```

The resulting columns are selected and sorted in the same way as the SQL query.

---

# 16. SQL JOIN vs pandas JOIN

The pipeline creates a side-by-side comparison:

```python
comparison_df = pd.concat(
    [
        sql_result.add_prefix("SQL_"),
        pandas_result.add_prefix("PANDAS_")
    ],
    axis=1
)
```

It also checks whether the results are equivalent:

```python
sql_result.equals(pandas_result)
```

Expected result:

```text
True
```

This demonstrates that the SQL JOIN and pandas `merge()` produce equivalent results.

---

# 17. Saved Query Outputs

The executed SQL queries and their outputs are saved to:

```text
query_results.txt
```

The file contains:

* Query 1 SQL + output
* Query 2 SQL + output
* Query 3 SQL + output
* Query 4 SQL + output
* Query 5 SQL + output
* Query 6 SQL + output
* SQL JOIN vs pandas `merge()` comparison
* Equivalence check

This provides an executed record of the SQL analysis required by the assignment.

---

# 18. Project Files

Recommended `/data_pipeline` structure:

```text
data_pipeline/
│
├── data_pipeline.py
├── requirements.txt
├── books.db
├── query_results.txt
└── README.md
```

### File descriptions

| File                | Purpose                                                 |
| ------------------- | ------------------------------------------------------- |
| `data_pipeline.py`  | Complete scraping, cleaning, database, and SQL pipeline |
| `requirements.txt`  | Python third-party dependencies                         |
| `books.db`          | SQLite database generated by the pipeline               |
| `query_results.txt` | Saved SQL queries and outputs                           |
| `README.md`         | Module documentation                                    |

requirements.txt should be present in the repo alongside the script (see Section 4) — it is a plain text file listing requests, beautifulsoup4, and pandas, one per line.

---

# 19. Reproducibility

The database is recreated automatically by the Python script.

The script removes the existing database:

```python
if os.path.exists("books.db"):
    os.remove("books.db")
```

and then creates the tables again.

Therefore, running:

```bash
python data_pipeline.py
```

rebuilds the database from the scraped source data.

---
## 20. Summary

This module demonstrates an end-to-end data engineering workflow:

```text
Scrape
  ↓
Clean
  ↓
Validate
  ↓
Convert
  ↓
Normalize
  ↓
Store in SQLite
  ↓
Query with SQL
  ↓
Read with pandas
  ↓
Reproduce JOIN with pd.merge()
  ↓
Compare results
  ↓
Save outputs
```

The fixed project currency conversion used throughout the pipeline is:

**1 GBP = 105.50 INR**
