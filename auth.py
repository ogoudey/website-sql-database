from fastapi.security.api_key import APIKeyHeader
from fastapi import HTTPException, Security

# --- Auth ---
API_KEY = "poppoppop"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key
