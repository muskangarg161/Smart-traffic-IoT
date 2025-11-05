import os
from fastapi import HTTPException, Header

API_KEY = os.getenv("API_KEY", "dev-secret-key")

def require_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
