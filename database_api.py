import mysql.connector

# --- Config ---
DB_CONFIG = {
    "host": "vlanet.db",
    "user": "oling",
    "password": "w!gwp%6*g4$G!",
    "database": "initvlanet",
}



def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_nodes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    return cursor.fetchall()

def get_edges():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM edges")
    return cursor.fetchall()

def get_graph():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    nodes = cursor.fetchall()
    cursor.execute("SELECT * FROM edges")
    edges = cursor.fetchall()
    return {"nodes": nodes, "edges": edges}