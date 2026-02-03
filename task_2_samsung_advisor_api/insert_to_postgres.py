# -*- coding: utf-8 -*-
"""
Insert Samsung phone data into PostgreSQL.

Reads scraped phone specifications from CSV and
stores them in a PostgreSQL table for RAG retrieval.
"""

import pandas as pd
from sqlalchemy import create_engine

# ✅ Load your scraped CSV file
df = pd.read_csv(r"C:\Users\hp\Desktop\samsung_phones.csv")  # change path when needed

# ✅ PostgreSQL connection details
USER = "postgres"
PASSWORD = "your_password"   # replace with your actual password
HOST = "localhost"
DBNAME = "samsungdb"

# ✅ Create connection string
engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DBNAME}")

# ✅ Insert data into table
df.to_sql("samsung_phones", engine, if_exists="replace", index=False) ## replace for demo simplicity

print("✅ Data inserted into PostgreSQL successfully!")
