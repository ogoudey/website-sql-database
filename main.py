from flask import Flask, jsonify, request

import database_api as db_api
import auth

app = Flask(__name__)

####################
#      VLANET      #
####################

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

@app.route('/api/host', methods=['POST'])
def post_host():
    data = request.get_json()
    agents   = data.get('agents', [])
    host     = data.get('host')
    lan_desc = data.get('lan')
    la       = data.get('la')

    db = db_api.get_db()
    cursor = db.cursor(dictionary=True)

    try:
        la_id  = db_api.handle_la(cursor, la)
        lan_id = db_api.handle_lan(cursor, lan_desc, la_id)
        host_id = db_api.handle_host_update(cursor, host, lan_id)
        db_api.handle_agents(cursor, agents, host_id)
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

    return jsonify({"status": "ok"}), 200

############################
# GAME SERVER INTERACTION  #
############################

@app.route("/api/game")
def post_game():
    auth.verify_key()
    data = request.get_json()
    event   = data.get('event')
    game_name   = data.get('game_name')
    player_name   = data.get('player_name')
    match event:
        case "start_game":
            db = db_api.get_db()
            cursor = db.cursor(dictionary=True)
            introductory_narrative  = db_api.handle_start_game(cursor, game_name, player_name)
            db.commit()
            return jsonify({"introductory_narrative": introductory_narrative})
        case "end_game":
            db = db_api.get_db()
            cursor = db.cursor(dictionary=True)
            db_api.handle_end_game(cursor, game_name, player_name)
            db.commit()
            return jsonify({"status": "ok"})
        case _:
            return jsonify({"error": str("Event not found!")}), 500

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)