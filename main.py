from flask import Flask, jsonify

import database_api as db_api
import auth

app = Flask(__name__)

@app.get("/api/nodes")
def get_nodes():
    auth.verify_key()
    return jsonify(db_api.get_nodes())

@app.get("/api/edges")
def get_edges():
    auth.verify_key()
    return jsonify(db_api.get_edges())

@app.get("/api/graph")
def get_graph():
    auth.verify_key()
    return jsonify(db_api.get_graph())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)