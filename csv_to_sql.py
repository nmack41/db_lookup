import pandas as pd
import sqlite3

# Replace with your actual CSV file path
csv_file = "C:/Users/nmack/Downloads/REPORT.csv"
db_file = 'data.db'
table_name = 'your_table'

# Read the CSV
df = pd.read_csv(csv_file)

# Connect to SQLite and insert data
conn = sqlite3.connect(db_file)
df.to_sql(table_name, conn, if_exists='replace', index=False)
conn.close()

print(f"Data from {csv_file} imported to {db_file} as table '{table_name}'.")
