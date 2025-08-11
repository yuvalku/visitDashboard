from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
from utils.db_loader import csv_to_sqlite, json_to_sqlite

app = FastAPI()
DB_PATH = "data.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def query(sql, params=()):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row  # rows as dict-like
    cur = con.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows