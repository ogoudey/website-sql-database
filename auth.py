from flask import request, abort

# --- Auth ---
API_KEY = "poppoppop"

def verify_key():
    if request.headers.get("X-API-Key") != API_KEY:
        abort(403)
