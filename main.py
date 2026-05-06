from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

import database_api as db

# --- App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to your frontend domain later
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- Auth ---

API_KEY = "poppoppop"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key

# --- API ---

@app.get("/api/nodes")
def get_nodes(db=Depends(db.get_db), key=Depends(verify_key)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    return cursor.fetchall()

@app.get("/api/edges")
def get_edges(db=Depends(db.get_db), key=Depends(verify_key)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM edges")
    return cursor.fetchall()

@app.get("/api/graph")
def get_graph(db=Depends(db.get_db), key=Depends(verify_key)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    nodes = cursor.fetchall()
    cursor.execute("SELECT * FROM edges")
    edges = cursor.fetchall()
    return {"nodes": nodes, "edges": edges}