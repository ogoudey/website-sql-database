from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import database_api as db_api
import auth
# --- App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to your frontend domain later
    allow_methods=["GET"],
    allow_headers=["*"],
)


# --- API ---
@app.get("/api/nodes")
def get_nodes(nodes=Depends(db_api.get_nodes), key=Depends(auth.verify_key)):
    return nodes

@app.get("/api/edges")
def get_edges(edges=Depends(db_api.get_edges), key=Depends(auth.verify_key)):
    return edges

@app.get("/api/graph")
def get_graph(graph=Depends(db_api.get_graph), key=Depends(auth.verify_key)):
    return graph