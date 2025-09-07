from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
from pydantic import BaseModel
import math


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data.db"
TABLE_NAME = "data"

def build_filters(start_date, end_date, poi_name, poi_category, dma, search):
    where = ["1=1"]
    params = []
    if start_date:
        where.append("date >= ?")
        params.append(start_date)
    if end_date:
        where.append("date <= ?")
        params.append(end_date)
    if poi_name:
        where.append("poi_name = ?")
        params.append(poi_name)
    if poi_category:
        where.append("poi_category = ?")
        params.append(poi_category)
    if dma:
        where.append("dma = ?")
        params.append(dma)
    if search:
        where.append("poi_name LIKE ?")
        params.append(f"%{search}%")
    return " AND ".join(where), params

# --- Response Models ---
class Visit(BaseModel):
    id: int
    date: str # YYYY-MM-DD format
    poi_name: str
    poi_category: str
    dma: str
    visits: int

class VisitResponse(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    data: List[Visit]

@app.get("/")
def root():
    return {"message": "Welcome to the API"}

@app.get("/visits", response_model=VisitResponse)
def get_visits(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    poi_name: Optional[str] = None,
    poi_category: Optional[str] = None,
    dma: Optional[str] = None,
    search: Optional[str] = None
):
    offset = (page - 1) * per_page
    where_clause, params = build_filters(start_date, end_date, poi_name, poi_category, dma, search)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE {where_clause}", tuple(params))
    total = cur.fetchone()[0]

    cur.execute(
        f"SELECT id, date, poi_name, poi_category, dma, visits FROM {TABLE_NAME} "
        f"WHERE {where_clause} LIMIT ? OFFSET ?",
        tuple(params) + (per_page, offset)
    )
    rows = cur.fetchall()
    con.close()

    return VisitResponse(
        page=page,
        per_page=per_page,
        total=total,
        pages=math.ceil(total / per_page),
        data=[Visit(**row_dict) for row_dict in [
            {"id": r[0], "date": r[1], "poi_name": r[2], "poi_category": r[3], "dma": r[4], "visits": r[5]}
            for r in rows
        ]]
    )

@app.get("/summary")
def total_visit_per_poi(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    poi_name: Optional[str] = None,
    poi_category: Optional[str] = None,
    dma: Optional[str] = None,
    search: Optional[str] = None    
):

    offset = (page - 1) * per_page
    where_clause, params = build_filters(start_date, end_date, poi_name, poi_category, dma, search)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(f"SELECT COUNT(DISTINCT poi_name) FROM {TABLE_NAME} WHERE {where_clause}", tuple(params))
    total = cur.fetchone()[0]

    cur.execute(f"SELECT poi_name, SUM(visits) FROM {TABLE_NAME} WHERE {where_clause} "
                 f"GROUP BY poi_name LIMIT ? OFFSET ?", tuple(params)+(per_page, offset))
    rows = cur.fetchall()
    con.close()    

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": math.ceil(total / per_page),
        "data": [
            {
                "poi_name": r[0],
                "total_visits": r[1]
            }
            for r in rows
        ]
    }


@app.get("/categories",response_model=List[str])
def get_category():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(f"SELECT DISTINCT poi_category FROM {TABLE_NAME}")
    rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows if r[0] is not None]   

@app.get("/dmas",response_model=List[str])
def get_dmas():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(f"SELECT DISTINCT dma FROM {TABLE_NAME}")
    rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows if r[0] is not None]  