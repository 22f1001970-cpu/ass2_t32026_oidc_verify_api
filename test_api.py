import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from main import app, ISSUER, AUDIENCE

client = TestClient(app)

@pytest.fixture
def keys(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    monkeypatch.setenv("JWT_PUBLIC_KEY", public)
    return private

def make_token(private, **overrides):
    d = dict(iss=ISSUER, aud=AUDIENCE, sub="abc", email="a@example.com", exp=datetime.now(timezone.utc) + timedelta(minutes=5))
    d.update(overrides)
    return jwt.encode(d, private, algorithm="RS256")

def test_valid(keys):
    response = client.post("/verify", json={"token": make_token(keys)})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "email": "a@example.com", "sub": "abc", "aud": AUDIENCE}

def test_expired(keys):
    r = client.post("/verify", json={"token": make_token(keys, exp=datetime.now(timezone.utc)-timedelta(minutes=2))})
    assert r.status_code == 401 and r.json() == {"valid": False}

def test_bad_audience(keys):
    r = client.post("/verify", json={"token": make_token(keys, aud="wrong")})
    assert r.status_code == 401 and r.json() == {"valid": False}

def test_bad_issuer(keys):
    r = client.post("/verify", json={"token": make_token(keys, iss="https://other")})
    assert r.status_code == 401 and r.json() == {"valid": False}

def test_tampered(keys):
    token = make_token(keys)
    head, body, sig = token.split(".")
    tampered = f"{head}.{body}.{('A' if sig[0] != 'A' else 'B') + sig[1:]}"
    r = client.post("/verify", json={"token": tampered})
    assert r.status_code == 401 and r.json() == {"valid": False}

def test_missing_config(monkeypatch):
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)
    assert client.post("/verify", json={"token": "abc"}).status_code == 503
