"""02_run_sql.py - loads telco_clean.csv into SQLite and runs every query in 02_queries.sql."""
import re, sqlite3
import pandas as pd
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)

df = pd.read_csv("telco_clean.csv")
conn = sqlite3.connect(":memory:")
df.to_sql("customers", conn, index=False, if_exists="replace")

sql_text = open("code/02_queries.sql").read()
blocks = re.split(r"^-- (Q\d+): ", sql_text, flags=re.M)[1:]      # [name, body, name, body, ...]
for name, body in zip(blocks[::2], blocks[1::2]):
    title, _, query = body.partition("\n")
    print(f"\n=== {name}: {title} ===")
    print(pd.read_sql(query, conn).to_string(index=False))
