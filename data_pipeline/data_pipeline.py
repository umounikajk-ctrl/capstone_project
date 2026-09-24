import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import os
import sqlite3


categories = {
    "Travel": "travel_2",
    "Mystery": "mystery_3",
    "Poetry": "poetry_23",
    "Fantasy": "fantasy_19",
    "Music": "music_14",
    "Historical_fiction": "historical-fiction_4"
}

books_data = []

for category_name, category_id in categories.items():
    url = f"https://books.toscrape.com/catalogue/category/books/{category_id}/index.html"

    while url:

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.strip()
            rating = book.find("p", class_="star-rating")["class"][1]
            availability = book.find("p", class_="instock availability").text.strip()

            books_data.append({
                "title": title,
                "price": price,
                "star_rating": rating,
                "availability": availability,
                "category": category_name
            })

        # Look for a next page ONLY after processing this page's books
        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link else None

# 8. Convert the list into a DataFrame
df = pd.DataFrame(books_data)

# 9. Display the data
print(f"Table: {df}")

# 10. Check how many books we collected
print("Total books:", len(df))


# -----------------------------
# CLEANING
# -----------------------------

# 1. Clean price and convert to float
df["price_gbp"] = pd.to_numeric(
    df["price"]
    .str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
)

# 2. Clean star rating
df["star_rating"] = (
    df["star_rating"]
    .str.strip()
    .str.lower()
)

rating_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}

df["rating"] = df["star_rating"].map(rating_map)


# 3. Convert availability to boolean
df["in_stock"] = (
    df["availability"]
    .str.contains("In stock", case=False, na=False)
)


# 4. Median imputation for numeric fields
df["price_gbp"] = df["price_gbp"].fillna(
    df["price_gbp"].median()
)

df["rating"] = df["rating"].fillna(
    df["rating"].median()).round().astype(int)


# 5. Remove original uncleaned columns
df = df.drop(
    columns=["price", "star_rating", "availability"]
)

# creating a column with fixed baseline conversion rate: 1 GBP = 105.50 INR.
df["price_inr"] = (df["price_gbp"] * 105.50).round(2)

# 6. Validation
print("\n========== DATA VALIDATION ==========")

print("Total books:", len(df))
print("Number of categories:", df["category"].nunique())

print("\nBooks per category:",df["category"].value_counts())

print("\nData types:",df.dtypes)

print("\nMissing values:",df.isna().sum())

print("\nDuplicate rows:",df.duplicated().sum())

print("\nSample cleaned data:",df.head())

#----------------------------------
# DATABASE
#----------------------------------

if os.path.exists("books.db"):
    os.remove("books.db")

conn = sqlite3.connect("books.db")

conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

#----------------------------------------
# CREATE TABLES
#-----------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
)
""")

#-----------------------------------------
# INSERT CATEGORIES
#-----------------------------------------


for category in df["category"].dropna().unique():

    cursor.execute("""
    INSERT OR IGNORE INTO categories (category_name)
    VALUES (?)
    """, (category,))


# Create category name → category ID mapping

category_map = {
    row[1]: row[0]
    for row in cursor.execute(
        "SELECT category_id, category_name FROM categories"
    )
}

#--------------------------------------
# INSERT BOOKS
#--------------------------------------

for _, row in df.iterrows():

    cursor.execute("""
    INSERT INTO books
    (title, price_gbp, price_inr, rating, in_stock, category_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        int(row["rating"]),
        int(row["in_stock"]),
        category_map[row["category"]]
    ))


conn.commit()

#------------------------------------------
# VERIFY DATA
#-----------------------------------------

count_df = pd.read_sql(
    "SELECT COUNT(*) AS total_books FROM books",
    conn
)

print("\nDatabase book count:")
print(count_df)

#-----------------------------------------
# QUERY 1 - SELECT + WHERE
#------------------------------------------

query1 = """
SELECT title, price_gbp, rating
FROM books
WHERE rating = 5;
"""

result1 = pd.read_sql(query1, conn)

print("\nQUERY 1")
print(result1)

#---------------------------------------------
# QUERY 2 - ORDER BY + LIMIT + OFFSET
#--------------------------------------------

query2 = """
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
LIMIT 10
OFFSET 5;
"""

result2 = pd.read_sql(query2, conn)

print("\nQUERY 2")
print(result2)

#--------------------------------------
# QUERY 3 - DISTINCT
#-------------------------------------

query3 = """
SELECT DISTINCT category_name
FROM categories;
"""

result3 = pd.read_sql(query3, conn)

print("\nQUERY 3")
print(result3)

#------------------------------------------
# QUERY 4 - BETWEEN
#-----------------------------------------

query4 = """
SELECT title, price_gbp, rating
FROM books
WHERE price_gbp BETWEEN 20 AND 30
ORDER BY price_gbp;
"""

result4 = pd.read_sql(query4, conn)

print("\nQUERY 4")
print(result4)

#-------------------------------------------------------
# QUERY 5 - GROUP BY + HAVING + count()-(aggregators)
#-------------------------------------------------------

query5 = """
SELECT
    category_id,
    COUNT(*) AS category_count
FROM books
GROUP BY category_id
HAVING COUNT(*) > 10
ORDER BY category_count DESC;
"""

result5 = pd.read_sql(query5, conn)

print("\nQUERY 5")
print(result5)

#--------------------------------------------
# QUERY 6 - JOIN
#-------------------------------------------

join_query = """
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
"""

sql_join_df = pd.read_sql(join_query, conn)

print("\nQUERY 6")
print(sql_join_df)

#----------------------------------------------
# REQUIREMENT 6
# REPRODUCE JOIN USING PANDAS
#----------------------------------------------

books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)


pandas_join_df = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)


pandas_join_df = pandas_join_df[
    [
        "title",
        "category_name",
        "rating",
        "price_gbp",
        "price_inr"
    ]
]


pandas_join_df = pandas_join_df.sort_values(
    by=["rating", "title"],
    ascending=[False, True]
).head(10)



#----------------------------------------
# COMPARE BOTH RESULTS
#----------------------------------------

sql_result = sql_join_df.reset_index(drop=True)

pandas_result = pandas_join_df.reset_index(drop=True)

comparison_df = pd.concat(
    [
        sql_result.add_prefix("SQL_"),
        pandas_result.add_prefix("PANDAS_")
    ],
    axis=1
)

print("\nSQL vs PANDAS JOIN RESULTS — SIDE BY SIDE")
print(comparison_df)

print("\nAre both results equivalent?")
print(sql_result.equals(pandas_result))

conn.close()

#---------------------------------------
# Saving Query Results
#-----------------------------------------

queries = {
    "Query 1 - SELECT/WHERE": query1,
    "Query 2 - ORDER BY/LIMIT": query2,
    "Query 3 - DISTINCT": query3,
    "Query 4 - BETWEEN": query4,
    "Query 5 - GROUP BY/HAVING": query5,
    "Query 6 - JOIN": join_query,
}

results = {
    "Query 1 - SELECT/WHERE": result1,
    "Query 2 - ORDER BY/LIMIT": result2,
    "Query 3 - DISTINCT": result3,
    "Query 4 - BETWEEN": result4,
    "Query 5 - GROUP BY/HAVING": result5,
    "Query 6 - JOIN": sql_join_df,
}

with open("query_results.txt", "w") as f:
    for label, sql in queries.items():
        f.write(f"{'='*60}\n{label}\n{'='*60}\n")
        f.write(f"SQL:\n{sql.strip()}\n\n")
        f.write(f"Output:\n{results[label].to_string(index=False)}\n\n\n")