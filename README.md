# TDS OAuth 2.0 / OIDC Token Verification Service

A FastAPI `POST /verify` endpoint that validates a signed RS256 JWT against the assigned issuer, audience, expiry, and RSA public key.

## Required configuration (important!)

The screenshot's RSA public key is not provided in this ZIP because the exact bytes must be copied from your assignment page. **Without the correct key, the grader will fail valid tokens.**

On Render, add an environment variable:

- **Key:** `JWT_PUBLIC_KEY`
- **Value:** Paste the **entire** `-----BEGIN PUBLIC KEY-----` through `-----END PUBLIC KEY-----` block from your assignment's *IdP public key (RS256)* field. Keep each line exactly as given. You can also use literal `\\n` between lines if your Render editor won't accept newlines.

Do not paste your personal API key, AI Pipe token, or private signing key here. This is a public verification key.

The assigned issuer and audience are already set in `main.py`:

- Issuer: `https://idp.exam.local`
- Audience: `tds-qtyhfe94.apps.exam.local`

**Double-check these strings against your own assignment page.** If yours differs, update the constants in `main.py`.

## GitHub and Render deployment

1. Create a public GitHub repository and upload the contents of this folder (so `main.py` is at the repository root).
2. On https://dashboard.render.com select **New -> Web Service**, connect the repo, choose Python and the free plan if available.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add `JWT_PUBLIC_KEY` in **Environment**, paste the exact public key, and deploy (or redeploy if you add it afterward).
6. Submit `https://YOUR-APP.onrender.com/verify` **including `/verify`**.

Alternative: select **New -> Blueprint** to apply `render.yaml`; Render should prompt you for the unsynced public key.

## Endpoint behavior

Request: `POST /verify` with JSON `{"token": "<JWT>"}`.

Valid response (200): `{"valid": true, "email": "...", "sub": "...", "aud": "..."}`.

Invalid signature, issuer, audience, or expired JWT response (401): `{"valid": false}`.

Missing public key on server returns 503 until configured.

Only `RS256` is accepted. Required claims: `exp`, `iss`, `aud`, `sub`, `email`.

## Tests

`pip install -r requirements-dev.txt && pytest -q`

The tests create a throwaway keypair and do not require the assignment public key.
