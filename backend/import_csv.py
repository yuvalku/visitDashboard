import pandas as pd
import sqlite3

df = pd.read_csv("data.csv")

df.columns = df.columns.str.strip()

connection = sqlite3.connect("data.db")

df.to_sql("data", connection, if_exists="replace")

connection.close()