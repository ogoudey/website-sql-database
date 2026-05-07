import mysql.connector

# --- Config ---
DB_CONFIG = {
    "host": "vlanet.db",
    "user": "oling",
    "password": "w!gwp%6*g4$G!",
    "database": "initvlanet",
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_nodes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    result = cursor.fetchall()
    db.close()
    return result

def get_edges():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM edges")
    result = cursor.fetchall()
    db.close()
    return result

def get_graph():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    nodes = cursor.fetchall()
    cursor.execute("SELECT * FROM edges")
    edges = cursor.fetchall()
    db.close()
    return {"nodes": nodes, "edges": edges}