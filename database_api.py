import mysql.connector
import json
import os

# --- Config ---
DB_CONFIG = {
    "host": "vlanet.db",
    "user": "oling",
    "password": "w!gwp%6*g4$G!",
    "database": "initvlanet",
}
debug_level = os.environ.get("VLANET_DEBUG", None)
match debug_level:
    case None:
        print(f"Running production")
    case _:
        print(f"Unsupported debug level: {debug_level}")


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

def handle_la(cursor, la_name):
    cursor.execute(
        "SELECT id FROM nodes WHERE name = %s AND type = 'local_area'",
        (la_name,)
    )
    row = cursor.fetchone()
    if row:
        return row['id']
    cursor.execute(
        "INSERT INTO nodes (name, type, parent_id, metadata) VALUES (%s, 'local_area', NULL, NULL)",
        (la_name,)
    )
    return cursor.lastrowid


def handle_lan(cursor, lan_name, la_id):
    cursor.execute(
        "SELECT id FROM nodes WHERE name = %s AND type = 'lan'",
        (lan_name,)
    )
    row = cursor.fetchone()
    if row:
        # update parent in case it moved
        cursor.execute(
            "UPDATE nodes SET parent_id = %s WHERE id = %s",
            (la_id, row['id'])
        )
        return row['id']
    cursor.execute(
        "INSERT INTO nodes (name, type, parent_id, metadata) VALUES (%s, 'lan', %s, NULL)",
        (lan_name, la_id)
    )
    return cursor.lastrowid

def handle_host_update(cursor, host, lan_id):
    # host is either a plain name string or a dict {"name": ..., "version": ...}
    if isinstance(host, dict):
        host_name    = host.get('name')
        host_version = host.get('version')
    else:
        host_name    = host
        host_version = None

    metadata = json.dumps({"version": host_version}) if host_version else None

    cursor.execute(
        "SELECT id FROM nodes WHERE name = %s AND type = 'host'",
        (host_name,)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            """UPDATE nodes
               SET parent_id = %s,
                   metadata  = COALESCE(%s, metadata)
               WHERE id = %s""",
            (lan_id, metadata, row['id'])
        )
        return row['id']

    cursor.execute(
        "INSERT INTO nodes (name, type, parent_id, metadata) VALUES (%s, 'host', %s, %s)",
        (host_name, lan_id, metadata)
    )
    return cursor.lastrowid

def handle_agents(cursor, manifest, host_id):
    incoming_names = []
    # manifest is a list of strings or dicts {"name": ..., "description": ...}
    for agent in manifest:
        if isinstance(agent, dict):
            agent_name = agent.get('name')
            agent_desc = agent.get('description')
        else:
            agent_name = agent
            agent_desc = None

        metadata = json.dumps({"description": agent_desc}) if agent_desc else None
        incoming_names.append(agent_name)

        cursor.execute(
            "SELECT id FROM nodes WHERE name = %s AND type = 'agent'",
            (agent_name,)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                """UPDATE nodes
                   SET parent_id = %s,
                       metadata  = COALESCE(%s, metadata)
                   WHERE id = %s""",
                (host_id, metadata, row['id'])
            )
        else:
            cursor.execute(
                "INSERT INTO nodes (name, type, parent_id, metadata) VALUES (%s, 'agent', %s, %s)",
                (agent_name, host_id, metadata)
            )
    # prune agents not appearing in this manifest
    if incoming_names:
        placeholders = ','.join(['%s'] * len(incoming_names))
        cursor.execute(
            f"""DELETE FROM nodes
                WHERE type = 'agent'
                AND parent_id = %s
                AND name NOT IN ({placeholders})""",
            (host_id, *incoming_names)
        )
    else:
        # incoming agents list was empty — remove all agents on this host
        cursor.execute(
            "DELETE FROM nodes WHERE type = 'agent' AND parent_id = %s",
            (host_id,)
        )

def get_graph():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nodes")
    nodes = cursor.fetchall()
    cursor.execute("SELECT * FROM edges")
    edges = cursor.fetchall()
    db.close()
    return {"nodes": nodes, "edges": edges}

def clean_database():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Find all host nodes with no parent
    cursor.execute("""
        SELECT id FROM nodes
        WHERE type = 'host'
          AND (
            parent_id IS NULL
            OR id NOT IN (SELECT DISTINCT parent_id FROM nodes WHERE parent_id IS NOT NULL)
          )
    """)
    orphaned_hosts = [row['id'] for row in cursor.fetchall()]

    if not orphaned_hosts:
        return 0

    fmt = ','.join(['%s'] * len(orphaned_hosts))

    # Delete related edges first (FK integrity)
    cursor.execute(f"""
        DELETE FROM edges
        WHERE source_id IN ({fmt})
           OR target_id IN ({fmt})
    """, orphaned_hosts + orphaned_hosts)

    # Delete the orphaned host nodes
    cursor.execute(f"""
        DELETE FROM nodes
        WHERE id IN ({fmt})
    """, orphaned_hosts)

    db.commit()
    cursor.close()

    return len(orphaned_hosts)