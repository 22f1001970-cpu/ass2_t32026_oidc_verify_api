"""TDS mock OIDC: strict RS256 JWT verification."""
import os

import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from jwt.exceptions import InvalidTokenError

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-qtyhfe94.apps.exam.local"
app = FastAPI(title="OIDC Token Verification Service")

class VerifyRequest(BaseModel):
    token: str = Field(min_length=1)

@app.post("/verify")
def verify(payload: VerifyRequest):
    pem = os.environ.get("JWT_PUBLIC_KEY", "").replace("\\n", "\n").strip()
    if not pem:
        raise HTTPException(status_code=503, detail="Verification key not configured")
    try:
        claims = jwt.decode(
            payload.token,
            pem,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["exp", "iss", "aud", "sub", "email"]},
            leeway=0,
        )
        return {
            "valid": True,
            "email": claims["email"],
            "sub": claims["sub"],
            "aud": claims["aud"],
        }
    except (InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail={"valid": False})

@app.get("/")
def health():
    return {"status": "ok", "endpoint": "/verify"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    if exc.status_code == 401:
        return JSONResponse(status_code=401, content={"valid": False})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
